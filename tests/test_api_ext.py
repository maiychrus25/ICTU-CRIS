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


def mk_person(conn, name, unit_id=None):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id) "
                   "VALUES ('lecturer',%s,%s,%s,%s) RETURNING id",
             name, name.lower(), [name.lower()], unit_id)[0]["id"]


def mk_mention(conn, work_id, raw_name, position=1):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw_name, raw_name.lower(), raw_name.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state="ChoXacNhan"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


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
