# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Rà soát trùng đề tài theo khoá (E5): chỉ đọc lại `ai_suggestion(kind='topic_overlap')`

đã ghi bằng `python -m cris ai screen --cohort <mã>` (xem `cris/ai/screen.py`) — không
có route nào ở đây chạy AI hay ghi dữ liệu; giao diện chỉ hiển thị gợi ý đã có sẵn.

`max_score`/`level` đọc thẳng từ payload (đã tính sẵn lúc `screen_cohort` ghi, theo
`SCREEN_THRESHOLDS` hiệu chỉnh trên DB thật — xem `cris/ai/screen.py`), không quét lại
`neighbours` ở đây; payload cũ (ghi trước khi có hai trường này) coi như `max_score=0.0`,
`level="thap"` — chạy lại `ai screen` để có số mới."""
from fastapi import APIRouter, Query

from cris.ai.screen import LEVELS
from cris.api.deps import Conn
from cris.api.schemas import Page, ScreenCohortSummary, ScreenItem, ScreenList

router = APIRouter(prefix="/api/ai", tags=["ai-ra-soat"])

_LEVEL_ORDER = {lvl: i for i, lvl in enumerate(reversed(LEVELS))}  # thap=0, vua=1, cao=2
PER_PAGE = 50


def _level_of(payload):
    lvl = payload.get("level")
    return lvl if lvl in _LEVEL_ORDER else "thap"


def _rows(conn):
    """Mọi gợi ý `topic_overlap` còn công trình sống, kèm tiêu đề hiện tại."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT s.target_id AS work_id, w.title AS title, s.payload AS payload "
            "FROM ai_suggestion s JOIN work w ON w.id = s.target_id "
            "WHERE s.kind = 'topic_overlap' AND w.merged_into_id IS NULL "
            "ORDER BY s.target_id"
        )
        return cur.fetchall()


@router.get("/screen", response_model=ScreenList)
def screen(conn: Conn, cohort: str | None = None,
           min: str | None = Query(None, pattern="^(cao|vua|thap)$"),
           min_score: float | None = Query(None, ge=0.0, le=1.0),
           page: int = Query(1, ge=1)):
    rows = _rows(conn)
    cohorts_seen = set()
    items = []
    for r in rows:
        payload = r["payload"]
        row_cohort = payload.get("cohort")
        if row_cohort:
            cohorts_seen.add(row_cohort)
        if cohort and row_cohort != cohort:
            continue
        max_score = payload.get("max_score") or 0.0
        level = _level_of(payload)
        if min and _LEVEL_ORDER[level] < _LEVEL_ORDER[min]:
            continue
        if min_score is not None and max_score < min_score:
            continue
        items.append(ScreenItem(work_id=r["work_id"], title=r["title"], cohort=row_cohort,
                                 neighbours=payload.get("neighbours") or [],
                                 max_score=max_score, level=level))
    items.sort(key=lambda it: it.max_score, reverse=True)
    total = len(items)
    start = (page - 1) * PER_PAGE
    return ScreenList(items=items[start:start + PER_PAGE],
                       page=Page(page=page, per_page=PER_PAGE, total=total),
                       cohorts=sorted(cohorts_seen))


@router.get("/screen/cohorts", response_model=list[ScreenCohortSummary])
def screen_cohorts(conn: Conn):
    rows = _rows(conn)
    stats: dict[str, dict[str, int]] = {}
    for r in rows:
        payload = r["payload"]
        c = payload.get("cohort")
        if not c:
            continue
        d = stats.setdefault(c, {"screened": 0, "flagged": 0})
        d["screened"] += 1
        if _level_of(payload) == "cao":
            d["flagged"] += 1
    return [ScreenCohortSummary(cohort=c, **v) for c, v in sorted(stats.items())]
