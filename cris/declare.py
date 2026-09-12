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

Giảng viên tự kê khai (H3): vai trò `lecturer` được kê khai (`add_declaration`,
kèm `actor_person_id` để kiểm công trình là của chính mình qua
`v_person_publications`) và chuyển `Nhap → ChoKhoaDuyet`, `Nhap/ChoBoSung →
Rut` (`set_state`) — nhưng chỉ với hồ sơ do chính mình tạo (`created_by =
actor_id`); khác người tạo → `PermissionError` (`_assert_owner`). Khi actor có
thêm vai trò `faculty_officer`/`rd_officer` thì không bị ràng buộc sở hữu này
(giữ hành vi rộng hơn của các vai trò đó).
"""
import hashlib
import io
import os
import pathlib
import zipfile

from cris import audit, report
from cris.db import tx

EVIDENCE_KINDS = ("link", "file", "note")

# Minh chứng dạng tệp (I2): kích thước tối đa và loại nội dung nhận qua chữ ký
# byte (không tin phần mở rộng tên tệp) — xem `sniff_content_type`.
EVIDENCE_MAX_BYTES = 10 * 1024 * 1024
EVIDENCE_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

# (from_state, to_state) hợp lệ kèm vai trò được phép và lý do có bắt buộc
# không — đúng bảng chuyển trạng thái của lát cắt H1 (docs/ba/03-state.md).
_TRANSITIONS = {
    ("Nhap", "ChoKhoaDuyet"): {"roles": ("faculty_officer", "rd_officer", "lecturer"), "reason": False},
    ("ChoKhoaDuyet", "KhoaDaDuyet"): {"roles": ("faculty_head",), "reason": False},
    ("ChoKhoaDuyet", "Nhap"): {"roles": ("faculty_head",), "reason": True},
    ("KhoaDaDuyet", "ChoPhongKiemTra"): {"roles": ("faculty_head", "rd_officer"), "reason": False},
    ("ChoPhongKiemTra", "DatYeuCau"): {"roles": ("rd_officer",), "reason": False},
    ("ChoPhongKiemTra", "Nhap"): {"roles": ("rd_officer",), "reason": True},
    ("Nhap", "ChoBoSung"): {"roles": ("faculty_officer", "rd_officer"), "reason": True},
    ("ChoBoSung", "Nhap"): {"roles": ("faculty_officer", "rd_officer"), "reason": False},
    ("Nhap", "Rut"): {"roles": ("faculty_officer", "rd_officer", "lecturer"), "reason": True},
    ("ChoBoSung", "Rut"): {"roles": ("faculty_officer", "rd_officer", "lecturer"), "reason": True},
}

# Các bước thuộc giai đoạn "chuẩn bị hồ sơ" (di sản từ trước H1): chỉ chạy
# được khi kỳ còn đang nhận hồ sơ. Từ ChoKhoaDuyet trở đi là luồng duyệt hai
# cấp, tiếp tục chạy được sau khi kỳ đã đóng nộp (đó chính là lúc khoa/phòng
# xét duyệt) — chỉ kỳ đã `Huy` mới chặn toàn bộ.
_PRE_CLOSE_ONLY_TRANSITIONS = {("Nhap", "ChoBoSung"), ("ChoBoSung", "Nhap"), ("Nhap", "Rut"), ("ChoBoSung", "Rut")}

# Vai trò được phép kê khai (tạo hồ sơ mới) — ma trận phân quyền K-01..04, K-07;
# `lecturer` thêm ở H3 (chỉ công trình/đơn vị của chính mình, xem `_assert_own_work`).
ADD_DECLARATION_ROLES = ("faculty_officer", "rd_officer", "lecturer")

# Vai trò "rộng" không bị ràng buộc sở hữu hồ sơ/công trình — chỉ `lecturer`
# đơn thuần (không kèm các vai trò này) mới bị `_assert_owner`/`_assert_own_work` kiểm.
_UNSCOPED_ROLES = ("faculty_officer", "rd_officer")


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


def _assert_owner(actor_roles, actor_id, created_by):
    """Vai trò `lecturer` đơn thuần (không kèm `faculty_officer`/`rd_officer`,
    xem `_UNSCOPED_ROLES`) chỉ thao tác được hồ sơ do chính mình tạo
    (`created_by`) — `PermissionError` nếu khác. Không kiểm gì nếu
    `actor_roles` là `None` (giữ hành vi cũ) hoặc không có vai trò `lecturer`."""
    is_plain_lecturer = actor_roles and "lecturer" in actor_roles and not any(r in actor_roles for r in _UNSCOPED_ROLES)
    if is_plain_lecturer and created_by != actor_id:
        raise PermissionError("chỉ thao tác được hồ sơ do mình tạo")


def _assert_own_work(conn, actor_roles, actor_person_id, work_id):
    """Vai trò `lecturer` đơn thuần chỉ kê khai được công trình của chính
    mình: cần có bản ghi `v_person_publications` còn sống (`DaNoiTuDong`/
    `DaXacNhan`) nối `actor_person_id` với `work_id`. `PermissionError` nếu
    không có `actor_person_id` (tài khoản chưa gắn hồ sơ giảng viên) hoặc công
    trình không phải của mình."""
    if not (actor_roles and "lecturer" in actor_roles and not any(r in actor_roles for r in _UNSCOPED_ROLES)):
        return
    if actor_person_id is None:
        raise PermissionError("tài khoản chưa gắn với hồ sơ giảng viên")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM v_person_publications WHERE person_id=%s AND work_id=%s "
            "AND state IN ('DaNoiTuDong','DaXacNhan')",
            (actor_person_id, work_id))
        if cur.fetchone() is None:
            raise PermissionError("chỉ kê khai được công trình của chính mình")


def add_declaration(conn, *, period_id, work_id, unit_id, actor_id, note=None,
                     actor_roles=None, actor_unit_id=None, actor_person_id=None):
    """Kê khai một công trình vào một kỳ cho một đơn vị.

    Kỳ phải đang `DangMo`; công trình phải còn sống (`merged_into_id IS
    NULL`, chưa bị gộp vào bản ghi khác); một (kỳ, công trình, đơn vị) chỉ kê
    khai một lần (UNIQUE). `actor_roles` khác `None` mà không có
    `faculty_officer`/`rd_officer`/`lecturer` → `PermissionError`;
    `actor_unit_id` khác `None` và vai trò không có `rd_officer` mà `unit_id`
    khác đơn vị của actor → `PermissionError` (NFR-02). Vai trò `lecturer` đơn
    thuần (H3) còn phải sở hữu công trình (`actor_person_id`, xem
    `_assert_own_work`) → `PermissionError` nếu không. Ghi
    `declaration_event(from_state=NULL, to_state='Nhap')` và
    `audit_log('declaration.add')`. Trả về id hồ sơ.
    """
    if actor_roles is not None and not any(r in actor_roles for r in ADD_DECLARATION_ROLES):
        raise PermissionError(f"cần vai trò: {', '.join(ADD_DECLARATION_ROLES)}")
    _check_unit_scope(actor_roles, actor_unit_id, unit_id)
    _assert_own_work(conn, actor_roles, actor_person_id, work_id)

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
    `rd_officer` và hồ sơ thuộc đơn vị khác → `PermissionError` (NFR-02). Vai
    trò `lecturer` đơn thuần (H3) chỉ chuyển được hồ sơ do chính mình tạo →
    `PermissionError` nếu không (`_assert_owner`).
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
        _assert_owner(actor_roles, actor_id, before["created_by"])
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
    từng hồ sơ được chốt, và một `audit_log('period.finalize')` cho kỳ. Sau khi
    chốt, tự sinh một bản báo cáo đóng băng (`cris.report.build_report`). Trả
    `{"finalized": n, "skipped": [{"id", "state"}, ...], "report_id": id}`.
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
    report_id = report.build_report(conn, period_id, actor_id, note="Tự sinh khi chốt kỳ")
    return {"finalized": len(finalized_ids), "skipped": skipped, "report_id": report_id}


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


def sniff_content_type(data: bytes) -> str | None:
    """Nhận diện loại tệp qua chữ ký byte đầu — không tin phần mở rộng tên
    tệp. `docx` là tệp zip (`PK\\x03\\x04`) có thư mục `word/` bên trong (kiểm
    bằng `zipfile`, không chỉ nhìn 4 byte đầu vì `.xlsx`/`.pptx` cũng là zip).
    Trả `None` nếu không khớp loại nào trong `EVIDENCE_TYPES`."""
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data[:4] == b"PK\x03\x04":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                if any(n.startswith("word/") for n in zf.namelist()):
                    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        except zipfile.BadZipFile:
            return None
    return None


def add_evidence_file(conn, declaration_id, *, data: bytes, original_name, actor_id, actor_roles=None,
                       actor_unit_id=None, note=None, data_dir=None):
    """Thêm một minh chứng dạng tệp thật (I2). Kiểm quyền như `add_evidence`
    (hồ sơ phải tồn tại — `ValueError` nếu không). Kiểm kích thước
    (`EVIDENCE_MAX_BYTES`) và loại nội dung (`sniff_content_type`, chữ ký
    byte — không tin tên/`Content-Type` tệp gửi lên) → `ValueError` nếu vượt
    kích thước hoặc loại không thuộc `EVIDENCE_TYPES`.

    Băm SHA-256 rồi ghi tệp vào `<data_dir hoặc biến môi trường
    CRIS_DATA_DIR hoặc /data>/evidence/<declaration_id>/<16 ký tự đầu của
    sha256><đuôi>` — ghi ra tệp tạm trong cùng thư mục rồi `os.replace` để
    không bao giờ để lại tệp ghi dở. Chèn `evidence(kind='file', ...)` và ghi
    `audit_log('declaration.evidence')` như `add_evidence`. Trả về id minh
    chứng.
    """
    with conn.cursor() as cur:
        _get_declaration(cur, declaration_id)

    if len(data) > EVIDENCE_MAX_BYTES:
        raise ValueError(f"tệp vượt quá kích thước cho phép {EVIDENCE_MAX_BYTES // (1024 * 1024)} MB")
    content_type = sniff_content_type(data)
    if content_type is None or content_type not in EVIDENCE_TYPES:
        raise ValueError("loại tệp không hợp lệ; chỉ nhận pdf, png, jpg, jpeg, docx")

    sha256 = hashlib.sha256(data).hexdigest()
    digest = sha256[:16]
    ext = EVIDENCE_TYPES[content_type]
    base_dir = pathlib.Path(data_dir or os.environ.get("CRIS_DATA_DIR", "/data"))
    dest_dir = base_dir / "evidence" / str(declaration_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{digest}{ext}"
    tmp_path = dest_dir / f".{digest}{ext}.tmp"
    tmp_path.write_bytes(data)
    os.replace(tmp_path, dest_path)

    with tx(conn), conn.cursor() as cur:
        _get_declaration(cur, declaration_id, lock=True)
        cur.execute(
            "INSERT INTO evidence(declaration_id, kind, file_name, original_name, storage_path, "
            "size_bytes, sha256, content_type, note, added_by) "
            "VALUES (%s,'file',%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (declaration_id, original_name, original_name, str(dest_path), len(data), sha256, content_type,
             note, actor_id))
        evidence_id = cur.fetchone()["id"]
        audit.log(conn, actor_id, "declaration.evidence", "declaration", declaration_id,
                  after={"evidence_id": evidence_id, "kind": "file", "sha256": sha256, "size_bytes": len(data)})
    return evidence_id


def get_evidence(conn, evidence_id, *, actor_roles=None, actor_unit_id=None):
    """Một minh chứng theo id, kiểm phạm vi đơn vị (NFR-02) của hồ sơ kê khai
    chứa nó như các hàm khác của module — `PermissionError` nếu vai trò cấp
    khoa khác đơn vị. Trả `None` nếu không có (tầng API map 404)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT e.*, d.unit_id AS declaration_unit_id FROM evidence e "
            "JOIN declaration d ON d.id = e.declaration_id WHERE e.id=%s",
            (evidence_id,))
        row = cur.fetchone()
    if row is None:
        return None
    _check_unit_scope(actor_roles, actor_unit_id, row["declaration_unit_id"])
    return row


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


def list_my_declarations(conn, actor_id):
    """Hồ sơ kê khai do chính `actor_id` tạo (`created_by`, H3 — giảng viên tự
    kê khai), mọi kỳ, mới nhất trước; cùng cột như `list_declarations`
    (`work_title`, `doc_type`, `unit_code`, `evidence_count`,
    `last_event_at`)."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.*, w.title AS work_title, w.doc_type AS doc_type, u.code AS unit_code,
                   (SELECT count(*) FROM evidence e WHERE e.declaration_id = d.id) AS evidence_count,
                   (SELECT max(ev.at) FROM declaration_event ev WHERE ev.declaration_id = d.id) AS last_event_at
            FROM declaration d
            JOIN work w ON w.id = d.work_id
            JOIN unit u ON u.id = d.unit_id
            WHERE d.created_by = %s
            ORDER BY d.created_at DESC, d.id DESC
        """, (actor_id,))
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
