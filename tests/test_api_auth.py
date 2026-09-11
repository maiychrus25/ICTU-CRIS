# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đăng nhập cục bộ (NFR-01, lát cắt G2): chế độ mở giữ nguyên hành vi cũ; sau khi
ai đó đặt mật khẩu, GET vẫn công khai nhưng POST quyết định/kỳ báo cáo và
`/api/audit` cần đăng nhập, `rd_officer` cho quyết định/kỳ báo cáo, mọi vai trò
đã đăng nhập cho `/api/compare`."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from cris import auth, cli, rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app
from cris.api.routes import auth as auth_routes


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_user(conn, roles, password=None, email=None):
    email = email or f"{uuid.uuid4().hex[:10]}@ictu.test"
    uid = q(conn, "INSERT INTO app_user(email, display_name, roles) VALUES (%s,%s,%s) RETURNING id",
            email, "Người kiểm thử", roles)[0]["id"]
    conn.commit()
    if password:
        auth.set_password(conn, email, password)
    return uid, email


def due_soon():
    return datetime.now(UTC) + timedelta(days=30)


@pytest.fixture(autouse=True)
def seed(conn):
    """`period.open_period` cần một `rule_set` (`year_rule`) đang hoạt động."""
    rules.seed_rules(conn, None)


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """`_failures` là dict bộ nhớ tiến trình (module-level) — dọn giữa các test để
    một test không bị 429 do lần đăng nhập sai của test khác trước đó."""
    auth_routes._failures.clear()
    yield
    auth_routes._failures.clear()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


# ---------- chế độ mở (chưa ai đặt mật khẩu) ----------

def test_open_mode_me_reports_no_auth_required_and_null_user(client, conn, user_id):
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json() == {"user": None, "auth_required": False}


def test_open_mode_about_reports_auth_required_false(client, conn, user_id):
    assert client.get("/api/about").json()["auth_required"] is False


def test_open_mode_period_open_still_works_without_login(client, conn, user_id):
    r = client.post("/api/periods", json={
        "code": "K2026-AUTH-1", "name": "Kỳ báo cáo", "scope": {}, "due_at": due_soon().isoformat()})
    assert r.status_code == 201, r.text


def test_open_mode_login_with_no_password_set_is_401(client, conn, user_id):
    r = client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "bat-ky"})
    assert r.status_code == 401


# ---------- đặt mật khẩu: chuyển sang bắt buộc đăng nhập ----------

def test_get_works_still_200_after_password_set(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    assert client.get("/api/works").status_code == 200
    assert client.get("/api/about").json()["auth_required"] is True


def test_post_without_cookie_is_401_after_password_set(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    r = client.post("/api/queue/authors/decide", json={"link_ids": [1], "decision": "confirm"})
    assert r.status_code == 401 and "detail" in r.json()


def test_login_wrong_password_is_401(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    r = client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "sai"})
    assert r.status_code == 401 and "detail" in r.json()


def test_login_rate_limited_after_five_failures(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    for _ in range(5):
        assert client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "sai"}).status_code == 401
    r = client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "sai"})
    assert r.status_code == 429
    # đúng mật khẩu cũng bị chặn khi đã vượt ngưỡng trong cửa sổ 5 phút
    r2 = client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "MatKhauManh!1"})
    assert r2.status_code == 429


def test_login_reports_unit_code_for_scoped_role(client, conn, user_id):
    """lát cắt H1: `GET /api/auth/me` trả thêm `unit_code` cho vai trò cấp khoa."""
    unit_id = q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id",
               "khoa-auth-h1", "Khoa Đăng nhập H1")[0]["id"]
    uid, email = mk_user(conn, ["faculty_officer"], password="MatKhauKhoa!4", email="khoa.h1@ictu.test")
    q(conn, "UPDATE app_user SET unit_id=%s WHERE id=%s", unit_id, uid)
    conn.commit()
    r = client.post("/api/auth/login", json={"email": email, "password": "MatKhauKhoa!4"})
    assert r.status_code == 200, r.text
    assert r.json()["unit_code"] == "khoa-auth-h1"
    me = client.get("/api/auth/me").json()
    assert me["user"]["unit_code"] == "khoa-auth-h1"


def test_login_success_sets_cookie_and_me_reflects_user(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    r = client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "MatKhauManh!1"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == "rd@ictu.test" and body["roles"] == ["rd_officer"]
    assert client.cookies.get("cris_session")
    me = client.get("/api/auth/me").json()
    assert me["auth_required"] is True and me["user"]["email"] == "rd@ictu.test"


def test_login_then_post_decide_succeeds_with_cookie(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    assert client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "MatKhauManh!1"}).status_code == 200
    r = client.post("/api/queue/authors/decide", json={"link_ids": [999999], "decision": "confirm"})
    # đã đăng nhập + đúng vai trò rd_officer → qua khỏi 401/403, còn lại là lỗi nghiệp vụ (id không tồn tại)
    assert r.status_code == 400 and "999999" in r.json()["detail"]


def test_logout_clears_cookie_and_protected_route_401(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "MatKhauManh!1"})
    r = client.post("/api/auth/logout")
    assert r.status_code == 200 and r.json() == {"ok": True}
    me = client.get("/api/auth/me").json()
    assert me["user"] is None
    r2 = client.post("/api/queue/authors/decide", json={"link_ids": [1], "decision": "confirm"})
    assert r2.status_code == 401


def test_wrong_role_is_403(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    mk_user(conn, ["lecturer"], password="MatKhauKhac!2", email="gv@ictu.test")
    assert client.post("/api/auth/login", json={"email": "gv@ictu.test", "password": "MatKhauKhac!2"}).status_code == 200
    r = client.post("/api/periods", json={
        "code": "K2026-AUTH-2", "name": "Kỳ báo cáo", "scope": {}, "due_at": due_soon().isoformat()})
    assert r.status_code == 403


def test_compare_open_to_any_logged_in_role(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    mk_user(conn, ["lecturer"], password="MatKhauKhac!2", email="gv2@ictu.test")
    assert client.post("/api/auth/login", json={"email": "gv2@ictu.test", "password": "MatKhauKhac!2"}).status_code == 200
    r = client.post("/api/compare", json={"title": "một đề tài bất kỳ để đối chiếu", "description": ""})
    assert r.status_code == 200, r.text


def test_compare_without_login_is_401_when_auth_required(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    r = client.post("/api/compare", json={"title": "một đề tài bất kỳ để đối chiếu", "description": ""})
    assert r.status_code == 401


def test_audit_requires_login_when_auth_required(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    assert client.get("/api/audit").status_code == 401
    assert client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "MatKhauManh!1"}).status_code == 200
    assert client.get("/api/audit").status_code == 200


def test_expired_session_is_treated_as_logged_out(client, conn, user_id):
    auth.set_password(conn, "rd@ictu.test", "MatKhauManh!1")
    client.post("/api/auth/login", json={"email": "rd@ictu.test", "password": "MatKhauManh!1"})
    token = client.cookies.get("cris_session")
    assert token
    q(conn, "UPDATE session SET expires_at = now() - interval '1 second' WHERE id=%s", token)
    conn.commit()
    me = client.get("/api/auth/me").json()
    assert me["user"] is None
    r = client.post("/api/queue/authors/decide", json={"link_ids": [1], "decision": "confirm"})
    assert r.status_code == 401


# ---------- CLI ----------

def test_cli_user_set_password_and_list(conn, user_id, monkeypatch, capsys):
    monkeypatch.setenv("CRIS_PASSWORD", "TuDongDatQuaCLI!3")
    cli.main(["user", "set-password", "rd@ictu.test"])
    row = q(conn, "SELECT password_hash FROM app_user WHERE email=%s", "rd@ictu.test")[0]
    assert row["password_hash"] and row["password_hash"].startswith("pbkdf2_sha256$")
    assert auth.verify(conn, "rd@ictu.test", "TuDongDatQuaCLI!3") is not None

    capsys.readouterr()
    cli.main(["user", "list"])
    out = capsys.readouterr().out
    assert "rd@ictu.test" in out and '"has_password": true' in out
