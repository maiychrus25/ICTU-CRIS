# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json
from collections import defaultdict
from cris import audit
from cris import rules as RU
from cris.db import tx

COMPARE = ("title", "doi", "year_issue", "journal", "volume", "pub_type_raw", "cohort")
MERGEABLE = ("title", "doi", "journal", "volume", "year_issue", "abstract", "keywords_raw",
             "pub_type_raw", "indexes", "quartile", "venue_kind", "score", "cohort")
ELIGIBLE_STATES = ("DaChuanHoa", "NghiTrung", "DaXacNhan", "GiuRieng")
NEW_SUSPECT_STATES = ("DaChuanHoa", "NghiTrung")

def _diff(w, others):
    return {k: {"this": w.get(k), "others": [o.get(k) for o in others]}
            for k in COMPARE if any(w.get(k) != o.get(k) for o in others)}

def _open_groups_members(cur):
    # chỉ nhóm đang chờ quyết (NghiTrung) mới khoá thành viên khỏi bị nhóm lại;
    # nhóm đã quyết (DaGop/GiuRieng) không còn giữ work ở trạng thái đủ điều kiện
    # (trừ người sống sót DaXacNhan, vốn cần được nhóm lại nếu có nghi trùng mới)
    cur.execute("SELECT work_id FROM duplicate_member m JOIN duplicate_group g ON g.id=m.group_id WHERE g.state = 'NghiTrung'")
    return {r["work_id"] for r in cur.fetchall()}

def find_duplicates(conn):
    rules = RU.load_active(conn)["dedup"][1]
    out = {"groups": 0, "group_hint": 0}
    with tx(conn), conn.cursor() as cur:
        busy = _open_groups_members(cur)
        cur.execute("SELECT * FROM work WHERE merged_into_id IS NULL AND state = ANY(%s)", (list(ELIGIBLE_STATES),))
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
                    elif basis == "title_norm":
                        buckets[w["title_norm"]].append(w)
                    elif basis == "title_student_cohort":
                        buckets[(w["title_norm"], w["cohort"])].append(w)
                for key, members in buckets.items():
                    if len(members) < 2:
                        continue
                    if not any(m["state"] in NEW_SUSPECT_STATES for m in members):
                        continue  # toàn bộ đã DaXacNhan: không phải nghi trùng mới
                    hint = None
                    if basis == "title_student_cohort":
                        studs = [students.get(w["id"], set()) for w in members]
                        if any(s and t and not (s & t) for i, s in enumerate(studs) for t in studs[i + 1:]):
                            hint = "nhiều khả năng là đồ án nhóm: cùng tiêu đề, khác sinh viên"
                    cur.execute("INSERT INTO duplicate_group(doc_type, basis, hint) VALUES (%s,%s,%s) RETURNING id", (doc_type, basis, hint))
                    gid = cur.fetchone()["id"]
                    for w in members:
                        others = [o for o in members if o["id"] != w["id"]]
                        cur.execute("INSERT INTO duplicate_member(group_id, work_id, diff) VALUES (%s,%s,%s)",
                                    (gid, w["id"], json.dumps(_diff(w, others), ensure_ascii=False, default=str)))
                        if w["state"] not in ("DaXacNhan", "GiuRieng"):
                            cur.execute("UPDATE work SET state='NghiTrung', updated_at=now() WHERE id=%s", (w["id"],))
                        grouped.add(w["id"])
                    out["groups"] += 1
                    out["group_hint"] += bool(hint)
    return out

def decide_group(conn, group_id, decision, actor_id, survivor_id=None, field_choices=None, reason=None):
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT state FROM duplicate_group WHERE id=%s", (group_id,))
        g = cur.fetchone()
        if not g or g["state"] != "NghiTrung":
            raise ValueError("nhóm không ở trạng thái nghi trùng")
        cur.execute("SELECT work_id FROM duplicate_member WHERE group_id=%s", (group_id,))
        members = [r["work_id"] for r in cur.fetchall()]
        if decision == "merge":
            if survivor_id not in members:
                raise ValueError("survivor phải thuộc nhóm")
            if any(f not in MERGEABLE for f in (field_choices or {})):
                raise ValueError("trường không được phép gộp")
            for field, from_id in (field_choices or {}).items():
                if from_id == survivor_id or from_id not in members:
                    continue
                cur.execute(f"SELECT {field} AS v FROM work WHERE id=%s", (from_id,))
                v = cur.fetchone()["v"]
                cur.execute(f"UPDATE work SET {field}=%s, updated_at=now() WHERE id=%s", (v, survivor_id))
                if field == "title":
                    cur.execute("UPDATE work SET title_norm=%s WHERE id=%s", (RU.norm_title(v), survivor_id))
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
