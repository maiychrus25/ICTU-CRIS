# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""`GET /api/feed.xml` (K1): RSS 2.0, 20 công trình mới nhất theo
`source_record.first_seen_at` của bản ghi nguồn hiện hành — công khai,
không cần đăng nhập."""
import os
from email.utils import format_datetime
from xml.sax.saxutils import escape

from fastapi import APIRouter, Response

from cris.api.deps import Conn

router = APIRouter(prefix="/api", tags=["rss"])

FEED_TITLE = "ICTU-CRIS — Công trình mới"
FEED_DESC = "Công trình khoa học mới cập nhật từ ICTU-CRIS."
LIMIT = 20


@router.get("/feed.xml")
def feed_xml(conn: Conn):
    base = (os.environ.get("CRIS_PUBLIC_URL") or "").rstrip("/")
    channel_link = base or "/"
    with conn.cursor() as cur:
        cur.execute(
            "SELECT w.id, w.title, w.abstract, sr.first_seen_at "
            "FROM work w JOIN source_record sr ON sr.id = w.primary_source_record_id "
            "WHERE w.merged_into_id IS NULL "
            "ORDER BY sr.first_seen_at DESC, w.id DESC LIMIT %s", (LIMIT,))
        rows = cur.fetchall()
    items = []
    for r in rows:
        link = f"{base}/cong-trinh/?id={r['id']}"
        desc = (r["abstract"] or "")[:300]
        items.append(
            "<item>"
            f"<title>{escape(r['title'] or '')}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="false">cris-work-{r["id"]}</guid>'
            f"<description>{escape(desc)}</description>"
            f"<pubDate>{format_datetime(r['first_seen_at'])}</pubDate>"
            "</item>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        f"<title>{escape(FEED_TITLE)}</title>"
        f"<link>{escape(channel_link)}</link>"
        f"<description>{escape(FEED_DESC)}</description>"
        + "".join(items) +
        "</channel></rss>")
    return Response(content=xml, media_type="application/rss+xml; charset=utf-8")
