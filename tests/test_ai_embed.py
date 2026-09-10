# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import pytest
from cris.ai import embed as E
from cris.ai.provider import FakeProvider


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, abstract=None, keywords=None, merged_into=None):
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,'do_an',%s,'{}')", title, title)
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, keywords_raw, "
                   "state, merged_into_id) VALUES ('do_an', currval('source_record_id_seq'), %s, %s, %s, %s, "
                   "%s, %s) RETURNING id", title, title.lower(), abstract, keywords,
            "DaGop" if merged_into else "DaChuanHoa", merged_into)[0]["id"]


def _counts(conn):
    return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"]
            for t in ("work", "author_link", "duplicate_group", "field_provenance")}


def test_work_text_joins_title_abstract_keywords():
    assert E.work_text({"title": "A", "abstract": "B", "keywords_raw": None}) == "A\nB"


def test_first_run_builds_every_live_work_second_run_builds_none(conn):
    p = FakeProvider()
    for i in range(3):
        mk_work(conn, f"Công trình {i}", abstract="tóm tắt")
    r1 = E.build_embeddings(conn, p)
    assert (r1["built"], r1["skipped"], r1["dim"]) == (3, 0, 32)
    r2 = E.build_embeddings(conn, p)
    assert (r2["built"], r2["skipped"]) == (0, 3)
    rows = q(conn, "SELECT work_id, model, dim, array_length(vector,1) AS n FROM ai_embedding ORDER BY work_id")
    assert len(rows) == 3 and all(r["model"] == "fake-32" and r["dim"] == r["n"] == 32 for r in rows)


def test_changed_text_is_rebuilt_only_for_that_work(conn):
    p = FakeProvider()
    a = mk_work(conn, "Đề tài A", abstract="x")
    mk_work(conn, "Đề tài B", abstract="y")
    E.build_embeddings(conn, p)
    before = q(conn, "SELECT vector FROM ai_embedding WHERE work_id=%s", a)[0]["vector"]
    q(conn, "UPDATE work SET title='Đề tài A đã sửa' WHERE id=%s", a)
    conn.commit()
    r = E.build_embeddings(conn, p)
    assert r["built"] == 1
    after = q(conn, "SELECT vector FROM ai_embedding WHERE work_id=%s", a)[0]["vector"]
    assert after != before


def test_merged_work_is_not_embedded(conn):
    p = FakeProvider()
    keep = mk_work(conn, "Bản giữ")
    mk_work(conn, "Bản đã gộp", merged_into=keep)
    r = E.build_embeddings(conn, p)
    assert r["built"] == 1
    assert q(conn, "SELECT count(*) AS n FROM ai_embedding")[0]["n"] == 1


def test_only_missing_false_rebuilds_everything(conn):
    p = FakeProvider()
    mk_work(conn, "A"); mk_work(conn, "B")
    E.build_embeddings(conn, p)
    r = E.build_embeddings(conn, p, only_missing=False)
    assert r["built"] == 2


def test_load_matrix_and_top_k_order(conn):
    np = pytest.importorskip("numpy")
    p = FakeProvider()
    ids = [mk_work(conn, t) for t in ("học tiếng Anh trẻ em", "học từ vựng tiếng Anh", "đèn chiếu sáng IoT")]
    E.build_embeddings(conn, p)
    wids, M = E.load_matrix(conn, p.model_id)
    assert wids == sorted(ids) and M.shape == (3, 32)
    qv = p.embed(["ứng dụng học tiếng Anh"])[0]
    ranked = E.top_k(M, qv, k=3)
    assert [wids[i] for i, _ in ranked][:2] == ids[:2]           # hai công trình tiếng Anh lên đầu
    assert ranked[0][1] >= ranked[1][1] >= ranked[2][1]
    assert E.top_k(np.zeros((0, 0), dtype=np.float32), qv) == []


def test_build_embeddings_never_touches_business_tables(conn):
    """Rào chắn BR-18: AI chỉ ghi vào bảng ai_*."""
    for i in range(2):
        mk_work(conn, f"W{i}")
    before = _counts(conn)
    E.build_embeddings(conn, FakeProvider())
    assert _counts(conn) == before


def test_status_reports_provider_and_counts(conn):
    p = FakeProvider()
    mk_work(conn, "A")
    E.build_embeddings(conn, p)
    s = E.status(conn, p)
    assert s["provider"] == "fake" and s["works"] == 1
    assert s["embeddings"][0]["model"] == "fake-32" and s["embeddings"][0]["n"] == 1
