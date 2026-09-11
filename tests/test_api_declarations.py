# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""API kê khai công trình vào kỳ (`/api/periods/{pid}/declarations`,
`/api/declarations/{id}`..., lát cắt K, G3) trên PostgreSQL thật (fixture
`conn`), theo khuôn `test_api_ext.py`."""
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


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
