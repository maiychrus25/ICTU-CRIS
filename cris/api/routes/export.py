# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Xuất CSV (SC-05, UX-07): danh sách công trình đã lọc và công bố của một giảng viên.
UTF-8 có BOM để Excel mở đúng dấu tiếng Việt, tối đa 20.000 dòng, `csv` stdlib."""
import csv
import io
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from cris.api.deps import Conn
from cris.api.routes.search import SORT_ORDER_SQL, SORT_SELECT_EXTRA, _works_query

router = APIRouter(prefix="/api", tags=["xuat-du-lieu"])

MAX_ROWS = 20_000
CSV_HEADER = ["id", "doc_type", "title", "year", "doi", "journal", "authors", "state"]

_AUTHORS_SUBSELECT = (
    "(SELECT string_agg(am.raw_name, '; ' ORDER BY am.position) "
    "FROM author_mention am WHERE am.work_id = w.id AND am.position > 0) AS authors"
)


def _csv_response(rows, filename):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_HEADER)
    for r in rows:
        writer.writerow([r.get(c) if r.get(c) is not None else "" for c in CSV_HEADER])
    body = ("\ufeff" + buf.getvalue()).encode("utf-8")
    return StreamingResponse(
        iter([body]), media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/works.csv")
def export_works_csv(conn: Conn, q: str = "", doc_type: str = "", year: int | None = None,
                      unit: str = "", topic: int | None = None, venue_kind: str = "",
                      sort: Literal["recent", "title", "added"] = "recent"):
    from_sql, where_sql, params = _works_query(q, doc_type, year, unit, topic, venue_kind=venue_kind)
    order_sql = SORT_ORDER_SQL[sort]
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT DISTINCT w.id, w.year_issue, {SORT_SELECT_EXTRA} {from_sql} WHERE {where_sql} "
            f"ORDER BY {order_sql} LIMIT %s",
            params + [MAX_ROWS])
        ids = [r["id"] for r in cur.fetchall()]
        rows_by_id = {}
        if ids:
            cur.execute(
                f"SELECT w.id, w.doc_type, w.title, w.year_issue AS year, w.doi, w.journal, w.state, "
                f"{_AUTHORS_SUBSELECT} FROM v_work_current w WHERE w.id = ANY(%s)",
                (ids,))
            rows_by_id = {r["id"]: r for r in cur.fetchall()}
        rows = [rows_by_id[i] for i in ids if i in rows_by_id]
    filename = f"cong-trinh-{datetime.now(UTC).date():%Y%m%d}.csv"
    return _csv_response(rows, filename)


@router.get("/persons/{pid}/publications.csv")
def export_person_publications_csv(conn: Conn, pid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM person WHERE id = %s", (pid,))
        if cur.fetchone() is None:
            raise HTTPException(404, f"không tìm thấy giảng viên #{pid}")
        cur.execute(
            f"SELECT w.id, w.doc_type, w.title, w.year_issue AS year, w.doi, w.journal, w.state, "
            f"{_AUTHORS_SUBSELECT} FROM v_person_publications vp JOIN work w ON w.id = vp.work_id "
            f"WHERE vp.person_id = %s ORDER BY w.year_issue DESC NULLS LAST, w.id DESC LIMIT %s",
            (pid, MAX_ROWS))
        rows = cur.fetchall()
    filename = f"cong-trinh-gv-{pid}-{datetime.now(UTC).date():%Y%m%d}.csv"
    return _csv_response(rows, filename)
