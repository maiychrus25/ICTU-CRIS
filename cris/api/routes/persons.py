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
from cris.api.schemas import (
    DirectoryPerson,
    FacetValue,
    Page,
    PersonDirectoryFacets,
    PersonDirectoryOut,
    PersonSearchRow,
    UnitRef,
)

router = APIRouter(prefix="/api", tags=["nguoi"])

DIRECTORY_DOC_TYPES = ("bai_bao", "do_an", "luan_van", "luan_an", "hoc_lieu")
_DIRECTORY_BY_TYPE_COLS = ", ".join(f"count(*) FILTER (WHERE w.doc_type='{t}') AS {t}" for t in DIRECTORY_DOC_TYPES)
# Học hàm (person.rank) đi trước học vị (person.degree_raw): nguồn ghi PGS/GS
# luôn kèm học vị TS (xem `archive.rank`/`archive.degree`, `cris/people.py`) nên
# một người chỉ rơi đúng một mục — không đếm hai lần ở facet `degrees`.
DEGREE_LABELS = [("gs", "Giáo sư"), ("pgs", "Phó Giáo sư"), ("ts", "Tiến sĩ"),
                 ("ths", "Thạc sĩ"), ("other", "Khác")]
_DEGREE_CASE_SQL = ("CASE WHEN lower(p.rank) = 'gs' THEN 'gs' WHEN lower(p.rank) = 'pgs' THEN 'pgs' "
                    "WHEN lower(p.degree_raw) = 'ts' THEN 'ts' WHEN lower(p.degree_raw) = 'ths' THEN 'ths' "
                    "ELSE 'other' END")


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


def _directory_base_where(q: str):
    """WHERE/params dùng cho cả danh sách và facet của `/persons/directory` — chỉ
    lọc `kind='lecturer'`, `active` và `q` (tên; không dấu cũng khớp nhờ
    `person.name_norm`, đã chuẩn hoá sẵn lúc nhập liệu — `cris.people.import_people`);
    chưa lọc `unit`/`degree`/`has_works` (facet đếm trên tập này)."""
    where, params = ["p.kind = 'lecturer'", "p.active"], []
    qs = q.strip()
    if qs:
        like = f"%{qs}%"
        norm_like = f"%{RU.strip_accents(qs).lower()}%"
        where.append("(p.display_name ILIKE %s OR p.name_norm ILIKE %s)")
        params += [like, norm_like]
    return where, params


@router.get("/persons/directory", response_model=PersonDirectoryOut)
def persons_directory(conn: Conn, q: str = "", unit: str = "", degree: str = "", has_works: bool = False,
                       sort: Literal["works", "name"] = "works",
                       page: int = Query(1, ge=1), per_page: int = Query(24, ge=1, le=60)):
    """Danh bạ giảng viên công khai (`/giang-vien/`) — chỉ `kind='lecturer'`,
    `active`; không email/điện thoại/ngày sinh. `works`/`by_type` đếm liên kết
    tác giả còn sống (`DaNoiTuDong`/`DaXacNhan`) trên công trình chưa gộp, qua
    một CTE gộp cho cả trang — không N+1. Khai báo TRƯỚC `/persons/{pid}` (xem
    thứ tự router ở `cris/api/app.py`) để không bị bắt nhầm là `pid`."""
    where, params = _directory_base_where(q)
    if unit:
        if unit == "none":
            where.append("p.unit_id IS NULL")
        elif unit.isdigit():
            where.append("p.unit_id = %s")
            params.append(int(unit))
        else:
            where.append("u.code = %s")
            params.append(unit)
    if degree:
        where.append(f"{_DEGREE_CASE_SQL} = %s")
        params.append(degree)
    if has_works:
        where.append("COALESCE(c.works, 0) > 0")
    where_sql = " AND ".join(where)
    # `sort=name`: tên gọi tiếng Việt (từ cuối họ tên) trước, rồi cả họ tên — không
    # phân biệt hoa/thường, ổn định (thêm `p.id`). `sort=works` (mặc định): nhiều
    # công trình trước, cũng ổn định nhờ `p.id`.
    # Tên gọi = từ cuối của họ tên, sau khi bỏ hậu tố trong ngoặc mà nguồn dùng để phân biệt người trùng tên
    # ("Nguyễn Thu Hương (88)" → "Hương"), nếu không "(88)" sẽ bị coi là tên gọi và đứng đầu danh bạ.
    _name = "regexp_replace(btrim(p.display_name), '\\s*\\([^)]*\\)\\s*$', '')"
    order_sql = (f"lower(regexp_replace({_name}, '^.*\\s+', '')), lower(p.display_name), p.id"
                if sort == "name" else "COALESCE(c.works, 0) DESC, p.id")
    from_sql = ("FROM person p LEFT JOIN unit u ON u.id = p.unit_id "
                "LEFT JOIN (SELECT vp.person_id, count(*) AS works, "
                f"{_DIRECTORY_BY_TYPE_COLS} FROM v_person_publications vp JOIN work w ON w.id = vp.work_id "
                "WHERE vp.state IN ('DaNoiTuDong','DaXacNhan') GROUP BY vp.person_id) c ON c.person_id = p.id")
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n {from_sql} WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(
            f"SELECT p.id, p.display_name, p.rank, p.degree_raw AS degree, p.position, p.field, p.avatar_url, "
            f"p.orcid, u.id AS unit_id, u.code AS unit_code, u.name AS unit_name, COALESCE(c.works, 0) AS works, "
            f"{', '.join(f'COALESCE(c.{t}, 0) AS {t}' for t in DIRECTORY_DOC_TYPES)} "
            f"{from_sql} WHERE {where_sql} ORDER BY {order_sql} LIMIT %s OFFSET %s",
            params + [per_page, (page - 1) * per_page])
        rows = cur.fetchall()
        base_where, base_params = _directory_base_where(q)
        base_where_sql = " AND ".join(base_where)
        cur.execute(
            f"SELECT COALESCE(u.code, 'none') AS value, COALESCE(u.name, 'Chưa gán khoa') AS label, count(*) AS n "
            f"FROM person p LEFT JOIN unit u ON u.id = p.unit_id WHERE {base_where_sql} "
            f"GROUP BY u.code, u.name ORDER BY n DESC, value", base_params)
        units_facet = [FacetValue(value=r["value"], label=r["label"], n=r["n"]) for r in cur.fetchall()]
        cur.execute(f"SELECT {_DEGREE_CASE_SQL} AS value, count(*) AS n FROM person p WHERE {base_where_sql} "
                    f"GROUP BY value", base_params)
        degree_n = {r["value"]: r["n"] for r in cur.fetchall()}
    items = []
    for r in rows:
        unit_ref = UnitRef(id=r["unit_id"], code=r["unit_code"], name=r["unit_name"]) if r["unit_id"] else None
        by_type = {t: r[t] for t in DIRECTORY_DOC_TYPES if r[t]}
        items.append(DirectoryPerson(id=r["id"], display_name=r["display_name"], rank=r["rank"], degree=r["degree"],
                                     position=r["position"], unit=unit_ref, field=r["field"],
                                     avatar_url=r["avatar_url"], orcid=r["orcid"], works=r["works"], by_type=by_type))
    degrees_facet = [FacetValue(value=code, label=label, n=degree_n.get(code, 0)) for code, label in DEGREE_LABELS]
    return PersonDirectoryOut(items=items, page=Page(page=page, per_page=per_page, total=total),
                              facets=PersonDirectoryFacets(units=units_facet, degrees=degrees_facet))


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
                     p.avatar_url, COALESCE(wc.n, 0) AS works, {exact_sql} AS is_exact
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
                            unit_code=r["unit_code"], kind=r["kind"], works=r["works"],
                            avatar_url=r["avatar_url"]) for r in rows]


@router.get("/persons/{pid}/cv")
def person_cv(conn: Conn, pid: int, format: Literal["html"] = "html"):
    """Lý lịch khoa học (K1): HTML in được, trang UI `window.print()`. Sinh
    trong `cris.cv` (self-contained, escape mọi chuỗi) — tái dùng `cris.cite`
    để mỗi công trình hiện đúng dạng APA đã có ở nơi khác."""
    doc = cv_mod.render(conn, pid)
    if doc is None:
        raise HTTPException(404, f"không tìm thấy giảng viên #{pid}")
    return HTMLResponse(content=doc)
