# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Giảng viên tự kê khai (lát cắt H3): công trình của tôi (`GET /api/me/works`,
theo `v_person_publications` của `app_user.person_id`), hồ sơ kê khai do tôi
tạo (`GET /api/me/declarations`) và tự kê khai một công trình của mình
(`POST /api/me/declarations`, vai trò `lecturer`, đơn vị tự suy từ
`app_user.unit_id`/`person.unit_id`). `cris.declare` kiểm sở hữu công trình/hồ
sơ (`_assert_own_work`/`_assert_owner`) — `PermissionError` → 403. Tài khoản
chưa gắn `person_id` → 409 khi xem công trình của mình."""
from fastapi import APIRouter, HTTPException, Query

from cris import declare
from cris.api.deps import Conn, CurrentUser
from cris.api.schemas import (
    DOC_TYPE_LABELS,
    DeclarationList,
    DeclarationRow,
    MyDeclarationCreateIn,
    MyWorkList,
    MyWorkRow,
    Page,
)

router = APIRouter(prefix="/api/me", tags=["ke-khai-cua-toi"])
PER_PAGE = 50


def _fetch_period(conn, pid):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM period WHERE id=%s", (pid,))
        if cur.fetchone() is None:
            raise HTTPException(404, f"không tìm thấy kỳ báo cáo #{pid}")


def _row_out(r):
    return DeclarationRow(id=r["id"], period_id=r["period_id"], work_id=r["work_id"], work_title=r["work_title"],
                          doc_type=r["doc_type"], doc_type_label=DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]),
                          unit_id=r["unit_id"], unit_code=r["unit_code"], state=r["state"], note=r["note"],
                          evidence_count=r["evidence_count"], last_event_at=r["last_event_at"],
                          created_at=r["created_at"], updated_at=r["updated_at"])


def _row_from_detail(data):
    d = data["declaration"]
    events = data["events"]
    last_event_at = events[-1]["at"] if events else None
    return DeclarationRow(id=d["id"], period_id=d["period_id"], work_id=d["work_id"], work_title=d["work_title"],
                          doc_type=d["doc_type"], doc_type_label=DOC_TYPE_LABELS.get(d["doc_type"], d["doc_type"]),
                          unit_id=d["unit_id"], unit_code=d["unit_code"], state=d["state"], note=d["note"],
                          evidence_count=len(data["evidence"]), last_event_at=last_event_at,
                          created_at=d["created_at"], updated_at=d["updated_at"])


def _resolve_own_unit_id(conn, user):
    """Đơn vị để giảng viên tự kê khai: `app_user.unit_id`, nếu `NULL` thì lấy
    `person.unit_id` của hồ sơ giảng viên gắn với tài khoản."""
    if user["unit_id"] is not None:
        return user["unit_id"]
    if user["person_id"] is None:
        return None
    with conn.cursor() as cur:
        cur.execute("SELECT unit_id FROM person WHERE id=%s", (user["person_id"],))
        row = cur.fetchone()
    return row["unit_id"] if row else None


@router.get("/works", response_model=MyWorkList)
def my_works(conn: Conn, user: CurrentUser, page: int = Query(1, ge=1)):
    person_id = user["person_id"]
    if person_id is None:
        raise HTTPException(409, "Tài khoản chưa gắn với hồ sơ giảng viên")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM v_person_publications WHERE person_id=%s", (person_id,))
        total = cur.fetchone()["n"]
        cur.execute(
            "SELECT vp.work_id, vp.state AS link_state, w.title, w.doc_type, w.year_issue, w.doi "
            "FROM v_person_publications vp JOIN work w ON w.id = vp.work_id "
            "WHERE vp.person_id = %s ORDER BY w.year_issue DESC NULLS LAST, w.id DESC LIMIT %s OFFSET %s",
            (person_id, PER_PAGE, (page - 1) * PER_PAGE))
        rows = cur.fetchall()
        work_ids = [r["work_id"] for r in rows]
        declared_by_work: dict[int, list[int]] = {}
        if work_ids:
            cur.execute("SELECT work_id, period_id FROM declaration WHERE work_id = ANY(%s) ORDER BY period_id",
                        (work_ids,))
            for d in cur.fetchall():
                declared_by_work.setdefault(d["work_id"], []).append(d["period_id"])
    items = [MyWorkRow(work_id=r["work_id"], title=r["title"], doc_type=r["doc_type"],
                       doc_type_label=DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]),
                       year=r["year_issue"], doi=r["doi"], link_state=r["link_state"],
                       declared_in=declared_by_work.get(r["work_id"], []))
             for r in rows]
    return MyWorkList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total))


@router.get("/declarations", response_model=DeclarationList)
def my_declarations(conn: Conn, user: CurrentUser):
    rows = declare.list_my_declarations(conn, user["id"])
    return DeclarationList(items=[_row_out(r) for r in rows])


@router.post("/declarations", response_model=DeclarationRow, status_code=201)
def add_my_declaration(conn: Conn, user: CurrentUser, body: MyDeclarationCreateIn):
    _fetch_period(conn, body.period_id)
    unit_id = _resolve_own_unit_id(conn, user)
    if unit_id is None:
        raise HTTPException(409, "Không xác định được đơn vị để kê khai")
    try:
        did = declare.add_declaration(conn, period_id=body.period_id, work_id=body.work_id, unit_id=unit_id,
                                      actor_id=user["id"], note=body.note,
                                      actor_roles=user["roles"], actor_unit_id=unit_id,
                                      actor_person_id=user["person_id"])
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return _row_from_detail(declare.get_declaration(conn, did))
