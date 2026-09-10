# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import io
import itertools
from urllib.parse import urlencode

import pytest

import cris.web.views_queue  # noqa: F401  # đăng ký route vào wsgi.ROUTES
from cris.ai import suggest as S
from cris.ai.provider import FakeProvider
from cris.web import wsgi

_seq = itertools.count()


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title=None, abstract=None):
    title = title or f"Công trình {next(_seq)}"
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,'do_an',%s,'{}')", title, title)
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, state) "
                   "VALUES ('do_an', currval('source_record_id_seq'), %s, %s, %s, 'DaChuanHoa') RETURNING id",
             title, title.lower(), abstract)[0]["id"]


def mk_person(conn, name):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) VALUES ('lecturer',%s,%s,%s) "
                   "RETURNING id", name, name.lower(), [name.lower()])[0]["id"]


def mk_mention(conn, work_id, raw="Tac gia", position=1):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw, raw.lower(), raw.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, basis, state) "
                   "VALUES (%s,%s,'ten_mot_phan','{}',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


def mk_group(conn, basis, work_ids, doc_type="do_an"):
    gid = q(conn, "INSERT INTO duplicate_group(doc_type, basis) VALUES (%s,%s) RETURNING id",
            doc_type, basis)[0]["id"]
    for wid in work_ids:
        q(conn, "INSERT INTO duplicate_member(group_id, work_id) VALUES (%s,%s)", gid, wid)
    return gid


def _counts(conn):
    return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"]
            for t in ("work", "author_link", "duplicate_group")}


def _seed_candidates(conn):
    """Một mention mới với 3 ứng viên: P1 có công trình đã xác nhận cùng chủ đề
    (tiếng Anh), P2 có công trình đã xác nhận nhưng khác chủ đề (IoT), P3 chưa
    có công trình đã xác nhận nào. Trả (l1, l2, l3)."""
    w1 = mk_work(conn, abstract="hoc tieng anh giao tiep cho nguoi moi bat dau")
    p1 = mk_person(conn, "Nguyen Van A")
    mk_link(conn, mk_mention(conn, w1, "Nguyen Van A"), p1, "DaXacNhan")

    w2 = mk_work(conn, abstract="iot cam bien nhiet do dieu khien tu xa qua internet")
    p2 = mk_person(conn, "Tran Thi B")
    mk_link(conn, mk_mention(conn, w2, "Tran Thi B"), p2, "DaXacNhan")

    p3 = mk_person(conn, "Le Van C")

    w_new = mk_work(conn, abstract="hoc tieng anh phat am va giao tiep co ban")
    m_new = mk_mention(conn, w_new, "Tac gia moi")
    l1 = mk_link(conn, m_new, p1, "ChoXacNhan")
    l2 = mk_link(conn, m_new, p2, "ChoXacNhan")
    l3 = mk_link(conn, m_new, p3, "ChoXacNhan")
    return l1, l2, l3


def test_confirmed_same_topic_candidate_ranks_first(conn):
    l1, l2, l3 = _seed_candidates(conn)
    out = S.suggest_author_links(conn, FakeProvider())
    assert out["suggestions"] == 3

    payload = {r["target_id"]: r["payload"] for r in
               q(conn, "SELECT target_id, payload FROM ai_suggestion WHERE kind='author_link'")}
    assert payload[l1]["rank"] == 1
    assert payload[l1]["score"] > payload[l2]["score"]
    assert payload[l3]["score"] is None
    assert payload[l3]["reason"] == "chưa có công trình đã xác nhận"
    assert payload[l3]["rank"] == 3


def test_suggest_author_links_rerun_does_not_duplicate_rows(conn):
    _seed_candidates(conn)
    p = FakeProvider()
    S.suggest_author_links(conn, p)
    S.suggest_author_links(conn, p)
    assert q(conn, "SELECT count(*) AS n FROM ai_suggestion WHERE kind='author_link'")[0]["n"] == 3


def test_mention_with_single_candidate_is_not_scored(conn):
    w = mk_work(conn, abstract="x")
    p = mk_person(conn, "Mot Minh")
    mk_link(conn, mk_mention(conn, w), p, "ChoXacNhan")
    S.suggest_author_links(conn, FakeProvider())
    assert q(conn, "SELECT count(*) AS n FROM ai_suggestion WHERE kind='author_link'")[0]["n"] == 0


def test_suggest_author_links_never_touches_business_tables(conn):
    """Rào chắn BR-18: suggest_author_links chỉ ghi vào ai_suggestion."""
    _seed_candidates(conn)
    before = _counts(conn)
    S.suggest_author_links(conn, FakeProvider())
    assert _counts(conn) == before


def test_duplicate_group_gets_pairwise_similarity_without_changing_hint(conn):
    a = mk_work(conn, "Website A", abstract="xay dung website ban hang truc tuyen")
    b = mk_work(conn, "Website B", abstract="xay dung website ban hang truc tuyen co ban")
    gid = mk_group(conn, "title_norm", [a, b])

    out = S.suggest_duplicates(conn, FakeProvider())
    assert out["suggestions"] == 1

    row = q(conn, "SELECT payload FROM ai_suggestion WHERE kind='duplicate' AND target_id=%s", gid)[0]
    payload = row["payload"]
    assert len(payload["pairs"]) == 1
    pa, pb, score = payload["pairs"][0]
    assert {pa, pb} == {a, b}
    assert payload["min"] == payload["max"] == pytest.approx(score)

    g = q(conn, "SELECT hint, state FROM duplicate_group WHERE id=%s", gid)[0]
    assert (g["hint"], g["state"]) == (None, "NghiTrung")


def test_duplicate_group_matched_by_doi_is_not_suggested(conn):
    a = mk_work(conn, "A"); b = mk_work(conn, "B")
    mk_group(conn, "doi", [a, b])
    out = S.suggest_duplicates(conn, FakeProvider())
    assert out["suggestions"] == 0
    assert q(conn, "SELECT count(*) AS n FROM ai_suggestion")[0]["n"] == 0


def test_suggest_duplicates_rerun_does_not_duplicate_rows(conn):
    a = mk_work(conn, "A", abstract="x"); b = mk_work(conn, "B", abstract="x y")
    mk_group(conn, "title_norm", [a, b])
    p = FakeProvider()
    S.suggest_duplicates(conn, p)
    S.suggest_duplicates(conn, p)
    assert q(conn, "SELECT count(*) AS n FROM ai_suggestion WHERE kind='duplicate'")[0]["n"] == 1


def test_suggest_duplicates_never_touches_business_tables(conn):
    a = mk_work(conn, "A", abstract="x"); b = mk_work(conn, "B", abstract="x y")
    mk_group(conn, "title_norm", [a, b])
    before = _counts(conn)
    S.suggest_duplicates(conn, FakeProvider())
    assert _counts(conn) == before


# --- giao diện: cột "Gợi ý AI" trong hàng đợi tác giả (SC-08) ---

def _call(method, path, headers=None, body=b"", query=""):
    environ = {
        "REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(body), "CONTENT_LENGTH": str(len(body)),
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


def test_queue_page_shows_ai_suggestion_column_when_present(conn):
    l1, l2, l3 = _seed_candidates(conn)
    S.suggest_author_links(conn, FakeProvider())
    conn.commit()  # wsgi.app dùng kết nối riêng, cần thấy dữ liệu đã ghi
    status, _, body = _call("GET", "/doi-soat/tac-gia", headers={"HTTP_X_CRIS_USER": "1"},
                             query=urlencode({"state": "ChoXacNhan"}))
    assert status.startswith("200")
    assert "Gợi ý AI" in body
    assert "#1 —" in body
    assert "chưa có công trình đã xác nhận" in body
    assert "Traceback" not in body


def test_queue_page_shows_dash_when_no_ai_suggestion(conn):
    w = mk_work(conn, abstract="x")
    p1 = mk_person(conn, "P Một"); p2 = mk_person(conn, "P Hai")
    m = mk_mention(conn, w, "Ung vien")
    mk_link(conn, m, p1, "ChoXacNhan")
    mk_link(conn, m, p2, "ChoXacNhan")
    conn.commit()  # wsgi.app dùng kết nối riêng, cần thấy dữ liệu đã ghi
    status, _, body = _call("GET", "/doi-soat/tac-gia", headers={"HTTP_X_CRIS_USER": "1"},
                             query=urlencode({"state": "ChoXacNhan"}))
    assert status.startswith("200")
    assert "Gợi ý AI" in body
    assert "—" in body
    assert "Traceback" not in body
