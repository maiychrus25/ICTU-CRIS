# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Lịch sử đồng bộ (lát cắt G, G1) — chỉ đọc `sync_run`/`source_record`; đồng bộ
tự nó vẫn chạy qua CLI (`python -m cris sync ...`, xem `cris/sync.py`)."""
from fastapi import APIRouter, HTTPException, Query

from cris.api.deps import Conn
from cris.api.schemas import (
    Page,
    SourceRecordRow,
    SyncRunDetail,
    SyncRunList,
    SyncRunSummary,
)

router = APIRouter(prefix="/api", tags=["dong-bo"])

PER_PAGE = 20


def _duration_s(row):
    if row["started_at"] is None or row["finished_at"] is None:
        return None
    return (row["finished_at"] - row["started_at"]).total_seconds()


def _summary(row):
    return SyncRunSummary(
        id=row["id"], source=row["source"], scope=row["scope"], status=row["status"],
        started_at=row["started_at"], finished_at=row["finished_at"], duration_s=_duration_s(row),
        added=row["added"], changed=row["changed"], vanished=row["vanished"],
        errors=row["errors"] or [], warnings=row["warnings"] or [],
    )


@router.get("/sync/runs", response_model=SyncRunList)
def list_runs(conn: Conn, page: int = Query(1, ge=1)):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM sync_run")
        total = cur.fetchone()["n"]
        cur.execute("SELECT * FROM sync_run ORDER BY id DESC LIMIT %s OFFSET %s",
                    (PER_PAGE, (page - 1) * PER_PAGE))
        rows = cur.fetchall()
    return SyncRunList(items=[_summary(r) for r in rows], page=Page(page=page, per_page=PER_PAGE, total=total))


@router.get("/sync/runs/{rid}", response_model=SyncRunDetail)
def run_detail(conn: Conn, rid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM sync_run WHERE id = %s", (rid,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(404, f"không tìm thấy lượt đồng bộ #{rid}")
        cur.execute("""SELECT id, source_key, doc_type, version, first_seen_at AS fetched_at
                       FROM source_record WHERE sync_run_id = %s ORDER BY id DESC LIMIT 20""", (rid,))
        records = cur.fetchall()
    base = _summary(row)
    return SyncRunDetail(**base.model_dump(), expected_count=row["expected_count"],
                         fetched_count=row["fetched_count"], triggered_by=row["triggered_by"],
                         records=[SourceRecordRow(**r) for r in records])
