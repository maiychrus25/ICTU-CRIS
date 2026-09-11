# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""`GET /api/recent` (K1): công trình thêm mới/cập nhật ở lượt đồng bộ gần
nhất đã xong (`status` 'ok'/'warning' — 'running'/'failed' chưa/không tính).

`work.primary_source_record_id` luôn được `cris.normalize` cập nhật về đúng
`source_record` mới nhất mỗi lần chuẩn hoá lại, nên join qua đó cho ra đúng
tập bản ghi nguồn "hiện hành" đã sinh/đổi trong lượt đó: `version=1` là công
trình mới thêm, `version>1` là công trình đã đổi nội dung."""
from fastapi import APIRouter

from cris.api.deps import Conn
from cris.api.routes.search import _split_keywords
from cris.api.schemas import (
    DOC_TYPE_LABELS,
    LastSync,
    RecentAddedRow,
    RecentChangedRow,
    RecentOut,
)

router = APIRouter(prefix="/api", tags=["gan-day"])


def _row(r):
    return dict(id=r["id"], title=r["title"], doc_type=r["doc_type"],
               doc_type_label=DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]),
               year=r["year_issue"], doi=r["doi"], state=r["state"],
               needs_review=bool(r["needs_review"]), keywords=_split_keywords(r["keywords_raw"], limit=6))


@router.get("/recent", response_model=RecentOut)
def recent(conn: Conn, limit: int = 20):
    with conn.cursor() as cur:
        cur.execute("SELECT id, source, scope, status, started_at, finished_at FROM sync_run "
                    "WHERE status IN ('ok','warning') ORDER BY id DESC LIMIT 1")
        run = cur.fetchone()
        if run is None:
            return RecentOut(added=[], changed=[], run=None)
        cur.execute(
            "SELECT w.id, w.title, w.doc_type, w.year_issue, w.doi, w.state, w.needs_review, w.keywords_raw, "
            "sr.version, sr.first_seen_at "
            "FROM work w JOIN source_record sr ON sr.id = w.primary_source_record_id "
            "WHERE sr.sync_run_id = %s AND w.merged_into_id IS NULL "
            "ORDER BY sr.first_seen_at DESC, w.id DESC LIMIT %s",
            (run["id"], limit))
        rows = cur.fetchall()
    added, changed = [], []
    for r in rows:
        base = _row(r)
        if r["version"] == 1:
            added.append(RecentAddedRow(**base, first_seen_at=r["first_seen_at"]))
        else:
            changed.append(RecentChangedRow(**base, version=r["version"]))
    return RecentOut(added=added, changed=changed, run=LastSync(**run))
