# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đăng nhập cục bộ (NFR-01): `POST /login` đặt cookie phiên `cris_session`
(HttpOnly, SameSite=Lax, `Secure` khi `CRIS_COOKIE_SECURE=1`), `POST /logout`
xoá phiên, `GET /me` trả người dùng hiện tại (hoặc `null`) và `auth_required` để
giao diện biết đăng nhập có bắt buộc không. Rate limit 5 lần sai/5 phút theo
email, bộ nhớ tiến trình — đủ cho một tiến trình `uvicorn` duy nhất, không
chia sẻ giữa nhiều worker."""
import os
import time

from fastapi import APIRouter, HTTPException, Request, Response

from cris import auth as auth_mod
from cris.api.deps import Conn
from cris.api.schemas import LoginIn, MeOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["dang-nhap"])

RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW_S = 300

_failures: dict[str, list[float]] = {}


def _cookie_secure() -> bool:
    return (os.environ.get("CRIS_COOKIE_SECURE") or "") == "1"


def _rate_limited(email: str) -> bool:
    now = time.monotonic()
    hits = [t for t in _failures.get(email, []) if now - t < RATE_LIMIT_WINDOW_S]
    _failures[email] = hits
    return len(hits) >= RATE_LIMIT_MAX


def _record_failure(email: str) -> None:
    _failures.setdefault(email, []).append(time.monotonic())


def _user_out(row) -> UserOut:
    return UserOut(id=row["id"], email=row["email"], display_name=row["display_name"],
                   roles=row["roles"] or [], unit_id=row["unit_id"])


@router.post("/login", response_model=UserOut)
def login(conn: Conn, request: Request, response: Response, body: LoginIn):
    email = body.email.strip()
    if _rate_limited(email):
        raise HTTPException(429, "Quá nhiều lần đăng nhập sai. Thử lại sau vài phút.")
    user = auth_mod.verify(conn, email, body.password)
    if user is None:
        _record_failure(email)
        raise HTTPException(401, "Email hoặc mật khẩu không đúng.")
    _failures.pop(email, None)
    token = auth_mod.create_session(conn, user["id"], request.headers.get("user-agent"))
    response.set_cookie(auth_mod.COOKIE_NAME, token, httponly=True, samesite="lax",
                        secure=_cookie_secure(), max_age=int(auth_mod.SESSION_TTL.total_seconds()))
    return _user_out(user)


@router.post("/logout")
def logout(conn: Conn, request: Request, response: Response):
    token = request.cookies.get(auth_mod.COOKIE_NAME)
    if token:
        auth_mod.revoke(conn, token)
    response.delete_cookie(auth_mod.COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=MeOut)
def me(conn: Conn, request: Request):
    required = auth_mod.auth_required(conn)
    token = request.cookies.get(auth_mod.COOKIE_NAME)
    user = auth_mod.session_user(conn, token) if token else None
    return MeOut(user=_user_out(user) if user else None, auth_required=required)
