import json
from collections import defaultdict
from cris import audit
from cris import rules as RU
from cris.db import tx

COMPARE = ("title", "doi", "year_issue", "journal", "volume", "pub_type_raw", "cohort")

def _diff(a, b):
    return {k: {"this": a.get(k), "other": b.get(k)} for k in COMPARE if a.get(k) != b.get(k)}

def _open_groups_members(cur):
    cur.execute("SELECT work_id FROM duplicate_member m JOIN duplicate_group g ON g.id=m.group_id WHERE g.state <> 'BoQua'")
    return {r["work_id"] for r in cur.fetchall()}

def find_duplicates(conn):
    rules = RU.load_active(conn)["dedup"][1]
    out = {"groups": 0, "group_hint": 0}
    with tx(conn), conn.cursor() as cur:
        busy = _open_groups_members(cur)
        cur.execute("SELECT * FROM work WHERE merged_into_id IS NULL AND state IN ('DaChuanHoa','NghiTrung')")
        works = [w for w in cur.fetchall() if w["id"] not in busy]
        cur.execute("SELECT work_id, name_key FROM author_mention WHERE role='student' AND position > 0")
        students = defaultdict(set)
        for r in cur.fetchall():
            students[r["work_id"]].add(r["name_key"])
        grouped = set()
        for doc_type, bases in rules.items():
            ws = [w for w in works if w["doc_type"] == doc_type]
            for basis in bases:
                buckets = defaultdict(list)
                for w in ws:
                    if w["id"] in grouped:
                        continue
                    if basis == "doi" and w["doi"]:
                        buckets[w["doi"]].append(w)
                    elif basis == "title_norm" and not w["doi"]:
                        buckets[w["title_norm"]].append(w)
                    elif basis == "title_student_cohort":
                        buckets[(w["title_norm"], w["cohort"])].append(w)
                for key, members in buckets.items():
                    if len(members) < 2:
                        continue
                    hint = None
                    if basis == "title_student_cohort":
                        studs = [students.get(w["id"], set()) for w in members]
                        if any(not (s & t) for i, s in enumerate(studs) for t in studs[i + 1:]):
                            hint = "nhiều khả năng là đồ án nhóm: cùng tiêu đề, khác sinh viên"
                    cur.execute("INSERT INTO duplicate_group(doc_type, basis, hint) VALUES (%s,%s,%s) RETURNING id", (doc_type, basis, hint))
                    gid = cur.fetchone()["id"]
                    for w in members:
                        others = [o for o in members if o["id"] != w["id"]]
                        cur.execute("INSERT INTO duplicate_member(group_id, work_id, diff) VALUES (%s,%s,%s)",
                                    (gid, w["id"], json.dumps(_diff(w, others[0]), ensure_ascii=False, default=str)))
                        cur.execute("UPDATE work SET state='NghiTrung', updated_at=now() WHERE id=%s", (w["id"],))
                        grouped.add(w["id"])
                    out["groups"] += 1
                    out["group_hint"] += bool(hint)
    return out

def decide_group(conn, group_id, decision, actor_id, survivor_id=None, field_choices=None, reason=None):
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT work_id FROM duplicate_member WHERE group_id=%s", (group_id,))
        members = [r["work_id"] for r in cur.fetchall()]
        if decision == "merge":
            if survivor_id not in members:
                raise ValueError("survivor phải thuộc nhóm")
            for field, from_id in (field_choices or {}).items():
                if from_id == survivor_id or from_id not in members:
                    continue
                cur.execute(f"SELECT {field} AS v FROM work WHERE id=%s", (from_id,))
                v = cur.fetchone()["v"]
                cur.execute(f"UPDATE work SET {field}=%s, updated_at=now() WHERE id=%s", (v, survivor_id))
                cur.execute("INSERT INTO field_provenance(work_id, field, raw_value, value, set_kind, set_by) VALUES (%s,%s,%s,%s,'merge',%s)",
                            (survivor_id, field, f"from work {from_id}", str(v), actor_id))
            for wid in members:
                if wid != survivor_id:
                    cur.execute("UPDATE work SET state='DaGop', merged_into_id=%s, updated_at=now() WHERE id=%s", (survivor_id, wid))
            cur.execute("UPDATE work SET state='DaXacNhan', updated_at=now() WHERE id=%s", (survivor_id,))
            cur.execute("UPDATE duplicate_group SET state='DaGop', survivor_work_id=%s, decided_by=%s, decided_at=now(), reason=%s WHERE id=%s",
                        (survivor_id, actor_id, reason, group_id))
        elif decision == "keep":
            if not reason:
                raise ValueError("lý do bắt buộc khi giữ riêng")
            for wid in members:
                cur.execute("UPDATE work SET state='GiuRieng', updated_at=now() WHERE id=%s", (wid,))
            cur.execute("UPDATE duplicate_group SET state='GiuRieng', decided_by=%s, decided_at=now(), reason=%s WHERE id=%s", (actor_id, reason, group_id))
        elif decision == "skip":
            cur.execute("UPDATE duplicate_group SET state='BoQua', decided_by=%s, decided_at=now(), reason=%s WHERE id=%s", (actor_id, reason, group_id))
        else:
            raise ValueError(decision)
        audit.log(conn, actor_id, f"dup.{decision}", "duplicate_group", group_id,
                  after={"members": members, "survivor": survivor_id, "fields": field_choices, "reason": reason})
