import json
import re
from cris import audit
from cris import rules as RU
from cris.db import tx

WORK_TYPES = ("bai_bao", "do_an", "luan_van", "luan_an", "hoc_lieu")
FIELDS = ("title", "title_norm", "doi", "journal", "volume", "year_issue", "abstract", "keywords_raw",
          "pub_type_raw", "indexes", "quartile", "venue_kind", "score", "needs_review", "cohort")

def _first(meta, labels):
    for lab in labels:
        if lab in meta and meta[lab]:
            return meta[lab]
    return None

def _year(s):
    m = re.search(r"(19|20)\d{2}", s or "")
    return int(m.group(0)) if m else None

def _doi(detail, archive):
    for u in (detail or {}).get("doi") or []:
        return re.sub(r"^https?://doi\.org/", "", u).strip().lower()
    return None

def extract_fields(rec, rules):
    raw = rec["raw"]
    arc, det = raw.get("archive", {}), raw.get("detail") or {}
    meta = {**(arc.get("meta") or {}), **(det.get("meta") or {})}
    fm = rules["field_map"][1]
    nb = rules["name_norm"][1]
    f = {"title": det.get("title") or arc.get("title") or "", "journal": arc.get("journal"),
         "volume": arc.get("volume"), "abstract": det.get("abstract") or arc.get("abstract"),
         "keywords_raw": arc.get("keywords"), "pub_type_raw": arc.get("pub_type"),
         "cohort": _first(meta, fm["cohort"]), "doi": _doi(det, arc),
         "year_issue": _year(arc.get("year")) or _year(_first(meta, fm["year"]))}
    f["title_norm"] = RU.norm_title(f["title"])
    if rec["doc_type"] == "bai_bao":
        f.update(RU.map_pub_type(f["pub_type_raw"], rules["pub_type_map"][1]))
        if f["pub_type_raw"] is None:
            f["needs_review"] = True
    else:
        f.update({"indexes": [], "quartile": None, "venue_kind": None, "score": None, "needs_review": False})

    mentions, truncated = [], False
    if rec["doc_type"] == "bai_bao":
        if det.get("authors"):
            names = det["authors"]
        else:
            names, truncated = RU.split_names(arc.get("authors"), nb)
        mentions += [{"role": "author", "raw_name": n} for n in names]
    else:
        student = _first(meta, fm["student"])
        if student:
            mentions += [{"role": "student", "raw_name": n} for n in RU.split_names(student, nb)[0]]
        for m in arc.get("mentors") or []:
            mentions += [{"role": "mentor", "raw_name": n} for n in RU.split_names(m.get("name"), nb)[0]]
    f["mentions"] = mentions
    f["authors_truncated"] = truncated
    return f

def _pending(cur):
    cur.execute("""
        SELECT s.* FROM source_record s
        WHERE s.status='active' AND s.doc_type = ANY(%s)
          AND s.version = (SELECT max(version) FROM source_record x WHERE x.source=s.source AND x.source_key=s.source_key)
          AND NOT EXISTS (SELECT 1 FROM work w WHERE w.primary_source_record_id = s.id)
        ORDER BY s.id""", (list(WORK_TYPES),))
    return cur.fetchall()

def normalize_record(conn, rec, rules, actor_id=None):
    f = extract_fields(rec, rules)
    rs_id = rules["name_norm"][0]
    nb = rules["name_norm"][1]
    with conn.cursor() as cur:
        cur.execute("""SELECT w.id FROM work w JOIN source_record s ON s.id=w.primary_source_record_id
                       WHERE s.source=%s AND s.source_key=%s AND w.merged_into_id IS NULL""",
                    (rec["source"], rec["source_key"]))
        existing = cur.fetchone()
        cols = {k: f[k] for k in FIELDS}
        cols["indexes"] = list(cols["indexes"])
        protected = set()
        if existing:
            work_id = existing["id"]
            cur.execute("""SELECT DISTINCT ON (field) field, set_kind FROM field_provenance
                           WHERE work_id=%s ORDER BY field, set_at DESC""", (work_id,))
            protected = {r["field"] for r in cur.fetchall() if r["set_kind"] in ("manual", "merge")}
            upd_cols = {k: v for k, v in cols.items() if k not in protected}
            sets = ", ".join(f"{k}=%s" for k in upd_cols)
            extra = "primary_source_record_id=%s, rule_set_id=%s, updated_at=now()"
            cur.execute(f"UPDATE work SET {(sets + ', ' + extra) if sets else extra} WHERE id=%s",
                        (*upd_cols.values(), rec["id"], rs_id, work_id))
            # giải phóng vị trí đang active (không vi phạm UNIQUE) trước khi khớp lại theo name_key;
            # không đụng tới các hàng đã mồ côi từ chu kỳ trước (đang giữ position âm)
            cur.execute("UPDATE author_mention SET position = -position WHERE work_id=%s AND position > 0 RETURNING id", (work_id,))
            freed = {r["id"] for r in cur.fetchall()}
            cur.execute("DELETE FROM author_mention WHERE work_id=%s AND id NOT IN (SELECT mention_id FROM author_link)", (work_id,))
        else:
            names = ", ".join(cols)
            ph = ", ".join(["%s"] * len(cols))
            cur.execute(f"INSERT INTO work(doc_type, primary_source_record_id, rule_set_id, state, {names}) VALUES (%s,%s,%s,'DaChuanHoa',{ph}) RETURNING id",
                        (rec["doc_type"], rec["id"], rs_id, *cols.values()))
            work_id = cur.fetchone()["id"]
        arc = rec["raw"].get("archive", {})
        raw_map = {"title": (rec["raw"].get("detail") or {}).get("title") or arc.get("title"),
                   "pub_type_raw": arc.get("pub_type"), "year_issue": arc.get("year"),
                   "doi": ",".join((rec["raw"].get("detail") or {}).get("doi") or [])}
        for k, v in cols.items():
            if k in protected or v in (None, [], ""):
                continue
            cur.execute("""SELECT value FROM field_provenance WHERE work_id=%s AND field=%s ORDER BY set_at DESC LIMIT 1""", (work_id, k))
            last = cur.fetchone()
            val = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, bool)) else str(v)
            if last and last["value"] == val:
                continue
            cur.execute("INSERT INTO field_provenance(work_id, field, raw_value, value, source_record_id, set_kind) VALUES (%s,%s,%s,%s,%s,'normalize')",
                        (work_id, k, raw_map.get(k), val, rec["id"]))
        pos, matched = {}, set()
        for m in f["mentions"]:
            pos[m["role"]] = pos.get(m["role"], 0) + 1
            nn, deg = RU.norm_name(m["raw_name"], nb)
            nk = RU.name_key(nn)
            is_ph = RU.is_placeholder(m["raw_name"], nb)
            is_tr = f["authors_truncated"] and m["role"] == "author"
            if existing:
                # chỉ khớp với hàng chưa nhận (position âm: mồ côi cũ hoặc vừa giải phóng ở trên);
                # tên trùng lặp trong cùng bản ghi mới sẽ không giành lại cùng một hàng đã khớp
                cur.execute("SELECT id FROM author_mention WHERE work_id=%s AND role=%s AND name_key=%s AND position < 0 ORDER BY id",
                            (work_id, m["role"], nk))
                candidates = [r["id"] for r in cur.fetchall() if r["id"] not in matched]
                if candidates:
                    matched.add(candidates[0])
                    cur.execute("""UPDATE author_mention SET position=%s, raw_name=%s, name_norm=%s, degree_raw=%s,
                                   is_placeholder=%s, is_truncated=%s WHERE id=%s""",
                                (pos[m["role"]], m["raw_name"], nn, deg, is_ph, is_tr, candidates[0]))
                    continue
            cur.execute("""INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, degree_raw, is_placeholder, is_truncated)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (work_id, m["role"], pos[m["role"]], m["raw_name"], nn, nk, deg, is_ph, is_tr))
        if existing:
            # chỉ ghi audit cho hàng vừa chuyển từ active sang mồ côi ở chu kỳ này (freed nhưng không được khớp lại);
            # mồ côi từ chu kỳ trước (đã nằm ngoài freed) không bị ghi lặp lại
            newly_orphaned = freed - matched
            if newly_orphaned:
                cur.execute("SELECT id, name_key FROM author_mention WHERE id = ANY(%s)", (list(newly_orphaned),))
                for orphan in cur.fetchall():
                    audit.log(conn, actor_id, "mention.orphaned", "author_mention", orphan["id"],
                              before={"work_id": work_id, "name_key": orphan["name_key"]})
    return work_id, bool(existing)

def normalize_pending(conn, actor_id=None):
    rules = RU.load_active(conn)
    out = {"created": 0, "updated": 0, "skipped": 0}
    with tx(conn), conn.cursor() as cur:
        pending = _pending(cur)
        cur.execute("SELECT count(*) AS n FROM source_record s WHERE s.status='active' AND s.doc_type = ANY(%s) AND EXISTS (SELECT 1 FROM work w WHERE w.primary_source_record_id=s.id)", (list(WORK_TYPES),))
        out["skipped"] = cur.fetchone()["n"]
        for rec in pending:
            _, updated = normalize_record(conn, rec, rules, actor_id)
            out["updated" if updated else "created"] += 1
    return out
