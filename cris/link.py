# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json
from cris import audit
from cris.db import tx

RANK = {"ThS": 1, "TS": 2, "PGS": 3, "PGS.TS": 3, "GS": 4, "GS.TS": 4}

def _conflict(a, b):
    return bool(a and b and RANK.get(a, a) != RANK.get(b, b))

def candidates(conn, m):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name_keys, degree_raw, unit_id, email FROM person WHERE active AND %s = ANY(name_keys)", (m["name_key"],))
        full = cur.fetchall()
        if full:
            conf = "ten_day_du_duy_nhat" if len(full) == 1 else "ten_day_du_nhieu_ung_vien"
            return [dict(person_id=p["id"], confidence=conf, degree_conflict=_conflict(m["degree_raw"], p["degree_raw"]),
                         basis={"name_key": m["name_key"], "unit_id": p["unit_id"], "email": p["email"]}) for p in full]
        toks = set(m["name_key"].split())
        if len(toks) < 2:
            return []
        cur.execute("SELECT id, name_keys, degree_raw, unit_id, email FROM person WHERE active")
        out = []
        for p in cur.fetchall():
            for k in p["name_keys"]:
                if toks <= set(k.split()) or (len(toks) >= 3 and set(k.split()) <= toks):
                    out.append(dict(person_id=p["id"], confidence="ten_mot_phan", degree_conflict=_conflict(m["degree_raw"], p["degree_raw"]),
                                    basis={"partial_of": k, "unit_id": p["unit_id"], "email": p["email"]}))
                    break
        return out

def _insert(cur, m_id, c, state):
    cur.execute("""INSERT INTO author_link(mention_id, person_id, confidence, basis, state, degree_conflict)
                   VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (mention_id, person_id) DO NOTHING""",
                (m_id, c["person_id"], c["confidence"], json.dumps(c["basis"], ensure_ascii=False), state, c["degree_conflict"]))
    return cur.rowcount

def link_by_orcid(conn, mention_id, orcid):
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT id, orcid_verified FROM person WHERE orcid=%s AND active", (orcid,))
        p = cur.fetchone()
        if not p:
            return False
        state = "DaNoiTuDong" if p["orcid_verified"] else "ChoXacNhan"
        return _insert(cur, mention_id, dict(person_id=p["id"], confidence="orcid", degree_conflict=False, basis={"orcid": orcid}), state) == 1

def link_pending(conn):
    out = {"auto": 0, "queued": 0, "none": 0}
    with tx(conn), conn.cursor() as cur:
        cur.execute("""SELECT m.* FROM author_mention m
                       WHERE NOT m.is_placeholder AND m.position > 0
                         AND NOT EXISTS (SELECT 1 FROM author_link l WHERE l.mention_id=m.id AND l.state IN ('DaNoiTuDong','DaXacNhan','ChoXacNhan'))
                       ORDER BY m.id""")
        for m in cur.fetchall():
            cur.execute("SELECT person_id FROM author_link WHERE mention_id=%s AND state='DaBacBo'", (m["id"],))
            rejected = {r["person_id"] for r in cur.fetchall()}
            cs = [c for c in candidates(conn, m) if c["person_id"] not in rejected]
            if not cs:
                out["none"] += 1
                continue
            if len(cs) == 1 and cs[0]["confidence"] == "ten_day_du_duy_nhat" and not cs[0]["degree_conflict"]:
                _insert(cur, m["id"], cs[0], "DaNoiTuDong"); out["auto"] += 1
            else:
                for c in cs:
                    _insert(cur, m["id"], c, "ChoXacNhan")
                out["queued"] += 1
    return out

def decide_link(conn, link_id, decision, actor_id, reason=None, person_id=None):
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT * FROM author_link WHERE id=%s", (link_id,))
        before = cur.fetchone()
        if decision == "confirm":
            cur.execute("UPDATE author_link SET state='DaXacNhan', decided_by=%s, decided_at=now() WHERE id=%s AND state IN ('ChoXacNhan','DaNoiTuDong')", (actor_id, link_id))
            if cur.rowcount == 0:
                raise ValueError("chỉ xác nhận được liên kết đang chờ hoặc đã nối tự động")
            cur.execute("UPDATE author_link SET state='DaBacBo', decided_by=%s, decided_at=now(), reason=%s WHERE mention_id=%s AND id<>%s AND state='ChoXacNhan'",
                        (actor_id, "chọn người khác", before["mention_id"], link_id))
            cur.execute("SELECT name_key FROM author_mention WHERE id=%s", (before["mention_id"],))
            key = cur.fetchone()["name_key"]
            cur.execute("UPDATE person SET name_keys = array(SELECT DISTINCT unnest(name_keys || %s::text[])) WHERE id=%s", ([key], before["person_id"]))
        elif decision == "reject":
            if not reason:
                raise ValueError("lý do bắt buộc khi bác bỏ")
            cur.execute("UPDATE author_link SET state='DaBacBo', decided_by=%s, decided_at=now(), reason=%s WHERE id=%s", (actor_id, reason, link_id))
        elif decision == "reassign":
            cur.execute("UPDATE author_link SET state='DaBacBo', decided_by=%s, decided_at=now(), reason=%s WHERE id=%s", (actor_id, reason or "chọn người khác", link_id))
            cur.execute("""INSERT INTO author_link(mention_id, person_id, confidence, basis, state, decided_by, decided_at)
                           VALUES (%s,%s,'ten_mot_phan','{"manual": true}','DaXacNhan',%s,now())
                           ON CONFLICT (mention_id, person_id) DO UPDATE SET
                             state='DaXacNhan', confidence=EXCLUDED.confidence, basis=EXCLUDED.basis,
                             decided_by=EXCLUDED.decided_by, decided_at=now(), reason=NULL
                           RETURNING id""", (before["mention_id"], person_id, actor_id))
            new_id = cur.fetchone()["id"]
        else:
            raise ValueError(decision)
        if decision == "reassign":
            audit.log(conn, actor_id, "link.reassign", "author_link", link_id,
                      before={k: str(v) for k, v in before.items()},
                      after={"new_link_id": new_id, "person_id": person_id, "state": "DaXacNhan"})
        else:
            cur.execute("SELECT * FROM author_link WHERE id=%s", (link_id,))
            after = cur.fetchone()
            audit.log(conn, actor_id, f"link.{decision}", "author_link", link_id,
                      before={k: str(v) for k, v in before.items()}, after={k: str(v) for k, v in after.items()})
