# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Cảnh báo bất thường dữ liệu (K2, SC-10): đọc lại `quality_flag` đã tính bởi
`python -m cris quality scan` (`cris/anomaly.py`) — route này không tự quét lại.
`POST .../dismiss` cần vai trò `rd_officer`, lý do bắt buộc (400 nếu thiếu),
404 nếu không có cờ; ghi audit `quality.dismiss` qua `anomaly.dismiss`."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from cris import anomaly
from cris.api.deps import Conn, require_role
from cris.api.schemas import (
    AnomalyList,
    AnomalyRow,
    DismissAnomalyIn,
    DismissAnomalyOut,
    Page,
)

router = APIRouter(prefix="/api/quality", tags=["chat-luong"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]

PER_PAGE = 50


@router.get("/anomalies", response_model=AnomalyList)
def list_anomalies(conn: Conn, kind: str | None = None, state: str = "open",
                    severity: str | None = None, page: int = Query(1, ge=1)):
    where, params = [], []
    if kind:
        where.append("f.kind = %s"); params.append(kind)
    if state:
        where.append("f.state = %s"); params.append(state)
    if severity:
        where.append("f.severity = %s"); params.append(severity)
    where_sql = " AND ".join(where) if where else "TRUE"
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n FROM quality_flag f WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(
            f"SELECT f.id, f.kind, f.severity, f.state, f.work_id, f.person_id, f.detail, f.created_at, "
            f"w.title AS work_title, p.display_name AS person_name "
            f"FROM quality_flag f "
            f"LEFT JOIN work w ON w.id = f.work_id "
            f"LEFT JOIN person p ON p.id = f.person_id "
            f"WHERE {where_sql} "
            f"ORDER BY (f.severity = 'cao') DESC, (f.severity = 'vua') DESC, f.created_at DESC, f.id DESC "
            f"LIMIT %s OFFSET %s",
            params + [PER_PAGE, (page - 1) * PER_PAGE],
        )
        rows = cur.fetchall()
        cur.execute("SELECT kind, count(*) AS n FROM quality_flag WHERE state='open' GROUP BY kind")
        summary_rows = cur.fetchall()
    items = [
        AnomalyRow(id=r["id"], kind=r["kind"], kind_label=anomaly.kind_label(r["kind"]), severity=r["severity"],
                   state=r["state"], work_id=r["work_id"], title=r["work_title"], person_id=r["person_id"],
                   display_name=r["person_name"], detail=r["detail"], created_at=r["created_at"])
        for r in rows
    ]
    summary = {k: {"open": 0} for k in anomaly.KINDS}
    for r in summary_rows:
        summary[r["kind"]] = {"open": r["n"]}
    return AnomalyList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total), summary=summary)


@router.post("/anomalies/{flag_id}/dismiss", response_model=DismissAnomalyOut)
def dismiss_anomaly(conn: Conn, actor: RdOfficer, flag_id: int, body: DismissAnomalyIn):
    try:
        anomaly.dismiss(conn, flag_id, actor, body.reason)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return DismissAnomalyOut(ok=True, id=flag_id, state="dismissed")
