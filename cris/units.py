# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Quản lý đơn vị thật (khoa/trung tâm) — lát cắt M. Đơn vị được seed ở migration
`0020_units_from_source.sql` (mã từ bộ lọc `dept` của kho nguồn); ở đây chỉ các
thao tác quản trị nhẹ (liệt kê, đổi tên, thêm bí danh, gán tay một giảng viên)
— mọi thay đổi đều ghi `audit_log` để tra ngược được ai sửa, lúc nào, vì sao."""
from cris import audit
from cris.db import tx


def list_units(conn, include_inactive=False):
    """Đơn vị kèm số công trình (`v_work_unit`, cả nguồn lẫn tác giả đã liên kết)
    và số giảng viên (`person.unit_id`), sắp theo `works` giảm dần."""
    where = "" if include_inactive else "WHERE u.active"
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT u.id, u.code, u.name, u.aliases, u.active,
                   count(DISTINCT vu.work_id) AS works,
                   count(DISTINCT p.id) FILTER (WHERE p.kind='lecturer') AS persons
            FROM unit u
            LEFT JOIN v_work_unit vu ON vu.unit_id = u.id
            LEFT JOIN person p ON p.unit_id = u.id
            {where}
            GROUP BY u.id, u.code, u.name, u.aliases, u.active
            ORDER BY works DESC, u.code
        """)
        return cur.fetchall()


def rename_unit(conn, code, name, actor_id=None, reason=None):
    """Đổi tên hiển thị của một đơn vị (mã giữ nguyên). `ValueError` nếu không
    tìm thấy mã — tầng gọi (CLI/API) tự map sang thông báo/HTTP phù hợp."""
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT id, name FROM unit WHERE code=%s", (code,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"không tìm thấy đơn vị có mã: {code}")
        cur.execute("UPDATE unit SET name=%s WHERE id=%s", (name, row["id"]))
        audit.log(conn, actor_id, "unit.rename", "unit", row["id"],
                  before={"name": row["name"]}, after={"name": name, "reason": reason})
        return row["id"]


def add_alias(conn, code, alias, actor_id=None, reason=None):
    """Thêm một bí danh (vd nguồn ghi biến thể "HTTKT" cho "HTTTKT") — không
    trùng lặp, không xoá bí danh cũ."""
    alias = (alias or "").strip()
    if not alias:
        raise ValueError("bí danh không được để trống")
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT id, aliases FROM unit WHERE code=%s", (code,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"không tìm thấy đơn vị có mã: {code}")
        if alias in (row["aliases"] or []):
            return row["id"]
        new_aliases = list(row["aliases"] or []) + [alias]
        cur.execute("UPDATE unit SET aliases=%s WHERE id=%s", (new_aliases, row["id"]))
        audit.log(conn, actor_id, "unit.alias", "unit", row["id"],
                  before={"aliases": row["aliases"]}, after={"aliases": new_aliases, "reason": reason})
        return row["id"]


def set_person_unit(conn, person_id, unit_id, actor_id=None, reason=None):
    """Gán/đổi đơn vị của một giảng viên bằng tay (quản trị) — đánh dấu
    `unit_source='manual'` để `assign_units_by_works` (đa số theo công trình)
    không còn ghi đè nữa. `unit_id=None` gỡ đơn vị (vẫn giữ 'manual')."""
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT id, unit_id, unit_source FROM person WHERE id=%s", (person_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"không tìm thấy giảng viên #{person_id}")
        if unit_id is not None:
            cur.execute("SELECT 1 FROM unit WHERE id=%s", (unit_id,))
            if cur.fetchone() is None:
                raise ValueError(f"không tìm thấy đơn vị #{unit_id}")
        cur.execute("UPDATE person SET unit_id=%s, unit_source='manual' WHERE id=%s", (unit_id, person_id))
        audit.log(conn, actor_id, "person.unit_manual", "person", person_id,
                  before={"unit_id": row["unit_id"], "unit_source": row["unit_source"]},
                  after={"unit_id": unit_id, "unit_source": "manual", "reason": reason})
        return person_id
