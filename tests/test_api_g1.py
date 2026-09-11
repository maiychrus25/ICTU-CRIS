# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Lát cắt G1: tìm người (`/api/persons`), chi tiết chủ đề (`/api/topics`,
`/api/topics/{id}`) và lịch sử đồng bộ (`/api/sync/runs`). API FastAPI trên
PostgreSQL thật (fixture `conn`), cùng khuôn với `test_api_ext.py`."""
import json

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_person(conn, display_name, kind="lecturer", unit_id=None):
    """Tạo `person` với `name_norm`/`name_keys` chuẩn hoá đúng như `cris/people.py`
    (`RU.norm_name` + `RU.name_key`) để khớp được với route tìm người."""
    nb = rules.load_active(conn)["name_norm"][1]
    name_norm, _degree = rules.norm_name(display_name, nb)
    key = rules.name_key(name_norm)
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id) "
                   "VALUES (%s,%s,%s,%s,%s) RETURNING id",
             kind, display_name, name_norm, [key], unit_id)[0]["id"]


def mk_mention(conn, work_id, raw_name, position=1):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,'author',%s,%s,%s,%s) RETURNING id",
             work_id, position, raw_name, raw_name.lower(), raw_name.lower())[0]["id"]


def mk_link(conn, mention_id, person_id, state="DaXacNhan"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat',%s) RETURNING id",
             mention_id, person_id, state)[0]["id"]


def mk_topic(conn, label, keywords):
    """`keywords`: danh sách `(keyword, weight)`. Ghi thẳng vào `ai_topic*` — không
    cần chạy `build_topics`/mô hình AI để kiểm thử mỗi route đọc."""
    tid = q(conn, "INSERT INTO ai_topic(model, label, size) VALUES ('test-model',%s,%s) RETURNING id",
            label, len(keywords))[0]["id"]
    for kw, w in keywords:
        q(conn, "INSERT INTO ai_topic_keyword(topic_id, keyword, weight) VALUES (%s,%s,%s)", tid, kw, w)
    return tid


def mk_sync_run(conn, *, source="repository", scope="full", status="ok",
                 started_sql="now() - interval '10 minutes'", finished_sql="now()",
                 added=0, changed=0, vanished=0, warnings=None):
    return q(conn, f"INSERT INTO sync_run(source, scope, started_at, finished_at, added, changed, vanished, "
                   f"status, warnings) VALUES (%s,%s,{started_sql},{finished_sql},%s,%s,%s,%s,%s::jsonb) RETURNING id",
             source, scope, added, changed, vanished, status, json.dumps(warnings or []))[0]["id"]


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


# ---------- /api/persons ----------

def test_persons_search_full_name_without_diacritics(client, conn, user_id):
    pid = mk_person(conn, "Nguyễn Thị Dung")
    conn.commit()
    r = client.get("/api/persons", params={"q": "nguyen thi dung"}).json()
    assert [p["id"] for p in r] == [pid]
    assert r[0]["kind"] == "lecturer"


def test_persons_search_partial_with_diacritics(client, conn, user_id):
    pid = mk_person(conn, "Nguyễn Đình Vịnh")
    mk_person(conn, "Trần Văn Khác")
    conn.commit()
    r = client.get("/api/persons", params={"q": "Vịnh"}).json()
    assert [p["id"] for p in r] == [pid]


def test_persons_search_filters_by_kind(client, conn, user_id):
    lecturer_id = mk_person(conn, "Lê Kiểm Thử", kind="lecturer")
    student_id = mk_person(conn, "Lê Kiểm Thử Sinh Viên", kind="student")
    conn.commit()
    r = client.get("/api/persons", params={"q": "Kiểm Thử", "kind": "student"}).json()
    ids = {p["id"] for p in r}
    assert student_id in ids and lecturer_id not in ids


def test_persons_search_respects_limit(client, conn, user_id):
    for i in range(5):
        mk_person(conn, f"Phạm Giới Hạn {i}")
    conn.commit()
    r = client.get("/api/persons", params={"q": "Giới Hạn", "limit": 2}).json()
    assert len(r) == 2


def test_persons_search_works_counts_confirmed_links_only(client, conn, user_id):
    pid = mk_person(conn, "Đỗ Đếm Công Trình")
    wid1 = mk_work(conn, "Công trình một")
    wid2 = mk_work(conn, "Công trình hai")
    mk_link(conn, mk_mention(conn, wid1, "Đỗ Đếm Công Trình", 1), pid, state="DaXacNhan")
    mk_link(conn, mk_mention(conn, wid2, "Đỗ Đếm Công Trình", 1), pid, state="ChoXacNhan")
    conn.commit()
    r = client.get("/api/persons", params={"q": "Đếm Công Trình"}).json()
    assert len(r) == 1 and r[0]["works"] == 1


def test_persons_search_no_active_rules_falls_back_to_ilike(client, conn, user_id):
    """Vô hiệu bộ luật `name_norm` (mô phỏng CSDL mới chưa `seed_rules`) → route
    chỉ còn khớp `display_name ILIKE`, vẫn phải trả đúng kết quả."""
    q(conn, "UPDATE rule_set SET active=false WHERE kind='name_norm'")
    pid = q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) "
                  "VALUES ('lecturer','Không Có Luật','khong co luat','{}') RETURNING id")[0]["id"]
    conn.commit()
    r = client.get("/api/persons", params={"q": "Có Luật"}).json()
    assert [p["id"] for p in r] == [pid]


# ---------- /api/topics ----------

def test_topics_list_returns_top8_keywords_and_built_at(client, conn, user_id):
    kws = [(f"tu khoa {i}", 10 - i) for i in range(10)]
    mk_topic(conn, "tu khoa 0", kws)
    conn.commit()
    r = client.get("/api/topics").json()
    assert len(r) == 1
    t = r[0]
    assert t["built_at"] is not None
    assert t["keywords"] == [f"tu khoa {i}" for i in range(8)]


def test_topic_detail_returns_full_keywords_and_matching_works(client, conn, user_id):
    tid = mk_topic(conn, "chu de x", [("tu khoa hot", 5), ("tu khoa lanh", 1)])
    wid = mk_work(conn, "Công trình khớp chủ đề", keywords="tu khoa hot, khac")
    mk_work(conn, "Không khớp chủ đề", keywords="khong lien quan")
    conn.commit()
    d = client.get(f"/api/topics/{tid}").json()
    assert d["label"] == "chu de x"
    assert {k["keyword"] for k in d["keywords"]} == {"tu khoa hot", "tu khoa lanh"}
    assert {w["id"] for w in d["works"]} == {wid}


def test_topic_detail_404(client, conn, user_id):
    assert client.get("/api/topics/999999").status_code == 404


# ---------- /api/sync/runs ----------

def test_sync_runs_empty(client, conn, user_id):
    r = client.get("/api/sync/runs").json()
    assert r["items"] == [] and r["page"]["total"] == 0


def test_sync_runs_list_duration_and_order(client, conn, user_id):
    finished_id = mk_sync_run(conn, status="ok", added=5, changed=2)
    running_id = mk_sync_run(conn, status="running", started_sql="now()", finished_sql="NULL")
    conn.commit()
    r = client.get("/api/sync/runs").json()
    assert r["page"]["total"] == 2
    assert r["items"][0]["id"] == running_id  # mới nhất (id lớn hơn) trước
    by_id = {it["id"]: it for it in r["items"]}
    assert by_id[finished_id]["duration_s"] is not None and by_id[finished_id]["duration_s"] > 0
    assert by_id[running_id]["duration_s"] is None


def test_sync_run_detail_has_warnings_and_20_newest_records(client, conn, user_id):
    rid = mk_sync_run(conn, warnings=["cảnh báo 1", "cảnh báo 2"])
    for i in range(25):
        q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
                "VALUES (%s,'repository',%s,'bai_bao',%s,'{}')", rid, f"key-{i}", f"hash-{i}")
    conn.commit()
    d = client.get(f"/api/sync/runs/{rid}").json()
    assert d["warnings"] == ["cảnh báo 1", "cảnh báo 2"]
    assert len(d["records"]) == 20
    assert d["records"][0]["source_key"] == "key-24"


def test_sync_run_detail_404(client, conn, user_id):
    assert client.get("/api/sync/runs/999999").status_code == 404
