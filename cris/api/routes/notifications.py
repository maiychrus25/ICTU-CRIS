# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Thông báo trong ứng dụng (lát cắt L2): danh sách/đếm chưa đọc của chính
người đang đăng nhập (`current_user`, đăng nhập bắt buộc khi auth bật; chế độ
mở dùng actor mặc định như mọi route khác — xem `cris.api.deps`), đánh dấu đã
đọc từng thông báo hoặc toàn bộ. Nội dung được sinh bởi `cris.notify` (móc gọi
từ các route khác) — router này chỉ đọc/đánh dấu, không tự ghi thông báo mới.
Đọc thông báo của người khác → 404 (không lộ có tồn tại thông báo đó hay
không, và không cho biết id đó thuộc về ai)."""
from fastapi import APIRouter, HTTPException, Query

from cris.api.deps import Conn, CurrentUser
from cris.api.schemas import MarkAllReadOut, NotificationList, NotificationRow, Page

router = APIRouter(prefix="/api/notifications", tags=["thong-bao"])
PER_PAGE = 50


def _row_out(r):
    return NotificationRow(id=r["id"], kind=r["kind"], title=r["title"], body=r["body"], link=r["link"],
                           created_at=r["created_at"], read_at=r["read_at"])


@router.get("", response_model=NotificationList)
def list_notifications(conn: Conn, user: CurrentUser, unread: int = 0, page: int = Query(1, ge=1)):
    uid = user["id"]
    where = ["user_id = %s"]
    params = [uid]
    if unread:
        where.append("read_at IS NULL")
    where_sql = " AND ".join(where)
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n FROM notification WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM notification WHERE user_id = %s AND read_at IS NULL", (uid,))
        unread_count = cur.fetchone()["n"]
        cur.execute(
            f"SELECT * FROM notification WHERE {where_sql} ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
            [*params, PER_PAGE, (page - 1) * PER_PAGE])
        rows = cur.fetchall()
    return NotificationList(items=[_row_out(r) for r in rows], page=Page(page=page, per_page=PER_PAGE, total=total),
                            unread=unread_count)


@router.post("/{nid}/read", response_model=NotificationRow)
def mark_read(conn: Conn, user: CurrentUser, nid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notification WHERE id=%s AND user_id=%s", (nid, user["id"]))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, f"không tìm thấy thông báo #{nid}")
    if row["read_at"] is None:
        with conn.cursor() as cur:
            cur.execute("UPDATE notification SET read_at = now() WHERE id=%s RETURNING *", (nid,))
            row = cur.fetchone()
        conn.commit()
    return _row_out(row)


@router.post("/read-all", response_model=MarkAllReadOut)
def mark_all_read(conn: Conn, user: CurrentUser):
    with conn.cursor() as cur:
        cur.execute("UPDATE notification SET read_at = now() WHERE user_id=%s AND read_at IS NULL", (user["id"],))
        marked = cur.rowcount
    conn.commit()
    return MarkAllReadOut(ok=True, marked=marked)
