# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Bản đồ tri thức, xu hướng chủ đề, đồng tác giả (J2): `cris.ai.map.build_map`,
`cris.ai.trends.topic_trends`, `cris.ai.coauthors.coauthor_graph`, và
`/api/ai/map`, `/api/ai/trends`, `/api/ai/coauthors`."""
import itertools

import pytest
from fastapi.testclient import TestClient

from cris.ai import coauthors as C
from cris.ai import embed as E
from cris.ai import map as M
from cris.ai import trends as T
from cris.ai.provider import (
    AIDisabled,
    FakeProvider,
    NoneProvider,
    clear_provider_cache,
)
from cris.api.app import create_app
from cris.api.routes.ai_map import MAP_NOT_BUILT

_seq = itertools.count()


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, *, abstract=None, cohort=None, year=None, keywords=None, doc_type="do_an"):
    source_key = f"{title} #{next(_seq)}"
    abstract = title if abstract is None else abstract
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,'h','{}')", source_key, doc_type)
    wid = q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, "
                  "cohort, year_issue, keywords_raw, state) "
                  "VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, %s, %s, 'DaChuanHoa') RETURNING id",
            doc_type, title, title.lower(), abstract, cohort, year, keywords)[0]["id"]
    conn.commit()   # API/hàm gọi qua kết nối khác — phải commit để thấy được
    return wid


def mk_topic(conn, model, label, keywords: dict):
    """Ghi thẳng một cụm `ai_topic`/`ai_topic_keyword` — dùng để kiểm map/trends
    với cụm biết trước, không phụ thuộc kết quả k-means ngẫu nhiên của
    `build_topics` trên `FakeProvider` (vector giả không mang nghĩa thật)."""
    tid = q(conn, "INSERT INTO ai_topic(model, label, size) VALUES (%s,%s,%s) RETURNING id",
            model, label, len(keywords))[0]["id"]
    for kw, w in keywords.items():
        q(conn, "INSERT INTO ai_topic_keyword(topic_id, keyword, weight) VALUES (%s,%s,%s)", tid, kw, w)
    conn.commit()
    return tid


def mk_unit(conn, code, name=None, active=True):
    return q(conn, "INSERT INTO unit(code, name, active) VALUES (%s,%s,%s) RETURNING id",
             code, name or code, active)[0]["id"]


def mk_person(conn, name, unit_id=None):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id) "
                   "VALUES ('lecturer',%s,%s,%s,%s) RETURNING id",
             name, name.lower(), [name.lower()], unit_id)[0]["id"]


def mk_mention(conn, work_id, raw, position=1, role="author"):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                   "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
             work_id, role, position, raw, raw.lower(), raw.lower())[0]["id"]


def link_work_to_person(conn, work, person, position=1, state="DaXacNhan"):
    """Một lượt tên vai `author`, vị trí > 0 (bắt buộc để `v_person_publications`/
    `v_work_unit` tính là công trình của người này), liên kết `state` đã cho."""
    m = mk_mention(conn, work, "Tác giả", position=position)
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, basis, state) "
                   "VALUES (%s,%s,'ten_day_du_duy_nhat','{}',%s) RETURNING id",
             m, person, state)[0]["id"]


WEB_KWS = {"website": 5, "bán hàng": 3, "trực tuyến": 2}
IOT_KWS = {"iot": 5, "cảm biến": 3, "đèn chiếu sáng": 2}


@pytest.fixture(autouse=True)
def _clean_ai_map(conn):
    """`ai_map` không nằm trong danh sách TRUNCATE của `tests/conftest.py`
    (bảng mới của J2) — dọn riêng ở đây để mỗi test bắt đầu từ trạng thái
    "chưa dựng bản đồ", nhất là test 404."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ai_map")
    conn.commit()
    yield


# ---------- cris.ai.map.build_map ----------

def test_build_map_points_count_and_coords_in_range(conn):
    for i in range(3):
        mk_work(conn, f"Công trình số {i}", keywords=f"tu khoa {i}")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    out = M.build_map(conn, p)
    assert out["points"] == 3
    assert out["seconds"] >= 0

    row = q(conn, "SELECT points, topics, method FROM ai_map WHERE model=%s", p.model_id)[0]
    assert row["method"] == "pca"
    assert len(row["points"]) == 3
    for pt in row["points"]:
        assert -1.0 <= pt["x"] <= 1.0
        assert -1.0 <= pt["y"] <= 1.0


def test_map_topic_id_matches_keyword_cluster(conn):
    p = FakeProvider()
    w_web = mk_work(conn, "Xây dựng website bán hàng trực tuyến", keywords="website, bán hàng, trực tuyến")
    w_iot = mk_work(conn, "Hệ thống đèn chiếu sáng IoT", keywords="iot, cảm biến, đèn chiếu sáng")
    w_none = mk_work(conn, "Không có từ khoá khớp cụm nào", keywords="tu khoa khong lien quan")
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    mk_topic(conn, p.model_id, "iot", IOT_KWS)
    E.build_embeddings(conn, p)
    conn.commit()

    M.build_map(conn, p)
    points = {pt["id"]: pt for pt in q(conn, "SELECT points FROM ai_map WHERE model=%s", p.model_id)[0]["points"]}
    web_label = q(conn, "SELECT label FROM ai_topic WHERE id=%s", points[w_web]["topic_id"])[0]["label"]
    iot_label = q(conn, "SELECT label FROM ai_topic WHERE id=%s", points[w_iot]["topic_id"])[0]["label"]
    assert web_label == "web"
    assert iot_label == "iot"
    assert points[w_none]["topic_id"] is None


def test_map_topic_center_is_mean_of_member_coords(conn):
    p = FakeProvider()
    w1 = mk_work(conn, "Website bán hàng một", keywords="website, bán hàng")
    w2 = mk_work(conn, "Website bán hàng hai", keywords="website, bán hàng")
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    E.build_embeddings(conn, p)
    conn.commit()

    M.build_map(conn, p)
    row = q(conn, "SELECT points, topics FROM ai_map WHERE model=%s", p.model_id)[0]
    by_id = {pt["id"]: pt for pt in row["points"]}
    topic = next(t for t in row["topics"] if t["label"] == "web")
    assert topic["size"] == 2
    expected_cx = (by_id[w1]["x"] + by_id[w2]["x"]) / 2
    expected_cy = (by_id[w1]["y"] + by_id[w2]["y"]) / 2
    assert topic["cx"] == pytest.approx(expected_cx, abs=1e-4)
    assert topic["cy"] == pytest.approx(expected_cy, abs=1e-4)


def test_rerun_replaces_single_row(conn):
    mk_work(conn, "Một công trình", keywords="a, b")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    M.build_map(conn, p)
    M.build_map(conn, p)
    assert q(conn, "SELECT count(*) AS n FROM ai_map WHERE model=%s", p.model_id)[0]["n"] == 1


def test_build_map_provider_none_raises_ai_disabled(conn):
    with pytest.raises(AIDisabled):
        M.build_map(conn, NoneProvider())


def test_build_map_no_works_returns_zero(conn):
    p = FakeProvider()
    out = M.build_map(conn, p)
    assert out == {"points": 0, "topics": 0, "seconds": out["seconds"]}
    row = q(conn, "SELECT points, topics FROM ai_map WHERE model=%s", p.model_id)[0]
    assert row["points"] == [] and row["topics"] == []


# ---------- GET /api/ai/map ----------

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


def test_api_map_404_when_not_built(client, conn, user_id):
    r = client.get("/api/ai/map")
    assert r.status_code == 404
    assert r.json()["detail"] == MAP_NOT_BUILT


def test_api_map_returns_points_topics_and_active_units(client, conn, user_id):
    unit_active = mk_unit(conn, "CNTT", "Khoa Công nghệ thông tin")
    unit_inactive = mk_unit(conn, "CNTT-CU", "Đơn vị cũ", active=False)
    person_a = mk_person(conn, "Nguyễn Văn A", unit_id=unit_active)
    person_b = mk_person(conn, "Trần Thị B", unit_id=unit_inactive)
    w_a = mk_work(conn, "Website bán hàng", keywords="website, bán hàng")
    w_b = mk_work(conn, "IoT chiếu sáng", keywords="iot, cảm biến")
    link_work_to_person(conn, w_a, person_a)
    link_work_to_person(conn, w_b, person_b)
    p = FakeProvider()
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    E.build_embeddings(conn, p)
    conn.commit()
    M.build_map(conn, p)
    conn.commit()

    r = client.get("/api/ai/map").json()
    assert r["method"] == "pca"
    assert len(r["points"]) == 2
    assert {pt["id"] for pt in r["points"]} == {w_a, w_b}
    assert r["built_at"]
    # chỉ đơn vị active mới xuất hiện dù cả hai đều có điểm gắn unit_id
    assert [u["code"] for u in r["units"]] == ["CNTT"]
    assert r["units"][0]["name"] == "Khoa Công nghệ thông tin"


def test_api_map_color_param_accepted_returns_full_fields(client, conn, user_id):
    """`color` chỉ để tương lai — mọi giá trị hợp lệ đều trả đủ trường, không lọc."""
    mk_work(conn, "Một công trình", keywords="a, b")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()
    M.build_map(conn, p)
    conn.commit()

    for color in ("topic", "unit", "year", "doc_type"):
        r = client.get("/api/ai/map", params={"color": color}).json()
        pt = r["points"][0]
        assert set(pt) >= {"id", "x", "y", "topic_id", "unit_id", "year", "doc_type", "title"}


# ---------- cris.ai.trends.topic_trends ----------

def test_trends_by_cohort_share_sums_to_one_per_key(conn):
    p = FakeProvider()
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    mk_topic(conn, p.model_id, "iot", IOT_KWS)
    mk_work(conn, "Web K17 một", cohort="K17", keywords="website, bán hàng")
    mk_work(conn, "Web K17 hai", cohort="K17", keywords="website, bán hàng")
    mk_work(conn, "IoT K17", cohort="K17", keywords="iot, cảm biến")
    mk_work(conn, "Web K18", cohort="K18", keywords="website, bán hàng")
    mk_work(conn, "Không cụm K18", cohort="K18", keywords="tu khong khop")  # bỏ khỏi mẫu số
    mk_work(conn, "Không khoá", keywords="website, bán hàng")  # cohort NULL — bỏ

    out = T.topic_trends(conn, by="cohort", top=12)
    assert out["keys"] == ["K17", "K18"]
    by_key = {}
    for series in out["series"]:
        for v in series["values"]:
            by_key.setdefault(v["key"], 0.0)
            by_key[v["key"]] += v["share"]
    assert by_key["K17"] == pytest.approx(1.0)
    assert by_key["K18"] == pytest.approx(1.0)
    web_series = next(s for s in out["series"] if s["label"] == "web")
    v17 = next(v for v in web_series["values"] if v["key"] == "K17")
    assert v17["count"] == 2
    assert v17["share"] == pytest.approx(2 / 3)


def test_trends_by_year_sorted_numerically(conn):
    p = FakeProvider()
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    mk_work(conn, "Web 2021", year=2021, keywords="website, bán hàng")
    mk_work(conn, "Web 2009", year=2009, keywords="website, bán hàng")
    mk_work(conn, "Web 2018", year=2018, keywords="website, bán hàng")

    out = T.topic_trends(conn, by="year", top=12)
    assert out["keys"] == [2009, 2018, 2021]


def test_trends_cohort_numeric_order_not_lexicographic(conn):
    """"K9" phải đứng trước "K17" — thứ tự chuỗi thường sẽ xếp ngược lại."""
    p = FakeProvider()
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    mk_work(conn, "Web K17", cohort="K17", keywords="website, bán hàng")
    mk_work(conn, "Web K9", cohort="K9", keywords="website, bán hàng")

    out = T.topic_trends(conn, by="cohort", top=12)
    assert out["keys"] == ["K9", "K17"]


def test_trends_overflow_topics_grouped_as_khac(conn):
    p = FakeProvider()
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    mk_topic(conn, p.model_id, "iot", IOT_KWS)
    mk_work(conn, "Web nhiều K17 một", cohort="K17", keywords="website, bán hàng")
    mk_work(conn, "Web nhiều K17 hai", cohort="K17", keywords="website, bán hàng")
    mk_work(conn, "IoT ít K17", cohort="K17", keywords="iot, cảm biến")

    out = T.topic_trends(conn, by="cohort", top=1)   # chỉ giữ 1 cụm lớn nhất -> "iot" gộp vào "khác"
    labels = [s["label"] for s in out["series"]]
    assert labels == ["web", "khác"]
    other = next(s for s in out["series"] if s["label"] == "khác")
    assert other["topic_id"] is None
    assert other["values"][0]["count"] == 1


def test_trends_invalid_by_raises_value_error(conn):
    with pytest.raises(ValueError):
        T.topic_trends(conn, by="thang")


# ---------- cris.ai.coauthors.coauthor_graph ----------

def test_coauthors_weight_and_min_works_filter(conn):
    unit = mk_unit(conn, "CNTT2")
    p1 = mk_person(conn, "Người Một", unit_id=unit)
    p2 = mk_person(conn, "Người Hai", unit_id=unit)
    p3 = mk_person(conn, "Người Ba", unit_id=unit)
    w1 = mk_work(conn, "Bài chung 1 và 2 (a)")
    w2 = mk_work(conn, "Bài chung 1 và 2 (b)")
    w3 = mk_work(conn, "Bài chung 1 và 3")
    link_work_to_person(conn, w1, p1, position=1)
    link_work_to_person(conn, w1, p2, position=2)
    link_work_to_person(conn, w2, p1, position=1)
    link_work_to_person(conn, w2, p2, position=2)
    link_work_to_person(conn, w3, p1, position=1)
    link_work_to_person(conn, w3, p3, position=2)

    out = C.coauthor_graph(conn, min_works=2)
    node_ids = {n["person_id"] for n in out["nodes"]}
    assert node_ids == {p1, p2}   # p3 chỉ có 1 công trình liên kết — dưới min_works=2
    works_of = {n["person_id"]: n["works"] for n in out["nodes"]}
    assert works_of[p1] == 3 and works_of[p2] == 2
    assert out["edges"] == [{"a": min(p1, p2), "b": max(p1, p2), "weight": 2}]


def test_coauthors_max_nodes_cutoff_keeps_highest_works(conn):
    people = []
    for i in range(4):
        pid = mk_person(conn, f"Người {i}")
        people.append(pid)
        for j in range(2):   # mỗi người 2 công trình riêng, đủ qua min_works=2, không đồng tác giả
            w = mk_work(conn, f"Bài của {i}-{j}")
            link_work_to_person(conn, w, pid)

    out = C.coauthor_graph(conn, min_works=2, max_nodes=2)
    assert len(out["nodes"]) == 2


def test_coauthors_empty_when_nobody_meets_min_works(conn):
    p1 = mk_person(conn, "Chỉ một bài")
    w = mk_work(conn, "Một bài duy nhất")
    link_work_to_person(conn, w, p1)

    assert C.coauthor_graph(conn, min_works=2) == {"nodes": [], "edges": []}


# ---------- GET /api/ai/trends, /api/ai/coauthors ----------

def test_api_trends_endpoint(client, conn, user_id):
    p = FakeProvider()
    mk_topic(conn, p.model_id, "web", WEB_KWS)
    mk_work(conn, "Web K17", cohort="K17", keywords="website, bán hàng")
    conn.commit()

    r = client.get("/api/ai/trends", params={"by": "cohort"}).json()
    assert r["keys"] == ["K17"]
    assert r["series"][0]["label"] == "web"


def test_api_coauthors_endpoint(client, conn, user_id):
    p1 = mk_person(conn, "A")
    p2 = mk_person(conn, "B")
    w1 = mk_work(conn, "Bài 1")
    w2 = mk_work(conn, "Bài 2")
    link_work_to_person(conn, w1, p1, position=1)
    link_work_to_person(conn, w1, p2, position=2)
    link_work_to_person(conn, w2, p1, position=1)
    link_work_to_person(conn, w2, p2, position=2)
    conn.commit()

    r = client.get("/api/ai/coauthors", params={"min_works": 2}).json()
    assert len(r["nodes"]) == 2
    assert r["edges"] == [{"a": min(p1, p2), "b": max(p1, p2), "weight": 2}]
