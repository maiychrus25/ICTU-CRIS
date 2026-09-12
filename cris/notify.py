# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Thông báo trong ứng dụng (lát cắt L2 — BA điểm "H": người dùng biết hồ sơ
của mình đổi trạng thái), migration `0019_notification.sql`.

`notify(conn, user_ids, ...)` là hàm ghi duy nhất: bỏ trùng người nhận, bỏ
chính người thao tác (`exclude_user_id`), ghi mọi dòng trong một giao dịch.
Ba hàm móc (`on_declaration_state`, `on_period_state`, `on_link_confirmed`)
gọi `notify` với danh sách người nhận tính theo vai trò/đơn vị — **gọi từ
route** (`cris/api/routes/{declarations,periods,queue}.py`) sau khi hàm
nghiệp vụ (`cris.declare`/`cris.period`/`cris.link`) đã thành công, không sửa
các module đó. Lỗi khi gửi thông báo không được làm hỏng thao tác chính: mỗi
hàm móc tự bắt mọi ngoại lệ và chỉ ghi log.

Nhãn trạng thái tiếng Việt của hồ sơ kê khai dùng lại `cris.report.STATE_LABELS`
(đã có sẵn từ lát cắt L1) — không định nghĩa lại.
"""
import logging

from cris.db import tx
from cris.report import STATE_LABELS

logger = logging.getLogger(__name__)

TITLE_MAX = 60

# to_state của declaration coi là "trả về" (hồ sơ quay lại tay người tạo để
# sửa/rút) — ngoài người tạo, còn báo thêm cho faculty_officer cùng đơn vị.
_RETURNED_STATES = ("Nhap", "ChoBoSung", "Rut")
# to_state chỉ cần báo cho người tạo, không cần thêm faculty_officer.
_CREATOR_ONLY_STATES = ("DatYeuCau", "DaChot")


def _truncate(text, limit=TITLE_MAX):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _format_date(dt):
    return dt.strftime("%d/%m/%Y") if dt is not None else None


def notify(conn, user_ids, *, kind, title, body="", link=None, exclude_user_id=None):
    """Ghi một thông báo cho mỗi người trong `user_ids` (bỏ trùng, bỏ
    `exclude_user_id` — không bao giờ tự báo cho chính người thao tác), trong
    một giao dịch. `user_ids` rỗng (sau khi lọc) thì không làm gì. Trả về danh
    sách id các thông báo đã ghi (rỗng nếu không có ai nhận)."""
    recipients = {uid for uid in user_ids if uid is not None}
    if exclude_user_id is not None:
        recipients.discard(exclude_user_id)
    if not recipients:
        return []
    ids = []
    with tx(conn), conn.cursor() as cur:
        for uid in recipients:
            cur.execute(
                "INSERT INTO notification(user_id, kind, title, body, link) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (uid, kind, title, body, link))
            ids.append(cur.fetchone()["id"])
    return ids


def recipients_by_role(conn, roles, unit_id=None):
    """id các `app_user` đang hoạt động (`active`) có ít nhất một vai trò
    trong `roles`; `unit_id` khác `None` lọc thêm theo đơn vị."""
    sql = "SELECT id FROM app_user WHERE active AND roles && %s::text[]"
    params = [list(roles)]
    if unit_id is not None:
        sql += " AND unit_id = %s"
        params.append(unit_id)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return [r["id"] for r in cur.fetchall()]


def on_declaration_state(conn, declaration_id, from_state, to_state, actor_id, reason=None):
    """Hồ sơ kê khai đổi trạng thái (`from_state` → `to_state`).

    Người nhận theo bảng của lát cắt L2: `ChoKhoaDuyet` → `faculty_head` cùng
    đơn vị hồ sơ; `KhoaDaDuyet`/`ChoPhongKiemTra` → mọi `rd_officer`;
    `DatYeuCau`/`DaChot`/nhóm "trả về" (`Nhap`/`ChoBoSung`/`Rut`) → người tạo
    hồ sơ, cộng thêm `faculty_officer` cùng đơn vị khi là nhóm "trả về". Không
    báo cho chính người vừa chuyển trạng thái (`actor_id`).
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT d.unit_id, d.created_by, w.title FROM declaration d "
                "JOIN work w ON w.id = d.work_id WHERE d.id=%s", (declaration_id,))
            row = cur.fetchone()
        if row is None:
            return
        unit_id, created_by, title = row["unit_id"], row["created_by"], row["title"]

        recipients = []
        if to_state == "ChoKhoaDuyet":
            recipients = recipients_by_role(conn, ("faculty_head",), unit_id=unit_id)
        elif to_state in ("KhoaDaDuyet", "ChoPhongKiemTra"):
            recipients = recipients_by_role(conn, ("rd_officer",))
        elif to_state in _CREATOR_ONLY_STATES:
            recipients = [created_by]
        elif to_state in _RETURNED_STATES:
            recipients = [created_by, *recipients_by_role(conn, ("faculty_officer",), unit_id=unit_id)]
        if not recipients:
            return

        label = STATE_LABELS.get(to_state, to_state)
        body = f"Lý do: {reason.strip()}" if reason and reason.strip() else ""
        notify(conn, recipients, kind="declaration_state",
               title=f"Hồ sơ «{_truncate(title)}» → {label}", body=body,
               link=f"/ke-khai/?id={declaration_id}", exclude_user_id=actor_id)
    except Exception:
        logger.exception("notify.on_declaration_state thất bại (hồ sơ #%s, %s -> %s)",
                         declaration_id, from_state, to_state)


def on_period_state(conn, period_id, to_state, actor_id, report_id=None):
    """Kỳ báo cáo mở/đóng nộp/huỷ/chốt → báo cho `faculty_officer` và
    `faculty_head` của MỌI đơn vị. `to_state='DaChot'` là trạng thái tự đặt
    của lời gọi (bản thân `period` không có trạng thái này — xem
    `cris.declare.finalize_period`); khi có `report_id` (bản báo cáo vừa tự
    sinh khi chốt), liên kết trỏ thẳng tới bản báo cáo đó thay vì trang kỳ."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name, due_at FROM period WHERE id=%s", (period_id,))
            row = cur.fetchone()
        if row is None:
            return
        name = row["name"]

        if to_state == "DangMo":
            due = _format_date(row["due_at"])
            title = f"Kỳ {name} đã mở, hạn {due}" if due else f"Kỳ {name} đã mở"
        elif to_state == "DaDongNop":
            title = f"Kỳ {name} đã đóng cổng nộp"
        elif to_state == "Huy":
            title = f"Kỳ {name} đã bị huỷ"
        elif to_state == "DaChot":
            title = f"Kỳ {name} đã chốt"
        else:
            title = f"Kỳ {name}: {STATE_LABELS.get(to_state, to_state)}"

        link = (f"/bao-cao/?id={report_id}" if to_state == "DaChot" and report_id is not None
                else f"/ky-bao-cao/chi-tiet/?id={period_id}")
        recipients = recipients_by_role(conn, ("faculty_officer", "faculty_head"))
        notify(conn, recipients, kind="period_state", title=title, link=link, exclude_user_id=actor_id)
    except Exception:
        logger.exception("notify.on_period_state thất bại (kỳ #%s -> %s)", period_id, to_state)


def on_link_confirmed(conn, link_id, actor_id):
    """Một liên kết tác giả được xác nhận (`confirm`/`reassign` ở hàng đợi) —
    báo cho `app_user` có `person_id` bằng người vừa được nối (nếu tài khoản
    nào có, giảng viên chưa có tài khoản thì không có ai nhận, im lặng)."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT al.person_id, w.title FROM author_link al "
                "JOIN author_mention m ON m.id = al.mention_id "
                "JOIN work w ON w.id = m.work_id WHERE al.id=%s", (link_id,))
            row = cur.fetchone()
        if row is None:
            return
        person_id, title = row["person_id"], row["title"]
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM app_user WHERE person_id=%s AND active", (person_id,))
            recipients = [r["id"] for r in cur.fetchall()]
        if not recipients:
            return
        notify(conn, recipients, kind="link_confirmed",
               title=f"Công trình «{_truncate(title)}» đã được nối vào hồ sơ của bạn",
               link=f"/giang-vien/?id={person_id}", exclude_user_id=actor_id)
    except Exception:
        logger.exception("notify.on_link_confirmed thất bại (liên kết #%s)", link_id)
