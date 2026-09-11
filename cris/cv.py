# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Lý lịch khoa học giảng viên (K1): trang HTML tự chứa (CSS in nhúng, A4,
in được), không dùng khuôn mẫu ngoài — ghép chuỗi trực tiếp, mọi giá trị
người dùng qua `html.escape`. Tái dùng `cris.cite.apa`/`authors_of` cho từng
công trình để trùng đúng dạng trích dẫn hiện ở nơi khác."""
import html
from datetime import UTC, datetime

from cris import cite

DOC_TYPE_LABELS = {
    "bai_bao": "Bài báo", "do_an": "Đồ án tốt nghiệp", "luan_van": "Luận văn thạc sĩ",
    "luan_an": "Luận án tiến sĩ", "hoc_lieu": "Học liệu",
}
DOC_TYPE_ORDER = ["bai_bao", "luan_an", "luan_van", "do_an", "hoc_lieu"]

STYLE = """
* { box-sizing: border-box; }
body { font-family: "Times New Roman", Georgia, serif; color: #111; margin: 2cm;
       font-size: 13px; line-height: 1.5; }
h1 { font-size: 20px; margin: 0 0 6px; }
h2 { font-size: 15px; border-bottom: 1px solid #999; padding-bottom: 2px; margin-top: 24px; }
.meta { margin: 2px 0; }
table { border-collapse: collapse; margin: 8px 0 16px; }
td, th { border: 1px solid #999; padding: 4px 8px; text-align: left; font-size: 12px; }
.pub { margin: 6px 0 6px 1.2em; text-indent: -1.2em; }
footer { margin-top: 32px; font-size: 11px; color: #666; border-top: 1px solid #ccc; padding-top: 6px; }
@media print { body { margin: 1.5cm; } }
@page { size: A4; margin: 2cm; }
"""


def _e(s):
    return html.escape(str(s)) if s is not None else ""


def _rank_degree(person):
    parts = [p for p in (person.get("rank"), person.get("degree_raw")) if p]
    return ".".join(parts) if parts else None


def render(conn, pid):
    """HTML lý lịch khoa học của giảng viên `pid`; `None` nếu không có giảng viên."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.*, u.code AS unit_code, u.name AS unit_name FROM person p "
            "LEFT JOIN unit u ON u.id = p.unit_id WHERE p.id = %s", (pid,))
        p = cur.fetchone()
        if p is None:
            return None
        cur.execute(
            "SELECT w.id, w.title, w.doc_type, w.year_issue, w.doi, w.journal, w.volume "
            "FROM v_person_publications vp JOIN work w ON w.id = vp.work_id "
            "WHERE vp.person_id = %s ORDER BY w.doc_type, w.year_issue DESC NULLS LAST, w.id DESC",
            (pid,))
        pubs = cur.fetchall()

    by_type, by_year, grouped = {}, {}, {}
    for w in pubs:
        by_type[w["doc_type"]] = by_type.get(w["doc_type"], 0) + 1
        y = str(w["year_issue"]) if w["year_issue"] is not None else "không rõ"
        by_year[y] = by_year.get(y, 0) + 1
        grouped.setdefault(w["doc_type"], []).append(w)

    rank_degree = _rank_degree(p)
    display = f"{rank_degree}. {p['display_name']}" if rank_degree else p["display_name"]
    header = [f"<h1>{_e(display)}</h1>"]
    if p.get("unit_name"):
        header.append(f'<div class="meta">Đơn vị: {_e(p["unit_name"])}</div>')
    if p.get("email"):
        header.append(f'<div class="meta">Email: {_e(p["email"])}</div>')
    if p.get("orcid"):
        orcid_url = f"https://orcid.org/{p['orcid']}"
        header.append(f'<div class="meta">ORCID: <a href="{_e(orcid_url)}">{_e(orcid_url)}</a></div>')
    if p.get("scholar_url"):
        header.append(f'<div class="meta">Google Scholar: <a href="{_e(p["scholar_url"])}">{_e(p["scholar_url"])}</a></div>')

    stats = ["<h2>Số liệu công bố</h2>", "<table><tr><th>Loại</th><th>Số lượng</th></tr>"]
    for dt in DOC_TYPE_ORDER:
        if dt in by_type:
            stats.append(f"<tr><td>{_e(DOC_TYPE_LABELS.get(dt, dt))}</td><td>{by_type[dt]}</td></tr>")
    stats.append("</table>")
    stats.append("<table><tr><th>Năm</th><th>Số lượng</th></tr>")
    for y, n in sorted(by_year.items(), key=lambda kv: kv[0], reverse=True):
        stats.append(f"<tr><td>{_e(y)}</td><td>{n}</td></tr>")
    stats.append("</table>")

    pub_sections = []
    for dt in DOC_TYPE_ORDER:
        works = grouped.get(dt)
        if not works:
            continue
        pub_sections.append(f"<h2>{_e(DOC_TYPE_LABELS.get(dt, dt))}</h2>")
        for w in works:
            authors = cite.authors_of(conn, w["id"])
            text = _e(cite.apa(w, authors))
            if w.get("doi"):
                doi_url = f"https://doi.org/{w['doi']}"
                text = text.replace(_e(doi_url), f'<a href="{_e(doi_url)}">{_e(doi_url)}</a>')
            pub_sections.append(f'<div class="pub">{text}</div>')

    today = datetime.now(UTC).strftime("%d/%m/%Y")
    footer = (f'<footer>Sinh từ ICTU-CRIS {today} — dữ liệu từ repository.ictu.edu.vn, '
              f'đã đối soát.</footer>')

    return (
        "<!doctype html><html lang=\"vi\"><head><meta charset=\"utf-8\">"
        f"<title>Lý lịch khoa học — {_e(p['display_name'])}</title>"
        f"<style>{STYLE}</style></head><body>"
        f"{''.join(header)}{''.join(stats)}{''.join(pub_sections)}{footer}"
        "</body></html>")
