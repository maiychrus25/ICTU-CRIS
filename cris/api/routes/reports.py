# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Bản báo cáo kỳ đóng băng, có phiên bản (lát cắt L1): lớp mỏng gọi
`cris.report`. `payload` lưu trong DB không đổi sau khi sinh; vai trò cấp
khoa (không có `rd_officer`, có `unit_id`) chỉ xem/xuất được `items` của đơn
vị mình — lọc NGAY TẠI ĐÂY khi trả về (`_scoped_items`), không sửa payload gốc.
Tạo báo cáo (`POST .../reports`) cần vai trò `rd_officer`; đọc/xuất không cần
vai trò cụ thể (đã lọc theo đơn vị cho cấp khoa)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from cris import report as report_mod
from cris.api.deps import Conn, CurrentUser, require_role
from cris.api.schemas import (
    ReportCreateIn,
    ReportCreateOut,
    ReportDetail,
    ReportItem,
    ReportListRow,
    ReportSummary,
    ReportTotals,
    ReportUnitRef,
    ReportUnitSummary,
    ReportWork,
)

router = APIRouter(prefix="/api", tags=["bao-cao"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _fetch_period(conn, pid):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM period WHERE id=%s", (pid,))
        if cur.fetchone() is None:
            raise HTTPException(404, f"không tìm thấy kỳ báo cáo #{pid}")


def _fetch_report(conn, rid):
    row = report_mod.get_report(conn, rid)
    if row is None:
        raise HTTPException(404, f"không tìm thấy báo cáo #{rid}")
    return row


def _is_faculty_scoped(user):
    """Vai trò cấp khoa (có đơn vị, không có `rd_officer`) chỉ xem được hồ sơ
    của đơn vị mình trong một báo cáo — cùng quy tắc NFR-02 dùng ở
    `cris.declare.list_declarations`."""
    return user["unit_id"] is not None and "rd_officer" not in (user["roles"] or [])


def _scoped_items(items, user):
    if not _is_faculty_scoped(user):
        return items
    return [it for it in items if it["unit"]["id"] == user["unit_id"]]


def _totals_out(t):
    return ReportTotals(declared=t["declared"], accepted=t["accepted"], by_state=t["by_state"])


def _summary_out(s):
    return ReportSummary(
        units=[ReportUnitSummary(**u) for u in s["units"]],
        by_doc_type=s["by_doc_type"],
        totals=_totals_out(s["totals"]),
    )


def _item_out(it):
    w = it["work"]
    return ReportItem(
        declaration_id=it["declaration_id"], state=it["state"],
        unit=ReportUnitRef(**it["unit"]),
        work=ReportWork(id=w["id"], title=w["title"], doc_type=w["doc_type"], year=w["year_issue"],
                        doi=w["doi"], indexes=w["indexes"], quartile=w["quartile"], journal=w["journal"]),
        authors=it["authors"], evidence_count=it["evidence_count"], events=it["events"],
    )


@router.post("/periods/{pid}/reports", response_model=ReportCreateOut, status_code=201)
def create_report(conn: Conn, actor: RdOfficer, pid: int, body: ReportCreateIn):
    _fetch_period(conn, pid)
    try:
        rid = report_mod.build_report(conn, pid, actor, note=body.note)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    row = _fetch_report(conn, rid)
    return ReportCreateOut(id=row["id"], period_id=row["period_id"], version=row["version"],
                           generated_at=row["generated_at"], generated_by=row["generated_by"],
                           note=row["note"], summary=_summary_out(row["summary"]), sha256=row["sha256"])


@router.get("/periods/{pid}/reports", response_model=list[ReportListRow])
def list_reports(conn: Conn, pid: int):
    _fetch_period(conn, pid)
    rows = report_mod.list_reports(conn, pid)
    return [ReportListRow(id=r["id"], version=r["version"], generated_at=r["generated_at"],
                          generated_by_name=r["generated_by_name"], note=r["note"],
                          totals=_totals_out(r["totals"])) for r in rows]


@router.get("/reports/{rid}", response_model=ReportDetail)
def report_detail(conn: Conn, user: CurrentUser, rid: int):
    row = _fetch_report(conn, rid)
    items = _scoped_items(row["payload"]["items"], user)
    return ReportDetail(id=row["id"], period_id=row["period_id"], version=row["version"],
                        generated_at=row["generated_at"], generated_by=row["generated_by"], note=row["note"],
                        summary=_summary_out(row["summary"]), items=[_item_out(it) for it in items],
                        sha256=row["sha256"])


@router.get("/reports/{rid}/export")
def export_report(conn: Conn, user: CurrentUser, rid: int, format: str = Query("csv")):
    if format not in ("csv", "xlsx"):
        raise HTTPException(400, "định dạng không hợp lệ; chỉ nhận csv hoặc xlsx")
    row = _fetch_report(conn, rid)
    scoped = dict(row)
    scoped["payload"] = {"items": _scoped_items(row["payload"]["items"], user)}
    base = f"bao-cao-{row['period_code']}-v{row['version']}"
    if format == "csv":
        body = report_mod.report_csv(scoped).encode("utf-8")
        return StreamingResponse(
            iter([body]), media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{base}.csv"'})
    body = report_mod.report_xlsx(scoped)
    return StreamingResponse(
        iter([body]), media_type=XLSX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{base}.xlsx"'})
