# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kê khai công trình vào kỳ báo cáo (lát cắt K, G3, nâng cấp H1, I2): lớp mỏng
gọi `cris.declare`. `ValueError` từ tầng nghiệp vụ (kỳ chưa mở, đã kê khai, sai
bước chuyển trạng thái, thiếu lý do...) → 409 (tệp minh chứng quá khổ/sai loại
→ 413/415 riêng, xem `add_evidence_file`); `PermissionError` (sai vai trò
hoặc khác đơn vị, NFR-02/NFR-03) → 403; không tìm thấy kỳ/hồ sơ/minh chứng
theo id trên đường dẫn → 404. Kê khai và chuyển trạng thái dùng `current_user`
để tầng nghiệp vụ kiểm vai trò/đơn vị; thêm minh chứng (kể cả tệp) vẫn cần vai
trò `rd_officer`; tải tệp minh chứng về cần đăng nhập khi auth bật và kiểm
phạm vi đơn vị (`cris.declare.get_evidence`)."""
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from cris import declare
from cris.api.deps import Conn, CurrentUser, require_role
from cris.api.schemas import (
    DOC_TYPE_LABELS,
    DeclarationCreateIn,
    DeclarationDetail,
    DeclarationEventOut,
    DeclarationEvidenceIn,
    DeclarationList,
    DeclarationRow,
    DeclarationStateIn,
    EvidenceFileOut,
    EvidenceOut,
)

router = APIRouter(prefix="/api", tags=["ke-khai"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]


def _fetch_period(conn, pid):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM period WHERE id=%s", (pid,))
        if cur.fetchone() is None:
            raise HTTPException(404, f"không tìm thấy kỳ báo cáo #{pid}")


def _fetch_declaration(conn, did):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM declaration WHERE id=%s", (did,))
        if cur.fetchone() is None:
            raise HTTPException(404, f"không tìm thấy hồ sơ kê khai #{did}")


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


@router.get("/periods/{pid}/declarations", response_model=DeclarationList)
def list_declarations(conn: Conn, user: CurrentUser, pid: int, unit_id: int | None = None):
    _fetch_period(conn, pid)
    rows = declare.list_declarations(conn, pid, unit_id=unit_id,
                                     actor_roles=user["roles"], actor_unit_id=user["unit_id"])
    return DeclarationList(items=[_row_out(r) for r in rows])


@router.post("/periods/{pid}/declarations", response_model=DeclarationRow, status_code=201)
def add_declaration(conn: Conn, user: CurrentUser, pid: int, body: DeclarationCreateIn):
    _fetch_period(conn, pid)
    try:
        did = declare.add_declaration(conn, period_id=pid, work_id=body.work_id, unit_id=body.unit_id,
                                      actor_id=user["id"], note=body.note,
                                      actor_roles=user["roles"], actor_unit_id=user["unit_id"])
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return _row_from_detail(declare.get_declaration(conn, did))


@router.get("/declarations/{did}", response_model=DeclarationDetail)
def declaration_detail(conn: Conn, did: int):
    _fetch_declaration(conn, did)
    data = declare.get_declaration(conn, did)
    d = data["declaration"]
    return DeclarationDetail(
        id=d["id"], period_id=d["period_id"], work_id=d["work_id"], work_title=d["work_title"],
        doc_type=d["doc_type"], doc_type_label=DOC_TYPE_LABELS.get(d["doc_type"], d["doc_type"]),
        unit_id=d["unit_id"], unit_code=d["unit_code"], state=d["state"], note=d["note"],
        created_at=d["created_at"], updated_at=d["updated_at"],
        events=[DeclarationEventOut(id=e["id"], from_state=e["from_state"], to_state=e["to_state"],
                                    actor_id=e["actor_id"], reason=e["reason"], at=e["at"])
                for e in data["events"]],
        evidence=[EvidenceOut(id=e["id"], kind=e["kind"], url=e["url"], file_name=e["file_name"], note=e["note"],
                              added_by=e["added_by"], added_at=e["added_at"], size_bytes=e.get("size_bytes"),
                              sha256=e.get("sha256"), content_type=e.get("content_type"))
                  for e in data["evidence"]],
    )


@router.post("/declarations/{did}/state", response_model=DeclarationRow)
def set_declaration_state(conn: Conn, user: CurrentUser, did: int, body: DeclarationStateIn):
    _fetch_declaration(conn, did)
    try:
        declare.set_state(conn, did, body.to_state, user["id"], reason=body.reason,
                          actor_roles=user["roles"], actor_unit_id=user["unit_id"])
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return _row_from_detail(declare.get_declaration(conn, did))


@router.post("/declarations/{did}/evidence", response_model=EvidenceOut, status_code=201)
def add_evidence(conn: Conn, actor: RdOfficer, did: int, body: DeclarationEvidenceIn):
    _fetch_declaration(conn, did)
    try:
        eid = declare.add_evidence(conn, did, kind=body.kind, url=body.url, file_name=body.file_name,
                                   note=body.note, actor_id=actor)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM evidence WHERE id=%s", (eid,))
        row = cur.fetchone()
    return EvidenceOut(id=row["id"], kind=row["kind"], url=row["url"], file_name=row["file_name"],
                       note=row["note"], added_by=row["added_by"], added_at=row["added_at"])


@router.post("/declarations/{did}/evidence/file", response_model=EvidenceFileOut, status_code=201)
def add_evidence_file(conn: Conn, actor: RdOfficer, did: int, file: Annotated[UploadFile, File()],
                      note: Annotated[str | None, Form()] = None):
    _fetch_declaration(conn, did)
    data = file.file.read()
    try:
        eid = declare.add_evidence_file(conn, did, data=data, original_name=file.filename or "minh-chung",
                                        actor_id=actor, note=note)
    except ValueError as exc:
        msg = str(exc)
        status = 413 if "kích thước" in msg else 415
        raise HTTPException(status, msg) from exc
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM evidence WHERE id=%s", (eid,))
        row = cur.fetchone()
    return EvidenceFileOut(id=row["id"], file_name=row["file_name"], size_bytes=row["size_bytes"],
                           sha256=row["sha256"], content_type=row["content_type"])


@router.get("/evidence/{eid}/file")
def get_evidence_file(conn: Conn, user: CurrentUser, eid: int):
    try:
        row = declare.get_evidence(conn, eid, actor_roles=user["roles"], actor_unit_id=user["unit_id"])
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    if row is None or not row.get("storage_path"):
        raise HTTPException(404, f"không tìm thấy minh chứng dạng tệp #{eid}")
    filename = row.get("file_name") or f"minh-chung-{eid}"
    return FileResponse(
        row["storage_path"], media_type=row["content_type"] or "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"})
