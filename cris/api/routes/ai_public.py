# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tìm chuyên gia (J1, `cris/ai/expert.py`) và cổng công khai kiểm tra đề tài
cho sinh viên (`cris/ai/search.py`, `cris/ai/expert.py`).

`POST /api/ai/experts` đòi đăng nhập khi `auth_required` (như mọi route dùng
`Actor`); lưu `ai_query(kind='experts')`. `GET /api/ai/experts/{id}` đọc lại,
không đòi actor (đọc một lượt đã lưu, giống `GET /api/compare/{qid}`).

`POST /api/public/check-topic` **không cần đăng nhập** — sinh viên trước khi
đăng ký đề tài. Rate-limit theo IP (bộ nhớ tiến trình, cùng cách
`cris/api/routes/auth.py` giới hạn đăng nhập sai — đủ cho một worker
`uvicorn`), **không lưu** `ai_query` (không có actor để gắn, và không nên giữ
lịch sử tra cứu của sinh viên nặc danh), và chỉ trả tối thiểu về giảng viên
(`person_id, display_name, degree, unit_code, score` — không email/điện
thoại, xem `ExpertResult` vs `CheckTopicExpert` trong `cris/api/schemas.py`)."""
import time

from fastapi import APIRouter, HTTPException, Request

from cris.ai import expert as ai_expert
from cris.ai.provider import AIDisabled, get_provider
from cris.ai.search import similar_topics
from cris.api.deps import Actor, Conn
from cris.api.schemas import (
    CheckTopicExpert,
    CheckTopicIn,
    CheckTopicOut,
    CheckTopicSimilar,
    ExpertEvidence,
    ExpertResult,
    ExpertsIn,
    ExpertsOut,
)

router = APIRouter(prefix="/api", tags=["ai-cong-khai"])

RATE_LIMIT_MAX = 20
RATE_LIMIT_WINDOW_S = 300

_hits: dict[str, list[float]] = {}


def _client_ip(request: Request) -> str:
    """IP của trình duyệt: `X-Forwarded-For` (đầu chuỗi, khi chạy sau proxy
    ngược) nếu có, ngược lại IP kết nối trực tiếp."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        first = fwd.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


def _rate_limited(ip: str) -> bool:
    now = time.monotonic()
    hits = [t for t in _hits.get(ip, []) if now - t < RATE_LIMIT_WINDOW_S]
    _hits[ip] = hits
    return len(hits) >= RATE_LIMIT_MAX


def _record_hit(ip: str) -> None:
    _hits.setdefault(ip, []).append(time.monotonic())


def _experts_out(query_id, provider, fallback, note, results) -> ExpertsOut:
    return ExpertsOut(
        query_id=query_id, provider=provider, fallback=fallback, note=note,
        results=[
            ExpertResult(**{**r, "evidence": [ExpertEvidence(**e) for e in r["evidence"]]})
            for r in results
        ],
    )


@router.post("/ai/experts", response_model=ExpertsOut)
def experts(conn: Conn, actor: Actor, body: ExpertsIn):
    r = ai_expert.find_experts(
        conn, get_provider(), title=body.title, description=body.description, aspects=body.aspects,
        k=body.k, exclude_person_ids=body.exclude_person_ids, min_degree=body.min_degree,
        unit_id=body.unit, recent_years=body.recent_years, actor_id=actor,
    )
    return _experts_out(r["query_id"], r["provider"], r["fallback"], r["note"], r["results"])


@router.get("/ai/experts/{qid}", response_model=ExpertsOut)
def experts_result(conn: Conn, qid: int):
    with conn.cursor() as cur:
        cur.execute("SELECT id, results, provider FROM ai_query WHERE id=%s AND kind='experts'", (qid,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(404, f"không tìm thấy lượt tìm chuyên gia #{qid}")
    fallback = row["provider"] == "none"
    note = ai_expert.DISABLED_NOTE if fallback else ai_expert.NOTE
    return _experts_out(row["id"], row["provider"], fallback, note, row["results"])


@router.post("/public/check-topic", response_model=CheckTopicOut)
def check_topic(conn: Conn, request: Request, body: CheckTopicIn):
    """Cổng công khai: sinh viên nhập đề tài dự kiến, xem đề tài tương tự các
    khoá trước và giảng viên gần chuyên môn — **không phải** kết luận trùng
    hay khẳng định người hướng dẫn, chỉ gợi ý để tự cân nhắc trước khi đăng
    ký chính thức (qua luồng nghiệp vụ hiện có, không đổi bởi route này)."""
    ip = _client_ip(request)
    if _rate_limited(ip):
        raise HTTPException(429, "Đã dùng hết lượt kiểm tra miễn phí trong 5 phút. Vui lòng thử lại sau ít phút.")
    _record_hit(ip)

    provider = get_provider()
    try:
        similar = similar_topics(conn, provider, title=body.title, description=body.description, k=8)
    except AIDisabled:
        similar = []
    r = ai_expert.find_experts(conn, provider, title=body.title, description=body.description, k=5, save=False)

    note = ai_expert.NOTE if not r["fallback"] else r["note"]
    similar_out = [
        CheckTopicSimilar(work_id=s["work_id"], title=s["title"], doc_type=s["doc_type"],
                          cohort=s.get("cohort"), year=s["year"], score=s["score"], level=s["level"])
        for s in similar
    ]
    experts_out = [
        CheckTopicExpert(person_id=e["person_id"], display_name=e["display_name"], degree=e["degree"],
                         unit_code=e["unit_code"], score=e["score"])
        for e in r["results"]
    ]
    return CheckTopicOut(similar=similar_out, experts=experts_out, note=note)
