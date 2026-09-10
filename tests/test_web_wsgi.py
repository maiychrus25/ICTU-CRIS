# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import io

import pytest

from cris.web import wsgi
from cris.web.render import e
from cris.web.wsgi import Redirect, route


def call(app, method, path, headers=None, body=b"", query=""):
    """Dựng environ WSGI giả, gọi app, trả (status, headers, body_text)."""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(body),
        "CONTENT_LENGTH": str(len(body)),
        # Mặc định khai actor qua header để các test định tuyến không phụ
        # thuộc vào có sẵn người dùng rd_officer nào trong DB.
        "HTTP_X_CRIS_USER": "1",
    }
    if headers:
        environ.update(headers)
    captured = {}

    def start_response(status, resp_headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = resp_headers

    result = app(environ, start_response)
    body_bytes = b"".join(result)
    return captured["status"], captured["headers"], body_bytes.decode("utf-8", errors="replace")


@pytest.fixture(autouse=True)
def clean_routes():
    """Cô lập ROUTES cho từng test: xoá, cho test tự đăng ký, rồi khôi phục."""
    saved = list(wsgi.ROUTES)
    wsgi.ROUTES.clear()
    yield
    wsgi.ROUTES.clear()
    wsgi.ROUTES.extend(saved)


def test_route_matches_and_int_param_is_cast():
    @route("GET", "/x/<int:pid>/<str:slug>")
    def h(req, pid, slug):
        return f"pid={pid!r} slug={slug!r} kind={type(pid).__name__}"

    status, _, body = call(wsgi.app, "GET", "/x/42/ten-bai")
    assert status.startswith("200")
    assert "pid=42" in body
    assert "slug='ten-bai'" in body
    assert "kind=int" in body


def test_unknown_path_returns_404_with_layout_and_no_traceback():
    status, _, body = call(wsgi.app, "GET", "/khong-ton-tai")
    assert status.startswith("404")
    assert "<!doctype html>" in body.lower()
    assert "Traceback" not in body


def test_wrong_method_returns_405():
    @route("GET", "/chi-get")
    def h(req):
        return "ok"

    status, _, body = call(wsgi.app, "POST", "/chi-get")
    assert status.startswith("405")
    assert "<!doctype html>" in body.lower()


def test_handler_exception_returns_500_without_leaking_traceback(capsys):
    @route("GET", "/loi")
    def h(req):
        raise ValueError("boom-chi-tiet-noi-bo")

    status, _, body = call(wsgi.app, "GET", "/loi")
    assert status.startswith("500")
    assert "boom-chi-tiet-noi-bo" not in body
    assert "Traceback" not in body
    assert "ValueError" not in body
    err = capsys.readouterr().err
    assert "boom-chi-tiet-noi-bo" in err
    assert "Traceback" in err


def test_redirect_returns_303_with_location_header():
    @route("GET", "/di")
    def h(req):
        return Redirect("/dich-den")

    status, headers, _ = call(wsgi.app, "GET", "/di")
    assert status.startswith("303")
    assert dict(headers)["Location"] == "/dich-den"


def test_e_escapes_script_tags_quotes_and_none():
    assert "<script>" not in e("<script>alert(1)</script>")
    assert "&lt;script&gt;" in e("<script>alert(1)</script>")
    assert e('Tên "đặc biệt"') == "Tên &quot;đặc biệt&quot;"
    assert e(None) == ""


def test_form_list_returns_multiple_values_for_same_key():
    @route("POST", "/lo")
    def h(req):
        return ",".join(req.form_list("link_id"))

    status, _, body = call(wsgi.app, "POST", "/lo", body=b"link_id=1&link_id=2&link_id=3")
    assert status.startswith("200")
    assert body == "1,2,3"


def test_form_is_flattened_taking_last_value():
    @route("POST", "/flat")
    def h(req):
        return req.form.get("decision", "")

    status, _, body = call(wsgi.app, "POST", "/flat", body=b"decision=confirm&decision=reject")
    assert status.startswith("200")
    assert body == "reject"


def test_query_string_is_parsed_into_dict():
    @route("GET", "/tim")
    def h(req):
        return req.query.get("q", "")

    status, _, body = call(wsgi.app, "GET", "/tim", query="q=nguyen+van+a")
    assert status.startswith("200")
    assert body == "nguyen van a"


def test_actor_id_taken_from_header_when_present():
    @route("GET", "/ai")
    def h(req):
        return str(req.actor_id)

    status, _, body = call(wsgi.app, "GET", "/ai", headers={"HTTP_X_CRIS_USER": "7"})
    assert status.startswith("200")
    assert body == "7"


def test_actor_id_falls_back_to_rd_officer_user(user_id):
    @route("GET", "/ai-mac-dinh")
    def h(req):
        return str(req.actor_id)

    status, _, body = call(wsgi.app, "GET", "/ai-mac-dinh", headers={"HTTP_X_CRIS_USER": ""})
    assert status.startswith("200")
    assert body == str(user_id)


def test_actor_missing_returns_503_with_vietnamese_instructions():
    @route("GET", "/can-nguoi-dung")
    def h(req):
        return "khong toi day"

    status, _, body = call(wsgi.app, "GET", "/can-nguoi-dung", headers={"HTTP_X_CRIS_USER": ""})
    assert status.startswith("503")
    assert "rd_officer" in body
    assert "khong toi day" not in body
