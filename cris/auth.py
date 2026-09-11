# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đăng nhập cục bộ (NFR-01): mật khẩu băm PBKDF2-HMAC-SHA256, phiên lưu trong
bảng `session`. Chỉ dùng thư viện chuẩn (`hashlib`, `secrets`, `hmac`) — không
thêm dependency (xem DEPENDENCIES.md).

"Chế độ mở": khi chưa `app_user` nào có `password_hash`, `auth_required()` trả
về False và tầng API không bắt buộc đăng nhập (giữ hành vi cũ cho bộ test và
bản demo). Ngay khi một người dùng đặt mật khẩu, chế độ mở tắt cho toàn hệ
thống.
"""
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from cris.db import tx

SCHEME = "pbkdf2_sha256"
ITERATIONS = 260_000
SALT_BYTES = 16
SESSION_TOKEN_BYTES = 32
SESSION_TTL = timedelta(hours=12)
SESSION_RENEW_AFTER = timedelta(minutes=5)   # gia hạn expires_at tối đa 1 lần/5 phút
COOKIE_NAME = "cris_session"


def hash_password(password: str) -> str:
    """`pbkdf2_sha256$<vòng>$<salt hex>$<hash hex>` — salt 16 byte, 260.000 vòng."""
    salt = secrets.token_hex(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS).hex()
    return f"{SCHEME}${ITERATIONS}${salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt, digest = encoded.split("$")
    except (ValueError, AttributeError):
        return False
    if scheme != SCHEME:
        return False
    calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)).hex()
    return hmac.compare_digest(calc, digest)


def set_password(conn, email, password):
    """Đặt/đổi mật khẩu cho `email` đã có trong `app_user`. Không tự tạo người
    dùng mới. Trả về id; ValueError nếu không tìm thấy email hoặc mật khẩu rỗng."""
    if not password:
        raise ValueError("mật khẩu không được rỗng")
    encoded = hash_password(password)
    with tx(conn), conn.cursor() as cur:
        cur.execute("UPDATE app_user SET password_hash=%s WHERE email=%s RETURNING id", (encoded, email))
        row = cur.fetchone()
    if row is None:
        raise ValueError(f"không tìm thấy người dùng: {email}")
    return row["id"]


def verify(conn, email, password):
    """`app_user` nếu email + mật khẩu khớp và tài khoản `active` có mật khẩu,
    ngược lại None (không phân biệt "không tồn tại" và "sai mật khẩu")."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM app_user WHERE email=%s AND active", (email,))
        user = cur.fetchone()
    if user is None or not user.get("password_hash"):
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def create_session(conn, user_id, user_agent=None):
    """Tạo phiên mới (token 32 byte urlsafe, hết hạn sau `SESSION_TTL`). Trả về token."""
    token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
    now = datetime.now(UTC)
    with tx(conn), conn.cursor() as cur:
        cur.execute(
            "INSERT INTO session(id, user_id, created_at, expires_at, last_seen_at, user_agent) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (token, user_id, now, now + SESSION_TTL, now, user_agent))
    return token


def session_user(conn, token):
    """`app_user` gắn với phiên còn hạn, hoặc None. Gia hạn `expires_at` khi phiên
    được dùng, tối đa một lần mỗi `SESSION_RENEW_AFTER` để tránh ghi liên tục."""
    if not token:
        return None
    now = datetime.now(UTC)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT s.expires_at AS session_expires_at, s.last_seen_at AS session_last_seen_at, u.* "
            "FROM session s JOIN app_user u ON u.id = s.user_id WHERE s.id=%s AND u.active", (token,))
        row = cur.fetchone()
    if row is None or row["session_expires_at"] < now:
        return None
    if now - row["session_last_seen_at"] >= SESSION_RENEW_AFTER:
        with tx(conn), conn.cursor() as cur:
            cur.execute("UPDATE session SET expires_at=%s, last_seen_at=%s WHERE id=%s",
                        (now + SESSION_TTL, now, token))
    return row


def revoke(conn, token):
    """Xoá phiên (đăng xuất). Không lỗi nếu token không tồn tại."""
    with tx(conn), conn.cursor() as cur:
        cur.execute("DELETE FROM session WHERE id=%s", (token,))


def auth_required(conn):
    """True nếu có ít nhất một `app_user.active` đã đặt mật khẩu — "chế độ mở"
    khi chưa ai đặt (xem docstring module)."""
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM app_user WHERE active AND password_hash IS NOT NULL LIMIT 1")
        return cur.fetchone() is not None


def create_lecturers(conn, unit_code=None, dry_run=False):
    """`python -m cris user create-lecturers` (H3): với mỗi `person`
    `kind='lecturer'` có `email` mà chưa có `app_user` cùng email, tạo tài
    khoản `roles=['lecturer']` không mật khẩu, `person_id`/`unit_id` map sẵn
    từ `person`. `unit_code` lọc theo `person.unit_id` (mã `unit.code`).
    `dry_run` chỉ đếm, không ghi gì vào CSDL. Idempotent — chạy lại không tạo
    trùng (khớp theo `email`). Trả `{"created": n, "skipped": n}`."""
    where = ["p.kind='lecturer'", "p.email IS NOT NULL"]
    params = []
    if unit_code:
        where.append("u.code=%s")
        params.append(unit_code)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT p.id, p.email, p.display_name, p.unit_id FROM person p "
            f"LEFT JOIN unit u ON u.id = p.unit_id WHERE {' AND '.join(where)} ORDER BY p.id",
            params)
        persons = cur.fetchall()
    created, skipped = 0, 0
    for p in persons:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM app_user WHERE email=%s", (p["email"],))
            exists = cur.fetchone() is not None
        if exists:
            skipped += 1
            continue
        if not dry_run:
            with tx(conn), conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO app_user(email, display_name, roles, person_id, unit_id) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (p["email"], p["display_name"], ["lecturer"], p["id"], p["unit_id"]))
        created += 1
    return {"created": created, "skipped": skipped}


def list_users(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, email, display_name, roles, unit_id, active, "
            "(password_hash IS NOT NULL) AS has_password FROM app_user ORDER BY id")
        return cur.fetchall()
