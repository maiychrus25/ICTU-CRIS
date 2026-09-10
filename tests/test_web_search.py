# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import importlib
import io
import itertools
import json
from urllib.parse import urlencode

import pytest

from cris import rules
from cris.web import wsgi
import cris.web.views_search as views_search  # noqa: F401  đăng ký route qua @route

_seq = itertools.count()


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
    importlib.reload(views_search)
    yield
    wsgi.ROUTES.clear()
    wsgi.ROUTES.extend(saved)


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def _mk_sync_raw(conn, status, source, scope, finished, added, changed, vanished, warnings):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO sync_run(source, scope, status, started_at, finished_at, added, changed, vanished, warnings)
               VALUES (%s,%s,%s, now(), CASE WHEN %s THEN now() ELSE NULL END, %s,%s,%s, %s) RETURNING id""",
            (source, scope, status, finished, added, changed, vanished, json.dumps(warnings or [])),
        )
        return cur.fetchone()["id"]


def mk_work(conn, sync_id, title, doc_type="bai_bao", doi=None, year=None, journal=None):
    key = f"{doc_type}/{title}/{next(_seq)}"
    q(
        conn,
        "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) VALUES (%s,'manual',%s,%s,'h','{}')",
        sync_id, key, doc_type,
    )
    return q(
        conn,
        """INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, doi, year_issue, journal, state)
           VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, %s, 'DaChuanHoa') RETURNING id""",
        doc_type, title, rules.norm_title(title), doi, year, journal,
    )[0]["id"]


def mk_mention(conn, work_id, raw, role="author", position=1):
    nb = rules.RULES_V1["name_norm"]
    nn, deg = rules.norm_name(raw, nb)
    return q(
        conn,
        """INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, degree_raw)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        work_id, role, position, raw, nn, rules.name_key(nn), deg,
    )[0]["id"]


def mk_person(conn, name, unit_id=None, email=None, orcid=None, kind="lecturer"):
    nb = rules.RULES_V1["name_norm"]
    nn, _ = rules.norm_name(name, nb)
    return q(
        conn,
        """INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id, email, orcid)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        kind, name, nn, [rules.name_key(nn)], unit_id, email, orcid,
    )[0]["id"]


def mk_link(conn, mention_id, person_id, state="DaXacNhan", confidence="ten_day_du_duy_nhat"):
    return q(
        conn,
        """INSERT INTO author_link(mention_id, person_id, confidence, state, decided_at)
           VALUES (%s,%s,%s,%s, now()) RETURNING id""",
        mention_id, person_id, confidence, state,
    )[0]["id"]


def mk_prov(conn, work_id, field, raw_value, value, set_kind="normalize", source_record_id=None, set_by=None):
    return q(
        conn,
        """INSERT INTO field_provenance(work_id, field, raw_value, value, source_record_id, set_kind, set_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        work_id, field, raw_value, value, source_record_id, set_kind, set_by,
    )[0]["id"]


def test_home_redirects_to_tra_cuu():
    status, headers, _ = call(wsgi.app, "GET", "/")
    assert status.startswith("303")
    assert dict(headers)["Location"] == "/tra-cuu"


def test_search_by_title_matches(conn):
    sid = _mk_sync_raw(conn, "ok", "manual", "t", True, 0, 0, 0, None)
    mk_work(conn, sid, "Học sâu cho ảnh y tế", doc_type="bai_bao", year=2025)
    mk_work(conn, sid, "Một chủ đề khác hoàn toàn", doc_type="bai_bao", year=2024)
    conn.commit()

    status, _, body = call(wsgi.app, "GET", "/tra-cuu", query=urlencode({"q": "học sâu"}))
    assert status.startswith("200")
    assert "Học sâu cho ảnh y tế" in body
    assert "Một chủ đề khác hoàn toàn" not in body


def test_search_by_author_name_matches(conn):
    sid = _mk_sync_raw(conn, "ok", "manual", "t", True, 0, 0, 0, None)
    w1 = mk_work(conn, sid, "Bài viết A", year=2025)
    mk_work(conn, sid, "Bài viết B", year=2025)
    mk_mention(conn, w1, "Nguyễn Văn Tác Giả")
    conn.commit()

    status, _, body = call(wsgi.app, "GET", "/tra-cuu", query=urlencode({"q": "Nguyễn Văn Tác Giả"}))
    assert status.startswith("200")
    assert "Bài viết A" in body
    assert "Bài viết B" not in body


def test_search_doc_type_filter_narrows(conn):
    sid = _mk_sync_raw(conn, "ok", "manual", "t", True, 0, 0, 0, None)
    mk_work(conn, sid, "Công trình bài báo", doc_type="bai_bao", year=2025)
    mk_work(conn, sid, "Công trình đồ án", doc_type="do_an", year=2025)
    conn.commit()

    status, _, body = call(wsgi.app, "GET", "/tra-cuu", query="doc_type=do_an")
    assert status.startswith("200")
    assert "Công trình đồ án" in body
    assert "Công trình bài báo" not in body


def test_work_detail_shows_current_raw_and_source_columns(conn):
    sid = _mk_sync_raw(conn, "ok", "manual", "t", True, 0, 0, 0, None)
    wid = mk_work(conn, sid, "Tiêu đề chuẩn hoá", doi="10.1/abc", year=2025)
    mk_prov(conn, wid, "title", "Tieu de tho tu nguon", "Tiêu đề chuẩn hoá", set_kind="normalize", source_record_id=1)
    mention_id = mk_mention(conn, wid, "Trần Văn X")
    pid = mk_person(conn, "Trần Văn X")
    mk_link(conn, mention_id, pid, state="DaXacNhan")
    conn.commit()

    status, _, body = call(wsgi.app, "GET", f"/tra-cuu/cong-trinh/{wid}")
    assert status.startswith("200")
    assert "Tiêu đề chuẩn hoá" in body  # giá trị đang dùng
    assert "Tieu de tho tu nguon" in body  # giá trị gốc
    assert "manual" in body or "Đồng bộ từ" in body  # cột nguồn có mô tả nguồn
    assert "Trần Văn X" in body
    assert "Đã xác nhận" in body


def test_work_detail_unknown_wid_returns_404(conn):
    status, _, body = call(wsgi.app, "GET", "/tra-cuu/cong-trinh/999999")
    assert status.startswith("404")
    assert "<!doctype html>" in body.lower()


def test_person_profile_unknown_pid_returns_404(conn):
    status, _, body = call(wsgi.app, "GET", "/tra-cuu/giang-vien/999999")
    assert status.startswith("404")
    assert "<!doctype html>" in body.lower()


def test_person_profile_shows_last_sync_and_unconfirmed_count(conn):
    sid = _mk_sync_raw(conn, "ok", "manual", "t", True, 0, 0, 0, None)
    wid = mk_work(conn, sid, "Bài đã xác nhận", year=2025)
    wid2 = mk_work(conn, sid, "Bài đang chờ xác nhận", year=2025)
    pid = mk_person(conn, "Phạm Thị Hồ Sơ")
    m1 = mk_mention(conn, wid, "Phạm Thị Hồ Sơ")
    m2 = mk_mention(conn, wid2, "Phạm Thị Hồ Sơ")
    mk_link(conn, m1, pid, state="DaXacNhan")
    mk_link(conn, m2, pid, state="ChoXacNhan")
    conn.commit()

    status, _, body = call(wsgi.app, "GET", f"/tra-cuu/giang-vien/{pid}")
    assert status.startswith("200")
    assert "Đồng bộ gần nhất" in body
    assert "còn 1 công trình nghi thuộc người này" in body.lower()
    assert "Bài đã xác nhận" in body


def test_person_profile_no_pending_line_when_zero(conn):
    sid = _mk_sync_raw(conn, "ok", "manual", "t", True, 0, 0, 0, None)
    wid = mk_work(conn, sid, "Bài đã xác nhận riêng", year=2025)
    pid = mk_person(conn, "Đỗ Văn Riêng")
    m1 = mk_mention(conn, wid, "Đỗ Văn Riêng")
    mk_link(conn, m1, pid, state="DaXacNhan")
    conn.commit()

    status, _, body = call(wsgi.app, "GET", f"/tra-cuu/giang-vien/{pid}")
    assert status.startswith("200")
    assert "chưa được xác nhận" not in body.lower()
