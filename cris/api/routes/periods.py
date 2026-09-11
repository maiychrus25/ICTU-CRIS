# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kỳ báo cáo (lát cắt K, phần đọc + mở/đóng; chốt kỳ ở lát cắt H1): lớp mỏng
gọi `cris.period`/`cris.declare`. `ValueError` từ tầng nghiệp vụ (mã kỳ trùng,
sai trạng thái, không tìm thấy kỳ, kỳ chưa đóng nộp khi chốt...) → 409. Mọi
POST cần vai trò `rd_officer` (NFR-01/G2)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from cris import declare
from cris import period as period_mod
from cris.api.deps import Conn, require_role
from cris.api.schemas import (
    PeriodFinalizeOut,
    PeriodOpenIn,
    PeriodOut,
    PeriodProgress,
    PeriodUnitProgress,
)

router = APIRouter(prefix="/api/periods", tags=["ky-bao-cao"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]


def _out(p):
    return PeriodOut(id=p["id"], code=p["code"], name=p["name"], scope=p["scope"], criteria=p["criteria"],
                     state=p["state"], opens_at=p["opens_at"], due_at=p["due_at"], created_at=p["created_at"])


def _fetch(conn, pid):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM period WHERE id = %s", (pid,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, f"không tìm thấy kỳ báo cáo #{pid}")
    return row


@router.get("", response_model=list[PeriodOut])
def list_periods(conn: Conn):
    return [_out(r) for r in period_mod.list_periods(conn)]


@router.get("/{pid}/progress", response_model=PeriodProgress)
def period_progress(conn: Conn, pid: int):
    try:
        p = period_mod.period_progress(conn, pid)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return PeriodProgress(period_id=p["period_id"], state=p["state"], due_at=p["due_at"],
                          days_remaining=p["days_remaining"],
                          units=[PeriodUnitProgress(**u) for u in p["units"]])


@router.post("", response_model=PeriodOut, status_code=201)
def open_period(conn: Conn, actor: RdOfficer, body: PeriodOpenIn):
    try:
        pid = period_mod.open_period(conn, code=body.code, name=body.name, scope=body.scope,
                                     criteria=body.criteria, due_at=body.due_at, actor_id=actor)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return _out(_fetch(conn, pid))


@router.post("/{pid}/close", response_model=PeriodOut)
def close_submissions(conn: Conn, actor: RdOfficer, pid: int):
    try:
        period_mod.close_submissions(conn, pid, actor)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return _out(_fetch(conn, pid))


@router.post("/{pid}/cancel", response_model=PeriodOut)
def cancel_period(conn: Conn, actor: RdOfficer, pid: int):
    try:
        period_mod.cancel_period(conn, pid, actor)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return _out(_fetch(conn, pid))


@router.post("/{pid}/finalize", response_model=PeriodFinalizeOut)
def finalize_period(conn: Conn, actor: RdOfficer, pid: int):
    _fetch(conn, pid)
    try:
        result = declare.finalize_period(conn, pid, actor)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return PeriodFinalizeOut(finalized=result["finalized"], skipped=result["skipped"])
