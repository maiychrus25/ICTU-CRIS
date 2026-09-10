# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Trang `/ve` — nguồn dữ liệu, mức dữ liệu, AI đang dùng, và giới hạn (FR-AI-08).

Đây là nơi trả lời câu "số này ở đâu ra": kho nào, đồng bộ lúc nào, có bao nhiêu
công trình, AI nào đang bật và nó dừng ở đâu. Trang chỉ đọc; không khởi tạo
provider (khởi tạo `local` sẽ nạp mô hình 118 MB), chỉ đọc tên provider từ biến
môi trường và hằng số mô hình.
"""
import os

from cris.web.render import badge, e, layout, table
from cris.web.wsgi import route

REPO_URL = "https://github.com/maiychrus25/CRIS"
SOURCE_URL = "https://repository.ictu.edu.vn"

LIMITS = [
    "Chỉ so trên tóm tắt: kho nguồn không có toàn văn (39/40 PDF là tóm tắt một trang do máy sinh). "
    "Không có dẫn chứng theo trang.",
    "Không hiện điểm phần trăm tương đồng tổng hợp; bảng theo khía cạnh buộc người đọc tự xét.",
    "Bài báo thiếu tóm tắt chỉ có vector từ tiêu đề và từ khoá — chất lượng thấp hơn.",
    "Ngưỡng khía cạnh (0,55 / 0,35) là mặc định, chưa tinh chỉnh trên tập gán tay.",
    "Tóm tắt tiếng Anh do máy sinh cho đồ án tiếng Việt; mô hình đa ngữ xử lý được nhưng không hoàn hảo.",
    "Gợi ý tác giả chỉ có khi người đó đã có công trình được xác nhận; tốt dần theo số quyết định của người dùng.",
    "AI gợi ý, người quyết: không có luồng nào để máy tự gộp bản ghi, tự nối tác giả hay đổi dữ liệu nghiệp vụ.",
]


def _provider_info():
    name = (os.environ.get("CRIS_AI_PROVIDER") or "none").strip().lower()
    if name == "local":
        from cris.ai import local as L      # chỉ hằng số; thư viện AI import bên trong lớp, không nạp ở đây
        return {"name": "local", "model": L.MODEL_ID, "dim": L.DIM, "repo": L.REPO,
                "licence": "Apache-2.0", "size": "118 MB mô hình + 17 MB tokenizer", "runs": "CPU, cục bộ, không gọi ra ngoài"}
    if name == "fake":
        return {"name": "fake", "model": "fake-32", "dim": 32, "repo": None,
                "licence": "—", "size": "—", "runs": "vector xác định từ túi từ — chỉ để kiểm thử"}
    return {"name": "none", "model": None, "dim": None, "repo": None, "licence": "—", "size": "—", "runs": "AI chưa bật"}


def _stats(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM work WHERE merged_into_id IS NULL")
        works = cur.fetchone()["n"]
        cur.execute("SELECT doc_type, count(*) AS n FROM work WHERE merged_into_id IS NULL GROUP BY doc_type ORDER BY n DESC")
        by_type = cur.fetchall()
        cur.execute("SELECT model, count(*) AS n FROM ai_embedding GROUP BY model ORDER BY n DESC")
        emb = cur.fetchall()
        cur.execute("SELECT count(*) AS n FROM ai_topic")
        topics = cur.fetchone()["n"]
        cur.execute("SELECT kind, count(*) AS n FROM ai_suggestion GROUP BY kind")
        sugg = {r["kind"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT scope, status, started_at, finished_at, warnings FROM sync_run ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()
    return {"works": works, "by_type": by_type, "embeddings": emb, "topics": topics, "suggestions": sugg, "last_sync": last}


DOC_TYPE_LABELS = {"bai_bao": "Bài báo", "do_an": "Đồ án", "luan_van": "Luận văn", "luan_an": "Luận án",
                   "hoc_lieu": "Học liệu", "giang_vien": "Giảng viên"}


def _fmt(v):
    try:
        return v.strftime("%d/%m/%Y %H:%M")
    except AttributeError:
        return "—" if v is None else str(v)


@route("GET", "/ve")
def about(req):
    p = _provider_info()
    s = _stats(req.conn)
    last = s["last_sync"]
    sync_rows = [
        ["Kho nguồn", f'<a href="{e(SOURCE_URL)}">{e(SOURCE_URL)}</a> — WordPress, đọc qua HTML, chỉ đọc'],
        ["Lần đồng bộ gần nhất", e(f'{_fmt(last["finished_at"] or last["started_at"])} · {last["scope"]} · {last["status"]}') if last else "Chưa đồng bộ lần nào"],
        ["Cảnh báo lệch số lượng", e(str(last["warnings"])) if last and last["warnings"] else "không"],
        ["Công trình sống", e(f'{s["works"]:,}'.replace(",", "."))],
    ]
    type_rows = [[e(DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"])), e(f'{r["n"]:,}'.replace(",", "."))] for r in s["by_type"]]
    ai_rows = [
        ["Nhà cung cấp", badge(p["name"], "ok" if p["name"] == "local" else ("warn" if p["name"] == "fake" else "default")) + f' <span class="muted">{e(p["runs"])}</span>'],
        ["Mô hình", e(p["model"] or "—") + (f' — <a href="https://huggingface.co/{e(p["repo"])}">{e(p["repo"])}</a>' if p["repo"] else "")],
        ["Giấy phép mô hình", e(p["licence"])],
        ["Kích thước", e(p["size"])],
        ["Chiều vector", e(p["dim"] if p["dim"] is not None else "—")],
        ["Vector đã sinh", ", ".join(e(f'{r["n"]:,}'.replace(",", ".") + " (" + r["model"] + ")") for r in s["embeddings"]) or "chưa có"],
        ["Cụm chủ đề", e(s["topics"]) if s["topics"] else "chưa có"],
        ["Gợi ý hàng đợi", e(f'tác giả {s["suggestions"].get("author_link", 0)} · nghi trùng {s["suggestions"].get("duplicate", 0)}')],
    ]
    limits = "".join(f"<li>{e(x)}</li>" for x in LIMITS)
    docs = [
        (f"{REPO_URL}/blob/main/docs/ai.md", "Tài liệu kỹ thuật AI"),
        (f"{REPO_URL}/blob/main/docs/BRD.md", "Yêu cầu nghiệp vụ (BRD)"),
        (f"{REPO_URL}/blob/main/docs/SRS.md", "Đặc tả phần mềm (SRS)"),
        (f"{REPO_URL}/blob/main/DEPENDENCIES.md", "Chính sách thư viện và giấy phép"),
        (f"{REPO_URL}/blob/main/CHANGELOG.md", "Lịch sử thay đổi"),
        (f"{REPO_URL}/issues", "Báo lỗi (bug tracker)"),
    ]
    doc_list = "".join(f'<li><a href="{e(h)}">{e(t)}</a></li>' for h, t in docs)
    body = f"""
<h1>Về hệ thống</h1>
<p class="muted">Một nguồn sự thật cho dữ liệu công bố khoa học — mỗi con số truy ngược được về bản ghi gốc.
Trang này ghi rõ dữ liệu đến từ đâu, AI nào đang bật, và hệ thống dừng ở đâu.</p>
<h2>Nguồn dữ liệu</h2>
{table(["Mục", "Giá trị"], sync_rows)}
<h3>Công trình theo loại</h3>
{table(["Loại", "Số lượng"], type_rows) if type_rows else '<p class="muted">Chưa có công trình.</p>'}
<h2>AI</h2>
<p>Mọi kết quả AI là <strong>gợi ý</strong>; người dùng quyết định và hệ thống ghi ai quyết. Đối chiếu đề tài
<strong>so trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn</strong>.</p>
{table(["Mục", "Giá trị"], ai_rows)}
<h2>Giới hạn — nói trước để không ai hiểu nhầm</h2>
<ol>{limits}</ol>
<h2>Tài liệu và mã nguồn</h2>
<p>Mã nguồn mở, giấy phép Apache-2.0: <a href="{e(REPO_URL)}">{e(REPO_URL)}</a></p>
<ul>{doc_list}</ul>
"""
    return layout("Về hệ thống", body, active="/ve")
