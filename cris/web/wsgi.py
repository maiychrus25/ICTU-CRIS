# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Khung WSGI thuần stdlib (không framework): router, Request/Response, `app()`.

GIỚI HẠN PHẠM VI — QUAN TRỌNG: mô-đun này KHÔNG triển khai đăng nhập thật, phiên
đăng nhập, hay phân quyền theo vai trò/đơn vị. Đó là NFR-01 và NFR-02, nằm NGOÀI
phạm vi lát cắt giao diện này. `actor_id` của một yêu cầu được suy ra theo thứ tự:

1. Header `X-CRIS-User` (một id số) nếu client tự khai — dùng cho test và cho môi
   trường vận hành thủ công khi biết trước id người dùng.
2. Nếu không có header đó: người dùng `app_user` đầu tiên (theo `id`) đang
   `active` và có vai trò `rd_officer`, coi là "người trực" mặc định của môi
   trường phát triển.
3. Nếu không tìm được ai: trả `503` kèm hướng dẫn tạo người dùng bằng SQL.

Mô-đun này chỉ dùng cho môi trường phát triển/nội bộ. KHÔNG triển khai lên mạng
công cộng khi chưa có đăng nhập thật.

Đăng ký route: mỗi `views_*.py` dùng decorator `@route(method, pattern)` để tự
đăng ký handler của mình vào `ROUTES` — các nhóm màn hình không tranh nhau sửa
cùng một bảng route. `wsgi.py` không phụ thuộc vào nội dung của các `views_*.py`;
việc import chúng (để decorator chạy) là trách nhiệm của bước ráp nối cuối cùng.
"""
import functools
import re
import sys
import traceback
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from cris import db
from cris.web.render import e, layout

MAX_BODY = 1024 * 1024  # 1 MiB, giới hạn đọc thân yêu cầu

ROUTES: list[tuple[str, str, callable]] = []

_PARAM_RE = re.compile(r"<(int|str):([a-zA-Z_][a-zA-Z0-9_]*)>")

_REASON = {
    200: "OK",
    303: "See Other",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
    503: "Service Unavailable",
}

_ERROR_MESSAGES = {
    404: ("Không tìm thấy", "Không tìm thấy đường dẫn được yêu cầu."),
    405: ("Không hỗ trợ phương thức", "Phương thức HTTP này không được hỗ trợ cho đường dẫn đó."),
    500: ("Lỗi máy chủ", "Đã có lỗi xảy ra ở máy chủ. Vui lòng thử lại sau."),
}


def route(method, pattern):
    """Decorator: đăng ký (method, pattern, handler) vào ROUTES.

    `pattern` hỗ trợ tham số kiểu `<int:name>` và `<str:name>`, ví dụ
    `/tra-cuu/giang-vien/<int:pid>`. Handler nhận `(req, **kwargs)` với các
    tham số đã ép kiểu, và trả về `str` (HTML, 200), `(status, headers, body)`,
    hoặc `Redirect(path)`.
    """
    method = method.upper()

    def deco(fn):
        ROUTES.append((method, pattern, fn))
        return fn

    return deco


class Redirect:
    """Kết quả handler yêu cầu chuyển hướng post/redirect/get: sinh `303 See Other`."""

    def __init__(self, path):
        self.path = path


class Request:
    """Yêu cầu HTTP đã phân tích.

    `query` và `form` là các dict phẳng hoá (lấy giá trị cuối khi có nhiều giá
    trị cùng tên). Dùng `form_list(key)` để lấy đủ danh sách giá trị — cần cho
    thao tác hàng loạt (chọn nhiều `link_id`, ...).
    """

    def __init__(self, environ, conn, actor_id=None):
        self.environ = environ
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.path = environ.get("PATH_INFO", "/") or "/"
        self.query = _flatten(parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True))
        self._form_multi = _read_form(environ)
        self.form = _flatten(self._form_multi)
        self.conn = conn
        self.actor_id = actor_id

    def form_list(self, key):
        return list(self._form_multi.get(key, []))


def _flatten(multi):
    return {k: v[-1] for k, v in multi.items() if v}


def _read_form(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    if length <= 0:
        return {}
    length = min(length, MAX_BODY)
    stream = environ.get("wsgi.input")
    raw = stream.read(length) if stream is not None else b""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return parse_qs(raw.decode("utf-8", errors="replace"), keep_blank_values=True)


@functools.lru_cache(maxsize=None)
def _compile(pattern):
    parts = []
    converters = {}
    last = 0
    for m in _PARAM_RE.finditer(pattern):
        parts.append(re.escape(pattern[last:m.start()]))
        kind, name = m.group(1), m.group(2)
        parts.append(f"(?P<{name}>-?\\d+)" if kind == "int" else f"(?P<{name}>[^/]+)")
        converters[name] = kind
        last = m.end()
    parts.append(re.escape(pattern[last:]))
    return re.compile("^" + "".join(parts) + "$"), tuple(converters.items())


def _find(method, path):
    """Tìm route khớp `path`. Trả (handler, kwargs, path_matched_any_method)."""
    path_ok = False
    for m, pattern, handler in ROUTES:
        rx, converters = _compile(pattern)
        mo = rx.match(path)
        if not mo:
            continue
        path_ok = True
        if m != method:
            continue
        kwargs = {name: (int(mo.group(name)) if kind == "int" else mo.group(name)) for name, kind in converters}
        return handler, kwargs, True
    return None, None, path_ok


def _error_page(status):
    title, msg = _ERROR_MESSAGES.get(status, ("Lỗi", "Đã có lỗi xảy ra."))
    return layout(title, f'<p class="error-page">{e(msg)}</p>')


def _resolve_actor(environ, conn):
    """Suy ra actor_id. Trả (actor_id, None) hoặc (None, (status, body))."""
    header = environ.get("HTTP_X_CRIS_USER")
    if header:
        try:
            return int(header), None
        except ValueError:
            pass
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM app_user WHERE active AND %s = ANY(roles) ORDER BY id LIMIT 1",
            ("rd_officer",),
        )
        row = cur.fetchone()
    if row:
        return row["id"], None
    msg = (
        "Chưa có người dùng nào có vai trò 'rd_officer' để ghi nhận thao tác. "
        "Hãy tạo một người dùng, ví dụ: INSERT INTO app_user(email, display_name, roles) "
        "VALUES ('ten@ictu.edu.vn', 'Tên hiển thị', ARRAY['rd_officer']);"
    )
    body = layout("Chưa sẵn sàng", f'<p class="error-page">{e(msg)}</p>')
    return None, (503, body)


def _send(start_response, status, body, extra_headers=None):
    data = body.encode("utf-8") if isinstance(body, str) else (body or b"")
    headers = [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(data)))]
    if extra_headers:
        headers = headers + list(extra_headers)
    start_response(f"{status} {_REASON.get(status, '')}".strip(), headers)
    return [data]


def _emit(start_response, result):
    if isinstance(result, Redirect):
        return _send(start_response, 303, "", extra_headers=[("Location", result.path)])
    if isinstance(result, tuple):
        status, headers, body = result
        return _send(start_response, status, body, extra_headers=headers)
    return _send(start_response, 200, result)


def app(environ, start_response):
    """WSGI callable. Một `psycopg.connect` cho mỗi yêu cầu khớp route, đóng ở `finally`."""
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/") or "/"
    try:
        handler, kwargs, path_ok = _find(method, path)
        if handler is None:
            status = 405 if path_ok else 404
            return _send(start_response, status, _error_page(status))
        conn = db.connect()
        try:
            actor_id, err = _resolve_actor(environ, conn)
            if err is not None:
                return _send(start_response, *err)
            req = Request(environ, conn, actor_id)
            result = handler(req, **kwargs)
            conn.commit()
            return _emit(start_response, result)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return _send(start_response, 500, _error_page(500))


def serve(host="127.0.0.1", port=8000):
    """Chạy máy chủ phát triển `wsgiref` (chặn cho tới Ctrl+C)."""
    httpd = make_server(host, port, app)
    print(f"Đang chạy tại http://{host}:{port}/", file=sys.stderr)
    print(
        "CẢNH BÁO: đây là máy chủ phát triển (wsgiref), không dùng cho môi trường vận hành.",
        file=sys.stderr,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


# Nạp các module view ở CUỐI tệp, sau khi `route` đã được định nghĩa: mỗi module
# `import ... route` ngược lại wsgi, nên đặt sớm hơn sẽ vòng lặp nhập. Đây là
# nhập lấy tác dụng phụ — chính hành vi nhập làm đầy ROUTES.
from cris.web import views_compare as _views_compare  # noqa: E402,F401
from cris.web import views_dedup as _views_dedup      # noqa: E402,F401
from cris.web import views_quality as _views_quality  # noqa: E402,F401
from cris.web import views_queue as _views_queue      # noqa: E402,F401
from cris.web import views_search as _views_search    # noqa: E402,F401
