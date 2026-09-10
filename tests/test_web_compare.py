# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Test giao diện đối chiếu đề tài (SC-13, SC-14): cris/web/views_compare.py."""
import html
import importlib
import io
import re
from urllib.parse import urlencode

import pytest

from cris.ai import embed as E
from cris.ai.provider import FakeProvider
from cris.web import wsgi
import cris.web.views_compare as views_compare  # noqa: F401  đăng ký route qua @route

ACTOR_HEADER = "HTTP_X_CRIS_USER"


def call(method, path, headers=None, body=b"", query=""):
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(body),
        "CONTENT_LENGTH": str(len(body)),
        ACTOR_HEADER: "1",
    }
    if headers:
        environ.update(headers)
    captured = {}

    def start_response(status, resp_headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = resp_headers

    result = wsgi.app(environ, start_response)
    body_bytes = b"".join(result)
    return captured["status"], dict(captured["headers"]), body_bytes.decode("utf-8", errors="replace")


def get(path, actor_id=1, query=""):
    return call("GET", path, headers={ACTOR_HEADER: str(actor_id)}, query=query)


def post(path, actor_id, fields):
    body = urlencode(fields, doseq=True, encoding="utf-8").encode("ascii")
    return call("POST", path, headers={ACTOR_HEADER: str(actor_id)}, body=body)


@pytest.fixture(autouse=True)
def clean_routes():
    saved = list(wsgi.ROUTES)
    wsgi.ROUTES.clear()
    importlib.reload(views_compare)
    yield
    wsgi.ROUTES.clear()
    wsgi.ROUTES.extend(saved)


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, abstract=None, keywords=None, doc_type="do_an"):
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,%s,'{}')", title, doc_type, title)
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, keywords_raw, "
                   "state) VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, 'DaChuanHoa') RETURNING id",
             doc_type, title, title.lower(), abstract, keywords)[0]["id"]


def test_get_form_returns_200_with_expected_fields():
    status, _, body = get("/doi-chieu")
    assert status.startswith("200")
    assert 'name="title"' in body
    assert 'name="description"' in body
    for a in ("bai_toan", "doi_tuong", "pham_vi", "phuong_phap"):
        assert f'name="{a}"' in body


def test_post_without_title_redirects_back_with_error(conn, user_id):
    status, headers, _ = post("/doi-chieu", user_id, {"title": "", "description": "x"})
    assert status.startswith("303")
    assert headers["Location"].startswith("/doi-chieu?")
    status2, _, body2 = get(headers["Location"].split("?", 1)[0], query=headers["Location"].split("?", 1)[1])
    assert status2.startswith("200")
    assert "Vui lòng nhập tên đề tài" in body2


def test_post_redirects_to_result_page_and_result_shows_note(conn, user_id):
    mk_work(conn, "Đề tài công nghệ giáo dục tiếng Anh", keywords="tiếng anh, giáo dục")
    conn.commit()

    status, headers, _ = post("/doi-chieu", user_id, {
        "title": "học tiếng Anh cho trẻ em", "description": "", "doc_types": [],
    })
    assert status.startswith("303")
    loc = headers["Location"]
    assert re.match(r"^/doi-chieu/\d+$", loc)

    status2, _, body2 = get(loc)
    assert status2.startswith("200")
    assert "không phải toàn văn" in body2


def test_result_page_shows_fallback_banner_when_ai_disabled(conn, user_id, monkeypatch):
    monkeypatch.delenv("CRIS_AI_PROVIDER", raising=False)
    mk_work(conn, "Đề tài học tiếng Anh cho trẻ em", keywords="tiếng anh, phát âm")
    conn.commit()

    status, headers, _ = post("/doi-chieu", user_id, {"title": "học tiếng Anh cho trẻ em", "description": ""})
    assert status.startswith("303")
    status2, _, body2 = get(headers["Location"])
    assert status2.startswith("200")
    assert "AI chưa bật" in body2
    assert "khớp từ khoá" in body2


def test_result_page_has_no_percent_sign_next_to_score(conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    mk_work(conn, "Đề tài công nghệ giáo dục tiếng Anh cho trẻ em")
    conn.commit()
    E.build_embeddings(conn, FakeProvider())
    conn.commit()

    status, headers, _ = post("/doi-chieu", user_id, {"title": "học tiếng Anh cho trẻ em", "description": ""})
    assert status.startswith("303")
    status2, _, body2 = get(headers["Location"])
    assert status2.startswith("200")
    result_blocks = re.findall(r'<article class="compare-result">.*?</article>', body2, re.S)
    assert result_blocks, "phải có ít nhất một khối kết quả để kiểm tra"
    assert all("%" not in block for block in result_blocks)


def test_unknown_qid_returns_404():
    status, _, body = get("/doi-chieu/999999")
    assert status.startswith("404")
    assert "<!doctype html>" in body.lower()


def test_script_tag_in_work_title_is_escaped_not_executed(conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    mk_work(conn, "Đề tài <script>alert(1)</script> tiếng Anh cho trẻ em")
    conn.commit()
    E.build_embeddings(conn, FakeProvider())
    conn.commit()

    status, headers, _ = post("/doi-chieu", user_id, {"title": "học tiếng Anh cho trẻ em", "description": ""})
    assert status.startswith("303")
    status2, _, body2 = get(headers["Location"])
    assert status2.startswith("200")
    assert "<script>alert(1)</script>" not in body2
    assert "&lt;script&gt;" in body2


def test_rerun_link_prefills_form(conn, user_id, monkeypatch):
    monkeypatch.delenv("CRIS_AI_PROVIDER", raising=False)
    mk_work(conn, "Đề tài học tiếng Anh cho trẻ em")
    conn.commit()

    status, headers, _ = post("/doi-chieu", user_id, {
        "title": "học tiếng Anh cho trẻ em", "description": "mô tả demo", "bai_toan": "phát âm",
    })
    status2, _, body2 = get(headers["Location"])
    assert status2.startswith("200")
    m = re.search(r'href="(/doi-chieu\?[^"]*)"', body2)
    assert m, "phải có nút chạy lại trỏ về biểu mẫu"
    rerun_href = html.unescape(m.group(1))  # href trong HTML đã qua e(): "&amp;" cần giải mã lại
    rerun_path, _, rerun_query = rerun_href.partition("?")
    status3, _, body3 = get(rerun_path, query=rerun_query)
    assert status3.startswith("200")
    assert "học tiếng Anh cho trẻ em" in body3
    assert "mô tả demo" in body3
    assert "phát âm" in body3
