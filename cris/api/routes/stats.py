# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tổng quan cho lãnh đạo (`/tong-quan/`): số liệu tổng hợp từ các view sẵn có
(`v_work_current`, `v_work_unit`, `v_person_publications`, `v_data_quality`), không tính
lại logic nghiệp vụ."""
from fastapi import APIRouter, Query

from cris.api.deps import Conn
from cris.api.schemas import (
    LastSync,
    StatsCoverage,
    StatsOut,
    StatsQueues,
    TopPerson,
    UnitWorks,
    UnknownYearRow,
    YearTypeRow,
)

router = APIRouter(prefix="/api", tags=["thong-ke"])

DOC_TYPES = ("bai_bao", "do_an", "luan_van", "luan_an", "hoc_lieu")
# An toàn nối chuỗi trực tiếp: DOC_TYPES là hằng số nội bộ, không phải đầu vào người dùng.
_COUNT_COLS = ", ".join(f"count(*) FILTER (WHERE w.doc_type='{t}') AS {t}" for t in DOC_TYPES)


@router.get("/stats", response_model=StatsOut)
def stats(conn: Conn, years: int = Query(5, ge=1, le=50)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT year_issue FROM v_work_current WHERE year_issue IS NOT NULL "
            "ORDER BY year_issue DESC LIMIT %s", (years,))
        year_list = [r["year_issue"] for r in cur.fetchall()]

        by_year_type = []
        if year_list:
            cur.execute(
                f"SELECT w.year_issue AS year, {_COUNT_COLS} FROM v_work_current w "
                f"WHERE w.year_issue = ANY(%s) GROUP BY w.year_issue ORDER BY w.year_issue DESC",
                (year_list,))
            by_year_type = [YearTypeRow(**r) for r in cur.fetchall()]

        cur.execute(f"SELECT {_COUNT_COLS} FROM v_work_current w WHERE w.year_issue IS NULL")
        u = cur.fetchone()
        unknown_year = UnknownYearRow(**u) if u else UnknownYearRow()

        cur.execute(
            "SELECT u.id AS unit_id, u.code, u.name, count(DISTINCT vu.work_id) AS works "
            "FROM unit u JOIN v_work_unit vu ON vu.unit_id = u.id "
            "GROUP BY u.id, u.code, u.name ORDER BY works DESC, u.name")
        by_unit = [UnitWorks(**r) for r in cur.fetchall()]

        cur.execute(
            "SELECT p.id AS person_id, p.display_name, u.code AS unit_code, count(DISTINCT vp.work_id) AS works "
            "FROM v_person_publications vp JOIN person p ON p.id = vp.person_id "
            "LEFT JOIN unit u ON u.id = p.unit_id "
            "WHERE vp.state IN ('DaNoiTuDong','DaXacNhan') "
            "GROUP BY p.id, p.display_name, u.code ORDER BY works DESC, p.display_name LIMIT 10")
        top_persons = [TopPerson(**r) for r in cur.fetchall()]

        cur.execute("SELECT works, works_with_link, works_without_unit, links_queued, dup_groups_open FROM v_data_quality")
        dq = cur.fetchone()

        cur.execute("SELECT id, source, scope, status, started_at, finished_at FROM sync_run ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()

    pct = round(dq["works_with_link"] / dq["works"] * 100, 1) if dq["works"] else 0.0
    return StatsOut(
        by_year_type=by_year_type,
        unknown_year=unknown_year,
        by_unit=by_unit,
        top_persons=top_persons,
        queues=StatsQueues(authors_pending=dq["links_queued"], dup_groups_open=dq["dup_groups_open"]),
        coverage=StatsCoverage(works_with_link_pct=pct, works_without_unit=dq["works_without_unit"]),
        last_sync=LastSync(**last) if last else None,
    )
