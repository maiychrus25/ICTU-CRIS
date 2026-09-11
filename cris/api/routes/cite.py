# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Trích dẫn công trình (K1): `GET /api/works/{id}/citation?style=apa|ieee|bibtex`.
Định dạng thật ở `cris.cite`; route chỉ nạp `work`/tác giả và chọn kiểu trả về."""
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from cris import cite
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
