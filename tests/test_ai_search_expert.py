# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tìm kiếm ngữ nghĩa (`mode=semantic` ở `/api/works`), tìm chuyên gia (J1,
`cris/ai/expert.py`, `/api/ai/experts`), cổng công khai kiểm tra đề tài
(`/api/public/check-topic`) — `cris/ai/search.py`, `cris/ai/expert.py`,
`cris/api/routes/ai_public.py`."""
import itertools

import pytest
from fastapi.testclient import TestClient

from cris.ai import embed as E
from cris.ai import expert as ai_expert
from cris.ai import search as ai_search
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app
from cris.api.routes import ai_public

_seq = itertools.count()

QUERY_TITLE = "Xây dựng ứng dụng quản lý bán hàng trực tuyến cho cửa hàng thời trang"


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, abstract=None, doc_type="do_an", year=None):
    source_key = f"{title} #{next(_seq)}"
    abstract = title if abstract is None else abstract
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,'h','{}')", source_key, doc_type)
    wid = q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, "
                  "year_issue, state) VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, 'DaChuanHoa') "
                  "RETURNING id",
            doc_type, title, title.lower(), abstract, year)[0]["id"]
    conn.commit()   # API gọi qua kết nối khác mỗi request — phải commit để thấy được
    return wid


def mk_mention(conn, work_id, raw, position=1, role="author"):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
             work_id, role, position, raw, raw.lower(), raw.lower())[0]["id"]


def mk_person(conn, name, degree=None, unit_id=None):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, degree_raw, unit_id) "
                   "VALUES ('lecturer',%s,%s,%s,%s,%s) RETURNING id",
             name, name.lower(), [name.lower()], degree, unit_id)[0]["id"]


def mk_link(conn, mention_id, person_id, state="DaXacNhan"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, basis, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat','{}',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


def mk_unit(conn, code, name=None):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name or code)[0]["id"]


def link_work_to_person(conn, work, person, position=1):
    """Một lượt tên vai `author`, vị trí > 0 (bắt buộc để `v_person_publications`
    tính là công trình của người này), liên kết `DaXacNhan`."""
    m = mk_mention(conn, work, "Tác giả", position=position)
    return mk_link(conn, m, person, "DaXacNhan")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    ai_public._hits.clear()
    yield
    ai_public._hits.clear()


# ---------- GET /api/works?mode=semantic ----------

def test_semantic_mode_returns_score_and_filters_doc_type(client, conn, user_id):
    w_do_an = mk_work(conn, QUERY_TITLE, doc_type="do_an")
    w_bai_bao = mk_work(conn, QUERY_TITLE, doc_type="bai_bao")
    from cris.ai.provider import FakeProvider
    E.build_embeddings(conn, FakeProvider())
    conn.commit()

    r = client.get("/api/works", params={"q": QUERY_TITLE, "mode": "semantic", "doc_type": "do_an"}).json()
    assert r["mode"] == "semantic"
    assert r["note"] == ai_search.NOTE
    ids = [it["id"] for it in r["items"]]
    assert w_do_an in ids
    assert w_bai_bao not in ids
    assert all(it["score"] is not None for it in r["items"])
    top = next(it for it in r["items"] if it["id"] == w_do_an)
    assert top["score"] == pytest.approx(1.0, abs=1e-4)


def test_semantic_mode_falls_back_to_keyword_when_ai_disabled(client, conn, user_id, monkeypatch):
    wid = mk_work(conn, "Nghiên cứu mạng nơ-ron nhân tạo", doc_type="bai_bao")
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    clear_provider_cache()

    r = client.get("/api/works", params={"q": "mạng nơ-ron", "mode": "semantic"}).json()
    assert r["mode"] == "keyword"
    assert r["note"] == ai_search.DISABLED_NOTE
    assert any(it["id"] == wid for it in r["items"])


# ---------- cris.ai.expert.find_experts ----------

def test_experts_two_works_score_higher_than_one(conn):
    from cris.ai.provider import FakeProvider
    p_two = mk_person(conn, "Nguyễn Hai Bài", degree="TS")
    p_one = mk_person(conn, "Trần Một Bài", degree="TS")
    w1 = mk_work(conn, QUERY_TITLE)
    w2 = mk_work(conn, QUERY_TITLE)
    w3 = mk_work(conn, QUERY_TITLE)
    link_work_to_person(conn, w1, p_two)
    link_work_to_person(conn, w2, p_two)
    link_work_to_person(conn, w3, p_one)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = ai_expert.find_experts(conn, prov, title=QUERY_TITLE, save=False)
    scores = {r["person_id"]: r["score"] for r in out["results"]}
    assert scores[p_two] > scores[p_one]
    matched = {r["person_id"]: r["works_matched"] for r in out["results"]}
    assert matched[p_two] == 2 and matched[p_one] == 1


def test_experts_excludes_given_person_ids(conn):
    from cris.ai.provider import FakeProvider
    p_keep = mk_person(conn, "Giữ Lại", degree="TS")
    p_excl = mk_person(conn, "Bị Loại", degree="TS")
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p_keep)
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p_excl)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = ai_expert.find_experts(conn, prov, title=QUERY_TITLE, exclude_person_ids=[p_excl], save=False)
    ids = {r["person_id"] for r in out["results"]}
    assert p_keep in ids
    assert p_excl not in ids


def test_experts_min_degree_ts_accepts_ts_pgs_gs_not_ths(conn):
    from cris.ai.provider import FakeProvider
    p_ts = mk_person(conn, "Tiến Sĩ", degree="TS")
    p_pgs = mk_person(conn, "Phó Giáo Sư", degree="PGS.TS")
    p_ths = mk_person(conn, "Thạc Sĩ", degree="ThS")
    p_none = mk_person(conn, "Không Học Vị", degree=None)
    for p in (p_ts, p_pgs, p_ths, p_none):
        link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = ai_expert.find_experts(conn, prov, title=QUERY_TITLE, min_degree="TS", k=10, save=False)
    ids = {r["person_id"] for r in out["results"]}
    assert ids == {p_ts, p_pgs}


def test_experts_min_degree_ths_accepts_ths_and_ts_plus(conn):
    from cris.ai.provider import FakeProvider
    p_ts = mk_person(conn, "Tiến Sĩ Hai", degree="TS")
    p_ths = mk_person(conn, "Thạc Sĩ Hai", degree="ThS.")
    p_none = mk_person(conn, "Không Học Vị Hai", degree=None)
    for p in (p_ts, p_ths, p_none):
        link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = ai_expert.find_experts(conn, prov, title=QUERY_TITLE, min_degree="ThS", k=10, save=False)
    ids = {r["person_id"] for r in out["results"]}
    assert ids == {p_ts, p_ths}


def test_experts_unit_filter(conn):
    from cris.ai.provider import FakeProvider
    u_khoa = mk_unit(conn, "KHOA-CNTT")
    u_other = mk_unit(conn, "KHOA-KHAC")
    p_in = mk_person(conn, "Trong Khoa", degree="TS", unit_id=u_khoa)
    p_out = mk_person(conn, "Khoa Khac", degree="TS", unit_id=u_other)
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p_in)
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p_out)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = ai_expert.find_experts(conn, prov, title=QUERY_TITLE, unit_id=u_khoa, k=10, save=False)
    ids = {r["person_id"] for r in out["results"]}
    assert ids == {p_in}


def test_experts_evidence_capped_at_three_sorted_desc(conn):
    from cris.ai.provider import FakeProvider
    p = mk_person(conn, "Nhiều Bài", degree="TS")
    titles = [
        QUERY_TITLE,
        "Xây dựng ứng dụng quản lý bán hàng trực tuyến cho cửa hàng",
        "Xây dựng ứng dụng quản lý bán hàng trực tuyến",
        "Xây dựng ứng dụng quản lý bán hàng",
        "Xây dựng ứng dụng quản lý",
    ]
    for t in titles:
        link_work_to_person(conn, mk_work(conn, t), p)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = ai_expert.find_experts(conn, prov, title=QUERY_TITLE, k=10, save=False)
    r = next(x for x in out["results"] if x["person_id"] == p)
    assert r["works_matched"] == 5
    assert len(r["evidence"]) == 3
    scores = [e["score"] for e in r["evidence"]]
    assert scores == sorted(scores, reverse=True)


# ---------- /api/ai/experts ----------

def test_api_experts_ai_disabled_returns_fallback_not_500(client, conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    clear_provider_cache()
    r = client.post("/api/ai/experts", json={"title": QUERY_TITLE})
    assert r.status_code == 200
    body = r.json()
    assert body["fallback"] is True
    assert body["results"] == []
    assert body["note"] == ai_expert.DISABLED_NOTE


def test_api_experts_saves_query_and_get_reads_back(client, conn, user_id):
    from cris.ai.provider import FakeProvider
    p = mk_person(conn, "Ứng Viên", degree="TS")
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p)
    E.build_embeddings(conn, FakeProvider())
    conn.commit()

    posted = client.post("/api/ai/experts", json={"title": QUERY_TITLE, "k": 5}).json()
    assert posted["fallback"] is False
    assert posted["query_id"] is not None
    assert any(r["person_id"] == p for r in posted["results"])

    row = q(conn, "SELECT kind FROM ai_query WHERE id=%s", posted["query_id"])[0]
    assert row["kind"] == "experts"

    got = client.get(f"/api/ai/experts/{posted['query_id']}").json()
    assert got["results"] == posted["results"]
    assert got["provider"] == posted["provider"]

    assert client.get("/api/ai/experts/999999").status_code == 404


# ---------- /api/public/check-topic ----------

def test_public_check_topic_no_cookie_needed(client, conn):
    """Không tạo `user_id`, không cookie — cổng công khai vẫn trả 200."""
    from cris.ai.provider import FakeProvider
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), mk_person(conn, "GV Công Khai", degree="TS"))
    E.build_embeddings(conn, FakeProvider())
    conn.commit()

    r = client.post("/api/public/check-topic", json={"title": QUERY_TITLE})
    assert r.status_code == 200
    body = r.json()
    assert "similar" in body and "experts" in body and "note" in body


def test_public_check_topic_does_not_save_ai_query(client, conn):
    from cris.ai.provider import FakeProvider
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), mk_person(conn, "GV Không Lưu", degree="TS"))
    E.build_embeddings(conn, FakeProvider())
    conn.commit()
    before = q(conn, "SELECT count(*) AS n FROM ai_query")[0]["n"]

    client.post("/api/public/check-topic", json={"title": QUERY_TITLE})

    after = q(conn, "SELECT count(*) AS n FROM ai_query")[0]["n"]
    assert after == before


def test_public_check_topic_experts_have_no_email_field(client, conn):
    from cris.ai.provider import FakeProvider
    p = mk_person(conn, "GV Ẩn Danh", degree="TS")
    q(conn, "UPDATE person SET email=%s WHERE id=%s", "bi_mat@ictu.edu.vn", p)
    link_work_to_person(conn, mk_work(conn, QUERY_TITLE), p)
    E.build_embeddings(conn, FakeProvider())
    conn.commit()

    body = client.post("/api/public/check-topic", json={"title": QUERY_TITLE}).json()
    assert body["experts"], "cần ít nhất một chuyên gia gợi ý để kiểm tra hình dạng"
    for e in body["experts"]:
        assert set(e) == {"person_id", "display_name", "degree", "unit_code", "score"}


def test_public_check_topic_rate_limited_after_20(client, conn):
    for _ in range(20):
        r = client.post("/api/public/check-topic", json={"title": QUERY_TITLE})
        assert r.status_code == 200
    r = client.post("/api/public/check-topic", json={"title": QUERY_TITLE})
    assert r.status_code == 429
    assert "detail" in r.json()
