# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đối chiếu đề tài (FR-AI-03/04): top-k theo cosine, so sánh khía cạnh, lưu ai_query.

Nguyên tắc gợi ý-không-quyết (BRD §3): hàm ở đây chỉ ghi vào `ai_query`, không
bao giờ ghi vào `work`, `author_link`, `duplicate_group`, `field_provenance`.
Khi `provider=none` (`AIDisabled`), có đường lui khớp từ khoá chuẩn hoá — không
bao giờ ném ngoại lệ ra ngoài, `fallback=True` để giao diện báo rõ.
"""
import json
import math
import re
import unicodedata

from cris.ai.embed import load_matrix, top_k
from cris.ai.provider import AIDisabled
from cris.db import tx

ASPECTS = ("bai_toan", "doi_tuong", "pham_vi", "phuong_phap")

NOTE = (
    "So trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn. "
    "Đây là tài liệu tham khảo cho giảng viên xem xét, không phải kết luận."
)

_SENT_SPLIT = re.compile(r"[.;\n]+")
_WORD = re.compile(r"[a-z0-9]+")

# Stopword tiếng Việt cơ bản dùng cho đường lui khớp từ khoá — so trên dạng đã
# bỏ dấu, hạ chữ (giống văn bản được so khớp).
_STOPWORDS_RAW = (
    "va", "cua", "cho", "trong", "voi", "cac", "mot", "la", "de", "ve", "nay",
    "co", "nhung", "duoc", "khi", "tu", "theo", "tren", "tai", "hay", "hoac",
    "nhu", "da", "se", "bi", "do", "vi", "nen", "neu", "ma", "thi", "cung",
    "con", "den", "sau", "truoc", "bang", "vao", "ra", "day", "ay", "kia",
    "nguoi", "moi", "rang", "gi",
)
_STOPWORDS = set(_STOPWORDS_RAW)


def _strip_accents(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _norm_tokens(text):
    """Bỏ dấu, hạ chữ, tách từ, bỏ stopword — dùng cho đường lui khớp từ khoá."""
    text = _strip_accents((text or "").lower())
    words = _WORD.findall(text)
    return [w for w in words if w not in _STOPWORDS and len(w) > 1]


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


def _bucket(score, thresholds):
    hi, lo = thresholds
    if score >= hi:
        return "giong"
    if score <= lo:
        return "khac"
    return "chua_du"


def _split_sentences(text):
    if not text:
        return []
    return [p.strip() for p in _SENT_SPLIT.split(text) if p.strip()]


def _load_meta(conn, work_ids, doc_types):
    """Thông tin hiển thị cho các work_id còn sống, lọc theo doc_types nếu có."""
    if not work_ids:
        return {}
    with conn.cursor() as cur:
        if doc_types:
            cur.execute(
                "SELECT id, title, doc_type, year_issue, abstract FROM work "
                "WHERE id = ANY(%s) AND merged_into_id IS NULL AND doc_type = ANY(%s)",
                (list(work_ids), list(doc_types)),
            )
        else:
            cur.execute(
                "SELECT id, title, doc_type, year_issue, abstract FROM work "
                "WHERE id = ANY(%s) AND merged_into_id IS NULL",
                (list(work_ids),),
            )
        rows = cur.fetchall()
    return {
        r["id"]: {"title": r["title"], "doc_type": r["doc_type"], "year": r["year_issue"], "abstract": r["abstract"]}
        for r in rows
    }


def _aspect_vectors(provider, aspects):
    """Embed một lần các mô tả khía cạnh người dùng đã nhập (dùng chung cho mọi công trình)."""
    texts = {a: (aspects.get(a) or "").strip() for a in ASPECTS}
    filled = [a for a in ASPECTS if texts[a]]
    if not filled:
        return {}
    vecs = provider.embed([texts[a] for a in filled])
    return dict(zip(filled, vecs))


def _score_aspects(provider, work_id, abstract, aspect_vecs, thresholds, sentence_cache):
    out = {}
    for a in ASPECTS:
        if a not in aspect_vecs:
            out[a] = "chua_du"
            continue
        if work_id not in sentence_cache:
            sentences = _split_sentences(abstract)
            sentence_cache[work_id] = provider.embed(sentences) if sentences else []
        svecs = sentence_cache[work_id]
        if not svecs:
            out[a] = "chua_du"
            continue
        s = max(_cosine(aspect_vecs[a], v) for v in svecs)
        out[a] = _bucket(s, thresholds)
    return out


def _semantic_results(conn, provider, title, description, k, doc_types, thresholds, aspects):
    query_text = (title + "\n" + description).strip()
    qv = provider.embed([query_text])[0]  # có thể ném AIDisabled, không bắt ở đây
    work_ids, M = load_matrix(conn, provider.model_id)
    if not work_ids:
        return []
    meta = _load_meta(conn, work_ids, doc_types)
    keep = [i for i, wid in enumerate(work_ids) if wid in meta]
    if not keep:
        return []
    sub_ids = [work_ids[i] for i in keep]
    sub_M = M[keep]
    ranked = top_k(sub_M, qv, k=k)
    aspect_vecs = _aspect_vectors(provider, aspects)
    sentence_cache = {}  # work_id -> vector các câu tóm tắt, tính một lần mỗi công trình
    results = []
    for row_idx, score in ranked:
        wid = sub_ids[row_idx]
        info = meta[wid]
        aspects_out = _score_aspects(provider, wid, info["abstract"], aspect_vecs, thresholds, sentence_cache)
        entry = {
            "work_id": wid,
            "title": info["title"],
            "doc_type": info["doc_type"],
            "year": info["year"],
            "score": score,
            "aspects": aspects_out,
            "url": f"/tra-cuu/cong-trinh/{wid}",
        }
        explanation = provider.explain(_explain_prompt(title, description, info))
        if explanation:
            entry["explanation"] = explanation
            entry["ai_generated"] = True
        results.append(entry)
    return results


def _explain_prompt(title, description, info):
    return (
        f"Đề tài đề xuất: {title}\nMô tả: {description}\n"
        f"So với công trình đã có: {info['title']}\nTóm tắt công trình đã có: {info['abstract'] or ''}"
    )


def _fallback_results(conn, title, description, k, doc_types):
    """Đường lui khi AI chưa bật: khớp từ khoá chuẩn hoá trên title + keywords_raw."""
    query_tokens = set(_norm_tokens(title) + _norm_tokens(description))
    if not query_tokens:
        return []
    with conn.cursor() as cur:
        if doc_types:
            cur.execute(
                "SELECT id, title, doc_type, year_issue, keywords_raw FROM work "
                "WHERE merged_into_id IS NULL AND title IS NOT NULL AND doc_type = ANY(%s)",
                (list(doc_types),),
            )
        else:
            cur.execute(
                "SELECT id, title, doc_type, year_issue, keywords_raw FROM work "
                "WHERE merged_into_id IS NULL AND title IS NOT NULL"
            )
        rows = cur.fetchall()
    scored = []
    for r in rows:
        text = (r["title"] or "") + " " + (r["keywords_raw"] or "")
        overlap = len(query_tokens & set(_norm_tokens(text)))
        if overlap > 0:
            scored.append((overlap, r))
    scored.sort(key=lambda t: (-t[0], t[1]["id"]))
    results = []
    for overlap, r in scored[:k]:
        results.append({
            "work_id": r["id"],
            "title": r["title"],
            "doc_type": r["doc_type"],
            "year": r["year_issue"],
            "score": float(overlap),
            "aspects": {a: "chua_du" for a in ASPECTS},
            "url": f"/tra-cuu/cong-trinh/{r['id']}",
        })
    return results


def _save_query(conn, *, title, description, aspects, doc_types, k, provider_name, results, actor_id):
    input_payload = {
        "title": title, "description": description, "aspects": aspects,
        "doc_types": list(doc_types) if doc_types else None, "k": k,
    }
    with tx(conn), conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ai_query(input, results, provider, created_by) VALUES (%s,%s,%s,%s) RETURNING id",
            (
                json.dumps(input_payload, ensure_ascii=False, default=str),
                json.dumps(results, ensure_ascii=False, default=str),
                provider_name,
                actor_id,
            ),
        )
        return cur.fetchone()["id"]


def compare_topic(conn, provider, *, title, description, aspects, k=10, doc_types=None,
                   thresholds=(0.55, 0.35), actor_id=None):
    """Đối chiếu một đề tài đề xuất với kho công trình đã có.

    Trả `{"results", "provider", "note", "fallback", "query_id"}`. Không bao giờ
    ném ngoại lệ ra ngoài: `provider=none` (hoặc lỗi `AIDisabled` khác) tự động
    chuyển sang đường lui khớp từ khoá, `fallback=True`.
    """
    title = title or ""
    description = description or ""
    aspects = dict(aspects or {})
    try:
        results = _semantic_results(conn, provider, title, description, k, doc_types, thresholds, aspects)
        fallback = False
    except AIDisabled:
        results = _fallback_results(conn, title, description, k, doc_types)
        fallback = True
    query_id = _save_query(
        conn, title=title, description=description, aspects=aspects, doc_types=doc_types, k=k,
        provider_name=provider.name, results=results, actor_id=actor_id,
    )
    return {"results": results, "provider": provider.name, "note": NOTE, "fallback": fallback, "query_id": query_id}
