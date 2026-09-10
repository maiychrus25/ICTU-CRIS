# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Test hàng đợi liên kết tác giả (SC-08): cris/web/views_queue.py.

Gọi thẳng WSGI callable với `environ` giả (không dựng server). Dữ liệu được
dựng bằng chính hàm tầng nghiệp vụ (`link.link_pending`, `link.decide_link`) —
chỉ dùng INSERT tay cho những thứ chưa có hàm sẵn (work/mention/person), giống
`tests/test_link.py`.
"""
import io
from urllib.parse import urlencode

import pytest

import cris.web.views_queue  # noqa: F401  # đăng ký route vào wsgi.ROUTES
from cris import link, rules
from cris.web import wsgi

ACTOR_HEADER = "HTTP_X_CRIS_USER"


def call(method, path, headers=None, body=b"", query=""):
    """Dựng environ WSGI giả, gọi wsgi.app, trả (status, headers, body_text)."""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(body),
        "CONTENT_LENGTH": str(len(body)),
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


def get(path_with_query, actor_id):
    path, _, query = path_with_query.partition("?")
    return call("GET", path, headers={ACTOR_HEADER: str(actor_id)}, query=query)


def post_decide(actor_id, link_ids, decision, reason=None, person_id=None):
    """POST /doi-soat/tac-gia/quyet-dinh với một hoặc nhiều `link_id`."""
    if isinstance(link_ids, int):
        link_ids = [link_ids]
    pairs = [("link_id", str(i)) for i in link_ids] + [("decision", decision)]
    if reason is not None:
        pairs.append(("reason", reason))
    if person_id is not None:
        pairs.append(("person_id", str(person_id)))
    body = urlencode(pairs, encoding="utf-8").encode("ascii")
    return call(
        "POST",
        "/doi-soat/tac-gia/quyet-dinh",
        headers={ACTOR_HEADER: str(actor_id)},
        body=body,
    )


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title="Bài báo"):
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(
        conn,
        "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
        "VALUES (1,'manual',%s,'bai_bao','h',%s)",
        title,
        "{}",
    )
    return q(
        conn,
        "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) "
        "VALUES ('bai_bao', currval('source_record_id_seq'), %s, %s, 'DaChuanHoa') RETURNING id",
        title,
        title,
    )[0]["id"]


def mk_mention(conn, work_id, raw, degree=None, position=1):
    nb = rules.RULES_V1["name_norm"]
    nn, deg = rules.norm_name(raw, nb)
    return q(
        conn,
        "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, degree_raw, is_placeholder) "
        "VALUES (%s,'author',%s,%s,%s,%s,%s,%s) RETURNING id",
        work_id,
        position,
        raw,
        nn,
        rules.name_key(nn),
        degree or deg,
        rules.is_placeholder(raw, nb),
    )[0]["id"]


def mk_person(conn, name, degree=None, email=None):
    nb = rules.RULES_V1["name_norm"]
    nn, _ = rules.norm_name(name, nb)
    return q(
        conn,
        "INSERT INTO person(kind, display_name, name_norm, name_keys, degree_raw, email) "
        "VALUES ('lecturer',%s,%s,%s,%s,%s) RETURNING id",
        name,
        nn,
        [rules.name_key(nn)],
        degree,
        email,
    )[0]["id"]


def queue_one(conn, raw="Nguyễn Đình Dũng", person_name="Nguyễn Đình Dũng", person_degree="TS",
              mention_degree="ThS", work_title="Bài báo"):
    """Dựng một work + person + mention lệch học vị -> một `author_link` ChoXacNhan
    duy nhất (không tự nối vì có mâu thuẫn học vị), trả (link_id, mention_id, person_id, work_id)."""
    w = mk_work(conn, work_title)
    p = mk_person(conn, person_name, degree=person_degree)
    m = mk_mention(conn, w, raw, degree=mention_degree)
    out = link.link_pending(conn)
    assert out["queued"] == 1
    lid = q(conn, "SELECT id FROM author_link WHERE mention_id=%s", m)[0]["id"]
    return lid, m, p, w


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


def test_empty_queue_shows_empty_state_without_error(conn):
    status, _, body = call("GET", "/doi-soat/tac-gia", headers={ACTOR_HEADER: "1"})
    assert status.startswith("200")
    assert "Không có lượt tên" in body
    assert "Traceback" not in body


def test_pending_link_shows_raw_name_candidate_and_confidence(conn):
    queue_one(conn, raw="ThS. Nguyễn Đình Dũng", person_name="Nguyễn Đình Dũng")
    status, _, body = call("GET", "/doi-soat/tac-gia", headers={ACTOR_HEADER: "1"})
    assert status.startswith("200")
    assert "Nguyễn Đình Dũng" in body
    assert "ten_day_du_duy_nhat" in body


def test_confirm_sets_state_and_records_actor(conn, user_id):
    lid, _, _, _ = queue_one(conn)
    status, headers, _ = post_decide(user_id, lid, "confirm")
    assert status.startswith("303")
    assert headers["Location"].startswith("/doi-soat/tac-gia?")
    row = q(conn, "SELECT state, decided_by FROM author_link WHERE id=%s", lid)[0]
    assert row["state"] == "DaXacNhan"
    assert row["decided_by"] == user_id


def test_reject_without_reason_changes_nothing_and_shows_error(conn, user_id):
    lid, _, _, _ = queue_one(conn)
    status, headers, _ = post_decide(user_id, lid, "reject")
    assert status.startswith("303")
    assert "error=" in headers["Location"]
    row = q(conn, "SELECT state FROM author_link WHERE id=%s", lid)[0]
    assert row["state"] == "ChoXacNhan"

    status2, _, body2 = get(headers["Location"], user_id)
    assert status2.startswith("200")
    assert "error-page" in body2 and "lý do" in body2.lower()


def test_reject_with_reason_sets_dabacbo_and_saves_reason(conn, user_id):
    lid, _, _, _ = queue_one(conn)
    status, _, _ = post_decide(user_id, lid, "reject", reason="trùng tên")
    assert status.startswith("303")
    row = q(conn, "SELECT state, reason FROM author_link WHERE id=%s", lid)[0]
    assert row["state"] == "DaBacBo"
    assert row["reason"] == "trùng tên"


def test_multiple_link_ids_all_change_state(conn, user_id):
    lid1, _, _, _ = queue_one(conn, raw="ThS. Trần Văn Một", person_name="Trần Văn Một",
                               work_title="Bài báo 1")
    lid2, _, _, _ = queue_one(conn, raw="ThS. Lê Thị Hai", person_name="Lê Thị Hai",
                               work_title="Bài báo 2")
    status, _, _ = post_decide(user_id, [lid1, lid2], "confirm")
    assert status.startswith("303")
    rows = q(conn, "SELECT id, state FROM author_link WHERE id IN (%s,%s)", lid1, lid2)
    assert {r["state"] for r in rows} == {"DaXacNhan"}


def test_bad_id_in_batch_rolls_back_the_whole_batch(conn, user_id):
    lid_good, _, _, _ = queue_one(conn)
    bad_id = lid_good + 999999
    status, headers, _ = post_decide(user_id, [lid_good, bad_id], "confirm")
    assert status.startswith("303")
    assert "error=" in headers["Location"]
    row = q(conn, "SELECT state, decided_by FROM author_link WHERE id=%s", lid_good)[0]
    assert row["state"] == "ChoXacNhan"
    assert row["decided_by"] is None


def test_script_tag_in_raw_name_is_escaped_not_executed(conn):
    w = mk_work(conn)
    p = mk_person(conn, "Nguyễn Văn X")
    mk_mention(conn, w, "Nguyễn Văn X <script>alert(1)</script>")
    out = link.link_pending(conn)
    assert out["queued"] == 1

    status, _, body = call("GET", "/doi-soat/tac-gia", headers={ACTOR_HEADER: "1"})
    assert status.startswith("200")
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
