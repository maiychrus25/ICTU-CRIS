# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Trích dẫn công trình (K1): APA 7, IEEE, BibTeX từ metadata đã chuẩn hoá
(`work`) và tác giả từ `author_mention` (vai `author` cho bài báo/học liệu;
vai `student`+`mentor` cho đồ án/luận văn/luận án — GVHD không phải đồng tác
giả nhưng vẫn cần xuất hiện trong trích dẫn).

Tên người Việt không đảo "Họ, Tên" như quy ước phương Tây — giữ nguyên thứ tự
đã ghi ở nguồn cho cả ba kiểu, đây là lựa chọn có chủ đích cho một hệ thống
tiếng Việt (không phải lệch chuẩn APA/IEEE gốc)."""
import re

from cris import rules as RU

INSTITUTION = "Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên"
THESIS_LABELS = {
    "do_an": "Đồ án tốt nghiệp",
    "luan_van": "Luận văn thạc sĩ",
    "luan_an": "Luận án tiến sĩ",
}
_ROLE_ORDER = {"author": 0, "student": 1, "mentor": 2}


def authors_of(conn, work_id):
    """Mention vai `author`/`student`/`mentor` của công trình, theo `position`
    trong từng vai (sinh viên trước, GVHD sau — mỗi vai có dãy `position`
    riêng nên không thể ORDER BY position chung mà không phân biệt vai)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT role, position, raw_name FROM author_mention "
            "WHERE work_id = %s AND position > 0 AND role IN ('author','student','mentor') "
            "ORDER BY role, position",
            (work_id,))
        rows = cur.fetchall()
    return sorted(rows, key=lambda r: (_ROLE_ORDER.get(r["role"], 9), r["position"]))


def _year(work):
    y = work.get("year_issue")
    return str(y) if y else "n.d."


def _author_names(authors, doc_type):
    """`(tác_giả_chính, người_hướng_dẫn)` — đồ án/luận văn/luận án: sinh viên
    là tác giả chính, GVHD tách riêng; còn lại: vai `author`."""
    if doc_type in THESIS_LABELS:
        students = [a["raw_name"] for a in authors if a["role"] == "student"]
        mentors = [a["raw_name"] for a in authors if a["role"] == "mentor"]
        return students, mentors
    return [a["raw_name"] for a in authors if a["role"] == "author"], []


def _join_names(names, sep_word):
    """Nối tên: 1 tên giữ nguyên, 2 tên `"A {sep_word} B"`, 3+ tên
    `"A, B, {sep_word} C"` (APA 7/IEEE: có dấu phẩy trước từ nối chỉ khi ≥ 3)."""
    names = [n for n in (names or []) if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} {sep_word} {names[1]}"
    return ", ".join(names[:-1]) + f", {sep_word} " + names[-1]


def apa(work, authors):
    """APA 7: `Tác giả (Năm). Tiêu đề. Tạp chí, Tập/số. https://doi.org/…`;
    đồ án/luận văn/luận án: `Sinh viên (Năm). Tiêu đề [Loại]. Trường… Người
    hướng dẫn: GVHD.`"""
    doc_type = work.get("doc_type")
    year = _year(work)
    title = (work.get("title") or "").strip() or "(không có tiêu đề)"
    names, mentors = _author_names(authors, doc_type)
    author_str = _join_names(names, "&") or "Khuyết danh"
    if doc_type in THESIS_LABELS:
        out = f"{author_str} ({year}). {title} [{THESIS_LABELS[doc_type]}]. {INSTITUTION}."
        if mentors:
            out += f" Người hướng dẫn: {_join_names(mentors, '&')}."
    else:
        out = f"{author_str} ({year}). {title}."
        if work.get("journal"):
            out += f" {work['journal']}"
            if work.get("volume"):
                out += f", {work['volume']}"
            out += "."
    if work.get("doi"):
        out += f" https://doi.org/{work['doi']}"
    return out


def ieee(work, authors):
    """IEEE: `Tác giả, "Tiêu đề," Tạp chí, vol. Tập/số, Năm. doi: …`; đồ án:
    `Sinh viên, "Tiêu đề," Loại, Trường…, Năm.`"""
    doc_type = work.get("doc_type")
    year = _year(work)
    title = (work.get("title") or "").strip() or "(không có tiêu đề)"
    names, mentors = _author_names(authors, doc_type)
    author_str = _join_names(names, "and") or "Khuyết danh"
    if doc_type in THESIS_LABELS:
        out = f'{author_str}, "{title}," {THESIS_LABELS[doc_type]}, {INSTITUTION}, {year}.'
        if mentors:
            out += f" Người hướng dẫn: {_join_names(mentors, 'and')}."
    else:
        out = f'{author_str}, "{title},"'
        if work.get("journal"):
            out += f" {work['journal']}"
            if work.get("volume"):
                out += f", vol. {work['volume']}"
            out += ","
        out += f" {year}."
    if work.get("doi"):
        out += f" doi: {work['doi']}."
    return out


def _bibtex_escape(s):
    s = str(s or "")
    s = s.replace("\\", r"\\")
    s = s.replace("{", r"\{").replace("}", r"\}")
    return s


def _ascii_word(s):
    return re.sub(r"[^A-Za-z0-9]", "", RU.strip_accents(s or ""))


def _bibtex_key(work, authors):
    doc_type = work.get("doc_type")
    names, _mentors = _author_names(authors, doc_type)
    first_author = names[0] if names else ""
    surname = _ascii_word(first_author.split()[0]) if first_author.split() else ""
    y = work.get("year_issue")
    year_part = str(y) if y else "nd"
    title_word = ""
    for w in (work.get("title") or "").split():
        title_word = _ascii_word(w)
        if title_word:
            break
    return f"{surname or 'Khuyetdanh'}{year_part}{title_word or 'KhongTieuDe'}"


def bibtex(work, authors):
    """BibTeX; khoá = họ tác giả đầu không dấu + năm + từ đầu tiêu đề; `{`/`}`
    trong nội dung được escape để không phá cú pháp."""
    doc_type = work.get("doc_type")
    names, mentors = _author_names(authors, doc_type)
    author_field = " and ".join(_bibtex_escape(n) for n in names) or "Khuyết danh"
    title = _bibtex_escape((work.get("title") or "").strip() or "(không có tiêu đề)")
    year = _year(work)
    key = _bibtex_key(work, authors)
    if doc_type == "luan_van":
        entry_type = "mastersthesis"
    elif doc_type == "luan_an":
        entry_type = "phdthesis"
    elif doc_type == "do_an":
        entry_type = "misc"
    else:
        entry_type = "article"
    fields = [("author", author_field), ("title", f"{{{title}}}"), ("year", year)]
    if doc_type in THESIS_LABELS:
        fields.append(("school", _bibtex_escape(INSTITUTION)))
        fields.append(("type", _bibtex_escape(THESIS_LABELS[doc_type])))
        if mentors:
            fields.append(("note", _bibtex_escape("Người hướng dẫn: " + _join_names(mentors, "và"))))
    else:
        if work.get("journal"):
            fields.append(("journal", _bibtex_escape(work["journal"])))
        if work.get("volume"):
            fields.append(("volume", _bibtex_escape(work["volume"])))
    if work.get("doi"):
        fields.append(("doi", work["doi"]))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields)
    return f"@{entry_type}{{{key},\n{body}\n}}"
