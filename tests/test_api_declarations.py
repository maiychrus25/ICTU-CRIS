# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""API kê khai công trình vào kỳ (`/api/periods/{pid}/declarations`,
`/api/declarations/{id}`..., lát cắt K, G3, nâng cấp H1) trên PostgreSQL thật
(fixture `conn`), theo khuôn `test_api_ext.py`. Chế độ mở (không đặt mật khẩu)
dùng header `X-CRIS-User=<id>` để đóng các vai trò khác nhau — xem
`cris.api.deps.current_user`."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def mk_actor(conn, roles, unit_id=None, email=None):
    """Tạo `app_user` với vai trò/đơn vị để đóng vai qua header `X-CRIS-User`."""
    email = email or f"actor-{uuid.uuid4().hex[:10]}@ictu.test"
    return q(conn, "INSERT INTO app_user(email, display_name, roles, unit_id) VALUES (%s,%s,%s,%s) RETURNING id",
             email, "Người kiểm thử API H1", roles, unit_id)[0]["id"]


def as_user(client, uid):
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


def open_period(client, code="K2026-API-1"):
    r = client.post("/api/periods", json={
        "code": code, "name": "Kỳ báo cáo kê khai", "scope": {"doc_types": ["bai_bao"]},
        "criteria": None, "due_at": due_soon().isoformat()})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_list_declarations_on_unknown_period_is_404(client, conn, user_id):
    r = client.get("/api/periods/999999/declarations")
    assert r.status_code == 404


def test_add_and_list_declaration(client, conn, user_id):
    unit_id = mk_unit(conn)
    work_id = mk_work(conn, "Bài báo API", doc_type="bai_bao")
    pid = open_period(client, "K2026-API-2")

    r = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["state"] == "Nhap" and body["work_title"] == "Bài báo API" and body["unit_id"] == unit_id
    assert body["evidence_count"] == 0

    listing = client.get(f"/api/periods/{pid}/declarations").json()
    assert listing["items"][0]["id"] == body["id"]

    filtered = client.get(f"/api/periods/{pid}/declarations", params={"unit_id": unit_id}).json()
    assert len(filtered["items"]) == 1
    other_unit = mk_unit(conn, "khoa-b", "Khoa B")
    empty = client.get(f"/api/periods/{pid}/declarations", params={"unit_id": other_unit}).json()
    assert empty["items"] == []


def test_add_declaration_duplicate_is_409(client, conn, user_id):
    unit_id = mk_unit(conn)
    work_id = mk_work(conn, "Bài báo trùng", doc_type="bai_bao")
    pid = open_period(client, "K2026-API-3")
    body = {"work_id": work_id, "unit_id": unit_id}
    assert client.post(f"/api/periods/{pid}/declarations", json=body).status_code == 201
    r = client.post(f"/api/periods/{pid}/declarations", json=body)
    assert r.status_code == 409 and "detail" in r.json()


def test_add_declaration_on_closed_period_is_409(client, conn, user_id):
    unit_id = mk_unit(conn)
    work_id = mk_work(conn, "Bài báo đóng", doc_type="bai_bao")
    pid = open_period(client, "K2026-API-4")
    assert client.post(f"/api/periods/{pid}/close").status_code == 200
    r = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id})
    assert r.status_code == 409


def test_declaration_detail_unknown_is_404(client, conn, user_id):
    assert client.get("/api/declarations/999999").status_code == 404
    assert client.post("/api/declarations/999999/state", json={"to_state": "Rut", "reason": "x"}).status_code == 404
    assert client.post("/api/declarations/999999/evidence", json={"kind": "note"}).status_code == 404


def test_state_transition_requires_reason_and_updates_state(client, conn, user_id):
    unit_id = mk_unit(conn)
    work_id = mk_work(conn, "Bài báo trạng thái", doc_type="bai_bao")
    pid = open_period(client, "K2026-API-5")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id}).json()["id"]

    missing_reason = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoBoSung"})
    assert missing_reason.status_code == 409

    ok = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoBoSung", "reason": "thiếu minh chứng"})
    assert ok.status_code == 200 and ok.json()["state"] == "ChoBoSung"

    detail = client.get(f"/api/declarations/{did}").json()
    assert [e["to_state"] for e in detail["events"]] == ["Nhap", "ChoBoSung"]
    assert detail["events"][-1]["reason"] == "thiếu minh chứng"


def test_add_evidence_appears_in_detail_and_count(client, conn, user_id):
    unit_id = mk_unit(conn)
    work_id = mk_work(conn, "Bài báo minh chứng", doc_type="bai_bao")
    pid = open_period(client, "K2026-API-6")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id}).json()["id"]

    r = client.post(f"/api/declarations/{did}/evidence", json={"kind": "link", "url": "https://example.org/bai"})
    assert r.status_code == 201 and r.json()["kind"] == "link"

    detail = client.get(f"/api/declarations/{did}").json()
    assert len(detail["evidence"]) == 1 and detail["evidence"][0]["url"] == "https://example.org/bai"

    listing = client.get(f"/api/periods/{pid}/declarations").json()
    assert listing["items"][0]["evidence_count"] == 1


def test_declaration_actions_appear_in_audit_log(client, conn, user_id):
    unit_id = mk_unit(conn)
    work_id = mk_work(conn, "Bài báo audit", doc_type="bai_bao")
    pid = open_period(client, "K2026-API-7")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id}).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoBoSung", "reason": "bổ sung"})
    client.post(f"/api/declarations/{did}/evidence", json={"kind": "note", "note": "đã xem"})

    rows = client.get("/api/audit", params={"entity": "declaration", "entity_id": did}).json()["items"]
    actions = [r["action"] for r in rows]
    assert "declaration.add" in actions and "declaration.ChoBoSung" in actions and "declaration.evidence" in actions
    assert all(r["action_label"] != r["action"] for r in rows)


# ---------- H1: duyệt hai cấp qua API, phạm vi đơn vị (NFR-02) ----------

def test_full_review_round_trip_via_api_each_role(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-h1-api-1", "Khoa H1 API 1")
    officer = mk_actor(conn, ["faculty_officer"], unit_id)
    head = mk_actor(conn, ["faculty_head"], unit_id)
    rd = mk_actor(conn, ["rd_officer"])
    work_id = mk_work(conn, "Bài H1 API 1", doc_type="bai_bao")
    pid = open_period(client, "K2026-H1-API-1")

    r = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                    headers=as_user(client, officer))
    assert r.status_code == 201, r.text
    did = r.json()["id"]

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"},
                    headers=as_user(client, officer))
    assert r.status_code == 200 and r.json()["state"] == "ChoKhoaDuyet"

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "KhoaDaDuyet"},
                    headers=as_user(client, head))
    assert r.status_code == 200 and r.json()["state"] == "KhoaDaDuyet"

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoPhongKiemTra"},
                    headers=as_user(client, head))
    assert r.status_code == 200 and r.json()["state"] == "ChoPhongKiemTra"

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "DatYeuCau"},
                    headers=as_user(client, rd))
    assert r.status_code == 200 and r.json()["state"] == "DatYeuCau"


def test_faculty_officer_approving_is_403(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-h1-api-2", "Khoa H1 API 2")
    officer = mk_actor(conn, ["faculty_officer"], unit_id)
    work_id = mk_work(conn, "Bài H1 API 2", doc_type="bai_bao")
    pid = open_period(client, "K2026-H1-API-2")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                      headers=as_user(client, officer)).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"}, headers=as_user(client, officer))

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "KhoaDaDuyet"},
                    headers=as_user(client, officer))
    assert r.status_code == 403 and "detail" in r.json()


def test_faculty_head_other_unit_is_403(client, conn, user_id):
    unit_a = mk_unit(conn, "khoa-h1-api-3a", "Khoa H1 API 3A")
    unit_b = mk_unit(conn, "khoa-h1-api-3b", "Khoa H1 API 3B")
    officer_a = mk_actor(conn, ["faculty_officer"], unit_a)
    head_b = mk_actor(conn, ["faculty_head"], unit_b)
    work_id = mk_work(conn, "Bài H1 API 3", doc_type="bai_bao")
    pid = open_period(client, "K2026-H1-API-3")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_a},
                      headers=as_user(client, officer_a)).json()["id"]
    client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"},
               headers=as_user(client, officer_a))

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "KhoaDaDuyet"},
                    headers=as_user(client, head_b))
    assert r.status_code == 403


def test_rd_officer_acts_across_units(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-h1-api-4", "Khoa H1 API 4")
    work_id = mk_work(conn, "Bài H1 API 4", doc_type="bai_bao")
    pid = open_period(client, "K2026-H1-API-4")
    did = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                      headers=as_user(client, user_id)).json()["id"]
    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"},
                    headers=as_user(client, user_id))
    assert r.status_code == 200 and r.json()["state"] == "ChoKhoaDuyet"


def test_list_declarations_scoped_to_faculty_unit(client, conn, user_id):
    unit_a = mk_unit(conn, "khoa-h1-api-5a", "Khoa H1 API 5A")
    unit_b = mk_unit(conn, "khoa-h1-api-5b", "Khoa H1 API 5B")
    officer_a = mk_actor(conn, ["faculty_officer"], unit_a)
    work_a = mk_work(conn, "Bài H1 API 5A", doc_type="bai_bao")
    work_b = mk_work(conn, "Bài H1 API 5B", doc_type="bai_bao")
    pid = open_period(client, "K2026-H1-API-5")
    client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_a, "unit_id": unit_a},
               headers=as_user(client, user_id))
    client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_b, "unit_id": unit_b},
               headers=as_user(client, user_id))

    listing = client.get(f"/api/periods/{pid}/declarations", headers=as_user(client, officer_a)).json()
    assert [i["unit_id"] for i in listing["items"]] == [unit_a]

    listing_rd = client.get(f"/api/periods/{pid}/declarations", headers=as_user(client, user_id)).json()
    assert len(listing_rd["items"]) == 2


def test_finalize_period_before_da_dong_nop_is_409(client, conn, user_id):
    pid = open_period(client, "K2026-H1-API-6")
    r = client.post(f"/api/periods/{pid}/finalize")
    assert r.status_code == 409


def test_finalize_period_moves_dat_yeu_cau_to_da_chot(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-h1-api-7", "Khoa H1 API 7")
    head = mk_actor(conn, ["faculty_head"], unit_id)
    work_ready = mk_work(conn, "Bài H1 API 7 đạt", doc_type="bai_bao")
    work_pending = mk_work(conn, "Bài H1 API 7 chưa xong", doc_type="bai_bao")
    pid = open_period(client, "K2026-H1-API-7")
    did_ready = client.post(f"/api/periods/{pid}/declarations",
                            json={"work_id": work_ready, "unit_id": unit_id}).json()["id"]
    did_pending = client.post(f"/api/periods/{pid}/declarations",
                              json={"work_id": work_pending, "unit_id": unit_id}).json()["id"]
    # ChoKhoaDuyet→KhoaDaDuyet chỉ faculty_head; các bước còn lại rd_officer (mặc định) đủ vai.
    assert client.post(f"/api/declarations/{did_ready}/state", json={"to_state": "ChoKhoaDuyet"}).status_code == 200
    r = client.post(f"/api/declarations/{did_ready}/state", json={"to_state": "KhoaDaDuyet"},
                    headers=as_user(client, head))
    assert r.status_code == 200, r.text
    for to_state in ("ChoPhongKiemTra", "DatYeuCau"):
        assert client.post(f"/api/declarations/{did_ready}/state", json={"to_state": to_state}).status_code == 200
    assert client.post(f"/api/declarations/{did_pending}/state",
                       json={"to_state": "ChoKhoaDuyet"}).status_code == 200

    assert client.post(f"/api/periods/{pid}/close").status_code == 200
    r = client.post(f"/api/periods/{pid}/finalize")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["finalized"] == 1
    assert body["skipped"] == [{"id": did_pending, "state": "ChoKhoaDuyet"}]

    detail_ready = client.get(f"/api/declarations/{did_ready}").json()
    assert detail_ready["state"] == "DaChot"
