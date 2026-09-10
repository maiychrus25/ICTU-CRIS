# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Nội suy HTML an toàn và các thành phần dùng chung — không dùng thư viện template.

Mọi giá trị không do chính mô-đun này tạo ra (tên người, tiêu đề công trình, dữ liệu
từ nguồn ngoài, tham số truy vấn, ...) PHẢI đi qua `e()` trước khi ghép vào HTML.
`table()`, `badge()`, `pager()` ghép chuỗi HTML mà chúng nhận được như đã an toàn —
người gọi chịu trách nhiệm tự `e()` các ô dữ liệu thô trước khi truyền vào.
"""
import html

from cris.web.static import CSS


def e(x):
    """html.escape(str(x), quote=True); None thành chuỗi rỗng."""
    if x is None:
        return ""
    return html.escape(str(x), quote=True)


NAV_ITEMS = [
    ("/doi-soat/tac-gia", "Hàng đợi tác giả"),
    ("/doi-soat/trung-lap", "Hàng đợi nghi trùng"),
    ("/tra-cuu", "Tra cứu"),
    ("/chat-luong-du-lieu", "Chất lượng dữ liệu"),
    ("/doi-chieu", "Đối chiếu đề tài"),
    ("/ve", "Về hệ thống"),
]


def layout(title, body, active=None):
    """Khung trang chung: doctype, lang=vi, thanh điều hướng, CSS nhúng.

    `title` được escape. `body` được chèn nguyên văn — người gọi phải tự đảm bảo
    mọi nội dung động bên trong `body` đã qua `e()`.
    """
    links = []
    for href, label in NAV_ITEMS:
        cls = ' class="active"' if href == active else ""
        links.append(f'<a href="{e(href)}"{cls}>{e(label)}</a>')
    nav = "".join(links)
    safe_title = e(title)
    return (
        "<!doctype html>\n"
        '<html lang="vi">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{safe_title} — ICTU-CRIS</title>\n"
        f"<style>{CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '<header class="site-header">\n'
        '<strong class="brand">ICTU-CRIS</strong>\n'
        f"<nav>{nav}</nav>\n"
        "</header>\n"
        "<main>\n"
        f"<h1>{safe_title}</h1>\n"
        f"{body}\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


def table(headers, rows):
    """Bảng HTML cuộn ngang trong khung riêng.

    `headers` được escape tự động. Mỗi phần tử của `rows` là một chuỗi HTML sẵn
    sàng cho từng ô (đã qua `e()` hoặc `badge()`/liên kết do người gọi dựng) —
    `table()` không escape lại các ô.
    """
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    if not rows:
        body = f'<tr><td colspan="{max(1, len(headers))}" class="empty">Không có dữ liệu.</td></tr>'
    else:
        body = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
        )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def badge(text, kind="default"):
    """Nhãn nhỏ, ví dụ trạng thái hoặc mức độ tin cậy. `kind`: ok|warn|danger|default."""
    kind = kind if kind in ("ok", "warn", "danger", "default") else "default"
    return f'<span class="badge badge-{kind}">{e(text)}</span>'


def pager(page, total, per, base_url):
    """Điều hướng phân trang, sinh liên kết `?page=N` (hoặc `&page=N` nếu
    `base_url` đã có tham số truy vấn khác)."""
    per = max(1, per)
    pages = max(1, (total + per - 1) // per)
    if pages <= 1:
        return ""
    sep = "&" if "?" in base_url else "?"

    def link(target_page, label, disabled):
        if disabled:
            return f'<span class="pager-link disabled">{e(label)}</span>'
        return f'<a class="pager-link" href="{e(base_url)}{sep}page={target_page}">{e(label)}</a>'

    parts = [
        link(page - 1, "« Trước", page <= 1),
        f'<span class="pager-status">Trang {e(page)}/{e(pages)}</span>',
        link(page + 1, "Sau »", page >= pages),
    ]
    return f'<nav class="pager">{"".join(parts)}</nav>'
