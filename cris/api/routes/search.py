# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tra cứu công trình, chi tiết có xuất xứ từng trường, hồ sơ giảng viên, trục chủ đề.
SQL chuyển nguyên từ UI HTML cũ (đã gỡ, xem CHANGELOG)."""
import re
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from cris import edit as edit_mod
from cris import rules as RU
from cris.ai import search as ai_search
from cris.ai.provider import AIDisabled, get_provider
from cris.api.deps import Conn, require_role
from cris.api.schemas import (
    DOC_TYPE_LABELS,
    FacetUnit,
    FacetValue,
    FacetYear,
    FieldEditIn,
    FieldEditOut,
    FieldRow,
    LastSync,
    MentionRow,
    Page,
    PersonProfile,
    PersonPublication,
    Topic,
    TopicDetail,
    TopicKeyword,
    WorkDetail,
    WorkList,
    WorksFacetsOut,
    WorkSummary,
)

router = APIRouter(prefix="/api", tags=["tra-cuu"])
RdOfficer = Annotated[int, Depends(require_role("rd_officer"))]

PER_PAGE = 50
SEMANTIC_TOP_K = 200   # top-k lấy từ semantic_works trước khi giao với các bộ lọc khác
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


def _split_keywords(raw, limit=None):
    """`keywords_raw` ("AI, học máy; thị giác máy tính") → danh sách đã strip,
    bỏ rỗng, giữ thứ tự, không trùng; `limit` cắt bớt (chip ở `WorkSummary`)."""
    if not raw:
        return []
    out, seen = [], set()
    for part in re.split(r"[,;]", raw):
        kw = part.strip()
        if kw and kw not in seen:
            seen.add(kw)
            out.append(kw)
    return out[:limit] if limit else out


def _keyword_pattern(keyword):
    """Regex ranh giới `[,;]`/đầu-cuối chuỗi cho `~*` — "AI" không khớp "AIoT"."""
    return rf"(^|[,;])\s*{re.escape(keyword.strip())}\s*([,;]|$)"


def _works_query(q: str, doc_type: str, year: int | None, unit: str, topic: int | None,
                  pub_type: str = "", quartile: str = "", cohort: str = "", keyword: str = ""):
    """Dựng `from_sql`/`where_sql`/`params` cho bộ lọc công trình dùng chung giữa
    tra cứu (`list_works`) và xuất CSV (`routes/export.py`)."""
    from_sql = ("FROM v_work_current w "
                "LEFT JOIN author_mention m ON m.work_id = w.id AND m.position > 0 "
                "LEFT JOIN v_work_unit vu ON vu.work_id = w.id "
                "LEFT JOIN unit u ON u.id = vu.unit_id")
    where, params = [], []
    if q.strip():
        like = f"%{q.strip()}%"
        norm_like = f"%{RU.strip_accents(q.strip()).lower()}%"
        where.append("(w.title ILIKE %s OR m.raw_name ILIKE %s OR w.title_norm ILIKE %s)")
        params += [like, like, norm_like]
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
    if pub_type:
        where.append("%s = ANY(w.indexes)"); params.append(pub_type)
    if quartile:
        where.append("w.quartile = %s"); params.append(quartile)
    if cohort:
        where.append("w.cohort = %s"); params.append(cohort)
    if keyword.strip():
        where.append("w.keywords_raw ~* %s"); params.append(_keyword_pattern(keyword))
    where_sql = " AND ".join(where) if where else "TRUE"
    return from_sql, where_sql, params


def _summary(r):
    return WorkSummary(id=r["id"], title=r["title"], doc_type=r["doc_type"],
                       doc_type_label=DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]),
                       year=r["year_issue"], doi=r["doi"], state=r["state"],
                       needs_review=bool(r["needs_review"]), score=r.get("score"),
                       keywords=_split_keywords(r.get("keywords_raw"), limit=6))


def _semantic_work_list(conn, q: str, doc_type: str, year, unit: str, topic, page: int,
                        pub_type: str = "", quartile: str = "", cohort: str = "", keyword: str = ""):
    """`mode=semantic`: top-k id từ `semantic_works` (embed `q`), giao với
    `_works_query` (giữ mọi bộ lọc trừ `q`, đã dùng để tìm theo nghĩa), sắp
    theo score giảm dần, phân trang. `None` nếu AI chưa bật — người gọi rơi
    về tra cứu từ khoá."""
    try:
        ranked = ai_search.semantic_works(conn, get_provider(), q, k=SEMANTIC_TOP_K,
                                          doc_types=[doc_type] if doc_type else None)
    except AIDisabled:
        return None
    if not ranked:
        return WorkList(items=[], page=Page(page=page, per_page=PER_PAGE, total=0),
                        mode="semantic", note=ai_search.NOTE)
    score_of = {wid: score for wid, score in ranked}
    from_sql, where_sql, params = _works_query("", doc_type, year, unit, topic,
                                               pub_type, quartile, cohort, keyword)
    ranked_ids = [wid for wid, _ in ranked]
    with conn.cursor() as cur:
        cur.execute(f"SELECT DISTINCT w.id {from_sql} WHERE {where_sql} AND w.id = ANY(%s)", params + [ranked_ids])
        keep = {r["id"] for r in cur.fetchall()}
    ordered = [wid for wid in ranked_ids if wid in keep]
    total = len(ordered)
    start = (page - 1) * PER_PAGE
    page_ids = ordered[start:start + PER_PAGE]
    items = []
    if page_ids:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, doc_type, year_issue, doi, state, needs_review, keywords_raw FROM work "
                        "WHERE id = ANY(%s)", (page_ids,))
            rows = {r["id"]: r for r in cur.fetchall()}
        for wid in page_ids:
            r = rows.get(wid)
            if r is None:
                continue
            r = dict(r, score=score_of.get(wid))
            items.append(_summary(r))
    return WorkList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total),
                    mode="semantic", note=ai_search.NOTE)


@router.get("/works", response_model=WorkList)
def list_works(conn: Conn, q: str = "", doc_type: str = "", year: int | None = None,
               unit: str = "", topic: int | None = None, mode: Literal["keyword", "semantic"] = "keyword",
               pub_type: str = "", quartile: str = "", cohort: str = "", keyword: str = "",
               page: int = Query(1, ge=1)):
    note = None
    if mode == "semantic" and q.strip():
        out = _semantic_work_list(conn, q, doc_type, year, unit, topic, page,
                                  pub_type, quartile, cohort, keyword)
        if out is not None:
            return out
        note = ai_search.DISABLED_NOTE   # AI tắt: rơi về từ khoá bên dưới, kèm giải thích
    from_sql, where_sql, params = _works_query(q, doc_type, year, unit, topic, pub_type, quartile, cohort, keyword)
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(DISTINCT w.id) AS n {from_sql} WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(f"SELECT DISTINCT w.id, w.title, w.doc_type, w.year_issue, w.doi, w.state, w.needs_review, "
                    f"w.keywords_raw {from_sql} WHERE {where_sql} ORDER BY w.year_issue DESC NULLS LAST, w.id DESC "
                    f"LIMIT %s OFFSET %s",
                    params + [PER_PAGE, (page - 1) * PER_PAGE])
        rows = cur.fetchall()
    items = [_summary(r) for r in rows]
    return WorkList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total), mode="keyword", note=note)


@router.get("/works/facets", response_model=WorksFacetsOut)
def works_facets(conn: Conn):
    """Đếm theo `indexes` (nhãn "pub_type" — chưa có bảng nhãn tiếng Việt
    trong `cris.rules`, giữ nguyên mã), `quartile`, `cohort`, năm và đơn vị
    trên công trình sống (`v_work_current`, chưa gộp)."""
    with conn.cursor() as cur:
        cur.execute("""SELECT idx AS value, count(*) AS n FROM v_work_current w,
                       LATERAL unnest(w.indexes) AS idx GROUP BY idx ORDER BY n DESC, idx""")
        pub_types = [FacetValue(value=r["value"], label=r["value"], n=r["n"]) for r in cur.fetchall()]
        cur.execute("""SELECT quartile AS value, count(*) AS n FROM v_work_current w
                       WHERE quartile IS NOT NULL GROUP BY quartile ORDER BY quartile""")
        quartiles = [FacetValue(value=r["value"], label=r["value"], n=r["n"]) for r in cur.fetchall()]
        cur.execute("""SELECT cohort AS value, count(*) AS n FROM v_work_current w
                       WHERE cohort IS NOT NULL GROUP BY cohort ORDER BY cohort DESC""")
        cohorts = [FacetValue(value=r["value"], label=r["value"], n=r["n"]) for r in cur.fetchall()]
        cur.execute("""SELECT year_issue AS value, count(*) AS n FROM v_work_current w
                       WHERE year_issue IS NOT NULL GROUP BY year_issue ORDER BY year_issue DESC""")
        years = [FacetYear(value=r["value"], n=r["n"]) for r in cur.fetchall()]
        cur.execute("""SELECT u.id AS value, u.code, u.name, count(DISTINCT vu.work_id) AS n
                       FROM v_work_unit vu JOIN unit u ON u.id = vu.unit_id
                       JOIN work w ON w.id = vu.work_id AND w.merged_into_id IS NULL
                       GROUP BY u.id, u.code, u.name ORDER BY n DESC, u.code""")
        units = [FacetUnit(value=r["value"], code=r["code"], name=r["name"], n=r["n"]) for r in cur.fetchall()]
    return WorksFacetsOut(pub_types=pub_types, quartiles=quartiles, cohorts=cohorts, years=years, units=units)


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
        cur.execute("SELECT raw FROM source_record WHERE id = %s", (w["primary_source_record_id"],))
        src = cur.fetchone()
    raw = (src["raw"] if src else {}) or {}
    det = raw.get("detail") or {}
    arc = raw.get("archive") or {}
    pdf_list = det.get("pdf") or []
    pdf_url = pdf_list[0] if pdf_list else None
    source_url = det.get("url") or arc.get("url")
    keywords = _split_keywords(w.get("keywords_raw"))
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
                      fields=fields, mentions=ms, pdf_url=pdf_url, source_url=source_url, keywords=keywords)


@router.patch("/works/{wid}/fields", response_model=FieldEditOut)
def edit_field(conn: Conn, actor: RdOfficer, wid: int, body: FieldEditIn):
    """Chỉnh tay một trường của công trình (H2, BR-23: chỉ các trường trong
    `cris.edit.EDITABLE` — không tác giả/đơn vị/minh chứng). 400 nếu trường
    không cho sửa, 404 nếu không có công trình, 409 cho lỗi nghiệp vụ (lý do
    trống, giá trị không hợp lệ, công trình đã gộp)."""
    if body.field not in edit_mod.EDITABLE:
        raise HTTPException(400, f"không cho phép chỉnh trường '{body.field}'; chỉ: "
                                  f"{', '.join(edit_mod.EDITABLE)}")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM work WHERE id=%s", (wid,))
        if cur.fetchone() is None:
            raise HTTPException(404, f"không tìm thấy công trình #{wid}")
    try:
        result = edit_mod.set_field(conn, wid, body.field, body.value, actor, body.reason)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return FieldEditOut(**result)


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
        pending_count=pending, last_sync=LastSync(**last) if last else None,
        rank=p.get("rank"), scholar_url=p.get("scholar_url"), citation_stats=None)


@router.get("/topics", response_model=list[Topic])
def topics(conn: Conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, label, size, built_at FROM ai_topic ORDER BY size DESC, label")
        rows = cur.fetchall()
        cur.execute("""SELECT topic_id, keyword FROM (
                          SELECT topic_id, keyword,
                                 row_number() OVER (PARTITION BY topic_id ORDER BY weight DESC, keyword) AS rn
                          FROM ai_topic_keyword) t
                       WHERE rn <= 8 ORDER BY topic_id, rn""")
        kw_rows = cur.fetchall()
    kw_by_topic: dict[int, list[str]] = {}
    for r in kw_rows:
        kw_by_topic.setdefault(r["topic_id"], []).append(r["keyword"])
    return [Topic(id=r["id"], label=r["label"], size=r["size"], built_at=r["built_at"],
                  keywords=kw_by_topic.get(r["id"], [])) for r in rows]


@router.get("/topics/{tid}", response_model=TopicDetail)
def topic_detail(conn: Conn, tid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT id, label, size FROM ai_topic WHERE id = %s", (tid,))
        t = cur.fetchone()
        if t is None:
            raise HTTPException(404, f"không tìm thấy chủ đề #{tid}")
        cur.execute("SELECT keyword, weight FROM ai_topic_keyword WHERE topic_id = %s ORDER BY weight DESC, keyword",
                    (tid,))
        kws = cur.fetchall()
        from_sql, where_sql, params = _works_query("", "", None, "", tid)
        cur.execute(f"SELECT DISTINCT w.id, w.title, w.doc_type, w.year_issue, w.doi, w.state, w.needs_review, "
                    f"w.keywords_raw {from_sql} WHERE {where_sql} ORDER BY w.year_issue DESC NULLS LAST, w.id DESC LIMIT 50",
                    params)
        works = cur.fetchall()
    items = [_summary(r) for r in works]
    return TopicDetail(id=t["id"], label=t["label"], size=t["size"],
                       keywords=[TopicKeyword(keyword=r["keyword"], weight=r["weight"]) for r in kws],
                       works=items)
