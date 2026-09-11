# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Phụ thuộc dùng chung: kết nối DB mỗi request, người thao tác, lô giao dịch,
đăng nhập (NFR-01) và kiểm vai trò."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from cris import auth as auth_mod
from cris import db


def get_conn():
    """Một kết nối psycopg cho mỗi request; FastAPI cache nên mọi Depends trong
    cùng request dùng chung kết nối này."""
    conn = db.connect()
    try:
        yield conn
    finally:
        conn.close()


Conn = Annotated[object, Depends(get_conn)]


def _cookie_user(conn, request: Request):
    """Người dùng gắn với cookie phiên `cris_session`, hoặc None nếu không có/hết hạn."""
    token = request.cookies.get(auth_mod.COOKIE_NAME)
    return auth_mod.session_user(conn, token) if token else None


def _resolve_actor_id(conn, request: Request, x_cris_user: str | None) -> int:
    """Chọn actor: `auth_required` → bắt buộc cookie phiên hợp lệ (401 nếu
    không); chế độ mở → header `X-CRIS-User`, nếu không thì `rd_officer` đầu
    tiên (503 nếu chưa có ai). Dùng chung cho `get_actor_id` và `current_user`."""
    if auth_mod.auth_required(conn):
        user = _cookie_user(conn, request)
        if user is None:
            raise HTTPException(401, "Cần đăng nhập.")
        return user["id"]
    with conn.cursor() as cur:
        if x_cris_user and x_cris_user.isdigit():
            cur.execute("SELECT id FROM app_user WHERE id=%s", (int(x_cris_user),))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(404, f"không có người dùng #{x_cris_user}")
            return row["id"]
        cur.execute("SELECT id FROM app_user WHERE 'rd_officer' = ANY(roles) ORDER BY id LIMIT 1")
        row = cur.fetchone()
    if row is None:
        raise HTTPException(
            503,
            "Chưa có người dùng nào có vai trò 'rd_officer' để ghi nhận thao tác. Tạo bằng: "
            "INSERT INTO app_user(email, display_name, roles) VALUES ('ten@ictu.edu.vn', 'Tên hiển thị', ARRAY['rd_officer']);",
        )
    return row["id"]


def get_actor_id(conn: Conn, request: Request,
                  x_cris_user: Annotated[str | None, Header(alias="X-CRIS-User")] = None) -> int:
    """Người thao tác.

    `auth_required` (đã có người đặt mật khẩu, NFR-01): bắt buộc cookie phiên
    `cris_session` hợp lệ, bỏ qua header `X-CRIS-User` → 401 nếu chưa đăng nhập.

    Chế độ mở (chưa ai đặt mật khẩu): giữ hành vi cũ — nhận id qua header
    `X-CRIS-User`, nếu không thì người dùng `rd_officer` đầu tiên; không có ai → 503.
    """
    return _resolve_actor_id(conn, request, x_cris_user)


Actor = Annotated[int, Depends(get_actor_id)]


def current_user(conn: Conn, request: Request,
                  x_cris_user: Annotated[str | None, Header(alias="X-CRIS-User")] = None) -> dict:
    """Người thao tác đầy đủ: `{id, roles, unit_id, unit_code, person_id}`.

    Chọn actor theo đúng quy tắc `get_actor_id` (chế độ mở vẫn dùng được
    header `X-CRIS-User` để thử vai). Trả thêm `roles`/`unit_id`/`unit_code`
    để tầng nghiệp vụ (`cris.declare`) kiểm vai trò và phạm vi đơn vị (NFR-02);
    `person_id` (H3) để giảng viên tự kê khai kiểm sở hữu công trình của mình.
    """
    actor_id = _resolve_actor_id(conn, request, x_cris_user)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT u.id, u.roles, u.unit_id, u.person_id, un.code AS unit_code "
            "FROM app_user u LEFT JOIN unit un ON un.id = u.unit_id WHERE u.id=%s",
            (actor_id,))
        row = cur.fetchone()
    return {"id": row["id"], "roles": row["roles"] or [], "unit_id": row["unit_id"],
            "unit_code": row["unit_code"], "person_id": row["person_id"]}


CurrentUser = Annotated[dict, Depends(current_user)]


def require_role(*roles: str):
    """Factory dependency: như `Actor`, và khi `roles` khác rỗng còn bắt buộc
    actor có ít nhất một trong các vai trò đó (403 nếu không) — áp dụng cả ở chế
    độ mở (actor mặc định luôn là `rd_officer` do cách `get_actor_id` chọn; header
    `X-CRIS-User` có thể trỏ tới người khác để thử quyền). `roles` rỗng = chỉ cần
    xác định được actor, không đòi vai trò cụ thể (dùng cho `/api/compare`: mọi
    vai trò đã đăng nhập)."""
    def _dep(conn: Conn, actor: Actor) -> int:
        if not roles:
            return actor
        with conn.cursor() as cur:
            cur.execute("SELECT roles FROM app_user WHERE id=%s", (actor,))
            row = cur.fetchone()
        actor_roles = (row["roles"] if row else None) or []
        if not any(r in actor_roles for r in roles):
            raise HTTPException(403, f"Cần vai trò: {', '.join(roles)}.")
        return actor
    return _dep


def require_login(conn: Conn, request: Request):
    """Bắt buộc phiên đăng nhập hợp lệ khi `auth_required`; chế độ mở thì không
    kiểm gì (giữ hành vi cũ — dùng cho GET không cần actor, vd `/api/audit`)."""
    if not auth_mod.auth_required(conn):
        return None
    user = _cookie_user(conn, request)
    if user is None:
        raise HTTPException(401, "Cần đăng nhập.")
    return user


class DeferredCommitConn:
    """Bọc kết nối thật: `commit()` là no-op, `rollback()` xuyên thẳng xuống.

    `link.decide_link` tự commit sau mỗi lời gọi; để một lô nhiều id nằm trong
    một giao dịch (một id hỏng → không id nào đổi), route gọi qua lớp bọc này rồi
    tự commit một lần khi cả lô xong.
    """

    def __init__(self, conn):
        self._conn = conn

    def commit(self):
        pass

    def rollback(self):
        self._conn.rollback()

    def __getattr__(self, name):
        return getattr(self._conn, name)
