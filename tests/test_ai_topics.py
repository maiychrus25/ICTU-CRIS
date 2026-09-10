# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import itertools
import pytest
from cris.ai import topics as T
from cris.ai.provider import FakeProvider

_seq = itertools.count()


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, keywords=None, title=None):
    title = title or f"Công trình {next(_seq)}"
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,'do_an',%s,'{}')", title, title)
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, keywords_raw, state) "
                   "VALUES ('do_an', currval('source_record_id_seq'), %s, %s, %s, 'DaChuanHoa') RETURNING id",
             title, title.lower(), keywords)[0]["id"]


def _counts(conn):
    return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"]
            for t in ("work", "author_link", "duplicate_group")}


# Ba nhóm từ khoá tách biệt hẳn về từ vựng (fake provider gom theo túi từ chia
# sẻ): tiếng Anh, IoT, cơ sở dữ liệu. Mỗi nhóm có một từ khoá "nhãn" được lặp ở
# nhiều công trình hơn hẳn ba từ khoá còn lại, để nhãn cụm dự đoán được.
GROUPS = {
    "hoc tieng anh a": (["hoc tieng anh a"] * 5 +
                        ["hoc tieng anh b", "hoc tieng anh c", "hoc tieng anh d"]),
    "mang cam bien e": (["mang cam bien e"] * 5 +
                        ["mang cam bien f", "mang cam bien g", "mang cam bien h"]),
    "co so du lieu i": (["co so du lieu i"] * 5 +
                        ["co so du lieu j", "co so du lieu k", "co so du lieu l"]),
}


def _seed_groups(conn):
    for kws in GROUPS.values():
        for kw in kws:
            mk_work(conn, keywords=kw)


def test_collect_keywords_splits_normalizes_counts_and_drops_single_char(conn):
    mk_work(conn, keywords="Học tiếng Anh, AI")
    mk_work(conn, keywords="học TIẾNG anh; Machine Learning")
    mk_work(conn, keywords="a, học tiếng anh")
    freq = T.collect_keywords(conn)
    assert freq["học tiếng anh"] == 3
    assert freq["ai"] == 1 and freq["machine learning"] == 1
    assert "a" not in freq


def test_build_topics_recovers_the_three_groups_with_correct_labels(conn):
    _seed_groups(conn)
    out = T.build_topics(conn, FakeProvider(), k=3, seed=0)
    assert out["topics"] == 3 and out["keywords"] == 12

    rows = q(conn, "SELECT t.label, tk.keyword FROM ai_topic t JOIN ai_topic_keyword tk ON tk.topic_id = t.id")
    by_label = {}
    for r in rows:
        by_label.setdefault(r["label"], set()).add(r["keyword"])

    assert set(by_label) == set(GROUPS)
    for label, keywords in GROUPS.items():
        assert by_label[label] == set(keywords)


def test_build_topics_rerun_does_not_duplicate_rows(conn):
    _seed_groups(conn)
    p = FakeProvider()
    T.build_topics(conn, p, k=3, seed=0)
    T.build_topics(conn, p, k=3, seed=0)
    assert q(conn, "SELECT count(*) AS n FROM ai_topic")[0]["n"] == 3
    assert q(conn, "SELECT count(*) AS n FROM ai_topic_keyword")[0]["n"] == 12


def test_k_larger_than_distinct_keywords_shrinks_k(conn):
    for kw in ("mot", "hai", "ba"):
        mk_work(conn, keywords=kw)
    out = T.build_topics(conn, FakeProvider(), k=40, seed=0)
    assert out["keywords"] == 3 and out["topics"] <= 3
    assert q(conn, "SELECT count(*) AS n FROM ai_topic")[0]["n"] == out["topics"]


def test_topic_of_work_returns_majority_label(conn):
    _seed_groups(conn)
    p = FakeProvider()
    T.build_topics(conn, p, k=3, seed=0)
    w = mk_work(conn, keywords="hoc tieng anh a, hoc tieng anh b")
    assert T.topic_of_work(conn, w) == "hoc tieng anh a"


def test_topic_of_work_without_keywords_is_none(conn):
    w = mk_work(conn, keywords=None)
    assert T.topic_of_work(conn, w) is None


def test_build_topics_never_touches_business_tables(conn):
    """Rào chắn BR-18: build_topics chỉ ghi vào ai_topic*."""
    _seed_groups(conn)
    before = _counts(conn)
    T.build_topics(conn, FakeProvider(), k=3, seed=0)
    assert _counts(conn) == before
