# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Trích dẫn (`cris.cite`, `/api/works/{id}/citation`), lý lịch khoa học
(`cris.cv`, `/api/persons/{id}/cv`), bộ lọc/facets công trình, "mới cập nhật"
(`/api/recent`) và RSS (`/api/feed.xml`) — lát cắt K1."""
import itertools
import json
import xml.etree.ElementTree as ET

import pytest
from fastapi.testclient import TestClient

from cris import cite
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app

_seq = itertools.count()


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, doc_type="bai_bao", year=None, journal=None, volume=None, doi=None,
           keywords=None, cohort=None, quartile=None, indexes=None, abstract=None,
           detail=None, archive=None, sync_run_id=None, source_key=None):
    """Công trình đầy đủ trường cho trích dẫn/facets/pdf-source-url; nếu
    `sync_run_id` không truyền thì tự tạo một `sync_run` mới (status 'ok')."""
    source_key = source_key or f"{title} #{next(_seq)}"
    if sync_run_id is None:
        sync_run_id = q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) "
                              "VALUES ('manual','t','ok',now()) RETURNING id")[0]["id"]
    raw = {"archive": archive or {}, "detail": detail or {}}
    sr_id = q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
                    "VALUES (%s,'manual',%s,%s,%s,%s) RETURNING id",
              sync_run_id, source_key, doc_type, f"h{next(_seq)}", json.dumps(raw, ensure_ascii=False))[0]["id"]
    wid = q(conn, """INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, year_issue,
                     journal, volume, doi, keywords_raw, cohort, quartile, indexes, abstract, state)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'DaChuanHoa') RETURNING id""",
            doc_type, sr_id, title, title.lower(), year, journal, volume, doi, keywords, cohort,
            quartile, indexes or [], abstract)[0]["id"]
    conn.commit()
    return wid


def mk_mention(conn, work_id, raw_name, position=1, role="author"):
    q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
            "VALUES (%s,%s,%s,%s,%s,%s)", work_id, role, position, raw_name, raw_name.lower(), raw_name.lower())
    conn.commit()


def mk_unit(conn, code, name=None):
    uid = q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name or code)[0]["id"]
    conn.commit()
    return uid


def mk_person(conn, name, degree=None, rank=None, unit_id=None):
    pid = q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, degree_raw, rank, unit_id) "
                  "VALUES ('lecturer',%s,%s,%s,%s,%s,%s) RETURNING id",
            name, name.lower(), [name.lower()], degree, rank, unit_id)[0]["id"]
    conn.commit()
    return pid


def link_work_to_person(conn, work_id, person_id, position=1):
    q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
            "VALUES (%s,'author',%s,'Tác giả','tac gia','tac gia') RETURNING id", work_id, position)
    mid = q(conn, "SELECT id FROM author_mention WHERE work_id=%s AND position=%s", work_id, position)[0]["id"]
    q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, basis, state) "
            "VALUES (%s,%s,'ten_day_du_duy_nhat','{}','DaXacNhan')", mid, person_id)
    conn.commit()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


# ---------- cris.cite: APA / IEEE / BibTeX ----------

def test_apa_full_fields_bai_bao(conn):
    wid = mk_work(conn, "Học sâu cho thị giác máy tính", year=2023, journal="Tạp chí CNTT",
                  volume="12(3)", doi="10.1234/abc")
    mk_mention(conn, wid, "Nguyễn Văn A", 1)
    mk_mention(conn, wid, "Trần Thị B", 2)
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.apa(w, cite.authors_of(conn, wid))
    assert text == ("Nguyễn Văn A & Trần Thị B (2023). Học sâu cho thị giác máy tính. "
                     "Tạp chí CNTT, 12(3). https://doi.org/10.1234/abc")


def test_apa_missing_year_is_nd(conn):
    wid = mk_work(conn, "Chưa rõ năm xuất bản", year=None, journal="Tạp chí X")
    mk_mention(conn, wid, "Lê Văn C", 1)
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.apa(w, cite.authors_of(conn, wid))
    assert "(n.d.)" in text


def test_apa_missing_journal_is_graceful(conn):
    wid = mk_work(conn, "Không có tạp chí ghi nhận", year=2020, journal=None)
    mk_mention(conn, wid, "Phạm Văn D", 1)
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.apa(w, cite.authors_of(conn, wid))
    assert text == "Phạm Văn D (2020). Không có tạp chí ghi nhận."


def test_apa_do_an_uses_student_as_author_and_mentor_as_advisor(conn):
    wid = mk_work(conn, "Xây dựng hệ thống quản lý thư viện", doc_type="do_an", year=2024, cohort="K19")
    mk_mention(conn, wid, "Phạm Văn C", 1, role="student")
    mk_mention(conn, wid, "Nguyễn Văn A", 1, role="mentor")
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.apa(w, cite.authors_of(conn, wid))
    assert text == ("Phạm Văn C (2024). Xây dựng hệ thống quản lý thư viện [Đồ án tốt nghiệp]. "
                     "Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên. "
                     "Người hướng dẫn: Nguyễn Văn A.")


def test_ieee_full_fields(conn):
    wid = mk_work(conn, "Học sâu cho thị giác máy tính", year=2023, journal="Tạp chí CNTT",
                  volume="12(3)", doi="10.1234/abc")
    mk_mention(conn, wid, "Nguyễn Văn A", 1)
    mk_mention(conn, wid, "Trần Thị B", 2)
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.ieee(w, cite.authors_of(conn, wid))
    assert text == ('Nguyễn Văn A and Trần Thị B, "Học sâu cho thị giác máy tính," Tạp chí CNTT, '
                     'vol. 12(3), 2023. doi: 10.1234/abc.')


def test_bibtex_key_strips_vietnamese_diacritics_and_escapes_braces(conn):
    wid = mk_work(conn, "Mô hình {X} nâng cao hiệu năng", year=2023, journal="Tạp chí Y", doi="10.1/z")
    mk_mention(conn, wid, "Nguyễn Văn A", 1)
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.bibtex(w, cite.authors_of(conn, wid))
    assert text.startswith("@article{Nguyen2023Mo,\n")
    assert r"\{X\}" in text
    assert "doi = {10.1/z}" in text


def test_bibtex_thesis_uses_school_and_note(conn):
    wid = mk_work(conn, "Đồ án tốt nghiệp mẫu", doc_type="do_an", year=2022)
    mk_mention(conn, wid, "Trần Văn E", 1, role="student")
    mk_mention(conn, wid, "Nguyễn Văn A", 1, role="mentor")
    w = q(conn, "SELECT * FROM v_work_current WHERE id=%s", wid)[0]
    text = cite.bibtex(w, cite.authors_of(conn, wid))
    assert text.startswith("@misc{")
    assert "school = {Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên}" in text
    assert "Người hướng dẫn: Nguyễn Văn A" in text


# ---------- GET /api/works/{id}/citation ----------

def test_citation_route_apa_and_bibtex_download_header(client, conn):
    wid = mk_work(conn, "Trích dẫn qua API", year=2021, journal="Tạp chí Z", doi="10.9/qrs")
    mk_mention(conn, wid, "Vũ Thị F", 1)
    r = client.get(f"/api/works/{wid}/citation", params={"style": "apa"})
    assert r.status_code == 200 and "Vũ Thị F" in r.text
    assert r.headers["content-type"].startswith("text/plain")
    r2 = client.get(f"/api/works/{wid}/citation", params={"style": "bibtex", "download": 1})
    assert r2.status_code == 200
    assert r2.headers["content-type"].startswith("application/x-bibtex")
    assert r2.headers["content-disposition"] == f'attachment; filename="cris-{wid}.bib"'


def test_citation_route_404_for_unknown_work(client):
    assert client.get("/api/works/999999/citation").status_code == 404


# ---------- keywords ở WorkSummary/WorkDetail ----------

def test_work_summary_keywords_split_and_capped_at_6(client, conn):
    wid = mk_work(conn, "Nhiều từ khoá", keywords="a, b; c,d ; e,f,g")
    r = client.get("/api/works", params={"q": "Nhiều từ khoá"}).json()
    item = next(it for it in r["items"] if it["id"] == wid)
    assert item["keywords"] == ["a", "b", "c", "d", "e", "f"]


def test_work_detail_pdf_source_url_and_keywords(client, conn):
    wid = mk_work(conn, "Có PDF và URL nguồn", keywords="IoT, AI",
                  detail={"pdf": ["https://r/f1.pdf", "https://r/f2.pdf"], "url": "https://r/detail/1"},
                  archive={"url": "https://r/archive/1"})
    d = client.get(f"/api/works/{wid}").json()
    assert d["pdf_url"] == "https://r/f1.pdf"
    assert d["source_url"] == "https://r/detail/1"
    assert d["keywords"] == ["IoT", "AI"]


# ---------- bộ lọc keyword/pub_type/cohort, facets ----------

def test_keyword_filter_respects_word_boundary(client, conn):
    w1 = mk_work(conn, "Công trình về AI", keywords="AI, Machine Learning")
    w2 = mk_work(conn, "Công trình về AIoT", keywords="AIoT, Cloud")
    r = client.get("/api/works", params={"keyword": "AI"}).json()
    ids = {it["id"] for it in r["items"]}
    assert w1 in ids and w2 not in ids


def test_pub_type_filter_matches_indexes_array(client, conn):
    w1 = mk_work(conn, "Bài Scopus", indexes=["Scopus"])
    w2 = mk_work(conn, "Bài không chỉ mục", indexes=[])
    r = client.get("/api/works", params={"pub_type": "Scopus"}).json()
    ids = {it["id"] for it in r["items"]}
    assert w1 in ids and w2 not in ids


def test_cohort_filter(client, conn):
    w1 = mk_work(conn, "Đồ án K19", doc_type="do_an", cohort="K19")
    w2 = mk_work(conn, "Đồ án K20", doc_type="do_an", cohort="K20")
    r = client.get("/api/works", params={"cohort": "K19"}).json()
    ids = {it["id"] for it in r["items"]}
    assert w1 in ids and w2 not in ids


def test_facets_counts(client, conn):
    u = mk_unit(conn, "CNTT", "Khoa CNTT")
    p = mk_person(conn, "Nguyễn Văn A", degree="TS", unit_id=u)
    w1 = mk_work(conn, "Bài Q1", year=2023, quartile="Q1", cohort="K19", indexes=["Scopus"])
    w2 = mk_work(conn, "Bài Q1 khác", year=2023, quartile="Q1", cohort="K20", indexes=["Scopus", "WoS"])
    link_work_to_person(conn, w1, p)
    link_work_to_person(conn, w2, p)
    f = client.get("/api/works/facets").json()
    assert {x["value"]: x["n"] for x in f["quartiles"]}["Q1"] == 2
    assert {x["value"]: x["n"] for x in f["pub_types"]}["Scopus"] == 2
    assert {x["value"]: x["n"] for x in f["pub_types"]}["WoS"] == 1
    assert {x["value"]: x["n"] for x in f["years"]}[2023] == 2
    units = {x["code"]: x["n"] for x in f["units"]}
    assert units["CNTT"] == 2


# ---------- lý lịch khoa học (/api/persons/{id}/cv) ----------

def test_cv_html_contains_name_and_escapes_lt(client, conn):
    pid = mk_person(conn, "Nguyễn Văn Mẫu", degree="TS", rank="PGS")
    wid = mk_work(conn, "So sánh A < B trong xử lý ảnh", year=2022, journal="Tạp chí ABC")
    link_work_to_person(conn, wid, pid)
    r = client.get(f"/api/persons/{pid}/cv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "PGS.TS. Nguyễn Văn Mẫu" in r.text
    assert "A &lt; B" in r.text
    assert "A < B" not in r.text


def test_cv_404_for_unknown_person(client):
    assert client.get("/api/persons/999999/cv").status_code == 404


# ---------- /api/recent ----------

def test_recent_lists_added_and_changed_from_last_finished_run(client, conn):
    run1 = q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) "
                   "VALUES ('manual','t','ok',now()) RETURNING id")[0]["id"]
    conn.commit()
    w_old = mk_work(conn, "Công trình cũ", sync_run_id=run1)

    run2 = q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) "
                   "VALUES ('manual','t','ok',now()) RETURNING id")[0]["id"]
    conn.commit()
    w_added = mk_work(conn, "Công trình mới thêm", sync_run_id=run2)
    # "Đổi" ở lượt run2: một source_record version 2 cho work cũ, trỏ primary_source_record_id về đó
    sr2 = q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, version, "
                  "content_hash, raw) VALUES (%s,'manual','k-old','bai_bao',2,'h2','{}') RETURNING id",
            run2)[0]["id"]
    q(conn, "UPDATE work SET primary_source_record_id=%s WHERE id=%s", sr2, w_old)
    conn.commit()

    r = client.get("/api/recent").json()
    assert r["run"]["id"] == run2
    added_ids = {it["id"] for it in r["added"]}
    changed_ids = {it["id"] for it in r["changed"]}
    assert w_added in added_ids
    assert w_old in changed_ids


def test_recent_empty_when_no_finished_run(client, conn):
    q(conn, "INSERT INTO sync_run(source, scope, status) VALUES ('manual','t','running')")
    conn.commit()
    r = client.get("/api/recent").json()
    assert r == {"added": [], "changed": [], "run": None}


# ---------- /api/feed.xml ----------

def test_feed_xml_is_valid_and_escapes_ampersand(client, conn):
    for i in range(3):
        mk_work(conn, f"Nghiên cứu A & B lần {i}", abstract="Tóm tắt " * 100)
    r = client.get("/api/feed.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/rss+xml")
    root = ET.fromstring(r.text)
    items = root.findall("./channel/item")
    assert len(items) == 3
    titles = [it.findtext("title") for it in items]
    assert any("A & B" in t for t in titles)
    descs = [it.findtext("description") for it in items]
    assert all(len(d) <= 300 for d in descs)
    assert all(it.findtext("pubDate") for it in items)


def test_feed_xml_caps_at_20_items(client, conn):
    for i in range(25):
        mk_work(conn, f"Bài số {i}")
    r = client.get("/api/feed.xml")
    root = ET.fromstring(r.text)
    assert len(root.findall("./channel/item")) == 20
