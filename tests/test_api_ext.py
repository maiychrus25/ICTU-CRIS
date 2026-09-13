# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tổng quan (`/api/stats`), xuất CSV, nhật ký thao tác (`/api/audit`) và kỳ báo cáo
(`/api/periods`) — lát cắt mở rộng E1-E4. API FastAPI trên PostgreSQL thật (fixture
`conn`), provider AI `fake` (không dùng ở đây nhưng giữ cùng khuôn với test_api_core)."""
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def mk_person(conn, name, unit_id=None, degree_raw=None, rank=None, position=None, field=None, orcid=None,
              email=None, phone=None):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id, degree_raw, rank, "
                   "position, field, orcid, email, phone) VALUES ('lecturer',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                   "RETURNING id",
             name, name.lower(), [name.lower()], unit_id, degree_raw, rank, position, field, orcid, email,
             phone)[0]["id"]


def mk_mention(conn, work_id, raw_name, position=1):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw_name, raw_name.lower(), raw_name.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state="ChoXacNhan", reason=None):
    if state == "DaBacBo" and reason is None:
        reason = "kiểm thử"  # CHECK (state <> 'DaBacBo' OR reason IS NOT NULL)
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state, reason) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat',%s,%s) RETURNING id",
             mention_id, person_id, state, reason)[0]["id"]


def due_soon(days=30):
    return datetime.now(UTC) + timedelta(days=days)


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


# ---------- E1: /api/stats ----------
def test_stats_on_empty_db_has_no_zero_division(client, conn, user_id):
    r = client.get("/api/stats").json()
    assert r["by_year_type"] == [] and r["by_unit"] == [] and r["top_persons"] == []
    assert r["coverage"]["works_with_link_pct"] == 0.0
    assert r["queues"] == {"authors_pending": 0, "dup_groups_open": 0}
    assert r["unknown_year"] == {"bai_bao": 0, "do_an": 0, "luan_van": 0, "luan_an": 0, "hoc_lieu": 0}


def test_stats_by_year_type_counts_and_unknown_year(client, conn, user_id):
    w1 = mk_work(conn, "Bài báo A", doc_type="bai_bao")
    w2 = mk_work(conn, "Đồ án B", doc_type="do_an")
    w3 = mk_work(conn, "Đồ án C", doc_type="do_an")
    q(conn, "UPDATE work SET year_issue=2024 WHERE id=%s", w1)
    q(conn, "UPDATE work SET year_issue=2025 WHERE id IN (%s,%s)", w2, w3)
    w4 = mk_work(conn, "Đồ án không rõ năm", doc_type="do_an")
    assert w4  # year_issue để NULL
    conn.commit()
    r = client.get("/api/stats", params={"years": 5}).json()
    by_year = {row["year"]: row for row in r["by_year_type"]}
    assert by_year[2024]["bai_bao"] == 1
    assert by_year[2025]["do_an"] == 2
    assert r["unknown_year"]["do_an"] == 1


def test_stats_by_unit_and_top_persons(client, conn, user_id):
    uid = mk_unit(conn)
    pid = mk_person(conn, "Nguyễn Văn A", unit_id=uid)
    wid = mk_work(conn, "Nghiên cứu X", doc_type="bai_bao")
    mid = mk_mention(conn, wid, "Nguyễn Văn A")
    mk_link(conn, mid, pid, state="DaXacNhan")
    conn.commit()
    r = client.get("/api/stats").json()
    assert any(u["unit_id"] == uid and u["works"] == 1 for u in r["by_unit"])
    assert any(p["person_id"] == pid and p["works"] == 1 and p["unit_code"] == "khoa-cntt" for p in r["top_persons"])
    assert r["coverage"]["works_with_link_pct"] > 0


# ---------- lát cắt M: đơn vị thật từ nguồn (work_unit) ----------
def test_stats_by_unit_counts_work_unit_from_source_too(client, conn, user_id):
    """`by_unit` nay đi qua `v_work_unit` — không chỉ đơn vị của tác giả đã liên
    kết (test ở trên) mà cả đơn vị suy từ nguồn (`work_unit.source='source'`,
    xem migration 0020/cris.normalize), không cần tác giả nào được liên kết."""
    cntt = q(conn, "INSERT INTO unit(code, name) VALUES ('CNTT','Khoa Công nghệ thông tin') RETURNING id")[0]["id"]
    wid = mk_work(conn, "Bài báo có đơn vị nguồn", doc_type="bai_bao")
    q(conn, "INSERT INTO work_unit(work_id, unit_id, source) VALUES (%s,%s,'source')", wid, cntt)
    conn.commit()
    r = client.get("/api/stats").json()
    assert any(u["unit_id"] == cntt and u["code"] == "CNTT" and u["works"] == 1 for u in r["by_unit"])


def test_units_endpoint_lists_active_units_sorted_by_works(client, conn, user_id):
    cntt = q(conn, "INSERT INTO unit(code, name) VALUES ('CNTT','Khoa Công nghệ thông tin') RETURNING id")[0]["id"]
    q(conn, "INSERT INTO unit(code, name, active) VALUES ('KHCB','Khoa Khoa học cơ bản', false)")
    for i in range(2):
        wid = mk_work(conn, f"Bài {i}", doc_type="bai_bao")
        q(conn, "INSERT INTO work_unit(work_id, unit_id, source) VALUES (%s,%s,'source')", wid, cntt)
    mk_person(conn, "Nguyễn Văn A", unit_id=cntt)
    conn.commit()
    r = client.get("/api/units").json()
    codes = [u["code"] for u in r]
    assert "KHCB" not in codes                    # đã tắt, không liệt kê
    cntt_row = next(u for u in r if u["code"] == "CNTT")
    assert cntt_row["works"] == 2 and cntt_row["persons"] == 1 and cntt_row["active"] is True
    # sắp theo works giảm dần: CNTT (2 công trình) phải đứng trước các đơn vị 0 công trình
    assert r[0]["code"] == "CNTT"


# ---------- E2: xuất CSV ----------
def test_export_works_csv_bom_rows_and_diacritics(client, conn, user_id):
    mk_work(conn, "Hệ thống quản lý đào tạo", doc_type="bai_bao")
    mk_work(conn, "Ứng dụng học máy trong y tế", doc_type="do_an")
    conn.commit()
    resp = client.get("/api/works.csv")
    assert resp.status_code == 200
    assert resp.content.startswith(b"\xef\xbb\xbf")
    assert 'attachment; filename="cong-trinh-' in resp.headers["content-disposition"]
    text = resp.content.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln]
    assert lines[0] == "id,doc_type,title,year,doi,journal,authors,state"
    assert len(lines) == 3  # header + 2 công trình
    assert "Hệ thống quản lý đào tạo" in text and "Ứng dụng học máy trong y tế" in text


def test_export_works_csv_filters_doc_type(client, conn, user_id):
    mk_work(conn, "Bài báo 1", doc_type="bai_bao")
    mk_work(conn, "Đồ án 1", doc_type="do_an")
    conn.commit()
    resp = client.get("/api/works.csv", params={"doc_type": "bai_bao"})
    text = resp.content.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln]
    assert len(lines) == 2
    assert "bai_bao" in lines[1] and "Đồ án 1" not in text


def test_export_works_csv_filters_venue_kind(client, conn, user_id):
    w1 = mk_work(conn, "Bài quốc tế", doc_type="bai_bao")
    w2 = mk_work(conn, "Bài trong nước", doc_type="bai_bao")
    q(conn, "UPDATE work SET venue_kind='journal_intl' WHERE id=%s", w1)
    q(conn, "UPDATE work SET venue_kind='journal_domestic' WHERE id=%s", w2)
    conn.commit()
    resp = client.get("/api/works.csv", params={"venue_kind": "journal_intl"})
    text = resp.content.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln]
    assert len(lines) == 2
    assert "Bài quốc tế" in text and "Bài trong nước" not in text


def test_export_person_publications_csv_404_and_authors_joined(client, conn, user_id):
    assert client.get("/api/persons/999999/publications.csv").status_code == 404
    pid = mk_person(conn, "Trần Thị Bích")
    wid = mk_work(conn, "Công trình có đồng tác giả", doc_type="bai_bao")
    m1 = mk_mention(conn, wid, "Trần Thị Bích", position=1)
    mk_mention(conn, wid, "Lê Văn Cường", position=2)
    mk_link(conn, m1, pid, state="DaXacNhan")
    conn.commit()
    resp = client.get(f"/api/persons/{pid}/publications.csv")
    assert resp.status_code == 200 and resp.content.startswith(b"\xef\xbb\xbf")
    text = resp.content.decode("utf-8-sig")
    assert "Trần Thị Bích; Lê Văn Cường" in text


# ---------- E3: /api/audit ----------
def test_audit_after_confirm_link_has_one_row_with_actor(client, conn, user_id):
    pid = mk_person(conn, "Phạm Văn Đức")
    wid = mk_work(conn, "Công trình cần xác nhận tác giả", doc_type="bai_bao")
    mid = mk_mention(conn, wid, "Phạm Văn Đức")
    lid = mk_link(conn, mid, pid, state="ChoXacNhan")
    conn.commit()
    r = client.post("/api/queue/authors/decide", json={"link_ids": [lid], "decision": "confirm"})
    assert r.status_code == 200, r.text
    a = client.get("/api/audit", params={"entity": "author_link", "entity_id": lid}).json()
    assert a["page"]["total"] == 1
    row = a["items"][0]
    assert row["action"] == "link.confirm" and row["action_label"] == "Xác nhận liên kết"
    assert row["actor_name"] == "Chuyên viên phòng" and row["entity_id"] == lid


def test_audit_filters_by_entity_and_unknown_action_passes_through(client, conn, user_id):
    from cris import audit as audit_mod
    audit_mod.log(conn, user_id, "custom.action_la", "unit", 1)
    conn.commit()
    r = client.get("/api/audit", params={"entity": "unit"}).json()
    assert r["page"]["total"] == 1 and r["items"][0]["action_label"] == "custom.action_la"
    assert client.get("/api/audit", params={"entity": "khong-ton-tai"}).json()["page"]["total"] == 0


# ---------- E4: /api/periods ----------
def test_period_open_appears_in_list_as_dangmo(client, conn, user_id):
    r = client.post("/api/periods", json={
        "code": "K2026-EXT-1", "name": "Kỳ báo cáo thử", "scope": {"doc_types": ["bai_bao"]},
        "criteria": None, "due_at": due_soon().isoformat()})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["state"] == "DangMo" and body["code"] == "K2026-EXT-1"
    listing = client.get("/api/periods").json()
    assert any(p["id"] == body["id"] and p["state"] == "DangMo" for p in listing)


def test_period_open_duplicate_code_is_409(client, conn, user_id):
    body = {"code": "K2026-EXT-2", "name": "Kỳ báo cáo", "scope": {}, "due_at": due_soon().isoformat()}
    assert client.post("/api/periods", json=body).status_code == 201
    r = client.post("/api/periods", json=body)
    assert r.status_code == 409 and "detail" in r.json()


def test_period_close_twice_is_409(client, conn, user_id):
    pid = client.post("/api/periods", json={
        "code": "K2026-EXT-3", "name": "Kỳ báo cáo", "scope": {}, "due_at": due_soon().isoformat()}).json()["id"]
    r1 = client.post(f"/api/periods/{pid}/close")
    assert r1.status_code == 200 and r1.json()["state"] == "DaDongNop"
    r2 = client.post(f"/api/periods/{pid}/close")
    assert r2.status_code == 409 and "detail" in r2.json()


def test_period_cancel(client, conn, user_id):
    pid = client.post("/api/periods", json={
        "code": "K2026-EXT-4", "name": "Kỳ báo cáo", "scope": {}, "due_at": due_soon().isoformat()}).json()["id"]
    r = client.post(f"/api/periods/{pid}/cancel")
    assert r.status_code == 200 and r.json()["state"] == "Huy"


def test_period_progress_lists_every_active_unit_including_zero(client, conn, user_id):
    u_with = mk_unit(conn, "khoa-a", "Khoa A")
    u_without = mk_unit(conn, "khoa-b", "Khoa B")
    pid = client.post("/api/periods", json={
        "code": "K2026-EXT-5", "name": "Kỳ báo cáo", "scope": {}, "due_at": due_soon().isoformat()}).json()["id"]
    wid = mk_work(conn, "Công trình kê khai", doc_type="bai_bao")
    q(conn, "INSERT INTO declaration(period_id, work_id, unit_id, created_by) VALUES (%s,%s,%s,%s)",
      pid, wid, u_with, user_id)
    conn.commit()
    r = client.get(f"/api/periods/{pid}/progress").json()
    by_unit = {u["unit_id"]: u for u in r["units"]}
    assert by_unit[u_with]["total"] == 1 and by_unit[u_with]["counts"]["Nhap"] == 1
    assert by_unit[u_without]["total"] == 0
    assert r["days_remaining"] >= 0


def test_period_progress_unknown_id_is_409(client, conn, user_id):
    r = client.get("/api/periods/999999/progress")
    assert r.status_code == 409


# ---------- Đợt 2 (rà soát UI): ứng viên trùng tên phải phân biệt được ----------
def mk_topic(conn, label, keywords, model="local-test"):
    """`keywords`: [(keyword, weight), ...]. Trả `topic_id`."""
    tid = q(conn, "INSERT INTO ai_topic(model, label, size) VALUES (%s,%s,0) RETURNING id", model, label)[0]["id"]
    for kw, weight in keywords:
        q(conn, "INSERT INTO ai_topic_keyword(topic_id, keyword, weight) VALUES (%s,%s,%s)", tid, kw, weight)
    return tid


def _seed_three_namesakes(conn):
    """3 ứng viên "Nguyễn Thị Dung" khác khoa/học vị/số công trình đã xác nhận,
    cùng đứng chờ xác nhận trên một công trình mới. Trả (p1, p2, p3, u_cntt, u_dtvt)."""
    u_cntt = mk_unit(conn, "khoa-cntt", "Khoa Công nghệ thông tin")
    u_dtvt = mk_unit(conn, "khoa-dtvt", "Khoa Điện tử viễn thông")
    p1 = mk_person(conn, "Nguyễn Thị Dung", unit_id=u_cntt, degree_raw="ThS", position="Trưởng bộ môn",
                   field="Khoa học máy tính", orcid="0000-0001-0001-000X")
    p2 = mk_person(conn, "Nguyễn Thị Dung", unit_id=u_dtvt, degree_raw="TS")
    p3 = mk_person(conn, "Nguyễn Thị Dung")  # chưa gán khoa/học vị/chức vụ/lĩnh vực/ORCID
    for i in range(2):
        w = mk_work(conn, f"Công trình đã xác nhận của P1 #{i}", doc_type="bai_bao")
        mk_link(conn, mk_mention(conn, w, "Nguyễn Thị Dung"), p1, state="DaXacNhan")
    w_p2 = mk_work(conn, "Công trình đã xác nhận của P2", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_p2, "Nguyễn Thị Dung"), p2, state="DaXacNhan")

    w_new = mk_work(conn, "Công trình mới chờ xác nhận tác giả", doc_type="bai_bao")
    m_new = mk_mention(conn, w_new, "Nguyễn Thị Dung")
    mk_link(conn, m_new, p1, state="ChoXacNhan")
    mk_link(conn, m_new, p2, state="ChoXacNhan")
    mk_link(conn, m_new, p3, state="ChoXacNhan")
    conn.commit()
    return p1, p2, p3, u_cntt, u_dtvt


def test_author_queue_namesakes_carry_unit_degree_position_field_orcid_and_work_count(client, conn, user_id):
    p1, p2, p3, u_cntt, u_dtvt = _seed_three_namesakes(conn)

    r = client.get("/api/queue/authors", params={"state": "ChoXacNhan"})
    assert r.status_code == 200, r.text
    items = {row["candidate_person_id"]: row for row in r.json()["items"]}
    assert set(items) == {p1, p2, p3}

    row1, row2 = items[p1], items[p2]
    assert row1["candidate_unit"]["code"] == "khoa-cntt" and row1["candidate_degree"] == "ThS"
    assert row1["candidate_position"] == "Trưởng bộ môn" and row1["candidate_field"] == "Khoa học máy tính"
    assert row1["candidate_orcid"] == "0000-0001-0001-000X" and row1["candidate_works"] == 2

    assert row2["candidate_unit"]["code"] == "khoa-dtvt" and row2["candidate_degree"] == "TS"
    assert row2["candidate_works"] == 1

    # ứng viên khác khoa/học vị/số công trình -> phân biệt được, không giống hệt nhau
    assert row1["candidate_unit"]["code"] != row2["candidate_unit"]["code"]
    assert row1["candidate_degree"] != row2["candidate_degree"]
    assert row1["candidate_works"] != row2["candidate_works"]


def test_author_queue_candidate_fields_are_null_when_unassigned(client, conn, user_id):
    p1, p2, p3, _u_cntt, _u_dtvt = _seed_three_namesakes(conn)

    items = {row["candidate_person_id"]: row for row in
             client.get("/api/queue/authors", params={"state": "ChoXacNhan"}).json()["items"]}
    row3 = items[p3]
    # ứng viên chưa gán gì -> null/0/[], không phải giá trị giả
    assert row3["candidate_unit"] is None and row3["candidate_degree"] is None
    assert row3["candidate_position"] is None and row3["candidate_field"] is None
    assert row3["candidate_orcid"] is None and row3["candidate_works"] == 0
    assert row3["candidate_top_topics"] == []
    assert p3 not in (p1, p2)  # ứng viên rỗng vẫn là ứng viên riêng biệt, không lẫn với p1/p2


def test_author_queue_candidate_works_counts_only_linked_states(client, conn, user_id):
    p = mk_person(conn, "Trần Văn Kiên")
    w_auto = mk_work(conn, "Công trình liên kết tự động", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_auto, "Trần Văn Kiên"), p, state="DaNoiTuDong")
    w_confirmed = mk_work(conn, "Công trình đã xác nhận", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_confirmed, "Trần Văn Kiên"), p, state="DaXacNhan")
    w_pending_other = mk_work(conn, "Công trình khác đang chờ", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_pending_other, "Trần Văn Kiên"), p, state="ChoXacNhan")
    w_rejected = mk_work(conn, "Công trình đã bác bỏ", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_rejected, "Trần Văn Kiên"), p, state="DaBacBo")

    w_new = mk_work(conn, "Công trình mới chờ xác nhận", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_new, "Trần Văn Kiên"), p, state="ChoXacNhan")
    conn.commit()

    r = client.get("/api/queue/authors", params={"state": "ChoXacNhan", "q": "Trần Văn Kiên"}).json()
    rows = [row for row in r["items"] if row["candidate_person_id"] == p]
    assert len(rows) >= 1
    assert all(row["candidate_works"] == 2 for row in rows)


def test_author_queue_candidate_top_topics_empty_without_ai_and_ranked_when_ai_ran(client, conn, user_id):
    p = mk_person(conn, "Lê Thị Hoa")
    w = mk_work(conn, "Công trình đã xác nhận với từ khoá", doc_type="bai_bao",
                keywords="an toan thong tin, hoc may, mang may tinh, co so du lieu")
    mk_link(conn, mk_mention(conn, w, "Lê Thị Hoa"), p, state="DaXacNhan")
    w_new = mk_work(conn, "Công trình mới chờ xác nhận", doc_type="bai_bao")
    mk_link(conn, mk_mention(conn, w_new, "Lê Thị Hoa"), p, state="ChoXacNhan")
    conn.commit()

    # Chưa chạy AI (chưa có ai_topic nào) -> rỗng, không lỗi
    before = client.get("/api/queue/authors", params={"state": "ChoXacNhan", "q": "Lê Thị Hoa"}).json()
    row_before = next(row for row in before["items"] if row["candidate_person_id"] == p)
    assert row_before["candidate_top_topics"] == []

    mk_topic(conn, "An toàn thông tin", [("an toan thong tin", 5.0)])
    mk_topic(conn, "Học máy", [("hoc may", 4.0)])
    mk_topic(conn, "Mạng máy tính", [("mang may tinh", 3.0)])
    mk_topic(conn, "Cơ sở dữ liệu", [("co so du lieu", 2.0)])
    conn.commit()

    after = client.get("/api/queue/authors", params={"state": "ChoXacNhan", "q": "Lê Thị Hoa"}).json()
    row_after = next(row for row in after["items"] if row["candidate_person_id"] == p)
    assert 1 <= len(row_after["candidate_top_topics"]) <= 3
    assert row_after["candidate_top_topics"][0] == "An toàn thông tin"


def test_author_queue_response_never_exposes_email_or_phone(client, conn, user_id):
    p1 = mk_person(conn, "Vũ Minh Anh", email="vu.minh.anh@example.test", phone="0900000001")
    p2 = mk_person(conn, "Vũ Minh Anh", phone="0900000002")
    m = mk_mention(conn, mk_work(conn, "Công trình chờ xác nhận, hai ứng viên trùng tên", doc_type="bai_bao"),
                   "Vũ Minh Anh")
    mk_link(conn, m, p1, state="ChoXacNhan")
    mk_link(conn, m, p2, state="ChoXacNhan")
    conn.commit()

    r = client.get("/api/queue/authors", params={"state": "ChoXacNhan", "q": "Vũ Minh Anh"})
    assert r.status_code == 200
    assert "vu.minh.anh@example.test" not in r.text
    assert "0900000001" not in r.text and "0900000002" not in r.text
    for row in r.json()["items"]:
        assert "email" not in row and "phone" not in row
