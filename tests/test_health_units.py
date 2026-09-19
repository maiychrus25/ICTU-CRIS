# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""`GET /api/health` mở rộng (lát cắt L3) và `GET /api/units/{id}/overview`
(góc nhìn khoa) — API FastAPI trên PostgreSQL thật (fixture `conn`), provider
AI `fake` trừ khi ghi rõ khác."""
import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_unit(conn, code, name):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def mk_person(conn, name, unit_id=None, kind="lecturer"):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id) "
                   "VALUES (%s,%s,%s,%s,%s) RETURNING id",
             kind, name, name.lower(), [name.lower()], unit_id)[0]["id"]


def mk_mention(conn, work_id, raw_name, position=1):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw_name, raw_name.lower(), raw_name.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state="ChoXacNhan"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


def mk_actor(conn, roles, unit_id=None, email=None):
    """Tạo `app_user` và commit ngay — dùng qua header `X-CRIS-User` (chế độ
    mở, chưa ai đặt mật khẩu, như `tests/test_report.py`)."""
    email = email or f"actor-{roles[0] if roles else 'x'}-{unit_id}@ictu.test"
    uid = q(conn, "INSERT INTO app_user(email, display_name, roles, unit_id) VALUES (%s,%s,%s,%s) RETURNING id",
            email, "Người kiểm thử L3", roles, unit_id)[0]["id"]
    conn.commit()
    return uid


def hdr(uid):
    return {"X-CRIS-User": str(uid)}


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


# ---------- GET /api/health ----------
def test_health_ok_has_all_contract_fields(client, conn, user_id):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"status", "db", "model", "last_sync_age_h", "version"}
    assert body["status"] == "ok" and body["db"] == "ok"
    assert body["model"] == "loaded"  # provider fake: nạp ngay, không lỗi
    assert body["last_sync_age_h"] is None  # chưa có sync_run nào
    assert isinstance(body["version"], str) and body["version"]


def test_health_db_error_is_503(client, monkeypatch):
    from cris.api import app as app_mod

    def boom(*a, **kw):
        raise RuntimeError("không kết nối được CSDL")

    monkeypatch.setattr(app_mod.db, "connect", boom)
    r = client.get("/api/health")
    assert r.status_code == 503
    assert r.json() == {"status": "error", "db": "error"}


def test_health_model_disabled_when_provider_none(monkeypatch, conn, user_id):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    clear_provider_cache()
    c = TestClient(create_app(static_dir="/nonexistent"))
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.json()["model"] == "disabled"


# ---------- GET /api/units/{id}/overview ----------
def test_unit_overview_counts_by_doc_type_top_persons_and_lecturers_without_works(client, conn, user_id):
    u1 = mk_unit(conn, "khoa-a", "Khoa A")
    u2 = mk_unit(conn, "khoa-b", "Khoa B")
    p1 = mk_person(conn, "Nguyễn Văn Một", unit_id=u1)
    mk_person(conn, "Trần Thị Hai", unit_id=u1)  # không có công trình liên kết
    w1 = mk_work(conn, "Công trình một", doc_type="bai_bao")
    w2 = mk_work(conn, "Công trình hai", doc_type="do_an")
    assert w2  # thuộc khoa B, không liên kết ai của khoa A
    m1 = mk_mention(conn, w1, "Nguyễn Văn Một")
    mk_link(conn, m1, p1, state="DaXacNhan")
    conn.commit()

    r1 = client.get(f"/api/units/{u1}/overview")
    assert r1.status_code == 200, r1.text
    b1 = r1.json()
    assert b1["unit"] == {"id": u1, "code": "khoa-a", "name": "Khoa A"}
    assert b1["works_total"] == 1
    assert b1["by_doc_type"] == {"bai_bao": 1}
    assert b1["lecturers_without_works"] == 1
    assert any(p["person_id"] == p1 and p["works"] == 1 for p in b1["top_persons"])

    b2 = client.get(f"/api/units/{u2}/overview").json()
    assert b2["works_total"] == 0 and b2["by_doc_type"] == {} and b2["top_persons"] == []


def test_unit_overview_pending_links_on_a_work_already_of_the_unit(client, conn, user_id):
    uid = mk_unit(conn, "khoa-f", "Khoa F")
    p1 = mk_person(conn, "Người đã xác nhận", unit_id=uid)
    p2 = mk_person(conn, "Người đang chờ")
    wid = mk_work(conn, "Công trình đồng tác giả", doc_type="bai_bao")
    m1 = mk_mention(conn, wid, "Người đã xác nhận", position=1)
    mk_link(conn, m1, p1, state="DaXacNhan")  # công trình nay thuộc khoa F
    m2 = mk_mention(conn, wid, "Người đang chờ", position=2)
    mk_link(conn, m2, p2, state="ChoXacNhan")
    conn.commit()
    body = client.get(f"/api/units/{uid}/overview").json()
    assert body["pending_links"] == 1


def test_unit_overview_declarations_by_state_defaults_to_latest_open_period(client, conn, user_id):
    uid = mk_unit(conn, "khoa-g", "Khoa G")
    wid = mk_work(conn, "Công trình kê khai", doc_type="bai_bao")
    pid = client.post("/api/periods", json={
        "code": "K2026-L3-1", "name": "Kỳ báo cáo L3", "scope": {}, "criteria": None,
        "due_at": "2027-01-01T00:00:00+00:00"}).json()["id"]
    q(conn, "INSERT INTO declaration(period_id, work_id, unit_id, created_by) VALUES (%s,%s,%s,%s)",
      pid, wid, uid, user_id)
    conn.commit()
    body = client.get(f"/api/units/{uid}/overview").json()
    assert body["declarations_by_state"] == {"Nhap": 1}
    body_explicit = client.get(f"/api/units/{uid}/overview", params={"period_id": pid}).json()
    assert body_explicit["declarations_by_state"] == {"Nhap": 1}


def test_unit_overview_404_unknown_unit(client, conn, user_id):
    r = client.get("/api/units/999999/overview")
    assert r.status_code == 404


def test_unit_overview_403_for_faculty_role_scoped_to_another_unit(client, conn):
    u1 = mk_unit(conn, "khoa-h", "Khoa H")
    u2 = mk_unit(conn, "khoa-i", "Khoa I")
    officer = mk_actor(conn, ["faculty_officer"], unit_id=u1)

    r_other = client.get(f"/api/units/{u2}/overview", headers=hdr(officer))
    assert r_other.status_code == 403

    r_own = client.get(f"/api/units/{u1}/overview", headers=hdr(officer))
    assert r_own.status_code == 200


def test_unit_overview_rd_officer_and_school_leader_see_any_unit(client, conn):
    u1 = mk_unit(conn, "khoa-j", "Khoa J")
    rd = mk_actor(conn, ["rd_officer"])
    leader = mk_actor(conn, ["school_leader"])
    assert client.get(f"/api/units/{u1}/overview", headers=hdr(rd)).status_code == 200
    assert client.get(f"/api/units/{u1}/overview", headers=hdr(leader)).status_code == 200


# ---------- lát cắt M: GET /api/units trả aliases; PATCH/POST alias (rd_officer) ----------
def test_units_list_includes_aliases_field(client, conn, user_id):
    mk_unit(conn, "khoa-k", "Khoa K")
    q(conn, "UPDATE unit SET aliases = ARRAY['Khoa K cũ'] WHERE code='khoa-k'")
    conn.commit()
    r = client.get("/api/units").json()
    row = next(u for u in r if u["code"] == "khoa-k")
    assert row["aliases"] == ["Khoa K cũ"]


def test_rename_unit_updates_name_returns_full_shape_and_logs_audit(client, conn, user_id):
    uid = mk_unit(conn, "khoa-l", "Khoa L")
    conn.commit()
    r = client.patch(f"/api/units/{uid}", json={"name": "Khoa L mới", "reason": "xác nhận với phòng đào tạo"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body == {"id": uid, "code": "khoa-l", "name": "Khoa L mới", "active": True,
                    "works": 0, "persons": 0, "aliases": []}
    log = q(conn, "SELECT action, after FROM audit_log WHERE entity='unit' AND entity_id=%s", uid)[0]
    assert log["action"] == "unit.rename" and log["after"]["reason"] == "xác nhận với phòng đào tạo"


def test_rename_unit_empty_name_is_400(client, conn, user_id):
    uid = mk_unit(conn, "khoa-m", "Khoa M")
    r = client.patch(f"/api/units/{uid}", json={"name": "   "})
    assert r.status_code == 400
    assert r.json()["detail"] == "Tên đơn vị không được để trống."


def test_rename_unit_unknown_id_is_404(client, conn, user_id):
    r = client.patch("/api/units/999999", json={"name": "X"})
    assert r.status_code == 404


def test_rename_unit_requires_rd_officer_403(client, conn):
    uid = mk_unit(conn, "khoa-n", "Khoa N")
    officer = mk_actor(conn, ["faculty_officer"], unit_id=uid)
    r = client.patch(f"/api/units/{uid}", json={"name": "Khoa N mới"}, headers=hdr(officer))
    assert r.status_code == 403


def test_add_unit_alias_is_idempotent_and_returns_full_shape(client, conn, user_id):
    uid = mk_unit(conn, "khoa-o", "Khoa O")
    conn.commit()
    r = client.post(f"/api/units/{uid}/aliases", json={"alias": "KO", "reason": "biến thể cũ"})
    assert r.status_code == 200, r.text
    assert r.json()["aliases"] == ["KO"]
    log = q(conn, "SELECT action FROM audit_log WHERE entity='unit' AND entity_id=%s AND action='unit.alias'", uid)
    assert len(log) == 1

    r2 = client.post(f"/api/units/{uid}/aliases", json={"alias": "KO"})    # lặp lại: không trùng, không ghi audit lần hai
    assert r2.status_code == 200 and r2.json()["aliases"] == ["KO"]
    log2 = q(conn, "SELECT action FROM audit_log WHERE entity='unit' AND entity_id=%s AND action='unit.alias'", uid)
    assert len(log2) == 1


def test_add_unit_alias_empty_is_400(client, conn, user_id):
    uid = mk_unit(conn, "khoa-p", "Khoa P")
    r = client.post(f"/api/units/{uid}/aliases", json={"alias": "  "})
    assert r.status_code == 400


def test_add_unit_alias_unknown_id_is_404(client, conn, user_id):
    r = client.post("/api/units/999999/aliases", json={"alias": "X"})
    assert r.status_code == 404


def test_add_unit_alias_requires_rd_officer_403(client, conn):
    uid = mk_unit(conn, "khoa-q", "Khoa Q")
    officer = mk_actor(conn, ["faculty_officer"], unit_id=uid)
    r = client.post(f"/api/units/{uid}/aliases", json={"alias": "KQ"}, headers=hdr(officer))
    assert r.status_code == 403


def test_health_version_is_the_installed_package_version_not_a_hardcoded_string(client):
    """Bản chạy thật 0.8.0 từng báo "0.7.0": mã tra tên gói "ictu-cris" (không tồn tại) rồi rơi về chuỗi viết cứng."""
    import pathlib
    import tomllib
    want = tomllib.loads((pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert client.get("/api/health").json()["version"] == want
    assert client.get("/openapi.json").json()["info"]["version"] == want
