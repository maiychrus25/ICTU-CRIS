# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Gom cụm từ khoá thành trục chủ đề (FR-AI-05) bằng k-means trên embedding.

Chỉ ghi vào `ai_topic`/`ai_topic_keyword` — không bao giờ đổi `work` hay các
bảng nghiệp vụ khác. Dùng làm bộ lọc chủ đề (FR-T-01) và cho `topic_of_work`.
"""
import re
from cris.db import tx

_SPLIT = re.compile(r"[,;]")


def _split_keywords(raw):
    """Tách một chuỗi `keywords_raw` thành các từ khoá đã chuẩn hoá (strip, hạ
    chữ), bỏ từ khoá rỗng hoặc chỉ 1 ký tự."""
    return [kw for kw in (p.strip().lower() for p in _SPLIT.split(raw or "")) if len(kw) > 1]


def collect_keywords(conn):
    """Đếm tần suất từ khoá phân biệt trong `work.keywords_raw` của công trình sống.

    Trả về `{keyword: count}`.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT keywords_raw FROM work WHERE keywords_raw IS NOT NULL AND merged_into_id IS NULL")
        rows = cur.fetchall()
    freq = {}
    for r in rows:
        for kw in _split_keywords(r["keywords_raw"]):
            freq[kw] = freq.get(kw, 0) + 1
    return freq


def _l2_normalize(M):
    import numpy as np
    norms = np.linalg.norm(M, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return M / norms


def _kmeans(M, k, seed=0, max_iter=50):
    """k-means trên vector đã chuẩn hoá L2, khoảng cách cosine (= tích vô hướng).

    Khởi tạo kiểu k-means++: tâm đầu ngẫu nhiên, các tâm sau chọn theo xác suất
    tỉ lệ với (1 - cosine tới tâm gần nhất đã chọn). Trả về nhãn cụm (0..k-1)
    cho từng hàng của `M`.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    n = M.shape[0]
    centers = np.empty((k, M.shape[1]), dtype=np.float64)
    centers[0] = M[rng.integers(n)]
    best_sim = M @ centers[0]
    for i in range(1, k):
        dist2 = np.clip(1.0 - best_sim, 0, None) ** 2
        total = dist2.sum()
        idx = rng.choice(n, p=dist2 / total) if total > 0 else rng.integers(n)
        centers[i] = M[idx]
        best_sim = np.maximum(best_sim, M @ centers[i])
    labels = np.full(n, -1)
    for _ in range(max_iter):
        sims = M @ centers.T
        new_labels = np.argmax(sims, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            members = M[labels == j]
            if len(members) == 0:
                continue  # cụm rỗng: giữ tâm cũ, vòng sau có thể có thành viên
            c = members.mean(axis=0)
            cn = np.linalg.norm(c)
            centers[j] = c / cn if cn > 0 else c
    return labels


def build_topics(conn, provider, *, k=40, seed=0):
    """Gom cụm từ khoá phân biệt bằng k-means; ghi `ai_topic` + `ai_topic_keyword`.

    `k` tự giảm xuống số từ khoá phân biệt nếu ít hơn `k`. Nhãn cụm là từ khoá
    tần suất cao nhất trong cụm. Chạy lại xoá hết cụm cũ của `provider.model_id`
    rồi ghi lại từ đầu (idempotent về số dòng).
    """
    freq = collect_keywords(conn)
    keywords = sorted(freq)
    n = len(keywords)
    with tx(conn), conn.cursor() as cur:
        cur.execute("DELETE FROM ai_topic WHERE model=%s", (provider.model_id,))
        if n == 0:
            return {"model": provider.model_id, "topics": 0, "keywords": 0}
        import numpy as np
        vecs = _l2_normalize(np.array(provider.embed(keywords), dtype=np.float64))
        k_eff = max(1, min(k, n))
        labels = _kmeans(vecs, k_eff, seed=seed)
        topics = 0
        for j in range(k_eff):
            members = [keywords[i] for i in range(n) if labels[i] == j]
            if not members:
                continue
            label = max(members, key=lambda w: (freq[w], w))
            cur.execute("INSERT INTO ai_topic(model, label, size) VALUES (%s,%s,%s) RETURNING id",
                        (provider.model_id, label, len(members)))
            tid = cur.fetchone()["id"]
            for w in members:
                cur.execute("INSERT INTO ai_topic_keyword(topic_id, keyword, weight) VALUES (%s,%s,%s)",
                            (tid, w, freq[w]))
            topics += 1
    return {"model": provider.model_id, "topics": topics, "keywords": n}


def topic_of_work(conn, work_id):
    """Nhãn cụm chiếm đa số trong từ khoá của một công trình, hoặc `None`.

    Dùng bộ `ai_topic` được xây gần nhất (theo `built_at`) — nếu nhiều mô hình
    cùng có cụm, chỉ mô hình mới nhất được xét, để tránh trộn nhãn giữa các lần
    gom cụm khác nhau.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT keywords_raw FROM work WHERE id=%s", (work_id,))
        row = cur.fetchone()
        kws = _split_keywords(row["keywords_raw"]) if row else []
        if not kws:
            return None
        cur.execute(
            "SELECT t.label FROM ai_topic_keyword tk JOIN ai_topic t ON t.id = tk.topic_id "
            "WHERE tk.keyword = ANY(%s) AND t.model = (SELECT model FROM ai_topic ORDER BY built_at DESC LIMIT 1) "
            "GROUP BY t.label ORDER BY count(*) DESC, t.label LIMIT 1",
            (kws,),
        )
        r = cur.fetchone()
        return r["label"] if r else None
