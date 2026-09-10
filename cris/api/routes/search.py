# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tra cứu công trình, chi tiết có xuất xứ từng trường, hồ sơ giảng viên, trục chủ đề.
SQL chuyển nguyên từ `cris/web/views_search.py`."""
from fastapi import APIRouter, HTTPException, Query

from cris.api.deps import Conn
from cris.api.schemas import (
    DOC_TYPE_LABELS,
    FieldRow,
    LastSync,
    MentionRow,
    Page,
    PersonProfile,
    PersonPublication,
    Topic,
    WorkDetail,
    WorkList,
    WorkSummary,
)

router = APIRouter(prefix="/api", tags=["tra-cuu"])

PER_PAGE = 50
FIELD_LABELS = [
    ("title", "Tiêu đề"), ("doi", "DOI"), ("journal", "Tạp chí"), ("volume", "Tập/số"),
    ("year_issue", "Năm"), ("abstract", "Tóm tắt"), ("keywords_raw", "Từ khoá"),
    ("pub_type_raw", "Loại xuất bản (thô)"), ("indexes", "Chỉ mục (Scopus/ISI/...)"),
    ("quartile", "Quartile"), ("venue_kind", "Loại nơi công bố"), ("score", "Điểm quy đổi"),
    ("needs_review", "Cần rà soát"), ("cohort", "Khoá/đợt"),
]
ROLE_LABELS = {"author": "Tác giả", "mentor": "Người hướng dẫn", "student": "Sinh viên thực hiện"}


def _fmt_dt(v):
    try:
        return v.strftime("%d/%m/%Y %H:%M")
    except AttributeError:
        return None


def _fmt_value(val):
    if val is None:
        return None
    if isinstance(val, bool):
        return "Có" if val else "Không"
    if isinstance(val, list):
        return ", ".join(str(x) for x in val) if val else None
    return str(val)


@router.get("/works", response_model=WorkList)
def list_works(conn: Conn, q: str = "", doc_type: str = "", year: int | None = None,
               unit: str = "", topic: int | None = None, page: int = Query(1, ge=1)):
    from_sql = ("FROM v_work_current w "
                "LEFT JOIN author_mention m ON m.work_id = w.id AND m.position > 0 "
                "LEFT JOIN v_work_unit vu ON vu.work_id = w.id "
                "LEFT JOIN unit u ON u.id = vu.unit_id")
    where, params = [], []
    if q.strip():
        like = f"%{q.strip()}%"
        where.append("(w.title ILIKE %s OR m.raw_name ILIKE %s)"); params += [like, like]
    if doc_type:
        where.append("w.doc_type = %s"); params.append(doc_type)
    if year is not None:
        where.append("w.year_issue = %s"); params.append(year)
    if unit:
        if unit.isdigit():
            where.append("vu.unit_id = %s"); params.append(int(unit))
        else:
            where.append("u.code = %s"); params.append(unit)
    if topic is not None:
        where.append("EXISTS (SELECT 1 FROM regexp_split_to_table(lower(w.keywords_raw), '[,;]') kw "
                     "JOIN ai_topic_keyword tk ON btrim(kw) = tk.keyword WHERE tk.topic_id = %s)")
        params.append(topic)
    where_sql = " AND ".join(where) if where else "TRUE"
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(DISTINCT w.id) AS n {from_sql} WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(f"SELECT DISTINCT w.id, w.title, w.doc_type, w.year_issue, w.doi, w.state, w.needs_review "
                    f"{from_sql} WHERE {where_sql} ORDER BY w.year_issue DESC NULLS LAST, w.id DESC LIMIT %s OFFSET %s",
                    params + [PER_PAGE, (page - 1) * PER_PAGE])
        rows = cur.fetchall()
    items = [WorkSummary(id=r["id"], title=r["title"], doc_type=r["doc_type"],
                         doc_type_label=DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]),
                         year=r["year_issue"], doi=r["doi"], state=r["state"], needs_review=bool(r["needs_review"]))
             for r in rows]
    return WorkList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total))


@router.get("/works/{wid}", response_model=WorkDetail)
def work_detail(conn: Conn, wid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM v_work_current WHERE id = %s", (wid,))
        w = cur.fetchone()
        if w is None:
            raise HTTPException(404, f"không tìm thấy công trình #{wid}")
        cur.execute("""SELECT DISTINCT ON (fp.field) fp.field, fp.raw_value, fp.value, fp.set_kind, fp.set_at,
                              sr.source AS src_source, sr.source_key AS src_key, au.display_name AS set_by_name
                       FROM field_provenance fp
                       LEFT JOIN source_record sr ON sr.id = fp.source_record_id
                       LEFT JOIN app_user au ON au.id = fp.set_by
                       WHERE fp.work_id = %s ORDER BY fp.field, fp.set_at DESC""", (wid,))
        prov = {r["field"]: r for r in cur.fetchall()}
        cur.execute("""SELECT m.id AS mention_id, m.role, m.position, m.raw_name, m.is_placeholder, m.is_truncated,
                              l.person_id AS linked_person_id, l.state AS link_state, p.display_name AS linked_person_name,
                              (SELECT count(*) FROM author_link l2 WHERE l2.mention_id = m.id AND l2.state = 'ChoXacNhan') AS pending_count
                       FROM author_mention m
                       LEFT JOIN author_link l ON l.mention_id = m.id AND l.state IN ('DaNoiTuDong','DaXacNhan')
                       LEFT JOIN person p ON p.id = l.person_id
                       WHERE m.work_id = %s AND m.position > 0 ORDER BY m.role, m.position""", (wid,))
        mentions = cur.fetchall()
    fields = []
    for field, label in FIELD_LABELS:
        p = prov.get(field)
        if p is None:
            raw, source = None, "Chưa ghi nhận nguồn"
        else:
            raw = p["raw_value"]
            when = _fmt_dt(p["set_at"]) or ""
            if p["set_kind"] in ("manual", "merge"):
                who = p["set_by_name"] or "không rõ người"
                source = f"{'Chỉnh tay' if p['set_kind'] == 'manual' else 'Gộp bản ghi trùng'} bởi {who}, lúc {when}"
            elif p["src_source"]:
                source = f"Đồng bộ từ {p['src_source']} (khoá {p['src_key']}), lúc {when}"
            else:
                source = f"Chuẩn hoá tự động, lúc {when}"
        fields.append(FieldRow(field=field, label=label, value=_fmt_value(w.get(field)), raw=raw, source=source))
    ms = [MentionRow(mention_id=m["mention_id"], role=m["role"], role_label=ROLE_LABELS.get(m["role"], m["role"]),
                     position=m["position"], raw_name=m["raw_name"], is_placeholder=bool(m["is_placeholder"]),
                     is_truncated=bool(m["is_truncated"]), linked_person_id=m["linked_person_id"],
                     linked_person_name=m["linked_person_name"], link_state=m["link_state"],
                     pending_count=m["pending_count"] or 0) for m in mentions]
    return WorkDetail(id=w["id"], title=w["title"], doc_type=w["doc_type"],
                      doc_type_label=DOC_TYPE_LABELS.get(w["doc_type"], w["doc_type"]), state=w["state"],
                      needs_review=bool(w["needs_review"]), has_manual=bool(w.get("has_manual")),
                      fields=fields, mentions=ms)


@router.get("/persons/{pid}", response_model=PersonProfile)
def person_profile(conn: Conn, pid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM person WHERE id = %s", (pid,))
        p = cur.fetchone()
        if p is None:
            raise HTTPException(404, f"không tìm thấy giảng viên #{pid}")
        cur.execute("""SELECT vp.work_id, vp.state, vp.confidence, w.title, w.doc_type, w.year_issue, w.doi
                       FROM v_person_publications vp JOIN work w ON w.id = vp.work_id
                       WHERE vp.person_id = %s ORDER BY w.year_issue DESC NULLS LAST, w.id DESC""", (pid,))
        pubs = cur.fetchall()
        cur.execute("""SELECT count(DISTINCT m.work_id) AS n FROM author_mention m JOIN author_link l ON l.mention_id = m.id
                       WHERE l.person_id = %s AND l.state = 'ChoXacNhan'""", (pid,))
        pending = cur.fetchone()["n"]
        cur.execute("SELECT id, source, scope, status, started_at, finished_at FROM sync_run ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()
    by_type, by_year = {}, {}
    for r in pubs:
        by_type[r["doc_type"]] = by_type.get(r["doc_type"], 0) + 1
        y = str(r["year_issue"]) if r["year_issue"] is not None else "không rõ"
        by_year[y] = by_year.get(y, 0) + 1
    return PersonProfile(
        id=p["id"], display_name=p["display_name"], degree=p.get("degree_raw"), email=p.get("email"), orcid=p.get("orcid"),
        by_type=by_type, by_year=dict(sorted(by_year.items())),
        publications=[PersonPublication(work_id=r["work_id"], title=r["title"], doc_type=r["doc_type"], year=r["year_issue"],
                                        doi=r["doi"], link_state=r["state"], confidence=r["confidence"]) for r in pubs],
        pending_count=pending, last_sync=LastSync(**last) if last else None)


@router.get("/topics", response_model=list[Topic])
def topics(conn: Conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, label, size FROM ai_topic ORDER BY size DESC, label")
        return [Topic(**r) for r in cur.fetchall()]
