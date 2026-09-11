# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tìm giảng viên/sinh viên theo tên (lát cắt G, G1) — dùng cho combobox chuyển
liên kết/gán lại ở UI, thay ô nhập `person_id` thô.

Khớp: khoá `name_keys` (GIN, không dấu, nguyên cụm tên — xem `cris/people.py`)
khi gõ đủ họ tên, hoặc `display_name ILIKE` khi gõ một phần (có dấu như đã
lưu). `works` đếm trên `v_person_publications` ở trạng thái liên kết sống."""
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from cris import cv as cv_mod
from cris import rules as RU
from cris.api.deps import Conn
from cris.api.schemas import PersonSearchRow

router = APIRouter(prefix="/api", tags=["nguoi"])


def _query_key(conn, q):
    """Khoá tìm kiếm từ `q`, chuẩn hoá bằng đúng hàm đã tạo `person.name_keys`
    (`cris.rules.norm_name` + `name_key`). `None` khi chưa có bộ luật
    `name_norm` active (CSDL mới, chưa `seed_rules`) — khi đó chỉ còn ILIKE."""
    rules = RU.load_active(conn)
    nb = rules.get("name_norm")
    if nb is None:
        return None
    name_norm, _degree = RU.norm_name(q, nb[1])
    return RU.name_key(name_norm) if name_norm else None


@router.get("/persons", response_model=list[PersonSearchRow])
def search_persons(conn: Conn, q: str = "", kind: str = "", limit: int = Query(20, ge=1, le=100)):
    q = q.strip()
    where, params = [], []
    exact_sql, exact_params = "FALSE", []
    if q:
        key = _query_key(conn, q)
        like = f"%{q}%"
        if key:
            where.append("(p.name_keys && %s::text[] OR p.display_name ILIKE %s)")
            params += [[key], like]
            exact_sql = "(p.name_keys && %s::text[] OR lower(p.display_name) = lower(%s))"
            exact_params = [[key], q]
        else:
            where.append("p.display_name ILIKE %s")
            params.append(like)
            exact_sql = "lower(p.display_name) = lower(%s)"
            exact_params = [q]
    if kind:
        where.append("p.kind = %s")
        params.append(kind)
    where_sql = " AND ".join(where) if where else "TRUE"
    sql = f"""SELECT p.id, p.display_name, p.degree_raw AS degree, u.code AS unit_code, p.kind,
                     COALESCE(wc.n, 0) AS works, {exact_sql} AS is_exact
              FROM person p
              LEFT JOIN unit u ON u.id = p.unit_id
              LEFT JOIN (SELECT person_id, count(*) AS n FROM v_person_publications
                         WHERE state IN ('DaNoiTuDong','DaXacNhan') GROUP BY person_id) wc ON wc.person_id = p.id
              WHERE {where_sql}
              ORDER BY is_exact DESC, works DESC, p.display_name
              LIMIT %s"""
    with conn.cursor() as cur:
        cur.execute(sql, exact_params + params + [limit])
        rows = cur.fetchall()
    return [PersonSearchRow(id=r["id"], display_name=r["display_name"], degree=r["degree"],
                            unit_code=r["unit_code"], kind=r["kind"], works=r["works"]) for r in rows]


@router.get("/persons/{pid}/cv")
def person_cv(conn: Conn, pid: int, format: Literal["html"] = "html"):
    """Lý lịch khoa học (K1): HTML in được, trang UI `window.print()`. Sinh
    trong `cris.cv` (self-contained, escape mọi chuỗi) — tái dùng `cris.cite`
    để mỗi công trình hiện đúng dạng APA đã có ở nơi khác."""
    doc = cv_mod.render(conn, pid)
    if doc is None:
        raise HTTPException(404, f"không tìm thấy giảng viên #{pid}")
    return HTMLResponse(content=doc)
