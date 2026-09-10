# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đối chiếu đề tài (FR-AI-03/04): gọi `cris.ai.compare.compare_topic`, lưu và đọc lại `ai_query`."""
from fastapi import APIRouter, HTTPException

from cris.ai.compare import compare_topic
from cris.ai.provider import get_provider
from cris.api.deps import Actor, Conn
from cris.api.schemas import CompareIn, CompareOut, CompareResultItem

router = APIRouter(prefix="/api", tags=["doi-chieu"])

NOTE = "So trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn. Đây là tài liệu tham khảo cho giảng viên xem xét, không phải kết luận."


def _out(query_id, provider, fallback, results, input_, created_at=None):
    return CompareOut(query_id=query_id, provider=provider, fallback=fallback, note=NOTE, input=input_,
                      results=[CompareResultItem(**{k: r.get(k) for k in CompareResultItem.model_fields if k in r})
                               for r in results], created_at=created_at)


@router.post("/compare", response_model=CompareOut)
def compare(conn: Conn, actor: Actor, body: CompareIn):
    aspects = {k: v.strip() for k, v in body.aspects.items() if v and v.strip()}
    r = compare_topic(conn, get_provider(), title=body.title, description=body.description, aspects=aspects,
                      k=body.k, doc_types=body.doc_types or None, actor_id=actor)
    input_ = {"title": body.title, "description": body.description, "aspects": aspects, "doc_types": body.doc_types}
    return _out(r["query_id"], r["provider"], bool(r.get("fallback")), r["results"], input_)


@router.get("/compare/{qid}", response_model=CompareOut)
def compare_result(conn: Conn, qid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT id, input, results, provider, created_at FROM ai_query WHERE id=%s", (qid,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, f"không tìm thấy lượt đối chiếu #{qid}")
    res = row["results"]
    items = res.get("results", res) if isinstance(res, dict) else res
    fallback = bool(res.get("fallback")) if isinstance(res, dict) else row["provider"] == "none"
    return _out(row["id"], row["provider"], fallback, items, row["input"], row["created_at"])
