# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import importlib
import io

import pytest

from cris import quality, sync
from cris.web import wsgi
import cris.web.views_quality as views_quality  # noqa: F401  đăng ký route qua @route


def call(app, method, path, headers=None, body=b"", query=""):
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(body),
        "CONTENT_LENGTH": str(len(body)),
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
    saved = list(wsgi.ROUTES)
    wsgi.ROUTES.clear()
    importlib.reload(views_quality)
    yield
    wsgi.ROUTES.clear()
    wsgi.ROUTES.extend(saved)


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def test_quality_report_shows_counts_from_quality_module(conn):
    q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) VALUES ('manual','t','ok',now())")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (1,'manual','a','bai_bao','h','{}'),(1,'manual','b','bai_bao','h','{}')")
    q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state, needs_review) "
            "VALUES ('bai_bao',1,'A','a','DaChuanHoa',true),('bai_bao',2,'B','b','DaChuanHoa',false)")
    q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, is_placeholder) "
            "VALUES (1,'author',1,'X Y','x y','x y',false),(2,'mentor',1,'ICTU_TEACHER','ictu_teacher','ictu_teacher',true)")
    q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) VALUES ('lecturer','X Y','x y', ARRAY['x y'])")
    q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) VALUES (1,1,'ten_day_du_duy_nhat','DaNoiTuDong')")
    conn.commit()

    expected = quality.report(conn)

    status, _, body = call(wsgi.app, "GET", "/chat-luong-du-lieu")
    assert status.startswith("200")
    assert str(expected["works"]) in body
    assert str(expected["works_needs_review"]) in body
    assert str(expected["mentions_placeholder"]) in body
    assert str(expected["links_auto"]) in body
    assert f"{expected['works_with_link_pct']}" in body


def test_quality_report_metrics_link_to_review_queues(conn):
    conn.commit()
    status, _, body = call(wsgi.app, "GET", "/chat-luong-du-lieu")
    assert status.startswith("200")
    assert 'href="/doi-soat/tac-gia"' in body
    assert 'href="/doi-soat/trung-lap"' in body


def test_quality_report_shows_last_sync_count_mismatch_warning(conn):
    rid = sync.run_sync(conn, source="repository", scope="do-an", doc_type="do_an",
                        records=[("u1", {})], expected=12, full=True)
    conn.commit()

    status, _, body = call(wsgi.app, "GET", "/chat-luong-du-lieu")
    assert status.startswith("200")
    assert "lệch số lượng" in body.lower()
    assert "12" in body and "1" in body


def test_quality_report_no_sync_yet(conn):
    status, _, body = call(wsgi.app, "GET", "/chat-luong-du-lieu")
    assert status.startswith("200")
    assert "chưa có lần đồng bộ" in body.lower()
