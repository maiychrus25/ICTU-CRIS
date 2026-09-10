# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Báo cáo chất lượng dữ liệu (SC-10) — trình bày `cris.quality.report`, không
tính lại các chỉ số: mọi con số đến từ `quality.report(conn)`."""
from cris import quality
from cris.web.render import badge, e, layout, table
from cris.web.wsgi import route

DOC_TYPE_LABELS = {
    "bai_bao": "Bài báo",
    "do_an": "Đồ án",
    "luan_van": "Luận văn",
    "luan_an": "Luận án",
    "hoc_lieu": "Học liệu",
    "giang_vien": "Giảng viên",
    "dang_ky_do_an": "Đăng ký đồ án",
}

# (khoá trong quality.report, nhãn tiếng Việt, đường dẫn hàng đợi liên quan hoặc None)
METRICS = [
    ("works", "Tổng số công trình", None),
    ("works_needs_review", "Công trình cần rà soát (nghi trùng/loại chưa rõ)", "/doi-soat/trung-lap"),
    ("mentions", "Tổng số lượt tên tác giả (author_mention)", None),
    ("mentions_placeholder", "Lượt tên giữ chỗ (không xác định được người)", "/doi-soat/tac-gia"),
    ("mentions_truncated", "Lượt tên bị cắt ngắn ở nguồn", "/doi-soat/tac-gia"),
    ("links_auto", "Liên kết tác giả đã nối tự động", None),
    ("links_queued", "Liên kết tác giả đang chờ xác nhận", "/doi-soat/tac-gia"),
    ("links_confirmed", "Liên kết tác giả đã xác nhận thủ công", None),
    ("works_with_link", "Công trình có ít nhất một tác giả đã liên kết", "/doi-soat/tac-gia"),
    ("works_without_unit", "Công trình chưa xác định được đơn vị", "/doi-soat/tac-gia"),
    ("dup_groups_open", "Nhóm nghi trùng đang chờ xử lý", "/doi-soat/trung-lap"),
]


def _fmt_dt(v):
    if v is None:
        return None
    try:
        return v.strftime("%d/%m/%Y %H:%M")
    except AttributeError:
        return str(v)


@route("GET", "/chat-luong-du-lieu")
def data_quality_report(req):
    r = quality.report(req.conn)

    rows = []
    for key, label, link in METRICS:
        value = r.get(key)
        if key == "works_with_link":
            value_text = f"{value} ({e(r.get('works_with_link_pct'))}%)"
        else:
            value_text = e(value)
        cell = f'<a href="{e(link)}">{value_text}</a>' if link else value_text
        rows.append([e(label), cell])
    metrics_table = table(["Chỉ số", "Giá trị"], rows)

    type_rows = [[e(DOC_TYPE_LABELS.get(k, k)), e(v)] for k, v in sorted((r.get("works_by_type") or {}).items())]
    by_type_table = table(["Loại công trình", "Số lượng"], type_rows)

    last_sync = r.get("last_sync")
    if last_sync is None:
        sync_body = "<p>Chưa có lần đồng bộ nào.</p>"
    else:
        status_kind = {"ok": "ok", "warning": "warn", "failed": "danger"}.get(last_sync["status"], "default")
        sync_body = (
            f"<p>Lần đồng bộ gần nhất: nguồn {e(last_sync['source'])}/{e(last_sync['scope'])}, "
            f"bắt đầu {e(_fmt_dt(last_sync['started_at']))}, "
            f"kết thúc {e(_fmt_dt(last_sync['finished_at'])) if last_sync['finished_at'] else 'chưa xong'} — "
            f"{badge(last_sync['status'], status_kind)}. "
            f"Thêm mới {e(last_sync['added'])}, thay đổi {e(last_sync['changed'])}, biến mất {e(last_sync['vanished'])}.</p>"
        )
        warnings = last_sync.get("warnings") or []
        if warnings:
            warn_items = "".join(
                f"<li>{badge('lệch số lượng', 'warn')} loại "
                f"{e(w.get('doc_type'))}: kỳ vọng {e(w.get('expected'))}, lấy được {e(w.get('fetched'))}.</li>"
                for w in warnings
            )
            sync_body += f"<ul class='sync-warnings'>{warn_items}</ul>"

    body = (
        "<h2>Chỉ số tổng quan</h2>"
        + metrics_table
        + "<h2>Theo loại công trình</h2>"
        + by_type_table
        + "<h2>Lần đồng bộ gần nhất</h2>"
        + sync_body
    )
    return layout("Chất lượng dữ liệu", body, active="/chat-luong-du-lieu")
