# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tìm kiếm ngữ nghĩa hướng ra người dùng cuối (J1): `mode=semantic` ở
`/api/works`, và láng giềng ngữ nghĩa dùng chung cho tìm chuyên gia
(`cris/ai/expert.py`) và cổng công khai kiểm tra đề tài
(`cris/api/routes/ai_public.py`).

Nguyên tắc gợi ý-không-quyết (BR-18) như phần còn lại của `cris/ai/`: các hàm
ở đây chỉ đọc, không bao giờ ghi bảng nghiệp vụ. Khác `cris.ai.compare`,
`similar_topics` ở đây **không lưu** `ai_query` — dùng cho cổng công khai
không có actor để gắn lượt tra cứu.
"""
# _semantic_results là hàm nội bộ (tên bắt đầu "_") của compare.py — tái dùng
# nguyên cách tìm láng giềng ngữ nghĩa (embed câu hỏi, top-k cosine trên toàn
# ma trận, khía cạnh) của đối chiếu đề tài mà không sửa compare.py; ở đây gọi
# với aspects rỗng (không có mô tả khía cạnh riêng cho tìm kiếm/cổng công
# khai) nên mọi `aspects` trả về luôn là "chua_du" — không dùng tới.
# _level là hàm nội bộ của screen.py — tái dùng cách quy điểm cosine sang mức
# cao/vừa/thấp theo SCREEN_THRESHOLDS (hiệu chỉnh trên so toàn văn bản hai
# công trình, không phải 0,55/0,35 của compare.py vốn hiệu chỉnh cho so một
# khía cạnh với một câu tóm tắt).
from cris.ai.compare import _semantic_results
from cris.ai.embed import load_matrix, top_k
from cris.ai.provider import AIDisabled
from cris.ai.screen import SCREEN_THRESHOLDS, _level

NOTE = "Tìm theo nghĩa (AI): kết quả có thể không chứa từ đã gõ."
DISABLED_NOTE = "AI chưa bật — tìm theo từ khoá."


def semantic_works(conn, provider, q, *, k=50, doc_types=None):
    """Top-`k` `work_id` gần nghĩa nhất với câu truy vấn tự do `q`.

    Embed `q` (có thể ném `AIDisabled`, không bắt ở đây — người gọi tự quyết
    định đường lui, xem `cris/api/routes/search.py`), rồi `top_k` trên toàn
    ma trận `load_matrix`. `doc_types`, nếu có, lọc **trước** khi lấy top-k để
    không mất chỗ trong top-k cho loại không cần; công trình đã gộp
    (`merged_into_id`) không có trong tập lọc — cùng cách `compare._load_meta`
    loại chúng.

    Trả `[(work_id, score)]` giảm dần theo `score` (cosine, 0..1 vì vector đã
    chuẩn hoá); rỗng nếu chưa có vector nào hoặc `q` rỗng.
    """
    query_text = (q or "").strip()
    if not query_text:
        return []
    qv = provider.embed([query_text])[0]  # có thể ném AIDisabled
    work_ids, M = load_matrix(conn, provider.model_id)
    if not work_ids:
        return []
    with conn.cursor() as cur:
        if doc_types:
            cur.execute(
                "SELECT id FROM work WHERE id = ANY(%s) AND merged_into_id IS NULL AND doc_type = ANY(%s)",
                (list(work_ids), list(doc_types)),
            )
        else:
            cur.execute(
                "SELECT id FROM work WHERE id = ANY(%s) AND merged_into_id IS NULL",
                (list(work_ids),),
            )
        alive = {r["id"] for r in cur.fetchall()}
    keep = [i for i, wid in enumerate(work_ids) if wid in alive]
    if not keep:
        return []
    sub_ids = [work_ids[i] for i in keep]
    sub_M = M[keep]
    return [(sub_ids[i], score) for i, score in top_k(sub_M, qv, k=k)]


def similar_topics(conn, provider, *, title, description="", k=8, thresholds=SCREEN_THRESHOLDS, doc_types=None):
    """Công trình gần nghĩa với một đề tài đề xuất (tiêu đề + mô tả), dùng cho
    tìm chuyên gia và cổng công khai kiểm tra đề tài — **không lưu** `ai_query`
    (khác `compare_topic`, xem docstring module).

    Trả kết quả cùng hình dạng `_semantic_results` của `compare.py`
    (`work_id, title, doc_type, year, score, aspects, url` — `aspects` luôn
    `"chua_du"` vì không có mô tả khía cạnh nào được truyền), thêm hai
    trường: `cohort` (đọc từ `work.cohort`, cho biết đề tài tương tự thuộc
    khoá nào) và `level` (`cao`/`vua`/`thap` của `score` theo `thresholds`,
    mặc định `SCREEN_THRESHOLDS` — cùng thang đo rà soát trùng đề tài theo
    khoá vì đây cũng so toàn văn bản hai công trình, không phải một khía cạnh
    với một câu tóm tắt như `compare_topic`).

    Có thể ném `AIDisabled` (từ `_semantic_results` → `provider.embed`),
    không bắt ở đây — người gọi (`cris/ai/expert.py`,
    `cris/api/routes/ai_public.py`) tự quyết định đường lui.
    """
    results = _semantic_results(conn, provider, title or "", description or "", k, doc_types, (0.55, 0.35), {})
    if not results:
        return results
    ids = [r["work_id"] for r in results]
    with conn.cursor() as cur:
        cur.execute("SELECT id, cohort FROM work WHERE id = ANY(%s)", (ids,))
        cohort_of = {r["id"]: r["cohort"] for r in cur.fetchall()}
    for r in results:
        r["cohort"] = cohort_of.get(r["work_id"])
        r["level"] = _level(r["score"], thresholds)
    return results


__all__ = ["semantic_works", "similar_topics", "NOTE", "DISABLED_NOTE", "AIDisabled"]
