# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Phụ thuộc dùng chung: kết nối DB mỗi request, người thao tác, lô giao dịch."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException

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


def get_actor_id(conn: Conn, x_cris_user: Annotated[str | None, Header(alias="X-CRIS-User")] = None) -> int:
    """Người thao tác. Chưa có đăng nhập (NFR-01 ngoài phạm vi): nhận id qua header
    `X-CRIS-User`, nếu không thì người dùng `rd_officer` đầu tiên; không có ai → 503."""
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


Actor = Annotated[int, Depends(get_actor_id)]


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
