# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Giảng viên tự kê khai (lát cắt H3): `GET/POST /api/me/works`,
`GET/POST /api/me/declarations`, CLI `user create-lecturers`. API FastAPI trên
PostgreSQL thật (fixture `conn`), theo khuôn `test_api_declarations.py`. Chế
độ mở dùng header `X-CRIS-User=<id>` để đóng vai `lecturer` — xem
`cris.api.deps.current_user`."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import auth, rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    uid = q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]
    conn.commit()
    return uid


def mk_person(conn, name, unit_id=None, email=None, kind="lecturer"):
    pid = q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id, email) "
                  "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            kind, name, name.lower(), [name.lower()], unit_id, email)[0]["id"]
    conn.commit()
    return pid


def mk_mention(conn, work_id, raw_name, position=1):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw_name, raw_name.lower(), raw_name.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state="DaNoiTuDong"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


def own_work(conn, person_id, title, unit_id=None, state="DaNoiTuDong"):
    """Tạo một công trình và liên kết tác giả sống với `person_id` — "công
    trình của tôi" theo `v_person_publications`."""
    work_id = mk_work(conn, title, doc_type="bai_bao")
    mention_id = mk_mention(conn, work_id, title)
    mk_link(conn, mention_id, person_id, state=state)
    conn.commit()
    return work_id


def mk_lecturer_user(conn, person_id, unit_id=None, email=None):
    """`app_user` vai trò `lecturer` gắn với `person_id` (đóng vai qua
    `X-CRIS-User` ở chế độ mở)."""
    email = email or f"gv-{uuid.uuid4().hex[:10]}@ictu.test"
    uid = q(conn, "INSERT INTO app_user(email, display_name, roles, person_id, unit_id) "
                  "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            email, "Giảng viên kiểm thử", ["lecturer"], person_id, unit_id)[0]["id"]
    conn.commit()
    return uid


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


def open_period(client, code="K2026-ME-1"):
    r = client.post("/api/periods", json={
        "code": code, "name": "Kỳ báo cáo kê khai", "scope": {"doc_types": ["bai_bao"]},
        "criteria": None, "due_at": due_soon().isoformat()})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ---------- GET /api/me/works ----------

def test_lecturer_sees_only_own_works(client, conn, user_id):
    unit_id = mk_unit(conn)
    me = mk_person(conn, "Giảng viên Một", unit_id, email="gv1@ictu.test")
    other = mk_person(conn, "Giảng viên Hai", unit_id, email="gv2@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    own_work(conn, me, "Bài của tôi")
    own_work(conn, other, "Bài của người khác")

    r = client.get("/api/me/works", headers=as_user(client, lecturer))
    assert r.status_code == 200, r.text
    titles = [i["title"] for i in r.json()["items"]]
    assert titles == ["Bài của tôi"]


def test_works_without_person_id_is_409(client, conn, user_id):
    lecturer = q(conn, "INSERT INTO app_user(email, display_name, roles) VALUES (%s,%s,%s) RETURNING id",
                "gv-no-person@ictu.test", "Giảng viên chưa gắn hồ sơ", ["lecturer"])[0]["id"]
    conn.commit()
    r = client.get("/api/me/works", headers=as_user(client, lecturer))
    assert r.status_code == 409
    assert r.json()["detail"] == "Tài khoản chưa gắn với hồ sơ giảng viên"


def test_my_works_declared_in_reflects_period_ids(client, conn, user_id):
    unit_id = mk_unit(conn)
    me = mk_person(conn, "Giảng viên Ba", unit_id, email="gv3@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    work_id = own_work(conn, me, "Bài đã kê khai")
    pid = open_period(client, "K2026-ME-2")
    r = client.post("/api/me/declarations", json={"period_id": pid, "work_id": work_id},
                    headers=as_user(client, lecturer))
    assert r.status_code == 201, r.text

    listing = client.get("/api/me/works", headers=as_user(client, lecturer)).json()
    item = next(i for i in listing["items"] if i["work_id"] == work_id)
    assert item["declared_in"] == [pid]


# ---------- POST /api/me/declarations ----------

def test_lecturer_declares_own_work_into_own_unit(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-1", "Khoa H3 Một")
    me = mk_person(conn, "Giảng viên Bốn", unit_id, email="gv4@ictu.test")
    # app_user.unit_id để NULL để kiểm tra suy ra từ person.unit_id.
    lecturer = mk_lecturer_user(conn, me, unit_id=None)
    work_id = own_work(conn, me, "Bài tự kê khai")
    pid = open_period(client, "K2026-ME-3")

    r = client.post("/api/me/declarations", json={"period_id": pid, "work_id": work_id},
                    headers=as_user(client, lecturer))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["state"] == "Nhap" and body["unit_id"] == unit_id and body["work_id"] == work_id


def test_lecturer_declaring_others_work_is_403(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-2", "Khoa H3 Hai")
    me = mk_person(conn, "Giảng viên Năm", unit_id, email="gv5@ictu.test")
    other = mk_person(conn, "Giảng viên Sáu", unit_id, email="gv6@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    others_work = own_work(conn, other, "Bài của người khác 2")
    pid = open_period(client, "K2026-ME-4")

    r = client.post("/api/me/declarations", json={"period_id": pid, "work_id": others_work},
                    headers=as_user(client, lecturer))
    assert r.status_code == 403 and "detail" in r.json()


def test_lecturer_declaring_into_closed_period_is_409(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-3", "Khoa H3 Ba")
    me = mk_person(conn, "Giảng viên Bảy", unit_id, email="gv7@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    work_id = own_work(conn, me, "Bài kỳ đã đóng")
    pid = open_period(client, "K2026-ME-5")
    assert client.post(f"/api/periods/{pid}/close").status_code == 200

    r = client.post("/api/me/declarations", json={"period_id": pid, "work_id": work_id},
                    headers=as_user(client, lecturer))
    assert r.status_code == 409


# ---------- vai trò lecturer đi qua set_state ----------

def test_lecturer_submits_own_declaration_for_faculty_review(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-4", "Khoa H3 Bốn")
    me = mk_person(conn, "Giảng viên Tám", unit_id, email="gv8@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    work_id = own_work(conn, me, "Bài trình khoa")
    pid = open_period(client, "K2026-ME-6")
    did = client.post("/api/me/declarations", json={"period_id": pid, "work_id": work_id},
                      headers=as_user(client, lecturer)).json()["id"]

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"},
                    headers=as_user(client, lecturer))
    assert r.status_code == 200 and r.json()["state"] == "ChoKhoaDuyet"


def test_lecturer_submitting_others_declaration_is_403(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-5", "Khoa H3 Năm")
    owner = mk_person(conn, "Giảng viên Chín", unit_id, email="gv9@ictu.test")
    stranger = mk_person(conn, "Giảng viên Mười", unit_id, email="gv10@ictu.test")
    owner_user = mk_lecturer_user(conn, owner, unit_id)
    stranger_user = mk_lecturer_user(conn, stranger, unit_id)
    work_id = own_work(conn, owner, "Bài của chủ hồ sơ")
    pid = open_period(client, "K2026-ME-7")
    did = client.post("/api/me/declarations", json={"period_id": pid, "work_id": work_id},
                      headers=as_user(client, owner_user)).json()["id"]

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "ChoKhoaDuyet"},
                    headers=as_user(client, stranger_user))
    assert r.status_code == 403


def test_lecturer_withdraws_own_declaration(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-6", "Khoa H3 Sáu")
    me = mk_person(conn, "Giảng viên Mười Một", unit_id, email="gv11@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    work_id = own_work(conn, me, "Bài rút")
    pid = open_period(client, "K2026-ME-8")
    did = client.post("/api/me/declarations", json={"period_id": pid, "work_id": work_id},
                      headers=as_user(client, lecturer)).json()["id"]

    r = client.post(f"/api/declarations/{did}/state", json={"to_state": "Rut", "reason": "kê khai nhầm"},
                    headers=as_user(client, lecturer))
    assert r.status_code == 200 and r.json()["state"] == "Rut"


# ---------- GET /api/me/declarations ----------

def test_my_declarations_lists_only_own(client, conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-7", "Khoa H3 Bảy")
    me = mk_person(conn, "Giảng viên Mười Hai", unit_id, email="gv12@ictu.test")
    other = mk_person(conn, "Giảng viên Mười Ba", unit_id, email="gv13@ictu.test")
    lecturer = mk_lecturer_user(conn, me, unit_id)
    other_lecturer = mk_lecturer_user(conn, other, unit_id)
    my_work = own_work(conn, me, "Bài của tôi kê khai")
    others_work = own_work(conn, other, "Bài người khác kê khai")
    pid = open_period(client, "K2026-ME-9")
    client.post("/api/me/declarations", json={"period_id": pid, "work_id": my_work},
               headers=as_user(client, lecturer))
    client.post("/api/me/declarations", json={"period_id": pid, "work_id": others_work},
               headers=as_user(client, other_lecturer))

    listing = client.get("/api/me/declarations", headers=as_user(client, lecturer)).json()
    assert [i["work_id"] for i in listing["items"]] == [my_work]


# ---------- GET /api/auth/me trả person_id ----------

def test_auth_me_reports_person_id_for_lecturer(client, conn, user_id):
    """`GET /api/auth/me` trả thêm `person_id` (H3) một khi đã đăng nhập bằng
    mật khẩu — chế độ mở không đọc `X-CRIS-User` cho `/api/auth/me`."""
    unit_id = mk_unit(conn, "khoa-me-8", "Khoa H3 Tám")
    me = mk_person(conn, "Giảng viên Mười Bốn", unit_id, email="gv14@ictu.test")
    mk_lecturer_user(conn, me, unit_id, email="gv14-login@ictu.test")
    auth.set_password(conn, "gv14-login@ictu.test", "MatKhauGV!14")

    r = client.post("/api/auth/login", json={"email": "gv14-login@ictu.test", "password": "MatKhauGV!14"})
    assert r.status_code == 200 and r.json()["person_id"] == me

    me_out = client.get("/api/auth/me").json()
    assert me_out["user"]["person_id"] == me


# ---------- CLI: python -m cris user create-lecturers ----------

def test_cli_create_lecturers_is_idempotent(conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-cli", "Khoa H3 CLI")
    mk_person(conn, "Giảng viên CLI Một", unit_id, email="cli1@ictu.test")
    mk_person(conn, "Giảng viên CLI Hai", unit_id, email="cli2@ictu.test")
    mk_person(conn, "Không phải giảng viên", unit_id, email="sv1@ictu.test", kind="student")
    conn.commit()

    result = auth.create_lecturers(conn, unit_code="khoa-me-cli")
    assert result == {"created": 2, "skipped": 0}
    rows = q(conn, "SELECT email, roles, person_id, unit_id FROM app_user WHERE email IN (%s,%s)",
            "cli1@ictu.test", "cli2@ictu.test")
    assert len(rows) == 2
    assert all(r["roles"] == ["lecturer"] for r in rows)
    assert all(r["unit_id"] == unit_id for r in rows)

    again = auth.create_lecturers(conn, unit_code="khoa-me-cli")
    assert again == {"created": 0, "skipped": 2}


def test_cli_create_lecturers_dry_run_does_not_write(conn, user_id):
    unit_id = mk_unit(conn, "khoa-me-cli-2", "Khoa H3 CLI 2")
    mk_person(conn, "Giảng viên CLI Ba", unit_id, email="cli3@ictu.test")
    conn.commit()

    result = auth.create_lecturers(conn, unit_code="khoa-me-cli-2", dry_run=True)
    assert result == {"created": 1, "skipped": 0}
    assert q(conn, "SELECT 1 FROM app_user WHERE email=%s", "cli3@ictu.test") == []
