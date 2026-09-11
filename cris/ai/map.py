# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Bản đồ tri thức (J2): chiếu 2 chiều toàn bộ vector ngữ nghĩa bằng PCA (SVD,
numpy) để tô lên canvas ở giao diện — **không phải** một phép đo chính xác,
2 chiều mất phần lớn thông tin của vector gốc; chỉ để định hướng "vùng nào gần
vùng nào", không dùng để so sánh khoảng cách tuyệt đối.

Nguyên tắc gợi ý-không-quyết (BR-18) như phần còn lại của `cris/ai/`: chỉ ghi
vào `ai_map` (bảng cache, migration `0015`), không bao giờ đổi `work` hay các
bảng nghiệp vụ khác. Đọc bằng `GET /api/ai/map` (`cris/api/routes/ai_map.py`).
"""
import json
import time

from cris.ai.embed import load_matrix
from cris.ai.provider import AIDisabled
from cris.db import tx

# Tiêu đề cắt bớt trong mỗi điểm — đủ cho tooltip trên bản đồ, không cần toàn văn
# (7.618 điểm × toàn văn tiêu đề sẽ đẩy JSON của /api/ai/map lên vài MB).
TITLE_MAX = 120


def _topic_of_works(conn, work_ids):
    """Gán mỗi `work_id` một `topic_id`: cụm có tổng weight từ khoá lớn nhất,
    khớp `ai_topic_keyword` của bộ cụm mới nhất (`ai_topic.built_at` lớn nhất).

    MỘT truy vấn SQL gộp cho toàn bộ danh sách — khác `cris.ai.topics.topic_of_work`
    (gọi một lần mỗi công trình, chọn theo *số lượng* từ khoá khớp mỗi cụm);
    ở đây chọn theo *tổng weight* và tính hàng loạt vì gọi `topic_of_work` riêng
    cho 7.618 công trình (mỗi lần một round-trip DB) sẽ quá chậm để dựng bản đồ.
    Trả `{work_id: topic_id}` — công trình không khớp từ khoá cụm nào thì vắng mặt.
    """
    if not work_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            "WITH latest AS (SELECT model FROM ai_topic ORDER BY built_at DESC LIMIT 1), "
            "kw AS (SELECT w.id AS work_id, btrim(lower(x)) AS keyword "
            "       FROM work w, regexp_split_to_table(coalesce(w.keywords_raw, ''), '[,;]') x "
            "       WHERE w.id = ANY(%s)), "
            "matched AS (SELECT kw.work_id, tk.topic_id, sum(tk.weight) AS total_weight "
            "            FROM kw JOIN ai_topic_keyword tk ON tk.keyword = kw.keyword "
            "            JOIN ai_topic t ON t.id = tk.topic_id AND t.model = (SELECT model FROM latest) "
            "            GROUP BY kw.work_id, tk.topic_id), "
            "ranked AS (SELECT work_id, topic_id, "
            "           row_number() OVER (PARTITION BY work_id ORDER BY total_weight DESC, topic_id) AS rn "
            "           FROM matched) "
            "SELECT work_id, topic_id FROM ranked WHERE rn = 1",
            (list(work_ids),),
        )
        return {r["work_id"]: r["topic_id"] for r in cur.fetchall()}


def _pca_2d(M):
    """PCA 2 chiều: trừ trung bình từng cột rồi SVD (`numpy.linalg.svd`,
    `full_matrices=False`), lấy 2 thành phần đầu, chuẩn hoá mỗi trục về
    [-1, 1] (chia cho trị tuyệt đối lớn nhất trên trục đó — giữ gốc toạ độ ở
    trung tâm dữ liệu, đúng ý nghĩa "đã trừ trung bình" thay vì kéo giãn hết
    cỡ min..max). Trả ma trận N×2 (numpy); N=0 → ma trận rỗng N×2.
    """
    import numpy as np
    n = M.shape[0]
    if n == 0:
        return np.zeros((0, 2))
    centered = M - M.mean(axis=0)
    _, _, Vt = np.linalg.svd(centered, full_matrices=False)
    k = min(2, Vt.shape[0])
    coords = centered @ Vt[:k].T
    if k < 2:
        coords = np.pad(coords, ((0, 0), (0, 2 - k)))
    for axis in range(2):
        m = float(np.max(np.abs(coords[:, axis]))) if n else 0.0
        if m > 0:
            coords[:, axis] = coords[:, axis] / m
    return coords


def build_map(conn, provider):
    """Dựng bản đồ tri thức: PCA 2 chiều trên `load_matrix(conn, provider.model_id)`,
    kèm `topic_id` (xem `_topic_of_works`), `unit_id` (đơn vị đầu tiên của công
    trình theo `v_work_unit`), `year_issue`, `doc_type`, `title` (cắt
    `TITLE_MAX` ký tự). Tâm mỗi cụm (`cx`, `cy`) là trung bình toạ độ các điểm
    cùng `topic_id`.

    Ghi `ai_map(model, method='pca', points, topics)` — xoá dòng cũ của cùng
    `model` trước khi ghi dòng mới (giữ đúng 1 dòng mới nhất mỗi model, cùng
    cách `ai_topic` được xây lại trong `cris.ai.topics.build_topics`).

    `provider` là `NoneProvider` → ném `AIDisabled` (bản đồ cần vector thật,
    `load_matrix` với model='none' luôn rỗng vì không ai embed được ở đó).

    Trả `{"points": N, "topics": k, "seconds": giây}`.
    """
    if getattr(provider, "name", None) == "none":
        raise AIDisabled("AI chưa bật: đặt CRIS_AI_PROVIDER=local (hoặc fake để kiểm thử) trước khi dựng bản đồ")

    t0 = time.monotonic()
    ids, M = load_matrix(conn, provider.model_id)
    coords = _pca_2d(M)

    meta, unit_of = {}, {}
    if ids:
        with conn.cursor() as cur:
            cur.execute("SELECT id, doc_type, year_issue, title FROM work WHERE id = ANY(%s)", (list(ids),))
            meta = {r["id"]: r for r in cur.fetchall()}
            cur.execute(
                "SELECT DISTINCT ON (work_id) work_id, unit_id FROM v_work_unit "
                "WHERE work_id = ANY(%s) ORDER BY work_id, unit_id",
                (list(ids),),
            )
            unit_of = {r["work_id"]: r["unit_id"] for r in cur.fetchall()}

    topic_of = _topic_of_works(conn, ids)

    points = []
    for i, wid in enumerate(ids):
        info = meta.get(wid)
        if info is None:
            continue  # phòng thân: công trình bị gộp/xoá giữa lúc load_matrix và truy vấn meta
        points.append({
            "id": wid,
            "x": round(float(coords[i, 0]), 4),
            "y": round(float(coords[i, 1]), 4),
            "topic_id": topic_of.get(wid),
            "unit_id": unit_of.get(wid),
            "year": info["year_issue"],
            "doc_type": info["doc_type"],
            "title": (info["title"] or "")[:TITLE_MAX],
        })

    with conn.cursor() as cur:
        cur.execute("SELECT id, label FROM ai_topic")
        label_of = {r["id"]: r["label"] for r in cur.fetchall()}

    by_topic: dict[int, list] = {}
    for p in points:
        tid = p["topic_id"]
        if tid is not None:
            by_topic.setdefault(tid, []).append((p["x"], p["y"]))
    topics = []
    for tid, coords_list in by_topic.items():
        cx = sum(c[0] for c in coords_list) / len(coords_list)
        cy = sum(c[1] for c in coords_list) / len(coords_list)
        topics.append({"id": tid, "label": label_of.get(tid, ""), "size": len(coords_list),
                        "cx": round(cx, 4), "cy": round(cy, 4)})
    topics.sort(key=lambda t: (-t["size"], t["id"]))

    with tx(conn), conn.cursor() as cur:
        cur.execute("DELETE FROM ai_map WHERE model=%s", (provider.model_id,))
        cur.execute(
            "INSERT INTO ai_map(model, method, points, topics) VALUES (%s,%s,%s,%s)",
            (provider.model_id, "pca", json.dumps(points, ensure_ascii=False), json.dumps(topics, ensure_ascii=False)),
        )

    return {"points": len(points), "topics": len(topics), "seconds": round(time.monotonic() - t0, 3)}
