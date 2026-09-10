# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Sinh và lưu vector ngữ nghĩa cho công trình; chạy lại chỉ tính phần đổi."""
import hashlib
from cris.db import tx


def work_text(w):
    """Văn bản đem embed: tiêu đề, tóm tắt, từ khoá — đúng những gì kho có."""
    parts = [w.get("title") or "", w.get("abstract") or "", w.get("keywords_raw") or ""]
    return "\n".join(p.strip() for p in parts).strip()


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_embeddings(conn, provider, *, only_missing=True, batch=32, progress=None):
    """Embed mọi công trình sống có tiêu đề. Trả về {model, dim, built, skipped}.

    Với only_missing, bỏ qua công trình đã có vector cùng mô hình và cùng băm văn
    bản; đổi tiêu đề/tóm tắt thì băm đổi và vector được tính lại.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, abstract, keywords_raw FROM work "
                    "WHERE merged_into_id IS NULL AND title IS NOT NULL ORDER BY id")
        works = cur.fetchall()
        existing = {}
        if only_missing:
            cur.execute("SELECT work_id, text_hash FROM ai_embedding WHERE model=%s", (provider.model_id,))
            existing = {r["work_id"]: r["text_hash"] for r in cur.fetchall()}
    todo = []
    for w in works:
        t = work_text(w)
        h = text_hash(t)
        if existing.get(w["id"]) == h:
            continue
        todo.append((w["id"], t, h))
    built = 0
    with tx(conn), conn.cursor() as cur:
        for i in range(0, len(todo), batch):
            chunk = todo[i:i + batch]
            vecs = provider.embed([t for _, t, _ in chunk])
            for (wid, _, h), v in zip(chunk, vecs):
                cur.execute(
                    "INSERT INTO ai_embedding(work_id, model, dim, vector, text_hash) VALUES (%s,%s,%s,%s,%s) "
                    "ON CONFLICT (work_id, model) DO UPDATE SET dim=EXCLUDED.dim, vector=EXCLUDED.vector, "
                    "text_hash=EXCLUDED.text_hash, built_at=now()",
                    (wid, provider.model_id, len(v), v, h))
                built += 1
            if progress:
                progress(built, len(todo))
    return {"model": provider.model_id, "dim": provider.dim, "built": built, "skipped": len(works) - built}


def load_matrix(conn, model):
    """Trả (work_ids, ma trận numpy N×dim) cho một mô hình; N=0 → ma trận rỗng."""
    import numpy as np
    with conn.cursor() as cur:
        cur.execute("SELECT work_id, vector FROM ai_embedding WHERE model=%s ORDER BY work_id", (model,))
        rows = cur.fetchall()
    if not rows:
        return [], np.zeros((0, 0), dtype=np.float32)
    ids = [r["work_id"] for r in rows]
    M = np.array([r["vector"] for r in rows], dtype=np.float32)
    return ids, M


def top_k(M, q, k=10):
    """k hàng gần nhất theo cosine (vector đã chuẩn hoá nên là tích vô hướng).

    Trả về danh sách (chỉ_số_hàng, điểm) giảm dần theo điểm.
    """
    import numpy as np
    if M.shape[0] == 0:
        return []
    q = np.asarray(q, dtype=np.float32)
    s = M @ q
    k = min(k, s.shape[0])
    idx = np.argpartition(-s, k - 1)[:k]
    idx = idx[np.argsort(-s[idx])]
    return [(int(i), float(s[i])) for i in idx]


def status(conn, provider):
    with conn.cursor() as cur:
        cur.execute("SELECT model, count(*) AS n, max(built_at) AS last FROM ai_embedding GROUP BY model ORDER BY model")
        rows = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT count(*) AS n FROM work WHERE merged_into_id IS NULL AND title IS NOT NULL")
        works = cur.fetchone()["n"]
    return {"provider": provider.name, "model": provider.model_id, "dim": provider.dim,
            "works": works, "embeddings": rows}
