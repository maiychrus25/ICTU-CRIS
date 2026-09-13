# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Trích dẫn công trình (K1): `GET /api/works/{id}/citation?style=apa|ieee|bibtex`;
trích dẫn toàn bộ công bố của một giảng viên (lát cắt N): `GET
/api/persons/{id}/citations?style=apa|ieee|bibtex`. Định dạng thật ở
`cris.cite`; route chỉ nạp `work`/tác giả và chọn kiểu trả về."""
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from cris import cite
from cris import rules as RU
from cris.api.deps import Conn

router = APIRouter(prefix="/api", tags=["trich-dan"])

_RENDER = {"apa": cite.apa, "ieee": cite.ieee, "bibtex": cite.bibtex}
_MEDIA = {"apa": "text/plain; charset=utf-8", "ieee": "text/plain; charset=utf-8",
          "bibtex": "application/x-bibtex"}
_EXT = {"apa": "txt", "ieee": "txt", "bibtex": "bib"}


@router.get("/works/{wid}/citation")
def work_citation(conn: Conn, wid: int, style: Literal["apa", "ieee", "bibtex"] = "apa",
                  download: int = Query(0, ge=0, le=1)):
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, doc_type, year_issue, journal, volume, doi FROM v_work_current WHERE id = %s",
                    (wid,))
        w = cur.fetchone()
        if w is None:
            raise HTTPException(404, f"không tìm thấy công trình #{wid}")
    authors = cite.authors_of(conn, wid)
    text = _RENDER[style](w, authors)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="cris-{wid}.{_EXT[style]}"'
    return PlainTextResponse(text, media_type=_MEDIA[style], headers=headers)


def _slug(name):
    """Tên hiển thị → phần tên tệp không dấu, không khoảng trắng (`"Phùng Trung
    Nghĩa"` → `"phung-trung-nghia"`); rỗng → `"giang-vien"`."""
    ascii_name = RU.strip_accents(name or "").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    return slug or "giang-vien"


_BIBTEX_KEY_RE = re.compile(r"^(@\w+\{)([^,]+)(,.*)$", re.S)


def _dedupe_bibtex_key(entry, seen):
    """Đổi khoá của một mục BibTeX nếu đã xuất hiện trước đó trong cùng tệp —
    thêm hậu tố a/b/c… (mục đầu tiên giữ nguyên khoá, không cắt bảng chữ cái
    khi vượt quá 26 lần trùng — dùng số thay hậu tố chữ)."""
    m = _BIBTEX_KEY_RE.match(entry)
    if not m:
        return entry
    prefix, key, rest = m.groups()
    n = seen.get(key, 0)
    seen[key] = n + 1
    if n == 0:
        return entry
    suffix = chr(ord("a") + n - 1) if n <= 26 else str(n)
    return f"{prefix}{key}{suffix}{rest}"


@router.get("/persons/{pid}/citations")
def person_citations(conn: Conn, pid: int, style: Literal["apa", "ieee", "bibtex"] = "apa"):
    """Trích dẫn mọi công trình đã liên kết còn sống (`DaNoiTuDong`/`DaXacNhan`)
    của một giảng viên, sắp theo năm giảm dần, mỗi mục cách nhau một dòng
    trống. BibTeX: khoá không trùng trong tệp (hậu tố a/b… nếu trùng)."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, display_name FROM person WHERE id = %s", (pid,))
        p = cur.fetchone()
        if p is None:
            raise HTTPException(404, f"không tìm thấy giảng viên #{pid}")
        cur.execute(
            """SELECT w.id, w.title, w.doc_type, w.year_issue, w.journal, w.volume, w.doi
               FROM v_person_publications vp JOIN v_work_current w ON w.id = vp.work_id
               WHERE vp.person_id = %s AND vp.state IN ('DaNoiTuDong','DaXacNhan')
               ORDER BY w.year_issue DESC NULLS LAST, w.id DESC""",
            (pid,))
        works = cur.fetchall()
    seen_keys: dict[str, int] = {}
    entries = []
    for w in works:
        authors = cite.authors_of(conn, w["id"])
        entry = _RENDER[style](w, authors)
        if style == "bibtex":
            entry = _dedupe_bibtex_key(entry, seen_keys)
        entries.append(entry)
    body = "\n\n".join(entries)
    filename = f"{_slug(p['display_name'])}.{_EXT[style]}"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return PlainTextResponse(body, media_type=_MEDIA[style], headers=headers)
