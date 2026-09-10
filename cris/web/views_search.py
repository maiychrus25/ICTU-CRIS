# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tra cứu công trình, chi tiết công trình, hồ sơ công bố giảng viên (SC-10..SC-12).

Chỉ đọc dữ liệu qua các view đã có (`v_work_current`, `v_work_unit`,
`v_person_publications`) — không viết lại logic đã nằm trong `cris/link.py`,
`cris/dedup.py`, `cris/normalize.py`.
"""
from urllib.parse import urlencode

from cris.web.render import badge, e, layout, pager, table
from cris.web.wsgi import Redirect, route

PER_PAGE = 50

DOC_TYPE_LABELS = {
    "bai_bao": "Bài báo",
    "do_an": "Đồ án",
    "luan_van": "Luận văn",
    "luan_an": "Luận án",
    "hoc_lieu": "Học liệu",
    "giang_vien": "Giảng viên",
    "dang_ky_do_an": "Đăng ký đồ án",
}

# Nhãn hiển thị cho các trường có ghi provenance trong `cris/normalize.py` (FIELDS),
# bỏ "title_norm" — đó là giá trị chuẩn hoá nội bộ để so khớp, không phải một
# trường nghiệp vụ hiển thị cho người dùng.
FIELD_LABELS = [
    ("title", "Tiêu đề"),
    ("doi", "DOI"),
    ("journal", "Tạp chí"),
    ("volume", "Tập/số"),
    ("year_issue", "Năm"),
    ("abstract", "Tóm tắt"),
    ("keywords_raw", "Từ khoá"),
    ("pub_type_raw", "Loại xuất bản (thô)"),
    ("indexes", "Chỉ mục (Scopus/ISI/...)"),
    ("quartile", "Quartile"),
    ("venue_kind", "Loại nơi công bố"),
    ("score", "Điểm quy đổi"),
    ("needs_review", "Cần rà soát"),
    ("cohort", "Khoá/đợt"),
]

ROLE_LABELS = {"author": "Tác giả", "mentor": "Người hướng dẫn", "student": "Sinh viên thực hiện"}

LINK_STATE_LABELS = {
    "DaNoiTuDong": "Đã nối tự động",
    "DaXacNhan": "Đã xác nhận",
}


def _page_num(raw):
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return 1
    return n if n > 0 else 1


def _not_found(what):
    body = f'<p class="error-page">Không tìm thấy {e(what)}.</p>'
    return (404, [], layout("Không tìm thấy", body))


def _fmt_dt(v):
    if v is None:
        return None
    try:
        return v.strftime("%d/%m/%Y %H:%M")
    except AttributeError:
        return str(v)


def _fmt_value(val):
    if val is None:
        return None
    if isinstance(val, bool):
        return "Có" if val else "Không"
    if isinstance(val, list):
        return ", ".join(str(x) for x in val) if val else None
    return str(val)


@route("GET", "/")
def home(req):
    return Redirect("/tra-cuu")


@route("GET", "/tra-cuu")
def search_works(req):
    q_param = (req.query.get("q") or "").strip()
    doc_type = (req.query.get("doc_type") or "").strip()
    year_raw = (req.query.get("year") or "").strip()
    unit = (req.query.get("unit") or "").strip()
    page = _page_num(req.query.get("page"))
    year = int(year_raw) if year_raw.isdigit() else None

    from_sql = (
        "FROM v_work_current w "
        "LEFT JOIN author_mention m ON m.work_id = w.id AND m.position > 0 "
        "LEFT JOIN v_work_unit vu ON vu.work_id = w.id "
        "LEFT JOIN unit u ON u.id = vu.unit_id"
    )
    where, params = [], []
    if q_param:
        where.append("(w.title ILIKE %s OR m.raw_name ILIKE %s)")
        like = f"%{q_param}%"
        params += [like, like]
    if doc_type:
        where.append("w.doc_type = %s")
        params.append(doc_type)
    if year is not None:
        where.append("w.year_issue = %s")
        params.append(year)
    if unit:
        if unit.isdigit():
            where.append("vu.unit_id = %s")
            params.append(int(unit))
        else:
            where.append("u.code = %s")
            params.append(unit)
    where_sql = " AND ".join(where) if where else "TRUE"

    with req.conn.cursor() as cur:
        cur.execute(f"SELECT count(DISTINCT w.id) AS n {from_sql} WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(
            f"SELECT DISTINCT w.id, w.title, w.doc_type, w.year_issue, w.doi, w.state, w.needs_review "
            f"{from_sql} WHERE {where_sql} "
            "ORDER BY w.year_issue DESC NULLS LAST, w.id DESC LIMIT %s OFFSET %s",
            params + [PER_PAGE, (page - 1) * PER_PAGE],
        )
        rows = cur.fetchall()

    filters = {}
    if q_param:
        filters["q"] = q_param
    if doc_type:
        filters["doc_type"] = doc_type
    if year_raw:
        filters["year"] = year_raw
    if unit:
        filters["unit"] = unit
    base_url = "/tra-cuu?" + urlencode(filters) if filters else "/tra-cuu"

    opts = "".join(
        f'<option value="{e(k)}"{" selected" if doc_type == k else ""}>{e(v)}</option>'
        for k, v in DOC_TYPE_LABELS.items()
    )
    form = f"""
    <form method="get" action="/tra-cuu" class="search-form">
      <label>Từ khoá (tiêu đề hoặc tên tác giả)
        <input type="text" name="q" value="{e(q_param)}">
      </label>
      <label>Loại công trình
        <select name="doc_type"><option value="">Tất cả</option>{opts}</select>
      </label>
      <label>Năm <input type="text" name="year" value="{e(year_raw)}"></label>
      <label>Đơn vị (mã) <input type="text" name="unit" value="{e(unit)}"></label>
      <button type="submit">Tìm</button>
    </form>
    """

    table_rows = []
    for r in rows:
        title_link = f'<a href="/tra-cuu/cong-trinh/{r["id"]}">{e(r["title"])}</a>'
        doc_type_label = e(DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]))
        state_badge = badge(r["state"], "warn" if r["needs_review"] else "default")
        table_rows.append([title_link, doc_type_label, e(r["year_issue"]), e(r["doi"]), state_badge])

    body = form + table(["Tiêu đề", "Loại", "Năm", "DOI", "Trạng thái"], table_rows)
    body += pager(page, total, PER_PAGE, base_url)
    body += f'<p class="result-count">Tìm thấy {e(total)} công trình.</p>'
    return layout("Tra cứu công trình", body, active="/tra-cuu")


@route("GET", "/tra-cuu/cong-trinh/<int:wid>")
def work_detail(req, wid):
    with req.conn.cursor() as cur:
        cur.execute("SELECT * FROM v_work_current WHERE id = %s", (wid,))
        w = cur.fetchone()
        if w is None:
            return _not_found("công trình")

        cur.execute(
            """SELECT DISTINCT ON (fp.field) fp.field, fp.raw_value, fp.value, fp.set_kind, fp.set_at,
                      sr.source AS src_source, sr.source_key AS src_key,
                      au.display_name AS set_by_name
               FROM field_provenance fp
               LEFT JOIN source_record sr ON sr.id = fp.source_record_id
               LEFT JOIN app_user au ON au.id = fp.set_by
               WHERE fp.work_id = %s
               ORDER BY fp.field, fp.set_at DESC""",
            (wid,),
        )
        prov_by_field = {r["field"]: r for r in cur.fetchall()}

        cur.execute(
            """SELECT m.id AS mention_id, m.role, m.position, m.raw_name, m.is_placeholder, m.is_truncated,
                      l.person_id AS linked_person_id, l.state AS link_state, p.display_name AS linked_person_name,
                      (SELECT count(*) FROM author_link l2 WHERE l2.mention_id = m.id AND l2.state = 'ChoXacNhan') AS pending_count
               FROM author_mention m
               LEFT JOIN author_link l ON l.mention_id = m.id AND l.state IN ('DaNoiTuDong','DaXacNhan')
               LEFT JOIN person p ON p.id = l.person_id
               WHERE m.work_id = %s AND m.position > 0
               ORDER BY m.role, m.position""",
            (wid,),
        )
        mentions = cur.fetchall()

    field_rows = []
    for field, label in FIELD_LABELS:
        current = _fmt_value(w.get(field))
        prov = prov_by_field.get(field)
        if prov is None:
            raw = None
            source = "Chưa ghi nhận nguồn"
        else:
            raw = prov["raw_value"]
            if prov["set_kind"] in ("manual", "merge"):
                who = prov["set_by_name"] or "không rõ người"
                action = "Chỉnh tay" if prov["set_kind"] == "manual" else "Gộp bản ghi trùng"
                source = f"{action} bởi {who}, lúc {_fmt_dt(prov['set_at']) or ''}"
            else:
                if prov["src_source"]:
                    source = f"Đồng bộ từ {prov['src_source']} (khoá {prov['src_key']}), lúc {_fmt_dt(prov['set_at']) or ''}"
                else:
                    source = f"Chuẩn hoá tự động, lúc {_fmt_dt(prov['set_at']) or ''}"
        field_rows.append([
            e(label),
            e(current) if current is not None else '<span class="muted">—</span>',
            e(raw) if raw is not None else '<span class="muted">—</span>',
            e(source),
        ])

    author_rows = []
    for m in mentions:
        role_label = e(ROLE_LABELS.get(m["role"], m["role"]))
        raw_name = e(m["raw_name"])
        if m["is_placeholder"]:
            raw_name += " " + badge("giữ chỗ", "warn")
        if m["is_truncated"]:
            raw_name += " " + badge("tên bị cắt", "warn")
        if m["linked_person_id"] is not None:
            status = badge(LINK_STATE_LABELS.get(m["link_state"], m["link_state"]), "ok")
            person_cell = f'<a href="/tra-cuu/giang-vien/{m["linked_person_id"]}">{e(m["linked_person_name"])}</a>'
        elif m["pending_count"]:
            status = badge(f"Chờ xác nhận ({m['pending_count']} ứng viên)", "warn")
            person_cell = '<span class="muted">chưa chọn</span>'
        else:
            status = badge("Chưa liên kết", "default")
            person_cell = '<span class="muted">—</span>'
        author_rows.append([role_label, raw_name, person_cell, status])

    doc_type_label = e(DOC_TYPE_LABELS.get(w["doc_type"], w["doc_type"]))
    state_badge = badge(w["state"], "warn" if w["needs_review"] else "default")
    header = (
        f'<p class="work-meta">{doc_type_label} &middot; {state_badge}'
        f'{" &middot; " + badge("có chỉnh tay/gộp thủ công", "warn") if w["has_manual"] else ""}</p>'
    )

    body = (
        header
        + "<h2>Từng trường: giá trị đang dùng, giá trị gốc và nguồn</h2>"
        + table(["Trường", "Giá trị đang dùng", "Giá trị gốc", "Nguồn"], field_rows)
        + "<h2>Tác giả / người liên quan và trạng thái liên kết</h2>"
        + table(["Vai trò", "Tên thô", "Người đã liên kết", "Trạng thái"], author_rows)
    )
    return layout(w["title"], body, active="/tra-cuu")


@route("GET", "/tra-cuu/giang-vien/<int:pid>")
def person_profile(req, pid):
    with req.conn.cursor() as cur:
        cur.execute("SELECT * FROM person WHERE id = %s", (pid,))
        p = cur.fetchone()
        if p is None:
            return _not_found("giảng viên")

        cur.execute(
            """SELECT vp.work_id, vp.state, vp.confidence, w.title, w.doc_type, w.year_issue, w.doi
               FROM v_person_publications vp
               JOIN work w ON w.id = vp.work_id
               WHERE vp.person_id = %s
               ORDER BY w.year_issue DESC NULLS LAST, w.id DESC""",
            (pid,),
        )
        pubs = cur.fetchall()

        cur.execute(
            """SELECT count(DISTINCT m.work_id) AS n
               FROM author_mention m JOIN author_link l ON l.mention_id = m.id
               WHERE l.person_id = %s AND l.state = 'ChoXacNhan'""",
            (pid,),
        )
        pending = cur.fetchone()["n"]

        cur.execute(
            "SELECT id, source, scope, status, started_at, finished_at FROM sync_run ORDER BY id DESC LIMIT 1"
        )
        last_sync = cur.fetchone()

    by_type = {}
    by_year = {}
    pub_rows = []
    for r in pubs:
        by_type[r["doc_type"]] = by_type.get(r["doc_type"], 0) + 1
        year_key = r["year_issue"] if r["year_issue"] is not None else "Không rõ năm"
        by_year[year_key] = by_year.get(year_key, 0) + 1
        title_link = f'<a href="/tra-cuu/cong-trinh/{r["work_id"]}">{e(r["title"])}</a>'
        doc_type_label = e(DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"]))
        state_label = LINK_STATE_LABELS.get(r["state"], r["state"])
        pub_rows.append([
            title_link, doc_type_label, e(r["year_issue"]), e(r["doi"]),
            badge(state_label, "ok" if r["state"] == "DaXacNhan" else "default"),
        ])

    type_rows = [[e(DOC_TYPE_LABELS.get(k, k)), e(v)] for k, v in sorted(by_type.items())]
    year_rows = [[e(k), e(v)] for k, v in sorted(by_year.items(), key=lambda kv: (kv[0] == "Không rõ năm", kv[0]))]

    if last_sync is None:
        sync_line = "<p><strong>Đồng bộ gần nhất:</strong> chưa có lần đồng bộ nào.</p>"
    else:
        when = _fmt_dt(last_sync["finished_at"]) or _fmt_dt(last_sync["started_at"]) or "đang chạy"
        sync_line = (
            f"<p><strong>Đồng bộ gần nhất:</strong> {e(when)} "
            f"(nguồn {e(last_sync['source'])}/{e(last_sync['scope'])}, {badge(last_sync['status'], 'ok' if last_sync['status'] == 'ok' else 'warn')})."
            " Danh sách công trình bên dưới dựa trên liên kết tác giả tại nguồn — hiện phủ chưa đầy đủ, "
            "xem cảnh báo bên dưới nếu còn công trình chưa xác nhận.</p>"
        )

    if pending:
        pending_line = (
            f'<p class="warn-line">Còn {e(pending)} công trình nghi thuộc người này '
            f'chưa được xác nhận. Xem <a href="/doi-soat/tac-gia">hàng đợi liên kết tác giả</a>.</p>'
        )
    else:
        pending_line = ""

    info = (
        f'<p><strong>{e(p["display_name"])}</strong>'
        f'{" &mdash; " + e(p["degree_raw"]) if p["degree_raw"] else ""}</p>'
        f'<p>Email: {e(p["email"]) if p["email"] else "—"} &middot; '
        f'ORCID: {e(p["orcid"]) if p["orcid"] else "—"}</p>'
    )

    body = (
        info
        + sync_line
        + pending_line
        + "<h2>Số công trình theo loại</h2>"
        + table(["Loại", "Số lượng"], type_rows)
        + "<h2>Phân bố theo năm</h2>"
        + table(["Năm", "Số lượng"], year_rows)
        + "<h2>Danh sách công trình</h2>"
        + table(["Tiêu đề", "Loại", "Năm", "DOI", "Trạng thái liên kết"], pub_rows)
    )
    return layout(f'Hồ sơ công bố — {p["display_name"]}', body, active="/tra-cuu")
