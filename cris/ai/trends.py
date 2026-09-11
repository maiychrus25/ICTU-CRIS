# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Xu hướng chủ đề theo khoá hoặc năm (J2): đếm công trình sống theo (cụm,
khoá|năm) — dùng cho biểu đồ vùng xếp chồng ở bản đồ tri thức.

Tính trực tiếp mỗi lần gọi (không cache như `ai_map`) — cùng cỡ dữ liệu với
`cris.ai.map._topic_of_works`, đủ nhanh để không cần bảng cache riêng. Chỉ đọc,
không ghi bảng nào — nguyên tắc gợi ý-không-quyết (BR-18) như phần còn lại của
`cris/ai/`.
"""
import re

_NUM = re.compile(r"(\d+)")


def _numeric_key(v):
    """Khoá sắp xếp tăng dần theo số: năm (`int`) dùng thẳng; khoá dạng "K17"
    lấy phần số trong chuỗi (17) — để "K9" đứng trước "K17", khác thứ tự chuỗi
    (nơi "K17" < "K9")."""
    if isinstance(v, int):
        return v
    m = _NUM.search(str(v))
    return int(m.group(1)) if m else 0


def topic_trends(conn, *, by="cohort", top=12):
    """Đếm công trình sống (`merged_into_id IS NULL`) theo (cụm chủ đề, khoá)
    khi `by="cohort"` (khoá = `work.cohort`) hay (cụm, năm) khi `by="year"`
    (năm = `work.year_issue`) — bỏ công trình có khoá/năm NULL.

    Khớp từ khoá ↔ cụm cùng cách `cris.ai.map._topic_of_works`: tách
    `keywords_raw` theo `[,;]`, khớp `ai_topic_keyword` của bộ cụm mới nhất
    (`ai_topic.built_at` lớn nhất), chọn cụm có tổng weight lớn nhất cho mỗi
    công trình — công trình không khớp từ khoá cụm nào không thuộc cụm nào,
    không tính vào bất cứ khoá/năm nào ở đây.

    Giữ `top` cụm lớn nhất (theo tổng số công trình mọi khoá/năm cộng lại) làm
    chuỗi riêng; phần còn lại gộp vào một chuỗi `"khác"` (`topic_id=None`).
    `share` mỗi (cụm, khoá|năm) = count / tổng số công trình đã khớp cụm của
    khoá|năm đó (nên tổng `share` của các chuỗi tại một khoá|năm cộng ≈ 1,0 —
    không tính công trình không khớp cụm nào vào mẫu số).

    `keys` sắp tăng dần theo số (xem `_numeric_key`).

    Trả `{"series": [{"topic_id", "label", "values": [{"key","count","share"}]}], "keys": [...]}`.
    """
    if by not in ("cohort", "year"):
        raise ValueError(f"by={by!r} không hợp lệ; chọn 'cohort' hoặc 'year'")
    key_col = "w.cohort" if by == "cohort" else "w.year_issue"

    with conn.cursor() as cur:
        cur.execute(
            f"WITH latest AS (SELECT model FROM ai_topic ORDER BY built_at DESC LIMIT 1), "
            f"kw AS (SELECT w.id AS work_id, {key_col} AS key, btrim(lower(x)) AS keyword "
            f"       FROM work w, regexp_split_to_table(coalesce(w.keywords_raw, ''), '[,;]') x "
            f"       WHERE w.merged_into_id IS NULL AND {key_col} IS NOT NULL), "
            f"matched AS (SELECT kw.work_id, kw.key, tk.topic_id, sum(tk.weight) AS total_weight "
            f"            FROM kw JOIN ai_topic_keyword tk ON tk.keyword = kw.keyword "
            f"            JOIN ai_topic t ON t.id = tk.topic_id AND t.model = (SELECT model FROM latest) "
            f"            GROUP BY kw.work_id, kw.key, tk.topic_id), "
            f"ranked AS (SELECT work_id, key, topic_id, "
            f"           row_number() OVER (PARTITION BY work_id ORDER BY total_weight DESC, topic_id) AS rn "
            f"           FROM matched) "
            f"SELECT key, topic_id FROM ranked WHERE rn = 1"
        )
        rows = cur.fetchall()

    counts: dict[tuple, int] = {}
    topic_totals: dict[int, int] = {}
    total_per_key: dict = {}
    for r in rows:
        key, tid = r["key"], r["topic_id"]
        counts[(tid, key)] = counts.get((tid, key), 0) + 1
        topic_totals[tid] = topic_totals.get(tid, 0) + 1
        total_per_key[key] = total_per_key.get(key, 0) + 1

    keys = sorted(total_per_key, key=_numeric_key)
    top_topics = sorted(topic_totals, key=lambda t: (-topic_totals[t], t))[:top]
    top_set = set(top_topics)

    label_of = {}
    if top_topics:
        with conn.cursor() as cur:
            cur.execute("SELECT id, label FROM ai_topic WHERE id = ANY(%s)", (top_topics,))
            label_of = {r["id"]: r["label"] for r in cur.fetchall()}

    def _values(counts_by_key):
        return [{"key": key, "count": counts_by_key.get(key, 0),
                  "share": (counts_by_key.get(key, 0) / total_per_key[key]) if total_per_key.get(key) else 0.0}
                for key in keys]

    series = []
    for tid in top_topics:
        counts_by_key = {key: counts.get((tid, key), 0) for key in keys}
        series.append({"topic_id": tid, "label": label_of.get(tid, ""), "values": _values(counts_by_key)})

    other_by_key: dict = {}
    for (tid, key), c in counts.items():
        if tid not in top_set:
            other_by_key[key] = other_by_key.get(key, 0) + c
    if any(other_by_key.values()):
        series.append({"topic_id": None, "label": "khác", "values": _values(other_by_key)})

    return {"series": series, "keys": keys}
