# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đối chiếu đề tài (SC-13, SC-14): biểu mẫu nhập đề tài và bảng kết quả.

Chỉ đọc/ghi qua `cris.ai.compare.compare_topic` (ghi mỗi lần đối chiếu vào
`ai_query`) — không viết lại thuật toán ở đây, không đụng `work`/`author_link`/
`duplicate_group`/`field_provenance`. `GET` không ghi; `POST` luôn `303` sang
trang kết quả, kể cả khi dữ liệu nhập chưa hợp lệ (quay lại biểu mẫu kèm lỗi).
"""
from urllib.parse import urlencode

from cris.ai.compare import ASPECTS, compare_topic
from cris.ai.provider import get_provider
from cris.web.render import badge, e, layout, table
from cris.web.wsgi import Redirect, route

PATH_FORM = "/doi-chieu"

ASPECT_LABELS = {
    "bai_toan": "Bài toán",
    "doi_tuong": "Đối tượng",
    "pham_vi": "Phạm vi",
    "phuong_phap": "Phương pháp",
}

ASPECT_STATE_LABELS = {
    "giong": "Giống",
    "khac": "Khác",
    "chua_du": "Chưa đủ thông tin",
}

ASPECT_BADGE_KIND = {"giong": "ok", "khac": "danger", "chua_du": "warn"}

# Nhãn loại tài liệu cho bộ lọc biểu mẫu — trùng cấu trúc với
# `views_search.DOC_TYPE_LABELS` nhưng khai báo riêng để không phụ thuộc
# module khác đang được một nhánh song song chỉnh sửa.
DOC_TYPE_LABELS = {
    "bai_bao": "Bài báo",
    "do_an": "Đồ án",
    "luan_van": "Luận văn",
    "luan_an": "Luận án",
    "hoc_lieu": "Học liệu",
    "giang_vien": "Giảng viên",
    "dang_ky_do_an": "Đăng ký đồ án",
}


def _not_found(what):
    body = f'<p class="error-page">Không tìm thấy {e(what)}.</p>'
    return (404, [], layout("Không tìm thấy", body))


def _rerun_url(input_payload):
    """Đường dẫn quay lại biểu mẫu, đã điền sẵn theo `ai_query.input` đã lưu."""
    params = {
        "title": input_payload.get("title") or "",
        "description": input_payload.get("description") or "",
    }
    aspects = input_payload.get("aspects") or {}
    for a in ASPECTS:
        v = aspects.get(a)
        if v:
            params[a] = v
    doc_types = input_payload.get("doc_types")
    if doc_types:
        params["doc_types"] = ",".join(doc_types)
    return f"{PATH_FORM}?{urlencode(params)}"


_NOTE_TEXT = (
    "So trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn. "
    "Đây là tài liệu tham khảo cho giảng viên xem xét, không phải kết luận."
)


def _render_form(prefill, selected_doc_types, error=None):
    error_html = f'<p class="error-page">{e(error)}</p>' if error else ""
    aspect_fields = "".join(
        f'<label>{e(ASPECT_LABELS[a])} '
        f'<textarea name="{e(a)}" rows="2">{e(prefill.get(a) or "")}</textarea></label>'
        for a in ASPECTS
    )
    doc_type_boxes = "".join(
        f'<label class="doc-type-choice"><input type="checkbox" name="doc_types" value="{e(code)}"'
        f'{" checked" if code in selected_doc_types else ""}> {e(label)}</label>'
        for code, label in DOC_TYPE_LABELS.items()
    )
    return f"""
    {error_html}
    <p class="ai-note">{e(_NOTE_TEXT)}</p>
    <form method="post" action="{e(PATH_FORM)}" class="compare-form">
      <label>Tên đề tài
        <input type="text" name="title" value="{e(prefill.get('title') or '')}" required>
      </label>
      <label>Mô tả đề tài
        <textarea name="description" rows="4">{e(prefill.get('description') or '')}</textarea>
      </label>
      <fieldset>
        <legend>Khía cạnh — điền để so sánh, bỏ trống nếu chưa rõ</legend>
        {aspect_fields}
      </fieldset>
      <fieldset>
        <legend>Loại tài liệu — bỏ trống nghĩa là tất cả</legend>
        {doc_type_boxes}
      </fieldset>
      <button type="submit">Đối chiếu</button>
    </form>
    """


@route("GET", PATH_FORM)
def compare_form_view(req):
    prefill = {
        "title": req.query.get("title") or "",
        "description": req.query.get("description") or "",
    }
    for a in ASPECTS:
        prefill[a] = req.query.get(a) or ""
    doc_types_raw = req.query.get("doc_types") or ""
    selected_doc_types = {t for t in doc_types_raw.split(",") if t}
    error = req.query.get("error")
    body = _render_form(prefill, selected_doc_types, error=error)
    return layout("Đối chiếu đề tài", body, active=PATH_FORM)


@route("POST", PATH_FORM)
def compare_submit(req):
    title = (req.form.get("title") or "").strip()
    description = (req.form.get("description") or "").strip()
    aspects = {a: (req.form.get(a) or "").strip() for a in ASPECTS}
    doc_types = req.form_list("doc_types") or None

    if not title:
        params = {"description": description, "error": "Vui lòng nhập tên đề tài."}
        params.update({a: v for a, v in aspects.items() if v})
        if doc_types:
            params["doc_types"] = ",".join(doc_types)
        return Redirect(f"{PATH_FORM}?{urlencode(params)}")

    provider = get_provider()
    result = compare_topic(
        req.conn, provider, title=title, description=description, aspects=aspects,
        doc_types=doc_types, actor_id=req.actor_id,
    )
    return Redirect(f"{PATH_FORM}/{result['query_id']}")


@route("GET", PATH_FORM + "/<int:qid>")
def compare_result_view(req, qid):
    with req.conn.cursor() as cur:
        cur.execute(
            "SELECT id, input, results, provider, created_at FROM ai_query WHERE id = %s", (qid,)
        )
        row = cur.fetchone()
    if row is None:
        return _not_found("kết quả đối chiếu")

    fallback = row["provider"] == "none"
    parts = [f'<p class="ai-note">{e(_NOTE_TEXT)}</p>']
    if fallback:
        parts.append(
            '<p class="warn-line">AI chưa bật — đang khớp từ khoá. '
            "Để bật, đặt biến môi trường <code>CRIS_AI_PROVIDER=local</code> "
            "(hoặc <code>fake</code> để kiểm thử) rồi chạy <code>python -m cris ai embed</code>.</p>"
        )
    parts.append(
        f'<p><a class="btn" href="{e(_rerun_url(row["input"]))}">Chỉnh mô tả và chạy lại</a></p>'
    )

    results = row["results"] or []
    if not results:
        parts.append('<p class="empty-state">Không có công trình nào phù hợp để so sánh.</p>')
    for r in results:
        title_link = f'<a href="{e(r.get("url") or "#")}">{e(r["title"])}</a>'
        doc_type_label = e(DOC_TYPE_LABELS.get(r.get("doc_type"), r.get("doc_type")))
        year = e(r.get("year")) if r.get("year") is not None else "—"
        meta_line = f'<p class="work-meta">{doc_type_label} &middot; {year}</p>'

        aspect_row = [
            badge(ASPECT_STATE_LABELS.get(r["aspects"].get(a, "chua_du"), "Chưa đủ thông tin"),
                  ASPECT_BADGE_KIND.get(r["aspects"].get(a, "chua_du"), "warn"))
            for a in ASPECTS
        ]
        aspect_table = table([ASPECT_LABELS[a] for a in ASPECTS], [aspect_row])

        explanation_html = ""
        if r.get("explanation"):
            explanation_html = (
                '<div class="ai-explain"><p><strong>Lời giải thích (do AI sinh, cần kiểm):</strong></p>'
                f"<p>{e(r['explanation'])}</p></div>"
            )

        parts.append(
            f'<article class="compare-result">'
            f"<h2>{title_link}</h2>{meta_line}{aspect_table}{explanation_html}"
            f"</article>"
        )

    return layout("Kết quả đối chiếu đề tài", "".join(parts), active=PATH_FORM)
