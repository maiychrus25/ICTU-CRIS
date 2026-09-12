# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Thông báo trong ứng dụng (`cris.notify`, lát cắt L2): móc gọi từ
`cris/api/routes/{declarations,periods,queue,me}.py` sau khi nghiệp vụ thành
công, và router mỏng `cris/api/routes/notifications.py`. API FastAPI trên
PostgreSQL thật (fixture `conn`), theo khuôn `test_api_declarations.py` —
đóng vai qua header `X-CRIS-User=<id>` (chế độ mở, chưa ai đặt mật khẩu)."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_unit(conn, code=None, name="Khoa kiểm thử thông báo"):
    code = code or f"khoa-noti-{uuid.uuid4().hex[:8]}"
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def mk_actor(conn, roles, unit_id=None, person_id=None, email=None):
    email = email or f"actor-{uuid.uuid4().hex[:10]}@ictu.test"
    uid = q(conn,
            "INSERT INTO app_user(email, display_name, roles, unit_id, person_id) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            email, "Người kiểm thử L2", roles, unit_id, person_id)[0]["id"]
    conn.commit()
    return uid


def mk_person(conn, name):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) VALUES ('lecturer',%s,%s,%s) RETURNING id",
             name, name.lower(), [name.lower()])[0]["id"]


def mk_mention(conn, work_id, raw_name, position=1):
    return q(conn,
             "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
             "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw_name, raw_name.lower(), raw_name.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state="ChoXacNhan"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


def as_user(uid):
    return {"X-CRIS-User": str(uid)}


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


def open_period(client, code, actor_uid=None):
    r = client.post("/api/periods", json={
        "code": code, "name": "Kỳ kiểm thử thông báo", "scope": {"doc_types": ["bai_bao"]},
        "criteria": None, "due_at": due_soon().isoformat()},
        headers=as_user(actor_uid) if actor_uid else {})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def notifications_for(client, uid, unread=None):
    params = {} if unread is None else {"unread": unread}
    r = client.get("/api/notifications", params=params, headers=as_user(uid))
    assert r.status_code == 200, r.text
    return r.json()


# ---------- declaration state ----------

def test_submit_to_khoa_notifies_head_same_unit_only(client, conn, user_id):
    # Mở kỳ TRƯỚC khi tạo các tài khoản faculty_officer/faculty_head — mở kỳ
    # cũng báo cho hai vai trò này (xem test_open_period_...), tạo tài khoản
    # sau đó tránh nhiễu số đếm không liên quan tới việc đang kiểm ở đây.
    pid = open_period(client, "K2026-NOTI-1")
    unit_a = mk_unit(conn)
    unit_b = mk_unit(conn)
    officer = mk_actor(conn, ["faculty_officer"], unit_a)
    head_a = mk_actor(conn, ["faculty_head"], unit_a)
    head_b = mk_actor(conn, ["faculty_head"], unit_b)
    work_id = mk_work(conn, "Bài Noti 1", doc_type="bai_bao")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_a},
                      headers=as_user(officer)).json()["id"]

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(officer))
    assert r.status_code == 200, r.text

    body_a = notifications_for(client, head_a)
    assert body_a["unread"] == 1
    assert body_a["items"][0]["kind"] == "declaration_state"
    assert body_a["items"][0]["link"] == f"/ke-khai/?id={did}"

    body_b = notifications_for(client, head_b)
    assert body_b["unread"] == 0 and body_b["items"] == []

    body_officer = notifications_for(client, officer)
    assert body_officer["items"] == []


def test_actor_never_notifies_self(client, conn, user_id):
    pid = open_period(client, "K2026-NOTI-2")
    unit_id = mk_unit(conn)
    officer = mk_actor(conn, ["faculty_officer"], unit_id)
    head = mk_actor(conn, ["faculty_head"], unit_id)
    rd_a = mk_actor(conn, ["rd_officer"])
    rd_b = mk_actor(conn, ["rd_officer"])
    work_id = mk_work(conn, "Bài Noti 2", doc_type="bai_bao")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                      headers=as_user(officer)).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(officer))
    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "KhoaDaDuyet"}, headers=as_user(head))
    assert r.status_code == 200, r.text

    # KhoaDaDuyet -> ChoPhongKiemTra báo cho mọi rd_officer: cả rd_a lẫn rd_b
    # đã nhận một thông báo ở bước trên (KhoaDaDuyet, do head thao tác). Bước
    # này rd_a tự thực hiện: rd_a có trong nhóm nhận nhưng bị loại vì là
    # người thao tác (số thông báo của rd_a không đổi); rd_b nhận thêm một cái.
    before_a = notifications_for(client, rd_a)["unread"]
    before_b = notifications_for(client, rd_b)["unread"]
    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoPhongKiemTra"}, headers=as_user(rd_a))
    assert r.status_code == 200, r.text

    assert notifications_for(client, rd_a)["unread"] == before_a
    body_b = notifications_for(client, rd_b)
    assert body_b["unread"] == before_b + 1 and body_b["items"][0]["kind"] == "declaration_state"


def test_return_to_nhap_has_reason_in_body_and_notifies_creator_plus_faculty_officer(client, conn, user_id):
    pid = open_period(client, "K2026-NOTI-3")
    unit_id = mk_unit(conn)
    creator = mk_actor(conn, ["faculty_officer"], unit_id)
    other_officer = mk_actor(conn, ["faculty_officer"], unit_id)
    head = mk_actor(conn, ["faculty_head"], unit_id)
    work_id = mk_work(conn, "Bài Noti 3", doc_type="bai_bao")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                      headers=as_user(creator)).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(creator))
    # Bước trên đã báo cho head (faculty_head cùng đơn vị) một lần — dùng làm
    # mốc để khẳng định bước trả về dưới đây không báo thêm cho chính head.
    head_before = notifications_for(client, head)["unread"]

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "Nhap", "reason": "thiếu minh chứng"},
                    headers=as_user(head))
    assert r.status_code == 200, r.text

    for uid in (creator, other_officer):
        body = notifications_for(client, uid)
        assert body["unread"] == 1, uid
        assert "thiếu minh chứng" in body["items"][0]["body"]
    assert notifications_for(client, head)["unread"] == head_before


def test_forbidden_transition_does_not_notify(client, conn, user_id):
    pid = open_period(client, "K2026-NOTI-4")
    unit_a = mk_unit(conn)
    unit_b = mk_unit(conn)
    officer_a = mk_actor(conn, ["faculty_officer"], unit_a)
    head_b = mk_actor(conn, ["faculty_head"], unit_b)
    work_id = mk_work(conn, "Bài Noti 4", doc_type="bai_bao")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_a},
                      headers=as_user(officer_a)).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(officer_a))

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "KhoaDaDuyet"}, headers=as_user(head_b))
    assert r.status_code == 403

    assert notifications_for(client, head_b)["items"] == []


# ---------- period state ----------

def test_open_period_notifies_faculty_roles_across_units_not_rd_officer(client, conn, user_id):
    unit_a = mk_unit(conn)
    unit_b = mk_unit(conn)
    officer_a = mk_actor(conn, ["faculty_officer"], unit_a)
    head_b = mk_actor(conn, ["faculty_head"], unit_b)
    rd = mk_actor(conn, ["rd_officer"])

    pid = open_period(client, "K2026-NOTI-5", actor_uid=rd)
    assert pid

    body_officer = notifications_for(client, officer_a)
    assert body_officer["unread"] == 1 and "đã mở" in body_officer["items"][0]["title"]
    body_head = notifications_for(client, head_b)
    assert body_head["unread"] == 1
    assert notifications_for(client, rd)["items"] == []


# ---------- author link ----------

def test_link_confirm_notifies_lecturer_with_account(client, conn, user_id):
    person_id = mk_person(conn, "Giảng viên Thông báo")
    lecturer_uid = mk_actor(conn, ["lecturer"], person_id=person_id)
    rd = mk_actor(conn, ["rd_officer"])
    work_id = mk_work(conn, "Bài có tác giả kiểm thử", doc_type="bai_bao")
    mention_id = mk_mention(conn, work_id, "Giảng viên Thông báo")
    link_id = mk_link(conn, mention_id, person_id, state="ChoXacNhan")
    conn.commit()

    r = client.post("/api/queue/authors/decide", json={"link_ids": [link_id], "decision": "confirm"},
                    headers=as_user(rd))
    assert r.status_code == 200, r.text

    body = notifications_for(client, lecturer_uid)
    assert body["unread"] == 1
    assert body["items"][0]["kind"] == "link_confirmed"
    assert body["items"][0]["link"] == f"/giang-vien/?id={person_id}"


# ---------- danh sách/đọc thông báo ----------

def test_unread_count_and_unread_filter(client, conn, user_id):
    # Một kỳ dùng chung cho cả ba hồ sơ (mở kỳ trước khi tạo tài khoản
    # faculty_* để việc mở kỳ không tự sinh thêm thông báo nhiễu số đếm ở đây).
    pid = open_period(client, "K2026-NOTI-6")
    unit_id = mk_unit(conn)
    head = mk_actor(conn, ["faculty_head"], unit_id)
    officer = mk_actor(conn, ["faculty_officer"], unit_id)
    for i in range(3):
        work_id = mk_work(conn, f"Bài Noti 6-{i}", doc_type="bai_bao")
        did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                          headers=as_user(officer)).json()["id"]
        client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(officer))

    body = notifications_for(client, head)
    assert body["unread"] == 3 and len(body["items"]) == 3

    nid = body["items"][0]["id"]
    r = client.post(f"/api/notifications/{nid}/read", headers=as_user(head))
    assert r.status_code == 200 and r.json()["read_at"] is not None

    filtered = notifications_for(client, head, unread=1)
    assert filtered["unread"] == 2 and len(filtered["items"]) == 2
    all_items = notifications_for(client, head)
    assert all_items["unread"] == 2 and len(all_items["items"]) == 3


def test_mark_all_read_zeros_unread(client, conn, user_id):
    pid = open_period(client, "K2026-NOTI-7")
    unit_id = mk_unit(conn)
    head = mk_actor(conn, ["faculty_head"], unit_id)
    officer = mk_actor(conn, ["faculty_officer"], unit_id)
    for i in range(2):
        work_id = mk_work(conn, f"Bài Noti 7-{i}", doc_type="bai_bao")
        did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                          headers=as_user(officer)).json()["id"]
        client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(officer))

    r = client.post("/api/notifications/read-all", headers=as_user(head))
    assert r.status_code == 200 and r.json()["marked"] == 2

    body = notifications_for(client, head)
    assert body["unread"] == 0
    assert notifications_for(client, head, unread=1)["items"] == []


def test_reading_someone_elses_notification_is_404(client, conn, user_id):
    unit_id = mk_unit(conn)
    head = mk_actor(conn, ["faculty_head"], unit_id)
    officer = mk_actor(conn, ["faculty_officer"], unit_id)
    other = mk_actor(conn, ["faculty_head"], unit_id)
    work_id = mk_work(conn, "Bài Noti 8", doc_type="bai_bao")
    pid = open_period(client, "K2026-NOTI-8")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                      headers=as_user(officer)).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(officer))

    nid = notifications_for(client, head)["items"][0]["id"]
    r = client.post(f"/api/notifications/{nid}/read", headers=as_user(other))
    assert r.status_code == 404
