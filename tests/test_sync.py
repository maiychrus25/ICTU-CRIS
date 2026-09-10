# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json
from cris import sync

def rows(conn, sql, *args):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchall()

def test_first_sync_adds_records_and_counts(conn):
    recs = [("u1", {"title": "A"}), ("u2", {"title": "B"})]
    rid = sync.run_sync(conn, source="repository", scope="bai-bao", doc_type="bai_bao",
                        records=recs, expected=2, full=True)
    run = rows(conn, "SELECT * FROM sync_run WHERE id=%s", rid)[0]
    assert run["status"] == "ok" and run["added"] == 2 and run["warnings"] == []
    assert run["fetched_count"] == {"bai_bao": 2}
    assert len(rows(conn, "SELECT 1 FROM source_record WHERE status='active'")) == 2

def test_unchanged_record_is_not_duplicated(conn):
    recs = [("u1", {"title": "A"})]
    sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao", records=recs, expected=1, full=True)
    rid = sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao", records=recs, expected=1, full=True)
    assert len(rows(conn, "SELECT 1 FROM source_record")) == 1
    assert rows(conn, "SELECT added, changed FROM sync_run WHERE id=%s", rid)[0] == {"added": 0, "changed": 0}

def test_changed_record_creates_new_version_keeps_old(conn):
    sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao", records=[("u1", {"title": "A"})], expected=1, full=True)
    rid = sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao", records=[("u1", {"title": "A2"})], expected=1, full=True)
    vs = rows(conn, "SELECT version, raw, status FROM source_record WHERE source_key='u1' ORDER BY version")
    assert [v["version"] for v in vs] == [1, 2]
    assert vs[0]["raw"] == {"title": "A"} and vs[1]["raw"] == {"title": "A2"}
    assert rows(conn, "SELECT changed FROM sync_run WHERE id=%s", rid)[0]["changed"] == 1

def test_missing_record_marked_vanished_not_deleted(conn):
    sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao",
                  records=[("u1", {}), ("u2", {})], expected=2, full=True)
    rid = sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao",
                        records=[("u1", {})], expected=1, full=True)
    st = {r["source_key"]: r["status"] for r in rows(conn, "SELECT source_key, status FROM source_record")}
    assert st == {"u1": "active", "u2": "vanished"}
    assert rows(conn, "SELECT vanished FROM sync_run WHERE id=%s", rid)[0]["vanished"] == 1

def test_count_mismatch_becomes_warning(conn):
    rid = sync.run_sync(conn, source="repository", scope="do-an", doc_type="do_an",
                        records=[("u1", {})], expected=12, full=True)
    run = rows(conn, "SELECT status, warnings FROM sync_run WHERE id=%s", rid)[0]
    assert run["status"] == "warning"
    assert run["warnings"][0]["expected"] == 12 and run["warnings"][0]["fetched"] == 1

def test_revert_to_old_hash_creates_new_version_without_error(conn):
    for raw in ({"title": "A"}, {"title": "B"}, {"title": "A"}):
        sync.run_sync(conn, source="repository", scope="s", doc_type="bai_bao",
                      records=[("u1", raw)], expected=1, full=True)
    vs = rows(conn, "SELECT version, raw FROM source_record WHERE source_key='u1' ORDER BY version")
    assert [v["version"] for v in vs] == [1, 2, 3]
    assert vs[0]["raw"] == vs[2]["raw"] == {"title": "A"}
    assert len(rows(conn, "SELECT 1 FROM sync_run")) == 3

def test_sync_repository_merges_archive_and_detail(conn, monkeypatch):
    from cris.source import repository as R
    monkeypatch.setattr(R, "iter_archive", lambda path, fetch=None: iter([{"url": "https://x/bai-bao/a/", "title": "T"}]))
    monkeypatch.setattr(R, "archive_total", lambda h: 1)
    monkeypatch.setattr(R, "parse_detail", lambda h, url: {"url": url, "authors": ["A B"], "doi": []})
    rid = sync.sync_repository(conn, "bai-bao", fetch=lambda url: "<html></html>")
    raw = rows(conn, "SELECT raw FROM source_record")[0]["raw"]
    assert raw["archive"]["title"] == "T" and raw["detail"]["authors"] == ["A B"]
    assert rows(conn, "SELECT status FROM sync_run WHERE id=%s", rid)[0]["status"] == "ok"

def test_sync_repository_detail_failure_unchanged_archive_keeps_one_version(conn, monkeypatch):
    from cris.source import repository as R
    url = "https://x/bai-bao/b/"
    monkeypatch.setattr(R, "iter_archive", lambda path, fetch=None: iter([{"url": url, "title": "T"}]))
    monkeypatch.setattr(R, "archive_total", lambda h: 1)
    monkeypatch.setattr(R, "parse_detail", lambda h, u: {"url": u, "authors": ["A B"], "doi": []})
    sync.sync_repository(conn, "bai-bao", fetch=lambda u: "<html></html>")

    def boom(h, u):
        raise RuntimeError("timeout")
    monkeypatch.setattr(R, "parse_detail", boom)
    sync.sync_repository(conn, "bai-bao", fetch=lambda u: "<html></html>")

    versions = rows(conn, "SELECT version, raw FROM source_record WHERE source_key=%s ORDER BY version", url)
    assert [v["version"] for v in versions] == [1]
    assert versions[0]["raw"]["detail"]["authors"] == ["A B"]
    assert "detail_error" not in versions[0]["raw"]

def test_sync_repository_detail_failure_changed_archive_marks_stale(conn, monkeypatch):
    from cris.source import repository as R
    url = "https://x/bai-bao/c/"
    monkeypatch.setattr(R, "iter_archive", lambda path, fetch=None: iter([{"url": url, "title": "T"}]))
    monkeypatch.setattr(R, "archive_total", lambda h: 1)
    monkeypatch.setattr(R, "parse_detail", lambda h, u: {"url": u, "authors": ["A B"], "doi": []})
    sync.sync_repository(conn, "bai-bao", fetch=lambda u: "<html></html>")

    def boom(h, u):
        raise RuntimeError("timeout")
    monkeypatch.setattr(R, "iter_archive", lambda path, fetch=None: iter([{"url": url, "title": "T2"}]))
    monkeypatch.setattr(R, "parse_detail", boom)
    sync.sync_repository(conn, "bai-bao", fetch=lambda u: "<html></html>")

    versions = rows(conn, "SELECT version, raw FROM source_record WHERE source_key=%s ORDER BY version", url)
    assert [v["version"] for v in versions] == [1, 2]
    assert versions[1]["raw"]["archive"]["title"] == "T2"
    assert versions[1]["raw"]["detail"]["authors"] == ["A B"]
    assert versions[1]["raw"]["detail_stale"] is True

def test_page_drift_does_not_create_a_fake_version(conn):
    """Kho sắp xếp không ổn định nên số trang trôi giữa các lần đồng bộ.
    `_page` là siêu dữ liệu tìm thấy, không phải nội dung: không được băm."""
    for page in (27, 28):
        sync.run_sync(conn, source="repository", scope="do-an", doc_type="do_an",
                      records=[("u1", {"archive": {"title": "A", "_page": page}})],
                      expected=1, full=True)
    vs = rows(conn, "SELECT version FROM source_record WHERE source_key='u1'")
    assert [v["version"] for v in vs] == [1]

def test_backfill_marker_does_not_create_a_fake_version(conn):
    sync.run_sync(conn, source="repository", scope="do-an", doc_type="do_an",
                  records=[("u1", {"archive": {"title": "A", "_page": 3}})], expected=1, full=True)
    sync.run_sync(conn, source="repository", scope="do-an", doc_type="do_an",
                  records=[("u1", {"archive": {"title": "A", "_page": 1, "_backfill": {"cohort": "21"}}})],
                  expected=1, full=True)
    assert len(rows(conn, "SELECT 1 FROM source_record WHERE source_key='u1'")) == 1

def test_real_content_change_still_creates_a_version(conn):
    for title in ("A", "B"):
        sync.run_sync(conn, source="repository", scope="do-an", doc_type="do_an",
                      records=[("u1", {"archive": {"title": title, "_page": 1}})], expected=1, full=True)
    vs = rows(conn, "SELECT version FROM source_record WHERE source_key='u1' ORDER BY version")
    assert [v["version"] for v in vs] == [1, 2]
