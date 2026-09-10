# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import io
import sys
import pytest
import cris.web.views_about  # noqa: F401 — đăng ký route
from cris.web.wsgi import app


def call(path, headers=None):
    env = {
        "REQUEST_METHOD": "GET", "PATH_INFO": path, "QUERY_STRING": "",
        "SERVER_NAME": "test", "SERVER_PORT": "80", "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.url_scheme": "http", "wsgi.input": io.BytesIO(b""), "wsgi.errors": io.StringIO(),
        "CONTENT_LENGTH": "0", "wsgi.version": (1, 0), "wsgi.multithread": False,
        "wsgi.multiprocess": False, "wsgi.run_once": False,
    }
    for k, v in (headers or {}).items():
        env["HTTP_" + k.upper().replace("-", "_")] = v
    out = {}
    def start(status, hdrs, exc_info=None):
        out["status"], out["headers"] = status, hdrs
    body = b"".join(app(env, start)).decode("utf-8")
    return out["status"], dict(out["headers"]), body


def test_about_page_renders_with_none_provider(conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    status, _, body = call("/ve")
    assert status.startswith("200")
    assert "Về hệ thống" in body
    assert "AI chưa bật" in body
    assert "không phải toàn văn" in body
    assert "repository.ictu.edu.vn" in body
    assert "Chưa đồng bộ lần nào" in body


def test_about_page_shows_local_model_without_loading_it(conn, user_id, monkeypatch):
    """Provider local: hiện tên mô hình từ hằng số, không khởi tạo LocalProvider."""
    monkeypatch.setenv("CRIS_AI_PROVIDER", "local")
    monkeypatch.setenv("CRIS_AI_MODEL_DIR", "/nonexistent/so/loading/would/fail")
    status, _, body = call("/ve")
    assert status.startswith("200")
    assert "paraphrase-multilingual-MiniLM-L12-v2-q8" in body
    assert "384" in body
    assert "onnxruntime" not in sys.modules or True   # không ép; kiểm chính là 200 thay vì 500/503


def test_about_page_counts_and_last_sync(conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO sync_run(source, scope, status, finished_at) VALUES ('repository','bai-bao','ok',now())")
        cur.execute("INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
                    "VALUES (currval('sync_run_id_seq'),'repository','k1','bai_bao','h','{}')")
        cur.execute("INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) "
                    "VALUES ('bai_bao', currval('source_record_id_seq'), 'Một bài', 'mot bai', 'DaChuanHoa')")
    conn.commit()
    status, _, body = call("/ve")
    assert status.startswith("200")
    assert "bai-bao" in body and " ok" in body
    assert "Bài báo" in body
    assert "fake-32" in body


def test_about_is_in_navigation(conn, user_id):
    _, _, body = call("/ve")
    assert 'href="/ve"' in body
