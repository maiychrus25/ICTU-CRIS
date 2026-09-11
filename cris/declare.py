# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kê khai công trình vào kỳ báo cáo (lát cắt K, G3, nâng cấp H1): một đơn vị
kê khai một công trình vào một kỳ đang mở, hồ sơ đi qua quy trình hai cấp của
`docs/ba/03-state.md` §3.2 — `Nhap → ChoKhoaDuyet → KhoaDaDuyet →
ChoPhongKiemTra → DatYeuCau → DaChot`, có thể trả về `Nhap` ở mỗi cấp duyệt,
cộng nhánh `ChoBoSung`/`Rut` cho giai đoạn chuẩn bị. Không sửa `cris/period.py`
— chỉ đọc trạng thái kỳ.

Phân quyền (NFR-02, NFR-03): mỗi bước chuyển gắn với một tập vai trò
(`_TRANSITIONS`); gọi `set_state`/`add_declaration`/`list_declarations` kèm
`actor_roles`/`actor_unit_id` để tầng nghiệp vụ kiểm — sai vai trò hoặc khác
đơn vị (với vai trò cấp khoa) → `PermissionError` (tầng API map 403). Không
truyền hai tham số này (mặc định `None`) giữ hành vi cũ, không kiểm gì — dùng
cho lời gọi nội bộ/kiểm thử không cần kiểm quyền.
"""
from cris import audit
from cris.db import tx

EVIDENCE_KINDS = ("link", "file", "note")

# (from_state, to_state) hợp lệ kèm vai trò được phép và lý do có bắt buộc
# không — đúng bảng chuyển trạng thái của lát cắt H1 (docs/ba/03-state.md).
_TRANSITIONS = {
    ("Nhap", "ChoKhoaDuyet"): {"roles": ("faculty_officer", "rd_officer"), "reason": False},
    ("ChoKhoaDuyet", "KhoaDaDuyet"): {"roles": ("faculty_head",), "reason": False},
    ("ChoKhoaDuyet", "Nhap"): {"roles": ("faculty_head",), "reason": True},
    ("KhoaDaDuyet", "ChoPhongKiemTra"): {"roles": ("faculty_head", "rd_officer"), "reason": False},
    ("ChoPhongKiemTra", "DatYeuCau"): {"roles": ("rd_officer",), "reason": False},
    ("ChoPhongKiemTra", "Nhap"): {"roles": ("rd_officer",), "reason": True},
    ("Nhap", "ChoBoSung"): {"roles": ("faculty_officer", "rd_officer"), "reason": True},
    ("ChoBoSung", "Nhap"): {"roles": ("faculty_officer", "rd_officer"), "reason": False},
    ("Nhap", "Rut"): {"roles": ("faculty_officer", "rd_officer"), "reason": True},
    ("ChoBoSung", "Rut"): {"roles": ("faculty_officer", "rd_officer"), "reason": True},
}

# Các bước thuộc giai đoạn "chuẩn bị hồ sơ" (di sản từ trước H1): chỉ chạy
# được khi kỳ còn đang nhận hồ sơ. Từ ChoKhoaDuyet trở đi là luồng duyệt hai
# cấp, tiếp tục chạy được sau khi kỳ đã đóng nộp (đó chính là lúc khoa/phòng
# xét duyệt) — chỉ kỳ đã `Huy` mới chặn toàn bộ.
_PRE_CLOSE_ONLY_TRANSITIONS = {("Nhap", "ChoBoSung"), ("ChoBoSung", "Nhap"), ("Nhap", "Rut"), ("ChoBoSung", "Rut")}

# Vai trò được phép kê khai (tạo hồ sơ mới) — ma trận phân quyền K-01..04, K-07.
ADD_DECLARATION_ROLES = ("faculty_officer", "rd_officer")


def _get_declaration(cur, declaration_id, lock=False):
    sql = "SELECT * FROM declaration WHERE id=%s"
    if lock:
        sql += " FOR UPDATE"
    cur.execute(sql, (declaration_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"không tìm thấy hồ sơ kê khai: {declaration_id}")
    return row


def _check_unit_scope(actor_roles, actor_unit_id, unit_id):
    """Vai trò cấp khoa (không có `rd_officer`) chỉ thao tác được hồ sơ của
    đơn vị mình (NFR-02) — `PermissionError` khác đơn vị. Không kiểm gì nếu
    `actor_unit_id` không được truyền (giữ hành vi cũ, không kiểm quyền)."""
    if actor_unit_id is None:
        return
    if actor_roles and "rd_officer" in actor_roles:
        return
    if unit_id != actor_unit_id:
        raise PermissionError("chỉ thao tác được hồ sơ của đơn vị mình")


def add_declaration(conn, *, period_id, work_id, unit_id, actor_id, note=None,
                     actor_roles=None, actor_unit_id=None):
    """Kê khai một công trình vào một kỳ cho một đơn vị.

    Kỳ phải đang `DangMo`; công trình phải còn sống (`merged_into_id IS
    NULL`, chưa bị gộp vào bản ghi khác); một (kỳ, công trình, đơn vị) chỉ kê
    khai một lần (UNIQUE). `actor_roles` khác `None` mà không có
    `faculty_officer`/`rd_officer` → `PermissionError`; `actor_unit_id` khác
    `None` và vai trò không có `rd_officer` mà `unit_id` khác đơn vị của actor
    → `PermissionError` (NFR-02). Ghi `declaration_event(from_state=NULL,
    to_state='Nhap')` và `audit_log('declaration.add')`. Trả về id hồ sơ.
    """
    if actor_roles is not None and not any(r in actor_roles for r in ADD_DECLARATION_ROLES):
        raise PermissionError(f"cần vai trò: {', '.join(ADD_DECLARATION_ROLES)}")
    _check_unit_scope(actor_roles, actor_unit_id, unit_id)

    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT state FROM period WHERE id=%s", (period_id,))
        period = cur.fetchone()
        if not period:
            raise ValueError(f"không tìm thấy kỳ báo cáo: {period_id}")
        if period["state"] != "DangMo":
            raise ValueError("chỉ kê khai được khi kỳ báo cáo đang mở")

        cur.execute("SELECT merged_into_id FROM work WHERE id=%s", (work_id,))
        work = cur.fetchone()
        if not work:
            raise ValueError(f"không tìm thấy công trình: {work_id}")
        if work["merged_into_id"] is not None:
            raise ValueError("công trình đã bị gộp vào bản ghi khác, không thể kê khai")

        cur.execute("SELECT id FROM declaration WHERE period_id=%s AND work_id=%s AND unit_id=%s",
                    (period_id, work_id, unit_id))
        if cur.fetchone():
            raise ValueError("đã kê khai")

        cur.execute(
            "INSERT INTO declaration(period_id, work_id, unit_id, note, created_by) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (period_id, work_id, unit_id, note, actor_id))
        declaration_id = cur.fetchone()["id"]
        cur.execute(
            "INSERT INTO declaration_event(declaration_id, from_state, to_state, actor_id) "
            "VALUES (%s, NULL, 'Nhap', %s)",
            (declaration_id, actor_id))
        audit.log(conn, actor_id, "declaration.add", "declaration", declaration_id,
                  after={"period_id": period_id, "work_id": work_id, "unit_id": unit_id, "state": "Nhap"})
    return declaration_id


def set_state(conn, declaration_id, to_state, actor_id, reason=None, *, actor_roles=None, actor_unit_id=None):
    """Chuyển trạng thái hồ sơ theo bảng `_TRANSITIONS` (quy trình hai cấp).

    Từ chối (`ValueError`) nếu kỳ của hồ sơ đã `Huy`, hoặc bước chuyển
    (`ChoBoSung`/`Rut`, giai đoạn chuẩn bị) mà kỳ đã `DaDongNop`, hoặc bước
    chuyển không nằm trong `_TRANSITIONS`, hoặc thiếu lý do bắt buộc.
    `actor_roles` khác `None` mà không khớp vai trò cho phép của bước chuyển
    → `PermissionError`; `actor_unit_id` khác `None`, vai trò không có
    `rd_officer` và hồ sơ thuộc đơn vị khác → `PermissionError` (NFR-02).
    Ghi `declaration_event` và `audit_log('declaration.<to_state>')`.
    """
    with tx(conn), conn.cursor() as cur:
        before = _get_declaration(cur, declaration_id, lock=True)
        cur.execute("SELECT state FROM period WHERE id=%s", (before["period_id"],))
        period = cur.fetchone()
        from_state = before["state"]
        if period and period["state"] == "Huy":
            raise ValueError("kỳ báo cáo đã huỷ, không thể đổi trạng thái hồ sơ")
        if (period and period["state"] == "DaDongNop"
                and (from_state, to_state) in _PRE_CLOSE_ONLY_TRANSITIONS):
            raise ValueError("kỳ báo cáo đã đóng nộp, không thể đổi trạng thái hồ sơ ở bước này")

        transition = _TRANSITIONS.get((from_state, to_state))
        if transition is None:
            raise ValueError(f"không thể chuyển hồ sơ từ {from_state} sang {to_state}")
        if actor_roles is not None and not any(r in actor_roles for r in transition["roles"]):
            raise PermissionError(f"cần vai trò: {', '.join(transition['roles'])}")
        _check_unit_scope(actor_roles, actor_unit_id, before["unit_id"])
        if transition["reason"] and not (reason or "").strip():
            raise ValueError(f"chuyển sang {to_state} bắt buộc phải nêu lý do")

        cur.execute("UPDATE declaration SET state=%s, updated_at=now() WHERE id=%s", (to_state, declaration_id))
        cur.execute(
            "INSERT INTO declaration_event(declaration_id, from_state, to_state, actor_id, reason) "
            "VALUES (%s,%s,%s,%s,%s)",
            (declaration_id, from_state, to_state, actor_id, reason))
        audit.log(conn, actor_id, f"declaration.{to_state}", "declaration", declaration_id,
                  before={"state": from_state}, after={"state": to_state, "reason": reason})


def finalize_period(conn, period_id, actor_id):
    """Chốt kỳ báo cáo (rd_officer, qua API): mọi hồ sơ `DatYeuCau` → `DaChot`.

    Kỳ phải ở `DaDongNop` (`ValueError` nếu không, hoặc không tìm thấy kỳ).
    Hồ sơ chưa ở `DatYeuCau` giữ nguyên trạng thái, được liệt kê trong
    `skipped`. Ghi `declaration_event` + `audit_log('declaration.DaChot')`
    từng hồ sơ được chốt, và một `audit_log('period.finalize')` cho kỳ. Trả
    `{"finalized": n, "skipped": [{"id", "state"}, ...]}`.
    """
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT * FROM period WHERE id=%s FOR UPDATE", (period_id,))
        period = cur.fetchone()
        if not period:
            raise ValueError(f"không tìm thấy kỳ báo cáo: {period_id}")
        if period["state"] != "DaDongNop":
            raise ValueError("chỉ chốt kỳ khi kỳ báo cáo đã đóng nộp")

        cur.execute("SELECT id, state FROM declaration WHERE period_id=%s ORDER BY id", (period_id,))
        rows = cur.fetchall()
        finalized_ids = []
        skipped = []
        for row in rows:
            if row["state"] == "DatYeuCau":
                cur.execute("UPDATE declaration SET state='DaChot', updated_at=now() WHERE id=%s", (row["id"],))
                cur.execute(
                    "INSERT INTO declaration_event(declaration_id, from_state, to_state, actor_id) "
                    "VALUES (%s,'DatYeuCau','DaChot',%s)",
                    (row["id"], actor_id))
                audit.log(conn, actor_id, "declaration.DaChot", "declaration", row["id"],
                          before={"state": "DatYeuCau"}, after={"state": "DaChot"})
                finalized_ids.append(row["id"])
            else:
                skipped.append({"id": row["id"], "state": row["state"]})

        audit.log(conn, actor_id, "period.finalize", "period", period_id,
                  before={"state": period["state"]},
                  after={"finalized": len(finalized_ids), "skipped": len(skipped)})
    return {"finalized": len(finalized_ids), "skipped": skipped}


def add_evidence(conn, declaration_id, *, kind, url=None, file_name=None, note=None, actor_id):
    """Thêm một minh chứng (`kind` ∈ link|file|note) vào hồ sơ kê khai."""
    if kind not in EVIDENCE_KINDS:
        raise ValueError(f"loại minh chứng không hợp lệ: {kind}")
    with tx(conn), conn.cursor() as cur:
        _get_declaration(cur, declaration_id)
        cur.execute(
            "INSERT INTO evidence(declaration_id, kind, url, file_name, note, added_by) "
            "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            (declaration_id, kind, url, file_name, note, actor_id))
        evidence_id = cur.fetchone()["id"]
        audit.log(conn, actor_id, "declaration.evidence", "declaration", declaration_id,
                  after={"evidence_id": evidence_id, "kind": kind})
    return evidence_id


def list_declarations(conn, period_id, unit_id=None, *, actor_roles=None, actor_unit_id=None):
    """Hồ sơ kê khai của một kỳ, mới nhất trước; kèm `work_title`, `doc_type`,
    `unit_code`, `evidence_count`, `last_event_at`. `unit_id` lọc theo đơn vị.

    Vai trò cấp khoa (`actor_unit_id` khác `None` mà không có `rd_officer`
    trong `actor_roles`) chỉ thấy hồ sơ của đơn vị mình: `unit_id` bị ép về
    `actor_unit_id`, bất kể tham số truyền vào — lọc ở tầng SQL (NFR-02), không
    chỉ ẩn trên giao diện.
    """
    if actor_unit_id is not None and not (actor_roles and "rd_officer" in actor_roles):
        unit_id = actor_unit_id
    where = ["d.period_id=%s"]
    params = [period_id]
    if unit_id is not None:
        where.append("d.unit_id=%s")
        params.append(unit_id)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT d.*, w.title AS work_title, w.doc_type AS doc_type, u.code AS unit_code,
                   (SELECT count(*) FROM evidence e WHERE e.declaration_id = d.id) AS evidence_count,
                   (SELECT max(ev.at) FROM declaration_event ev WHERE ev.declaration_id = d.id) AS last_event_at
            FROM declaration d
            JOIN work w ON w.id = d.work_id
            JOIN unit u ON u.id = d.unit_id
            WHERE {" AND ".join(where)}
            ORDER BY d.created_at DESC, d.id DESC
        """, params)
        return cur.fetchall()


def get_declaration(conn, declaration_id):
    """Hồ sơ một công trình: bản ghi (kèm `work_title`, `doc_type`, `unit_code`),
    toàn bộ `events` (cũ→mới) và `evidence` (cũ→mới). `ValueError` nếu không có."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.*, w.title AS work_title, w.doc_type AS doc_type, u.code AS unit_code
            FROM declaration d
            JOIN work w ON w.id = d.work_id
            JOIN unit u ON u.id = d.unit_id
            WHERE d.id=%s""", (declaration_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"không tìm thấy hồ sơ kê khai: {declaration_id}")
        cur.execute("SELECT * FROM declaration_event WHERE declaration_id=%s ORDER BY at, id", (declaration_id,))
        events = cur.fetchall()
        cur.execute("SELECT * FROM evidence WHERE declaration_id=%s ORDER BY added_at, id", (declaration_id,))
        evidence = cur.fetchall()
    return {"declaration": row, "events": events, "evidence": evidence}
