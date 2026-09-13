# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Góc nhìn theo đơn vị (lát cắt L3 — Codex L "Góc nhìn khoa"): số liệu tổng hợp
từ `v_work_unit`/`v_person_publications` (như `cris/api/routes/stats.py`, ở đây
lọc theo một đơn vị) cùng `author_link`/`declaration` — không tính lại logic
nghiệp vụ. Vai trò cấp khoa (có đơn vị, không `rd_officer`/`school_leader`)
chỉ xem được đơn vị của chính mình (403 khác); `rd_officer`/`school_leader`
xem được mọi đơn vị.

Lát cắt M: `PATCH /api/units/{id}`/`POST /api/units/{id}/aliases` (trang quản
trị `/don-vi/`, chỉ `rd_officer`) dùng chung logic đổi tên/thêm bí danh với CLI
`units rename|alias` (`cris/units.py`) — không viết lại, chỉ gọi qua đây."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from cris import units as units_mod
from cris.api.deps import Conn, CurrentUser, require_role
from cris.api.schemas import (
    TopPerson,
    UnitAliasIn,
    UnitListItem,
    UnitOverviewOut,
    UnitRef,
    UnitRenameIn,
    UnitYearCount,
)

router = APIRouter(prefix="/api", tags=["khoa"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]

# Vai trò thấy được mọi đơn vị (không bị giới hạn theo `unit_id` của tài khoản).
UNSCOPED_ROLES = ("rd_officer", "school_leader")

_UNIT_ROW_SQL = """
    SELECT u.id, u.code, u.name, u.active, u.aliases,
           count(DISTINCT vu.work_id) AS works,
           count(DISTINCT p.id) FILTER (WHERE p.kind='lecturer') AS persons
    FROM unit u
    LEFT JOIN v_work_unit vu ON vu.unit_id = u.id
    LEFT JOIN person p ON p.unit_id = u.id
    {where}
    GROUP BY u.id, u.code, u.name, u.active, u.aliases
"""


@router.get("/units", response_model=list[UnitListItem])
def list_units(conn: Conn):
    """Đơn vị thật (khoa/trung tâm) đang hoạt động — bộ lọc Đơn vị ở tra cứu và
    trang quản trị `/don-vi/` đọc từ đây. `works` qua `v_work_unit` (nguồn +
    tác giả đã liên kết), `persons` đếm giảng viên đang gán đơn vị này."""
    with conn.cursor() as cur:
        cur.execute(_UNIT_ROW_SQL.format(where="WHERE u.active") + " ORDER BY works DESC, u.code")
        rows = cur.fetchall()
    return [UnitListItem(**r) for r in rows]


def _unit_row(conn, unit_id):
    """Một đơn vị theo đúng hình dạng `UnitListItem` (bất kể `active`) — dùng để
    trả về sau `PATCH`/`POST` bên dưới; `None` nếu không có id này."""
    with conn.cursor() as cur:
        cur.execute(_UNIT_ROW_SQL.format(where="WHERE u.id = %s"), (unit_id,))
        return cur.fetchone()


@router.patch("/units/{unit_id}", response_model=UnitListItem)
def rename_unit(conn: Conn, actor: RdOfficer, unit_id: int, body: UnitRenameIn):
    """Đổi tên hiển thị của một đơn vị (mã giữ nguyên) — chỉ `rd_officer`.
    400 nếu tên rỗng sau khi cắt khoảng trắng; 404 nếu không có đơn vị; ghi
    `audit_log` qua `cris.units.rename_unit` (như CLI `units rename`)."""
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(400, "Tên đơn vị không được để trống.")
    row = _fetch_unit(conn, unit_id)
    units_mod.rename_unit(conn, row["code"], name, actor_id=actor, reason=body.reason)
    return UnitListItem(**_unit_row(conn, unit_id))


@router.post("/units/{unit_id}/aliases", response_model=UnitListItem)
def add_unit_alias(conn: Conn, actor: RdOfficer, unit_id: int, body: UnitAliasIn):
    """Thêm một bí danh cho đơn vị (không xoá bí danh cũ, không trùng lặp) —
    chỉ `rd_officer`. 400 nếu bí danh rỗng; 404 nếu không có đơn vị; ghi
    `audit_log` qua `cris.units.add_alias` (như CLI `units alias`)."""
    alias = (body.alias or "").strip()
    if not alias:
        raise HTTPException(400, "Bí danh không được để trống.")
    row = _fetch_unit(conn, unit_id)
    units_mod.add_alias(conn, row["code"], alias, actor_id=actor, reason=body.reason)
    return UnitListItem(**_unit_row(conn, unit_id))


def _is_unit_scoped(user: dict) -> bool:
    """Vai trò cấp khoa (có đơn vị, không có `rd_officer`/`school_leader`) chỉ
    xem được đơn vị của chính mình — cùng quy tắc NFR-02 dùng ở
    `cris.declare`/`cris/api/routes/reports.py`."""
    return user["unit_id"] is not None and not any(r in (user["roles"] or []) for r in UNSCOPED_ROLES)


def _fetch_unit(conn, unit_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id, code, name FROM unit WHERE id=%s", (unit_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, f"không tìm thấy đơn vị #{unit_id}")
    return row


def _latest_open_period_id(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM period WHERE state='DangMo' ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
    return row["id"] if row else None


@router.get("/units/{unit_id}/overview", response_model=UnitOverviewOut)
def unit_overview(conn: Conn, user: CurrentUser, unit_id: int, period_id: int | None = Query(None)):
    unit = _fetch_unit(conn, unit_id)
    if _is_unit_scoped(user) and user["unit_id"] != unit_id:
        raise HTTPException(403, "chỉ xem được đơn vị của mình")

    with conn.cursor() as cur:
        cur.execute("SELECT count(DISTINCT vu.work_id) AS n FROM v_work_unit vu WHERE vu.unit_id=%s", (unit_id,))
        works_total = cur.fetchone()["n"]

        cur.execute(
            "SELECT w.doc_type, count(DISTINCT w.id) AS n "
            "FROM v_work_unit vu JOIN work w ON w.id = vu.work_id "
            "WHERE vu.unit_id=%s GROUP BY w.doc_type", (unit_id,))
        by_doc_type = {r["doc_type"]: r["n"] for r in cur.fetchall()}

        cur.execute(
            "SELECT w.year_issue AS year, count(DISTINCT w.id) AS n "
            "FROM v_work_unit vu JOIN work w ON w.id = vu.work_id "
            "WHERE vu.unit_id=%s AND w.year_issue IS NOT NULL "
            "GROUP BY w.year_issue ORDER BY w.year_issue DESC LIMIT 5", (unit_id,))
        by_year = [UnitYearCount(**r) for r in cur.fetchall()]

        cur.execute(
            "SELECT p.id AS person_id, p.display_name, u.code AS unit_code, count(DISTINCT vp.work_id) AS works "
            "FROM v_person_publications vp JOIN person p ON p.id = vp.person_id "
            "LEFT JOIN unit u ON u.id = p.unit_id "
            "WHERE p.unit_id=%s AND vp.state IN ('DaNoiTuDong','DaXacNhan') "
            "GROUP BY p.id, p.display_name, u.code ORDER BY works DESC, p.display_name LIMIT 10", (unit_id,))
        top_persons = [TopPerson(**r) for r in cur.fetchall()]

        # Lượt chờ xác nhận (author_link.state='ChoXacNhan') của mention thuộc
        # một công trình đã xác định là của đơn vị này (qua v_work_unit).
        cur.execute(
            "SELECT count(DISTINCT l.id) AS n FROM author_link l "
            "JOIN author_mention m ON m.id = l.mention_id "
            "WHERE l.state='ChoXacNhan' AND m.work_id IN "
            "(SELECT work_id FROM v_work_unit WHERE unit_id=%s)", (unit_id,))
        pending_links = cur.fetchone()["n"]

        pid = period_id if period_id is not None else _latest_open_period_id(conn)
        declarations_by_state: dict[str, int] = {}
        if pid is not None:
            cur.execute(
                "SELECT state, count(*) AS n FROM declaration WHERE unit_id=%s AND period_id=%s GROUP BY state",
                (unit_id, pid))
            declarations_by_state = {r["state"]: r["n"] for r in cur.fetchall()}

        # Giảng viên của đơn vị chưa có công trình nào được liên kết còn sống.
        cur.execute(
            "SELECT count(*) AS n FROM person p WHERE p.unit_id=%s AND p.kind='lecturer' "
            "AND NOT EXISTS (SELECT 1 FROM v_person_publications vp "
            "WHERE vp.person_id=p.id AND vp.state IN ('DaNoiTuDong','DaXacNhan'))", (unit_id,))
        lecturers_without_works = cur.fetchone()["n"]

    return UnitOverviewOut(
        unit=UnitRef(id=unit["id"], code=unit["code"], name=unit["name"]),
        works_total=works_total,
        by_doc_type=by_doc_type,
        by_year=by_year,
        top_persons=top_persons,
        pending_links=pending_links,
        declarations_by_state=declarations_by_state,
        lecturers_without_works=lecturers_without_works,
    )
