# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Bản đồ tri thức, xu hướng chủ đề, đồ thị đồng tác giả (J2): `GET /api/ai/map`,
`GET /api/ai/trends`, `GET /api/ai/coauthors`.

`map` đọc bảng cache `ai_map` (tính sẵn bởi `python -m cris ai map`,
`cris/ai/map.py`) — không có route nào ở đây chạy AI; 404 khi chưa từng chạy
lệnh trên. `trends`/`coauthors` tính trực tiếp mỗi lần gọi (`cris/ai/trends.py`,
`cris/ai/coauthors.py`), không cache."""
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from cris.ai.coauthors import coauthor_graph
from cris.ai.trends import topic_trends
from cris.api.deps import Conn
from cris.api.schemas import (
    CoauthorsOut,
    MapOut,
    MapPoint,
    MapTopic,
    MapUnit,
    TrendsOut,
)

router = APIRouter(prefix="/api/ai", tags=["ai-ban-do"])

MAP_NOT_BUILT = "Chưa dựng bản đồ — chạy python -m cris ai map"


@router.get("/map", response_model=MapOut)
def map_(conn: Conn, color: Literal["topic", "unit", "year", "doc_type"] | None = None):
    """`color` chỉ dành cho giao diện tô màu điểm theo tiêu chí — chọn tiêu chí
    nào cũng trả về đủ mọi trường (`topic_id`, `unit_id`, `year`, `doc_type`),
    không lọc gì ở phía máy chủ."""
    with conn.cursor() as cur:
        cur.execute("SELECT built_at, method, points, topics FROM ai_map ORDER BY built_at DESC LIMIT 1")
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, MAP_NOT_BUILT)
    unit_ids = sorted({p["unit_id"] for p in row["points"] if p.get("unit_id") is not None})
    units = []
    if unit_ids:
        with conn.cursor() as cur:
            cur.execute("SELECT id, code, name FROM unit WHERE id = ANY(%s) AND active ORDER BY code", (unit_ids,))
            units = [MapUnit(**u) for u in cur.fetchall()]
    return MapOut(
        points=[MapPoint(**p) for p in row["points"]],
        topics=[MapTopic(**t) for t in row["topics"]],
        units=units,
        built_at=row["built_at"],
        method=row["method"],
    )


@router.get("/trends", response_model=TrendsOut)
def trends(conn: Conn, by: Literal["cohort", "year"] = "cohort"):
    return TrendsOut(**topic_trends(conn, by=by))


@router.get("/coauthors", response_model=CoauthorsOut)
def coauthors(conn: Conn, min_works: int = Query(2, ge=1)):
    return CoauthorsOut(**coauthor_graph(conn, min_works=min_works))
