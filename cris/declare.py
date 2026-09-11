# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kê khai công trình vào kỳ báo cáo (lát cắt K, G3): một đơn vị kê khai một
công trình vào một kỳ đang mở, hồ sơ đi qua `Nhap`/`ChoBoSung`/`Rut` kèm minh
chứng. Không sửa `cris/period.py` — chỉ đọc trạng thái kỳ."""
from cris import audit
from cris.db import tx

EVIDENCE_KINDS = ("link", "file", "note")

# (from_state, to_state) hợp lệ; ChoBoSung/Rut bắt buộc nêu lý do.
_TRANSITIONS = {
    ("Nhap", "ChoBoSung"),
    ("ChoBoSung", "Nhap"),
    ("Nhap", "Rut"),
    ("ChoBoSung", "Rut"),
}
_REASON_REQUIRED = {"ChoBoSung", "Rut"}


def _get_declaration(cur, declaration_id, lock=False):
    sql = "SELECT * FROM declaration WHERE id=%s"
    if lock:
        sql += " FOR UPDATE"
    cur.execute(sql, (declaration_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"không tìm thấy hồ sơ kê khai: {declaration_id}")
    return row


def add_declaration(conn, *, period_id, work_id, unit_id, actor_id, note=None):
    """Kê khai một công trình vào một kỳ cho một đơn vị.

    Kỳ phải đang `DangMo`; công trình phải còn sống (`merged_into_id IS
    NULL`, chưa bị gộp vào bản ghi khác); một (kỳ, công trình, đơn vị) chỉ kê
    khai một lần (UNIQUE). Ghi `declaration_event(from_state=NULL,
    to_state='Nhap')` và `audit_log('declaration.add')`. Trả về id hồ sơ.
    """
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


def set_state(conn, declaration_id, to_state, actor_id, reason=None):
    """Chuyển trạng thái hồ sơ: `Nhap`↔`ChoBoSung`, `Nhap`/`ChoBoSung`→`Rut`.

    `ChoBoSung` và `Rut` bắt buộc `reason`. Từ chối nếu kỳ của hồ sơ đã
    `DaDongNop`/`Huy`, hoặc bước chuyển không nằm trong các bước cho phép ở
    trên. Ghi `declaration_event` và `audit_log('declaration.<to_state>')`.
    """
    with tx(conn), conn.cursor() as cur:
        before = _get_declaration(cur, declaration_id, lock=True)
        cur.execute("SELECT state FROM period WHERE id=%s", (before["period_id"],))
        period = cur.fetchone()
        if period and period["state"] in ("DaDongNop", "Huy"):
            raise ValueError("kỳ báo cáo đã đóng nộp hoặc đã huỷ, không thể đổi trạng thái hồ sơ")
        from_state = before["state"]
        if (from_state, to_state) not in _TRANSITIONS:
            raise ValueError(f"không thể chuyển hồ sơ từ {from_state} sang {to_state}")
        if to_state in _REASON_REQUIRED and not (reason or "").strip():
            raise ValueError(f"chuyển sang {to_state} bắt buộc phải nêu lý do")

        cur.execute("UPDATE declaration SET state=%s, updated_at=now() WHERE id=%s", (to_state, declaration_id))
        cur.execute(
            "INSERT INTO declaration_event(declaration_id, from_state, to_state, actor_id, reason) "
            "VALUES (%s,%s,%s,%s,%s)",
            (declaration_id, from_state, to_state, actor_id, reason))
        audit.log(conn, actor_id, f"declaration.{to_state}", "declaration", declaration_id,
                  before={"state": from_state}, after={"state": to_state, "reason": reason})


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


def list_declarations(conn, period_id, unit_id=None):
    """Hồ sơ kê khai của một kỳ, mới nhất trước; kèm `work_title`, `doc_type`,
    `unit_code`, `evidence_count`, `last_event_at`. `unit_id` lọc theo đơn vị."""
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
