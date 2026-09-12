# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Hai hàng đợi người quyết: liên kết tác giả và nghi trùng.
SQL chuyển nguyên từ UI HTML cũ (đã gỡ, xem CHANGELOG); quyết định đi qua
`link.decide_link` / `dedup.decide_group` (BR-18), lô nhiều id trong một giao dịch.
Cả hai POST quyết định cần vai trò `rd_officer` (NFR-01/G2)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from cris import dedup, link, notify
from cris.api.deps import Conn, DeferredCommitConn, require_role
from cris.api.schemas import (
    AuthorQueueList,
    AuthorQueueRow,
    DecideAuthorsIn,
    DecideDupIn,
    DecideResult,
    DupGroupDetail,
    DupGroupList,
    DupGroupSummary,
    DupMember,
    Page,
)

router = APIRouter(prefix="/api/queue", tags=["hang-doi"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]

PER_PAGE = 50
AUTHOR_STATES = ("ChoXacNhan", "DaNoiTuDong", "DaXacNhan", "DaBacBo")
BASIS_LABELS = {"doi": "DOI", "title_norm": "Tiêu đề", "title_student_cohort": "Tiêu đề + khoá sinh viên"}
DUP_FIELD_LABELS = {"title": "Tiêu đề", "doi": "DOI", "year_issue": "Năm/kỳ", "journal": "Tạp chí",
                    "volume": "Tập/số", "pub_type_raw": "Loại xuất bản (thô)", "cohort": "Khoá"}


@router.get("/authors", response_model=AuthorQueueList)
def list_author_queue(conn: Conn, state: str = "ChoXacNhan", q: str = "", page: int = Query(1, ge=1)):
    if state not in AUTHOR_STATES:
        raise HTTPException(400, f"state phải là một trong {', '.join(AUTHOR_STATES)}")
    where = ["l.state = %(state)s"]; params = {"state": state}
    if q.strip():
        where.append("m.raw_name ILIKE %(q)s"); params["q"] = f"%{q.strip()}%"
    where_sql = " AND ".join(where)
    where_sql_g = where_sql.replace("l.", "l2.").replace("m.", "m2.")
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n FROM author_link l JOIN author_mention m ON m.id = l.mention_id WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(f"""
            SELECT l.id AS link_id, l.confidence, l.degree_conflict, l.person_id AS candidate_person_id,
                   m.raw_name, w.id AS work_id, w.title, p.display_name AS candidate_name,
                   g.group_work_count, ai.payload AS ai_payload
            FROM author_link l
            JOIN author_mention m ON m.id = l.mention_id
            JOIN work w ON w.id = m.work_id
            JOIN person p ON p.id = l.person_id
            JOIN (SELECT m2.raw_name, count(DISTINCT m2.work_id) AS group_work_count
                  FROM author_link l2 JOIN author_mention m2 ON m2.id = l2.mention_id
                  WHERE {where_sql_g} GROUP BY m2.raw_name) g ON g.raw_name = m.raw_name
            LEFT JOIN LATERAL (SELECT payload FROM ai_suggestion WHERE kind='author_link' AND target_id=l.id
                               ORDER BY built_at DESC LIMIT 1) ai ON true
            WHERE {where_sql}
            ORDER BY g.group_work_count DESC, m.raw_name, w.id, l.id
            LIMIT %(limit)s OFFSET %(offset)s""", {**params, "limit": PER_PAGE, "offset": (page - 1) * PER_PAGE})
        rows = cur.fetchall()
    items = []
    for r in rows:
        ai = r["ai_payload"] or {}
        items.append(AuthorQueueRow(link_id=r["link_id"], raw_name=r["raw_name"], work_id=r["work_id"], work_title=r["title"],
                                    candidate_person_id=r["candidate_person_id"], candidate_name=r["candidate_name"],
                                    confidence=r["confidence"], degree_conflict=bool(r["degree_conflict"]),
                                    group_work_count=r["group_work_count"], ai_rank=ai.get("rank"),
                                    ai_score=ai.get("score"), ai_reason=ai.get("reason")))
    return AuthorQueueList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total), state=state)


@router.post("/authors/decide", response_model=DecideResult)
def decide_authors(conn: Conn, actor: RdOfficer, body: DecideAuthorsIn):
    if body.decision == "reject" and not (body.reason or "").strip():
        raise HTTPException(400, "Bác bỏ bắt buộc phải nêu lý do.")
    if body.decision == "reassign" and body.person_id is None:
        raise HTTPException(400, "Chuyển cho người khác bắt buộc phải chọn người (person_id).")
    proxy = DeferredCommitConn(conn)
    done, failed = [], None
    try:
        for lid in body.link_ids:
            failed = lid
            link.decide_link(proxy, lid, body.decision, actor, reason=(body.reason or None), person_id=body.person_id)
            done.append(lid)
    except ValueError as exc:
        conn.rollback()
        raise HTTPException(400, f"Không xử lý được liên kết #{failed}: {exc}. Không thay đổi nào được ghi.")
    conn.commit()
    if body.decision in ("confirm", "reassign"):
        for lid in done:
            target_id = lid
            if body.decision == "reassign":
                # `decide_link` không trả về id của liên kết mới (bản ghi
                # `lid` cũ đã chuyển DaBacBo) — tra lại theo (mention_id của
                # liên kết cũ, person_id vừa gán) để báo đúng người được nối.
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT al2.id FROM author_link al1 JOIN author_link al2 "
                        "ON al2.mention_id = al1.mention_id "
                        "WHERE al1.id=%s AND al2.person_id=%s AND al2.state='DaXacNhan'",
                        (lid, body.person_id))
                    row = cur.fetchone()
                target_id = row["id"] if row else lid
            notify.on_link_confirmed(conn, target_id, actor)
    return DecideResult(ok=True, processed=done)


@router.get("/duplicates", response_model=DupGroupList)
def list_duplicate_groups(conn: Conn, state: str = "NghiTrung", page: int = Query(1, ge=1)):
    show_all = state == "all"
    with conn.cursor() as cur:
        if show_all:
            cur.execute("SELECT count(*) AS n FROM duplicate_group")
        else:
            cur.execute("SELECT count(*) AS n FROM duplicate_group WHERE state=%s", (state,))
        total = cur.fetchone()["n"]
        base = ("SELECT g.id, g.doc_type, g.basis, g.hint, g.state, g.created_at, "
                "(SELECT count(*) FROM duplicate_member m WHERE m.group_id = g.id) AS member_count "
                "FROM duplicate_group g {where} ORDER BY (g.basis <> 'doi'), g.created_at, g.id LIMIT %s OFFSET %s")
        off = (page - 1) * PER_PAGE
        if show_all:
            cur.execute(base.format(where=""), (PER_PAGE, off))
        else:
            cur.execute(base.format(where="WHERE g.state=%s"), (state, PER_PAGE, off))
        rows = cur.fetchall()
    items = [DupGroupSummary(id=g["id"], doc_type=g["doc_type"], basis=g["basis"],
                             basis_label=BASIS_LABELS.get(g["basis"], g["basis"]), hint=g["hint"], state=g["state"],
                             member_count=g["member_count"], created_at=g["created_at"]) for g in rows]
    return DupGroupList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total))


def _load_group(conn, gid):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM duplicate_group WHERE id=%s", (gid,))
        g = cur.fetchone()
        if g is None:
            raise HTTPException(404, f"không tìm thấy nhóm nghi trùng #{gid}")
        cur.execute("SELECT w.*, m.diff AS diff FROM duplicate_member m JOIN work w ON w.id = m.work_id "
                    "WHERE m.group_id=%s ORDER BY w.id", (gid,))
        members = cur.fetchall()
        cur.execute("SELECT payload FROM ai_suggestion WHERE kind='duplicate' AND target_id=%s ORDER BY built_at DESC LIMIT 1", (gid,))
        ai = cur.fetchone()
    return g, members, (ai["payload"] if ai else None)


@router.get("/duplicates/{gid}", response_model=DupGroupDetail)
def duplicate_group_detail(conn: Conn, gid: int):
    g, members, ai = _load_group(conn, gid)
    changed = set()
    for m in members:
        changed.update((m.get("diff") or {}).keys())
    diff_fields = [f for f in dedup.COMPARE if f in changed]
    return DupGroupDetail(
        id=g["id"], doc_type=g["doc_type"], basis=g["basis"], basis_label=BASIS_LABELS.get(g["basis"], g["basis"]),
        hint=g["hint"], state=g["state"], compare_fields=list(dedup.COMPARE), field_labels=DUP_FIELD_LABELS,
        diff_fields=diff_fields,
        members=[DupMember(id=m["id"], state=m["state"], title=m["title"],
                           fields={f: m.get(f) for f in dedup.COMPARE}, diff=m.get("diff")) for m in members],
        ai_similarity=ai, decided_by=g.get("decided_by"), decided_at=g.get("decided_at"),
        reason=g.get("reason"), survivor_work_id=g.get("survivor_work_id"))


@router.post("/duplicates/{gid}/decide", response_model=DecideResult)
def decide_duplicate_group(conn: Conn, actor: RdOfficer, gid: int, body: DecideDupIn):
    _load_group(conn, gid)
    if body.decision == "keep" and not (body.reason or "").strip():
        raise HTTPException(400, "Cần nhập lý do khi chọn Giữ riêng.")
    if body.decision == "merge" and body.survivor_id is None:
        raise HTTPException(400, "Cần chọn bản ghi sống sót (survivor_id).")
    try:
        if body.decision == "merge":
            dedup.decide_group(conn, gid, "merge", actor, survivor_id=body.survivor_id,
                               field_choices=body.field_choices, reason=body.reason)
        else:
            dedup.decide_group(conn, gid, body.decision, actor, reason=body.reason)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    return DecideResult(ok=True, processed=[gid])
