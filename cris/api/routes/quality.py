# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Chất lượng dữ liệu (SC-10) và trang Về hệ thống (FR-AI-08) — số liệu từ `quality.report`
và các bảng, không tính lại; không khởi tạo provider AI (chỉ đọc hằng số)."""
import os

from fastapi import APIRouter

from cris import auth as auth_mod
from cris import quality
from cris.api.deps import Conn
from cris.api.schemas import AboutOut, LastSync, QualityMetric, QualityOut

router = APIRouter(prefix="/api", tags=["chat-luong"])

REPO_URL = "https://github.com/maiychrus25/ICTU-CRIS"
SOURCE_URL = "https://repository.ictu.edu.vn"

METRICS = [
    ("works", "Tổng số công trình", None),
    ("works_needs_review", "Công trình cần rà soát", "/doi-soat/trung-lap"),
    ("mentions", "Lượt tên tác giả", None),
    ("mentions_placeholder", "Lượt tên giữ chỗ (sinh viên)", "/doi-soat/tac-gia"),
    ("mentions_truncated", "Lượt tên bị cắt ngắn ở nguồn", "/doi-soat/tac-gia"),
    ("links_auto", "Liên kết đã nối tự động", None),
    ("links_queued", "Liên kết đang chờ xác nhận", "/doi-soat/tac-gia"),
    ("links_confirmed", "Liên kết đã xác nhận thủ công", None),
    ("works_with_link", "Công trình có ít nhất một tác giả đã liên kết", "/doi-soat/tac-gia"),
    ("works_without_unit", "Công trình chưa xác định được đơn vị", "/doi-soat/tac-gia"),
    ("dup_groups_open", "Nhóm nghi trùng đang chờ xử lý", "/doi-soat/trung-lap"),
    ("anomalies_open", "Cảnh báo bất thường đang mở", "/chat-luong-du-lieu/canh-bao"),
]

LIMITS = [
    "Chỉ so trên tóm tắt: kho nguồn không có toàn văn (39/40 PDF là tóm tắt một trang do máy sinh). Không có dẫn chứng theo trang.",
    "Không hiện điểm phần trăm tương đồng tổng hợp; bảng theo khía cạnh buộc người đọc tự xét.",
    "Bài báo thiếu tóm tắt chỉ có vector từ tiêu đề và từ khoá — chất lượng thấp hơn.",
    "Ngưỡng khía cạnh (0,55 / 0,35) là mặc định, chưa tinh chỉnh trên tập gán tay.",
    "Tóm tắt tiếng Anh do máy sinh cho đồ án tiếng Việt; mô hình đa ngữ xử lý được nhưng không hoàn hảo.",
    "Gợi ý tác giả chỉ có khi người đó đã có công trình được xác nhận; tốt dần theo số quyết định của người dùng.",
    "AI gợi ý, người quyết: không có luồng nào để máy tự gộp bản ghi, tự nối tác giả hay đổi dữ liệu nghiệp vụ.",
]


@router.get("/quality", response_model=QualityOut)
def quality_report(conn: Conn):
    r = quality.report(conn)
    # `anomalies_open` (K2): đếm trực tiếp `quality_flag`, không qua `quality.report`
    # (tầng nghiệp vụ có sẵn, không sửa) — bảng mới ở migration `0017_quality_flag.sql`.
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM quality_flag WHERE state='open'")
        r["anomalies_open"] = cur.fetchone()["n"]
    metrics = [QualityMetric(key=k, label=label, value=r.get(k), queue_url=url) for k, label, url in METRICS]
    return QualityOut(metrics=metrics, works_by_type=r.get("works_by_type", {}),
                      works_with_link_pct=r.get("works_with_link_pct", 0.0), last_sync=r.get("last_sync"))


def _provider_info():
    name = (os.environ.get("CRIS_AI_PROVIDER") or "none").strip().lower()
    if name == "local":
        from cris.ai import local as L
        return {"provider": "local", "model": L.MODEL_ID, "dim": L.DIM, "repo": L.REPO, "licence": "Apache-2.0",
                "size": "118 MB mô hình + 17 MB tokenizer", "runs": "CPU, cục bộ, không gọi ra ngoài"}
    if name == "fake":
        return {"provider": "fake", "model": "fake-32", "dim": 32, "repo": None, "licence": None, "size": None,
                "runs": "vector xác định từ túi từ — chỉ để kiểm thử"}
    return {"provider": "none", "model": None, "dim": None, "repo": None, "licence": None, "size": None, "runs": "AI chưa bật"}


@router.get("/about", response_model=AboutOut)
def about(conn: Conn):
    with conn.cursor() as cur:
        cur.execute("SELECT doc_type, count(*) AS n FROM work WHERE merged_into_id IS NULL GROUP BY doc_type ORDER BY n DESC")
        by_type = {r["doc_type"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT model, count(*) AS n FROM ai_embedding GROUP BY model ORDER BY n DESC")
        emb = {r["model"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM ai_topic")
        topics = cur.fetchone()["n"]
        cur.execute("SELECT kind, count(*) AS n FROM ai_suggestion GROUP BY kind")
        sugg = {r["kind"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT id, source, scope, status, started_at, finished_at FROM sync_run ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()
    ai = _provider_info() | {"embeddings": emb, "topics": topics, "suggestions": sugg}
    return AboutOut(source_url=SOURCE_URL, repo_url=REPO_URL, last_sync=LastSync(**last) if last else None,
                    works=sum(by_type.values()), works_by_type=by_type, ai=ai, limits=LIMITS,
                    auth_required=auth_mod.auth_required(conn))
