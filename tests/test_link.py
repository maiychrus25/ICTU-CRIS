# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import pytest
from cris import link, rules

def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None

def mk_work(conn, title="w"):
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) VALUES (1,'manual',%s,'bai_bao','h',%s)", title, "{}")
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) VALUES ('bai_bao', currval('source_record_id_seq'), %s, %s, 'DaChuanHoa') RETURNING id", title, title)[0]["id"]

def mk_mention(conn, work_id, raw, degree=None, position=1):
    nb = rules.RULES_V1["name_norm"]
    nn, deg = rules.norm_name(raw, nb)
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, degree_raw, is_placeholder) VALUES (%s,'author',%s,%s,%s,%s,%s,%s) RETURNING id",
             work_id, position, raw, nn, rules.name_key(nn), degree or deg, rules.is_placeholder(raw, nb))[0]["id"]

def mk_person(conn, name, degree=None, orcid=None, verified=False, email=None):
    nb = rules.RULES_V1["name_norm"]
    nn, _ = rules.norm_name(name, nb)
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, degree_raw, orcid, orcid_verified, email) VALUES ('lecturer',%s,%s,%s,%s,%s,%s,%s) RETURNING id",
             name, nn, [rules.name_key(nn)], degree, orcid, verified, email)[0]["id"]

@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)

def test_unique_full_name_links_automatically(conn):
    w = mk_work(conn); p = mk_person(conn, "Nguyễn Thế Vịnh")
    m = mk_mention(conn, w, "The-Vinh Nguyen")
    assert link.link_pending(conn)["auto"] == 1
    l = q(conn, "SELECT * FROM author_link")[0]
    assert (l["mention_id"], l["person_id"], l["confidence"], l["state"]) == (m, p, "ten_day_du_duy_nhat", "DaNoiTuDong")

def test_two_candidates_go_to_queue(conn):
    w = mk_work(conn); mk_person(conn, "Nguyễn Văn An", email="a1@x"); mk_person(conn, "Nguyễn Văn An", email="a2@x")
    mk_mention(conn, w, "Nguyễn Văn An")
    assert link.link_pending(conn)["queued"] == 1
    ls = q(conn, "SELECT confidence, state FROM author_link")
    assert len(ls) == 2 and all(l["state"] == "ChoXacNhan" and l["confidence"] == "ten_day_du_nhieu_ung_vien" for l in ls)

def test_degree_conflict_blocks_auto_link(conn):
    w = mk_work(conn); mk_person(conn, "Nguyễn Đình Dũng", degree="TS")
    mk_mention(conn, w, "ThS. Nguyễn Đình Dũng")
    out = link.link_pending(conn)
    assert out == {"auto": 0, "queued": 1, "none": 0}
    l = q(conn, "SELECT state, degree_conflict FROM author_link")[0]
    assert l["state"] == "ChoXacNhan" and l["degree_conflict"] is True

def test_partial_name_is_queued_as_ten_mot_phan(conn):
    w = mk_work(conn); mk_person(conn, "Nguyễn Thị Vân Anh")
    mk_mention(conn, w, "Van Anh Nguyen")
    link.link_pending(conn)
    assert q(conn, "SELECT confidence FROM author_link")[0]["confidence"] == "ten_mot_phan"

def test_placeholder_never_linked_and_no_candidate_is_none(conn):
    w = mk_work(conn); p = mk_person(conn, "Ai Đó")
    mk_mention(conn, w, "ICTU_TEACHER", position=1); mk_mention(conn, w, "Người Lạ Hoắc", position=2)
    assert link.link_pending(conn) == {"auto": 0, "queued": 0, "none": 1}
    assert q(conn, "SELECT 1 FROM author_link") == []

def test_rejected_pair_is_not_proposed_again(conn, user_id):
    w = mk_work(conn); p = mk_person(conn, "Nguyễn Thị Vân Anh")
    m = mk_mention(conn, w, "Van-Anh Nguyen Thi")
    link.link_pending(conn)
    lid = q(conn, "SELECT id FROM author_link")[0]["id"]
    link.decide_link(conn, lid, "reject", user_id, reason="người trùng tên ở trường khác")
    assert link.link_pending(conn) == {"auto": 0, "queued": 0, "none": 1}
    ls = q(conn, "SELECT state, reason FROM author_link")
    assert ls == [{"state": "DaBacBo", "reason": "người trùng tên ở trường khác"}]
    assert q(conn, "SELECT action FROM audit_log")[-1]["action"] == "link.reject"

def test_confirm_learns_name_variant(conn, user_id):
    w = mk_work(conn); p = mk_person(conn, "Nguyễn Thị Vân Anh")
    mk_mention(conn, w, "Van Anh Nguyen")
    link.link_pending(conn)
    lid = q(conn, "SELECT id FROM author_link")[0]["id"]
    link.decide_link(conn, lid, "confirm", user_id)
    assert q(conn, "SELECT state FROM author_link")[0]["state"] == "DaXacNhan"
    assert "anh nguyen van" in q(conn, "SELECT name_keys FROM person WHERE id=%s", p)[0]["name_keys"]
    w2 = mk_work(conn, "w2"); mk_mention(conn, w2, "Van Anh Nguyen")
    assert link.link_pending(conn)["auto"] == 1

def test_confirm_rejected_link_raises(conn, user_id):
    w = mk_work(conn); mk_person(conn, "Nguyễn Thị Vân Anh")
    mk_mention(conn, w, "Van Anh Nguyen")
    link.link_pending(conn)
    lid = q(conn, "SELECT id FROM author_link")[0]["id"]
    link.decide_link(conn, lid, "reject", user_id, reason="trùng tên")
    with pytest.raises(ValueError):
        link.decide_link(conn, lid, "confirm", user_id)
    assert q(conn, "SELECT state FROM author_link WHERE id=%s", lid)[0]["state"] == "DaBacBo"

def test_reassign_records_new_link_in_audit(conn, user_id):
    w = mk_work(conn)
    mk_person(conn, "Nguyễn Văn An", email="a1@x"); mk_person(conn, "Nguyễn Văn An", email="a2@x")
    p3 = mk_person(conn, "Trần Văn Ba", email="a3@x")
    mk_mention(conn, w, "Nguyễn Văn An")
    link.link_pending(conn)
    lid = q(conn, "SELECT id FROM author_link ORDER BY id LIMIT 1")[0]["id"]
    link.decide_link(conn, lid, "reassign", user_id, person_id=p3)
    new_row = q(conn, "SELECT id FROM author_link WHERE person_id=%s AND state='DaXacNhan'", p3)[0]
    a = q(conn, "SELECT action, after FROM audit_log ORDER BY id DESC LIMIT 1")[0]
    assert a["action"] == "link.reassign"
    assert a["after"]["person_id"] == p3
    assert a["after"]["new_link_id"] == new_row["id"]

def test_reassign_overrides_earlier_rejection(conn, user_id):
    w = mk_work(conn)
    p_a = mk_person(conn, "Nguyễn Văn An", email="a1@x")
    p_b = mk_person(conn, "Nguyễn Văn An", email="a2@x")
    mk_mention(conn, w, "Nguyễn Văn An")
    link.link_pending(conn)
    rows = {r["person_id"]: r["id"] for r in q(conn, "SELECT id, person_id FROM author_link")}
    link.decide_link(conn, rows[p_b], "reject", user_id, reason="trùng tên")
    link.decide_link(conn, rows[p_a], "reassign", user_id, person_id=p_b)
    final = {r["person_id"]: r for r in q(conn, "SELECT person_id, state, reason FROM author_link")}
    assert final[p_b]["state"] == "DaXacNhan" and final[p_b]["reason"] is None
    assert final[p_a]["state"] == "DaBacBo"

def test_conflict_treats_unranked_degrees_as_distinct():
    assert link._conflict("KS", "CN") is True
    assert link._conflict("PGS", "PGS.TS") is False
    assert link._conflict("TS", "PGS.TS") is True
    assert link._conflict(None, "TS") is False

def test_orcid_links_only_when_verified(conn):
    w = mk_work(conn)
    p = mk_person(conn, "Trần X", orcid="0000-0001-2345-6789", verified=True)
    m = mk_mention(conn, w, "X Tran")
    q(conn, "UPDATE author_mention SET name_key='khac' WHERE id=%s", m)   # tên không khớp, chỉ còn ORCID
    link.link_by_orcid(conn, m, "0000-0001-2345-6789")
    assert q(conn, "SELECT confidence, state FROM author_link")[0] == {"confidence": "orcid", "state": "DaNoiTuDong"}
    q(conn, "UPDATE person SET orcid_verified=false WHERE id=%s", p); q(conn, "DELETE FROM author_link")
    link.link_by_orcid(conn, m, "0000-0001-2345-6789")
    assert q(conn, "SELECT state FROM author_link")[0]["state"] == "ChoXacNhan"


def test_decide_link_unknown_id_gives_a_readable_error(conn, user_id):
    """id không tồn tại phải báo rõ, không nổ AttributeError/TypeError ở bước audit."""
    for decision, kw in (("confirm", {}), ("reject", {"reason": "x"}), ("reassign", {"person_id": 1})):
        with pytest.raises(ValueError) as ei:
            link.decide_link(conn, 999999, decision, user_id, **kw)
        assert "999999" in str(ei.value) or "chỉ xác nhận được" in str(ei.value)
        conn.rollback()


def test_reassign_without_person_id_is_refused(conn, user_id):
    """Phải dựng liên kết thật: id không tồn tại sẽ dừng ở kiểm tra tồn tại trước."""
    w = mk_work(conn)
    mk_person(conn, "Nguyễn Văn An", email="a1@x")
    mk_person(conn, "Nguyễn Văn An", email="a2@x")
    mk_mention(conn, w, "Nguyễn Văn An")
    link.link_pending(conn)
    lid = q(conn, "SELECT id FROM author_link ORDER BY id LIMIT 1")[0]["id"]
    with pytest.raises(ValueError, match="person_id"):
        link.decide_link(conn, lid, "reassign", user_id)
