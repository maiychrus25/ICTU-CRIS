import json
import re
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
    f.update(RU.map_pub_type(f["pub_type_raw"], rules["pub_type_map"][1]))
    if rec["doc_type"] == "bai_bao" and f["pub_type_raw"] is None:
        f["needs_review"] = True

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
        if existing:
            work_id = existing["id"]
            sets = ", ".join(f"{k}=%s" for k in cols)
            cur.execute(f"UPDATE work SET {sets}, primary_source_record_id=%s, rule_set_id=%s, updated_at=now() WHERE id=%s",
                        (*cols.values(), rec["id"], rs_id, work_id))
            cur.execute("DELETE FROM author_mention WHERE work_id=%s AND id NOT IN (SELECT mention_id FROM author_link)", (work_id,))
        else:
            names = ", ".join(cols)
            ph = ", ".join(["%s"] * len(cols))
            cur.execute(f"INSERT INTO work(doc_type, primary_source_record_id, rule_set_id, state, {names}) VALUES (%s,%s,%s,'DaChuanHoa',{ph}) RETURNING id",
                        (rec["doc_type"], rec["id"], rs_id, *cols.values()))
            work_id = cur.fetchone()["id"]
        raw_map = {"title": (rec["raw"].get("detail") or {}).get("title") or rec["raw"]["archive"].get("title"),
                   "pub_type_raw": rec["raw"]["archive"].get("pub_type"), "year_issue": rec["raw"]["archive"].get("year"),
                   "doi": ",".join((rec["raw"].get("detail") or {}).get("doi") or [])}
        for k, v in cols.items():
            if v in (None, [], ""):
                continue
            cur.execute("""SELECT value FROM field_provenance WHERE work_id=%s AND field=%s ORDER BY set_at DESC LIMIT 1""", (work_id, k))
            last = cur.fetchone()
            val = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, bool)) else str(v)
            if last and last["value"] == val:
                continue
            cur.execute("INSERT INTO field_provenance(work_id, field, raw_value, value, source_record_id, set_kind) VALUES (%s,%s,%s,%s,%s,'normalize')",
                        (work_id, k, raw_map.get(k), val, rec["id"]))
        pos = {}
        for m in f["mentions"]:
            pos[m["role"]] = pos.get(m["role"], 0) + 1
            nn, deg = RU.norm_name(m["raw_name"], nb)
            cur.execute("""INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, degree_raw, is_placeholder, is_truncated)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON CONFLICT (work_id, role, position) DO UPDATE SET raw_name=EXCLUDED.raw_name, name_norm=EXCLUDED.name_norm,
                             name_key=EXCLUDED.name_key, degree_raw=EXCLUDED.degree_raw, is_placeholder=EXCLUDED.is_placeholder, is_truncated=EXCLUDED.is_truncated""",
                        (work_id, m["role"], pos[m["role"]], m["raw_name"], nn, RU.name_key(nn), deg,
                         RU.is_placeholder(m["raw_name"], nb), f["authors_truncated"] and m["role"] == "author"))
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
