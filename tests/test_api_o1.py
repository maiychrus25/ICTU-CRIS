# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Lát cắt O1: facet `doc_types` (`GET /api/works/facets`), thứ tự mặc định mới
và `sort` của `GET /api/works`/`GET /api/works.csv`, `totals` của `GET /api/stats`,
và danh bạ giảng viên `GET /api/persons/directory`. API FastAPI trên PostgreSQL
thật (fixture `conn`), cùng khuôn với `test_api_core.py`/`test_api_ext.py`."""
import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q
from test_api_ext import mk_link, mk_mention, mk_unit

from cris import rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


def mk_person(conn, display_name, unit_id=None, degree_raw=None, rank=None, position=None,
              field=None, avatar_url=None, orcid=None, email=None, phone=None, dob=None, active=True):
    """`name_norm`/`name_keys` chuẩn hoá đúng `cris/people.py` (`RU.norm_name`)
    để `q` (kể cả không dấu, một phần) khớp được như dữ liệu thật."""
    nb = rules.load_active(conn)["name_norm"][1]
    name_norm, _degree = rules.norm_name(display_name, nb)
    key = rules.name_key(name_norm)
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, unit_id, degree_raw, rank, "
                   "position, field, avatar_url, orcid, email, phone, dob, active) "
                   "VALUES ('lecturer',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
             display_name, name_norm, [key], unit_id, degree_raw, rank, position, field, avatar_url, orcid,
             email, phone, dob, active)[0]["id"]


def _first_seen(conn, work_id):
    return q(conn, "SELECT sr.id FROM work w JOIN source_record sr ON sr.id = w.primary_source_record_id "
                   "WHERE w.id = %s", work_id)[0]["id"]


def set_first_seen(conn, work_id, when_sql):
    sr_id = _first_seen(conn, work_id)
    q(conn, f"UPDATE source_record SET first_seen_at = {when_sql} WHERE id = %s", sr_id)


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


# ---------- GET /api/works/facets — doc_types ----------

def test_works_facets_doc_types_has_all_five_even_when_empty(client, conn, user_id):
    r = client.get("/api/works/facets").json()
    dt = {d["value"]: d for d in r["doc_types"]}
    assert list(dt) == ["bai_bao", "do_an", "luan_van", "luan_an", "hoc_lieu"]
    assert all(d["n"] == 0 for d in dt.values())
    assert dt["do_an"]["label"] == "Đồ án/Khoá luận"
    assert dt["luan_van"]["label"] == "Luận văn ThS"
    assert dt["luan_an"]["label"] == "Luận án TS"
    assert dt["hoc_lieu"]["label"] == "Học liệu số"


def test_works_facets_doc_types_counts_real_works(client, conn, user_id):
    mk_work(conn, "Bài báo A", doc_type="bai_bao")
    mk_work(conn, "Đồ án A", doc_type="do_an")
    mk_work(conn, "Đồ án B", doc_type="do_an")
    conn.commit()
    r = client.get("/api/works/facets").json()
    dt = {d["value"]: d["n"] for d in r["doc_types"]}
    assert dt["bai_bao"] == 1 and dt["do_an"] == 2 and dt["luan_van"] == 0


# ---------- GET /api/works — thứ tự mặc định, sort ----------

def test_works_default_order_surfaces_cohorts_after_dated_works(client, conn, user_id):
    """Mặc định: có năm trước; trong nhóm không năm, khoá (số trích từ `cohort`)
    lớn hơn đứng trước; không khoá (NULL) đứng cuối."""
    dated = mk_work(conn, "Bài báo có năm", doc_type="bai_bao")
    q(conn, "UPDATE work SET year_issue=2024 WHERE id=%s", dated)
    k21 = mk_work(conn, "Đồ án khoá 21", doc_type="do_an")
    q(conn, "UPDATE work SET cohort='K21' WHERE id=%s", k21)
    k19 = mk_work(conn, "Đồ án khoá 19", doc_type="do_an")
    q(conn, "UPDATE work SET cohort='19' WHERE id=%s", k19)
    no_cohort = mk_work(conn, "Đồ án không khoá", doc_type="do_an")
    conn.commit()
    r = client.get("/api/works").json()
    ids = [it["id"] for it in r["items"]]
    assert ids == [dated, k21, k19, no_cohort]


def test_works_sort_title_orders_a_to_z(client, conn, user_id):
    c = mk_work(conn, "Cong trinh C")
    a = mk_work(conn, "Cong trinh A")
    b = mk_work(conn, "Cong trinh B")
    conn.commit()
    r = client.get("/api/works", params={"sort": "title"}).json()
    ids = [it["id"] for it in r["items"]]
    assert ids.index(a) < ids.index(b) < ids.index(c)


def test_works_sort_added_orders_newest_first_seen_first(client, conn, user_id):
    older = mk_work(conn, "Công trình cũ hơn")
    newer = mk_work(conn, "Công trình mới hơn")
    conn.commit()
    set_first_seen(conn, older, "now() - interval '10 days'")
    set_first_seen(conn, newer, "now()")
    conn.commit()
    r = client.get("/api/works", params={"sort": "added"}).json()
    ids = [it["id"] for it in r["items"]]
    assert ids.index(newer) < ids.index(older)


def test_works_sort_invalid_value_returns_422(client, conn, user_id):
    assert client.get("/api/works", params={"sort": "xyz"}).status_code == 422


def test_works_csv_accepts_sort_param(client, conn, user_id):
    b = mk_work(conn, "Bai B")
    a = mk_work(conn, "Bai A")
    conn.commit()
    resp = client.get("/api/works.csv", params={"sort": "title"})
    assert resp.status_code == 200
    text = resp.content.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln]
    assert lines[1].startswith(str(a) + ",") and lines[2].startswith(str(b) + ",")


# ---------- GET /api/stats — totals ----------

def test_stats_totals_matches_direct_count_and_excludes_merged(client, conn, user_id):
    bai_bao = mk_work(conn, "Bài báo 1", doc_type="bai_bao")
    do_an = mk_work(conn, "Đồ án 1", doc_type="do_an")
    survivor = mk_work(conn, "Đồ án gốc", doc_type="do_an")
    merged = mk_work(conn, "Đồ án đã gộp", doc_type="do_an")
    q(conn, "UPDATE work SET state='DaGop', merged_into_id=%s WHERE id=%s", survivor, merged)
    mk_person(conn, "Giảng viên Hoạt động", active=True)
    mk_person(conn, "Giảng viên Ngừng hoạt động", active=False)
    q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) "
            "VALUES ('student','Sinh viên','sinh vien','{}')")
    conn.commit()
    r = client.get("/api/stats").json()
    t = r["totals"]
    assert t["works"] == 3  # bai_bao, do_an, survivor — merged bị loại
    assert t["by_type"]["bai_bao"] == 1 and t["by_type"]["do_an"] == 2
    assert t["by_type"]["luan_van"] == 0
    assert t["persons"] == 1  # chỉ giảng viên đang hoạt động
    assert bai_bao and do_an  # giữ tham chiếu, tránh cảnh báo biến chưa dùng


# ---------- GET /api/persons/directory ----------

def test_directory_route_does_not_shadow_person_by_id(client, conn, user_id):
    pid = mk_person(conn, "Nguyễn Văn Kiểm")
    conn.commit()
    assert client.get("/api/persons/directory").status_code == 200
    assert client.get(f"/api/persons/{pid}").status_code == 200


def test_directory_pagination_and_total(client, conn, user_id):
    for i in range(3):
        mk_person(conn, f"Giảng viên Số {i}")
    conn.commit()
    r1 = client.get("/api/persons/directory", params={"per_page": 2, "page": 1}).json()
    assert r1["page"]["total"] == 3 and len(r1["items"]) == 2
    r2 = client.get("/api/persons/directory", params={"per_page": 2, "page": 2}).json()
    assert len(r2["items"]) == 1


def test_directory_filters_unit_code_id_and_none(client, conn, user_id):
    uid = mk_unit(conn, code="CNTT", name="Khoa Công nghệ thông tin")
    with_unit = mk_person(conn, "Có Khoa", unit_id=uid)
    without_unit = mk_person(conn, "Không Khoa")
    conn.commit()
    by_code = client.get("/api/persons/directory", params={"unit": "CNTT"}).json()
    assert [p["id"] for p in by_code["items"]] == [with_unit]
    by_id = client.get("/api/persons/directory", params={"unit": str(uid)}).json()
    assert [p["id"] for p in by_id["items"]] == [with_unit]
    none_unit = client.get("/api/persons/directory", params={"unit": "none"}).json()
    assert [p["id"] for p in none_unit["items"]] == [without_unit]


def test_directory_filter_degree_categories(client, conn, user_id):
    gs = mk_person(conn, "Giáo Sư", rank="gs", degree_raw="ts")
    pgs = mk_person(conn, "Phó Giáo Sư", rank="pgs", degree_raw="ts")
    ts = mk_person(conn, "Tiến Sĩ", degree_raw="ts")
    ths = mk_person(conn, "Thạc Sĩ", degree_raw="ths")
    other = mk_person(conn, "Đại Học", degree_raw="dh")
    conn.commit()
    for value, pid in (("gs", gs), ("pgs", pgs), ("ts", ts), ("ths", ths), ("other", other)):
        r = client.get("/api/persons/directory", params={"degree": value}).json()
        assert [p["id"] for p in r["items"]] == [pid], value


def test_directory_filter_has_works(client, conn, user_id):
    with_work = mk_person(conn, "Có Công Trình")
    without_work = mk_person(conn, "Không Công Trình")
    wid = mk_work(conn, "Công trình liên kết")
    mid = mk_mention(conn, wid, "Có Công Trình")
    mk_link(conn, mid, with_work, state="DaXacNhan")
    conn.commit()
    r = client.get("/api/persons/directory", params={"has_works": "true"}).json()
    ids = {p["id"] for p in r["items"]}
    assert with_work in ids and without_work not in ids
    hit = next(p for p in r["items"] if p["id"] == with_work)
    assert hit["works"] == 1 and hit["by_type"] == {"do_an": 1}


def test_directory_q_matches_without_diacritics_partial(client, conn, user_id):
    pid = mk_person(conn, "Phùng Trung Nghĩa")
    mk_person(conn, "Người Khác")
    conn.commit()
    r = client.get("/api/persons/directory", params={"q": "nghia"}).json()
    assert [p["id"] for p in r["items"]] == [pid]


def test_directory_sort_name_orders_by_given_name(client, conn, user_id):
    an = mk_person(conn, "Nguyễn Văn An")
    binh = mk_person(conn, "Trần Thị Bình")
    cuong = mk_person(conn, "Lê Văn Cường")
    conn.commit()
    r = client.get("/api/persons/directory", params={"sort": "name"}).json()
    ids = [p["id"] for p in r["items"]]
    assert ids.index(an) < ids.index(binh) < ids.index(cuong)


def test_directory_facets_not_self_filtered(client, conn, user_id):
    a = mk_unit(conn, code="A", name="Khoa A")
    b = mk_unit(conn, code="B", name="Khoa B")
    mk_person(conn, "Người Khoa A 1", unit_id=a)
    mk_person(conn, "Người Khoa A 2", unit_id=a)
    mk_person(conn, "Người Khoa B", unit_id=b, degree_raw="ts")
    conn.commit()
    r = client.get("/api/persons/directory", params={"unit": "A"}).json()
    assert len(r["items"]) == 2   # đã lọc theo unit=A
    units_by_value = {u["value"]: u["n"] for u in r["facets"]["units"]}
    assert units_by_value == {"A": 2, "B": 1}   # facet KHÔNG tự lọc theo unit
    degrees_by_value = {d["value"]: d["n"] for d in r["facets"]["degrees"]}
    assert degrees_by_value["ts"] == 1 and degrees_by_value["other"] == 2


def test_directory_payload_excludes_email_phone_dob(client, conn, user_id):
    mk_person(conn, "Có Thông Tin Riêng Tư", email="gv@ictu.test", phone="0900000000", dob="1980-01-01")
    conn.commit()
    r = client.get("/api/persons/directory").json()
    item = r["items"][0]
    assert "email" not in item and "phone" not in item and "dob" not in item
