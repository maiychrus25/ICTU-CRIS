# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Gợi ý người hướng dẫn thật cho đồ án đang ghi `ICTU_TEACHER` (lát cắt I3):

chỉ đọc lại `ai_suggestion(kind='mentor')` đã ghi bằng `python -m cris ai
mentors` (`cris/ai/mentor.py`) — không route nào ở đây chạy AI hay tự ghi
gợi ý.

`POST /mentors/{work_id}/accept` đưa một ứng viên vào **hàng đợi tác giả**
(`author_link` trạng thái `ChoXacNhan`, qua `cris.link.add_candidate`) —
quyết định cuối vẫn ở hàng đợi tác giả (`GET /api/queue/authors`,
`cris.link.decide_link`), đúng nguyên tắc gợi ý-không-quyết (BR-18): route
này **không bao giờ** tự xác nhận liên kết hay đổi trường dữ liệu nghiệp vụ
nào khác ngoài `author_link` + `audit_log`.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from cris import link
from cris.api.deps import Conn, require_role
from cris.api.schemas import (
    AcceptMentorIn,
    AcceptMentorResult,
    MentorCandidate,
    MentorItem,
    MentorList,
    MentorPendingLink,
    Page,
)
from cris.audit import log as audit_log

router = APIRouter(prefix="/api/ai", tags=["ai-mentor"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]
PER_PAGE = 50

# Liên kết ở các trạng thái này đã "vào hàng đợi rồi" — dùng để dựng
# pending_link (đã được ai đó đưa vào hàng đợi/xác nhận, kể cả trước khi có
# gợi ý AI) và để cris.link.add_candidate từ chối xếp chồng ứng viên khác.
_QUEUED_STATES = ("ChoXacNhan", "DaNoiTuDong", "DaXacNhan")


def _rows(conn, unit):
    """Mọi gợi ý `mentor` còn đồ án sống, kèm liên kết đang chờ/đã có (nếu
    có) cho lượt tên giữ chỗ — để giao diện biết đã đưa vào hàng đợi chưa."""
    unit_join = ""
    where = ["s.kind = 'mentor'", "w.merged_into_id IS NULL"]
    params = [list(_QUEUED_STATES)]
    if unit:
        # Cùng cách lọc unit= của /api/works (cris/api/routes/search.py):
        # v_work_unit suy ra đơn vị của đồ án từ tác giả/sinh viên đã liên kết.
        unit_join = "LEFT JOIN v_work_unit vu ON vu.work_id = s.target_id LEFT JOIN unit u ON u.id = vu.unit_id"
        if unit.isdigit():
            where.append("vu.unit_id = %s"); params.append(int(unit))
        else:
            where.append("u.code = %s"); params.append(unit)
    where_sql = " AND ".join(where)
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT s.target_id AS work_id, w.title AS title, w.cohort AS cohort, s.payload AS payload,
                       al.id AS link_id, al.person_id AS link_person_id, al.state AS link_state
                FROM ai_suggestion s
                JOIN work w ON w.id = s.target_id
                {unit_join}
                LEFT JOIN LATERAL (
                    SELECT id, person_id, state FROM author_link
                    WHERE mention_id = (s.payload->>'mention_id')::bigint
                      AND state = ANY(%s)
                    ORDER BY id DESC LIMIT 1
                ) al ON true
                WHERE {where_sql}
                ORDER BY s.target_id""",
            params,
        )
        return cur.fetchall()


@router.get("/mentors", response_model=MentorList)
def list_mentors(conn: Conn, unit: str = "", min_votes: int | None = Query(None, ge=1), page: int = Query(1, ge=1)):
    rows = _rows(conn, unit.strip())
    items = []
    for r in rows:
        payload = r["payload"]
        candidates = payload.get("candidates") or []
        if min_votes is not None and not any((c.get("votes") or 0) >= min_votes for c in candidates):
            continue
        pending = None
        if r["link_id"] is not None:
            pending = MentorPendingLink(link_id=r["link_id"], person_id=r["link_person_id"], state=r["link_state"])
        items.append(MentorItem(
            work_id=r["work_id"], title=r["title"], cohort=r["cohort"], mention_id=payload.get("mention_id"),
            candidates=[MentorCandidate(**c) for c in candidates], pending_link=pending,
        ))
    total = len(items)
    start = (page - 1) * PER_PAGE
    return MentorList(items=items[start:start + PER_PAGE], page=Page(page=page, per_page=PER_PAGE, total=total))


@router.post("/mentors/{work_id}/accept", response_model=AcceptMentorResult)
def accept_mentor(conn: Conn, actor: RdOfficer, work_id: int, body: AcceptMentorIn):
    """Đưa một ứng viên trong gợi ý của `work_id` vào hàng đợi tác giả.

    404 nếu đồ án chưa có gợi ý `mentor`, hoặc ứng viên không nằm trong danh
    sách gợi ý (không cho gán tuỳ ý ngoài gợi ý AI — đúng route này, gán tay
    thì dùng `/api/queue/authors/decide` với `reassign`). 409 nếu lượt tên
    giữ chỗ đã có liên kết đang chờ hoặc đã xác nhận (đã đưa vào hàng đợi
    rồi, bởi lần chạy trước hoặc do luồng khác)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT payload FROM ai_suggestion WHERE kind='mentor' AND target_id=%s "
            "ORDER BY built_at DESC LIMIT 1", (work_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, f"không có gợi ý người hướng dẫn cho đồ án #{work_id}")
    payload = row["payload"]
    mention_id = payload.get("mention_id")
    candidate = next((c for c in (payload.get("candidates") or []) if c.get("person_id") == body.person_id), None)
    if candidate is None:
        raise HTTPException(404, f"ứng viên #{body.person_id} không nằm trong gợi ý của đồ án #{work_id}")
    basis = {"ai": True, "votes": candidate.get("votes"), "score": candidate.get("score")}
    try:
        link_id = link.add_candidate(conn, mention_id, body.person_id, "ai_mentor", basis)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    audit_log(conn, actor, "link.ai_candidate", "author_link", link_id,
              before=None, after={"work_id": work_id, "mention_id": mention_id, "person_id": body.person_id, "basis": basis})
    conn.commit()
    return AcceptMentorResult(ok=True, link_id=link_id, person_id=body.person_id, state="ChoXacNhan")
