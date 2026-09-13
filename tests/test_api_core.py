# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""API FastAPI trên PostgreSQL thật (fixture `conn`), provider AI `fake`/`none`."""
import pytest
from fastapi.testclient import TestClient

from cris.ai import embed as E
from cris.ai.provider import FakeProvider, clear_provider_cache
from cris.api.app import create_app


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, abstract=None, keywords=None, doc_type="do_an"):
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,'h','{}')", title, doc_type)
    wid = q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, keywords_raw, state) "
                  "VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, 'DaChuanHoa') RETURNING id",
            doc_type, title, title.lower(), abstract, keywords)[0]["id"]
    conn.commit()
    return wid


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


def test_health_and_openapi(client):
    # Hợp đồng đầy đủ (db/model/last_sync_age_h/version, DB lỗi -> 503, model
    # theo provider) có test riêng ở tests/test_health_units.py; ở đây chỉ
    # kiểm sơ bộ endpoint còn sống.
    assert client.get("/api/health").json()["status"] == "ok"
    spec = client.get("/openapi.json").json()
    paths = set(spec["paths"])
    for p in ("/api/works", "/api/works/{wid}", "/api/persons", "/api/persons/{pid}", "/api/queue/authors",
              "/api/queue/authors/decide", "/api/queue/duplicates", "/api/queue/duplicates/{gid}",
              "/api/queue/duplicates/{gid}/decide", "/api/compare", "/api/compare/{qid}", "/api/quality", "/api/about", "/api/topics",
              "/api/topics/{tid}", "/api/stats", "/api/works.csv", "/api/persons/{pid}/publications.csv", "/api/audit",
              "/api/periods", "/api/periods/{pid}/progress", "/api/periods/{pid}/close", "/api/periods/{pid}/cancel",
              "/api/ai/screen", "/api/ai/screen/cohorts", "/api/sync/runs", "/api/sync/runs/{rid}",
              "/api/periods/{pid}/declarations", "/api/declarations/{did}", "/api/declarations/{did}/state",
              "/api/declarations/{did}/evidence",
              "/api/ai/experts", "/api/ai/experts/{qid}", "/api/public/check-topic",
              "/api/ai/map", "/api/ai/trends", "/api/ai/coauthors",
              "/api/works/{wid}/citation", "/api/works/facets", "/api/persons/{pid}/cv",
              "/api/recent", "/api/feed.xml",
              "/api/periods/{pid}/reports", "/api/reports/{rid}", "/api/reports/{rid}/export",
              "/api/notifications", "/api/notifications/{nid}/read", "/api/notifications/read-all",
              "/api/units", "/api/units/{unit_id}", "/api/units/{unit_id}/aliases", "/api/units/{unit_id}/overview"):
        assert p in paths, p


def test_about_and_quality_on_empty_db(client, conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    a = client.get("/api/about").json()
    assert a["works"] == 0 and a["ai"]["provider"] == "none" and len(a["limits"]) == 7 and a["last_sync"] is None
    m = client.get("/api/quality").json()
    assert {x["key"] for x in m["metrics"]} >= {"works", "links_queued", "dup_groups_open"}


def test_works_search_and_detail_with_provenance(client, conn, user_id):
    wid = mk_work(conn, "Xây dựng website bán hàng", keywords="thương mại điện tử")
    r = client.get("/api/works", params={"q": "website"}).json()
    assert r["page"]["total"] == 1 and r["items"][0]["id"] == wid and r["items"][0]["doc_type_label"] == "Đồ án"
    assert client.get("/api/works", params={"q": "không có"}).json()["page"]["total"] == 0
    d = client.get(f"/api/works/{wid}").json()
    assert d["title"] == "Xây dựng website bán hàng"
    assert {f["field"] for f in d["fields"]} >= {"title", "doi", "abstract", "keywords_raw"}
    assert all({"value", "raw", "source"} <= set(f) for f in d["fields"])
    assert client.get("/api/works/999999").status_code == 404


def test_person_404_and_topics_empty(client, conn, user_id):
    assert client.get("/api/persons/999999").status_code == 404
    assert client.get("/api/topics").json() == []


def test_author_queue_empty_and_bad_state(client, conn, user_id):
    r = client.get("/api/queue/authors").json()
    assert r["items"] == [] and r["state"] == "ChoXacNhan"
    assert client.get("/api/queue/authors", params={"state": "xyz"}).status_code == 400


def test_decide_authors_validation_and_atomic_batch(client, conn, user_id):
    assert client.post("/api/queue/authors/decide", json={"link_ids": [], "decision": "confirm"}).status_code == 422
    assert client.post("/api/queue/authors/decide", json={"link_ids": [1], "decision": "reject"}).status_code == 400
    r = client.post("/api/queue/authors/decide", json={"link_ids": [999999], "decision": "confirm"})
    assert r.status_code == 400 and "999999" in r.json()["detail"]


def test_duplicates_404_and_keep_requires_reason(client, conn, user_id):
    assert client.get("/api/queue/duplicates").json()["items"] == []
    assert client.get("/api/queue/duplicates/999999").status_code == 404
    assert client.post("/api/queue/duplicates/999999/decide", json={"decision": "keep"}).status_code == 404


def test_compare_fake_provider_and_saved_result(client, conn, user_id):
    for t in ("học tiếng Anh cho trẻ em luyện phát âm", "học từ vựng tiếng Anh", "đèn chiếu sáng IoT"):
        mk_work(conn, t, abstract=t)
    E.build_embeddings(conn, FakeProvider())
    conn.commit()
    r = client.post("/api/compare", json={"title": "ứng dụng học tiếng Anh cho trẻ em", "description": "luyện phát âm",
                                          "aspects": {"bai_toan": "luyện phát âm tiếng Anh"}, "k": 3})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider"] == "fake" and body["fallback"] is False and "không phải toàn văn" in body["note"]
    assert body["results"][0]["title"].startswith("học tiếng Anh")
    assert "%" not in body["note"]
    again = client.get(f"/api/compare/{body['query_id']}").json()
    assert again["query_id"] == body["query_id"] and len(again["results"]) == len(body["results"])
    assert client.get("/api/compare/999999").status_code == 404


def test_compare_with_provider_none_falls_back(client, conn, user_id, monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    clear_provider_cache()
    mk_work(conn, "hệ thống quản lý thư viện", keywords="thư viện, quản lý")
    r = client.post("/api/compare", json={"title": "quản lý thư viện", "description": ""}).json()
    assert r["fallback"] is True and r["provider"] == "none"


def test_compare_never_touches_business_tables(client, conn, user_id):
    mk_work(conn, "A", abstract="a")
    E.build_embeddings(conn, FakeProvider()); conn.commit()
    def counts():
        return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"] for t in ("work", "author_link", "duplicate_group", "field_provenance")}
    before = counts()
    client.post("/api/compare", json={"title": "A", "description": ""})
    assert counts() == before


def test_503_when_no_rd_officer(client, conn):
    r = client.post("/api/compare", json={"title": "abc", "description": ""})
    assert r.status_code == 503 and "rd_officer" in r.json()["detail"]


# ---------- lát cắt M: điểm quy đổi (score/min_score), chip đơn vị, chức vụ ----------
def test_works_filter_by_exact_score_and_none(client, conn, user_id):
    w1 = mk_work(conn, "Bài A", doc_type="bai_bao")
    w2 = mk_work(conn, "Bài B", doc_type="bai_bao")
    w3 = mk_work(conn, "Bài C", doc_type="bai_bao")
    q(conn, "UPDATE work SET score=0.5 WHERE id=%s", w1)
    q(conn, "UPDATE work SET score=1 WHERE id=%s", w2)
    conn.commit()          # w3 giữ score NULL — "Chưa xác định"

    r = client.get("/api/works", params={"doc_type": "bai_bao", "score": "0.5"}).json()
    assert [i["id"] for i in r["items"]] == [w1]

    r_none = client.get("/api/works", params={"doc_type": "bai_bao", "score": "none"}).json()
    assert {i["id"] for i in r_none["items"]} == {w3}

    r_all = client.get("/api/works", params={"doc_type": "bai_bao"}).json()
    by_id = {i["id"]: i["score"] for i in r_all["items"]}
    assert by_id[w1] == 0.5 and by_id[w2] == 1.0 and by_id[w3] is None


def test_works_filter_by_min_score(client, conn, user_id):
    w1 = mk_work(conn, "Bài A", doc_type="bai_bao")
    w2 = mk_work(conn, "Bài B", doc_type="bai_bao")
    q(conn, "UPDATE work SET score=0.5 WHERE id=%s", w1)
    q(conn, "UPDATE work SET score=1 WHERE id=%s", w2)
    conn.commit()
    r = client.get("/api/works", params={"doc_type": "bai_bao", "min_score": 0.75}).json()
    assert {i["id"] for i in r["items"]} == {w2}


def test_works_facets_include_scores_with_labels(client, conn, user_id):
    w1 = mk_work(conn, "Bài A", doc_type="bai_bao")
    mk_work(conn, "Bài B", doc_type="bai_bao")     # giữ score NULL
    q(conn, "UPDATE work SET score=0.75 WHERE id=%s", w1)
    conn.commit()
    r = client.get("/api/works/facets").json()
    by_value = {s["value"]: s for s in r["scores"]}
    assert by_value["0.75"]["n"] == 1 and by_value["0.75"]["label"] == "0,75 điểm"
    assert by_value["none"]["n"] == 1 and by_value["none"]["label"] == "Chưa xác định"
    # thứ tự cố định: 1, 0,75, 0,5, chưa xác định
    assert [s["value"] for s in r["scores"]] == sorted(
        (s["value"] for s in r["scores"]), key=lambda v: {"1": 0, "0.75": 1, "0.5": 2, "none": 3}.get(v, 4))


def test_work_list_and_detail_include_unit_chips(client, conn, user_id):
    wid = mk_work(conn, "Bài với đơn vị", doc_type="bai_bao")
    cntt = q(conn, "INSERT INTO unit(code, name) VALUES ('CNTT','Khoa Công nghệ thông tin') RETURNING id")[0]["id"]
    q(conn, "INSERT INTO work_unit(work_id, unit_id, source) VALUES (%s,%s,'source')", wid, cntt)
    conn.commit()

    items = client.get("/api/works", params={"doc_type": "bai_bao"}).json()["items"]
    item = next(i for i in items if i["id"] == wid)
    assert item["units"] == [{"id": cntt, "code": "CNTT"}]

    detail = client.get(f"/api/works/{wid}").json()
    assert detail["units"] == [{"id": cntt, "code": "CNTT"}]


def test_person_profile_includes_position_and_unit(client, conn, user_id):
    cntt = q(conn, "INSERT INTO unit(code, name) VALUES ('CNTT','Khoa Công nghệ thông tin') RETURNING id")[0]["id"]
    pid = q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id, unit_source, position) "
                  "VALUES ('lecturer','Nguyễn Văn A','nguyen van a',ARRAY['nguyen van a'],%s,'auto','Trưởng bộ môn') "
                  "RETURNING id", cntt)[0]["id"]
    conn.commit()
    r = client.get(f"/api/persons/{pid}").json()
    assert r["position"] == "Trưởng bộ môn"
    assert r["unit"] == {"id": cntt, "code": "CNTT", "name": "Khoa Công nghệ thông tin"}
    assert r["unit_source"] == "auto"


def test_person_profile_unit_is_null_when_unassigned(client, conn, user_id):
    pid = q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) "
                  "VALUES ('lecturer','Trần Thị B','tran thi b',ARRAY['tran thi b']) RETURNING id")[0]["id"]
    conn.commit()
    r = client.get(f"/api/persons/{pid}").json()
    assert r["unit"] is None and r["position"] is None and r["unit_source"] == "auto"
