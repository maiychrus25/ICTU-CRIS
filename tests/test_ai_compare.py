# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import pytest

from cris.ai import compare as C
from cris.ai import embed as E
from cris.ai.provider import FakeProvider, NoneProvider


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, abstract=None, keywords=None, doc_type="do_an", merged_into=None):
    """Sao chép từ `tests/test_ai_embed.py` — công trình gộp mang state='DaGop'."""
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,%s,'{}')", title, doc_type, title)
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, keywords_raw, "
                   "state, merged_into_id) VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, "
                   "%s, %s) RETURNING id", doc_type, title, title.lower(), abstract, keywords,
            "DaGop" if merged_into else "DaChuanHoa", merged_into)[0]["id"]


def _counts(conn):
    return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"]
            for t in ("work", "author_link", "duplicate_group", "field_provenance")}


ENGLISH_TITLES = [
    "Ứng dụng học tiếng Anh cho trẻ em luyện phát âm",
    "Phần mềm học từ vựng tiếng Anh dành cho học sinh tiểu học",
    "Hệ thống luyện nghe nói tiếng Anh cho trẻ em mẫu giáo",
]
OTHER_TITLES = [
    "Thiết kế hệ thống đèn chiếu sáng thông minh IoT",
    "Xây dựng cơ sở dữ liệu quản lý kho hàng",
    "Mạng cảm biến không dây giám sát môi trường",
]


def _seed_six_works(conn, abstract_for_first=None):
    english_ids = []
    for i, t in enumerate(ENGLISH_TITLES):
        abstract = abstract_for_first if (i == 0 and abstract_for_first) else None
        english_ids.append(mk_work(conn, t, abstract=abstract))
    other_ids = [mk_work(conn, t) for t in OTHER_TITLES]
    return english_ids, other_ids


# ---- Sentence split / keyword normalization (hàm thuần, không cần DB) ----

def test_split_sentences_on_dot_semicolon_newline():
    text = "Câu một. Câu hai; Câu ba\nCâu bốn."
    assert C._split_sentences(text) == ["Câu một", "Câu hai", "Câu ba", "Câu bốn"]


def test_split_sentences_empty_text_gives_empty_list():
    assert C._split_sentences(None) == []
    assert C._split_sentences("   ") == []


def test_norm_tokens_strips_accents_lowercases_and_drops_stopwords():
    toks = C._norm_tokens("Học Tiếng Anh của trẻ em")
    assert "hoc" in toks and "tieng" in toks and "anh" in toks
    assert "cua" not in toks  # stopword


# ---- Đối chiếu ngữ nghĩa (provider fake) ----

def test_semantic_top_k_ranks_same_topic_works_first(conn):
    p = FakeProvider()
    english_ids, other_ids = _seed_six_works(conn)
    E.build_embeddings(conn, p)

    r = C.compare_topic(
        conn, p, title="học tiếng Anh cho trẻ em luyện phát âm", description="",
        aspects={}, k=6,
    )
    assert r["fallback"] is False
    top3 = {res["work_id"] for res in r["results"][:3]}
    assert top3 == set(english_ids)
    assert set(res["work_id"] for res in r["results"][3:]) == set(other_ids)


def test_aspect_filled_produces_non_chua_du_and_unfilled_stays_chua_du(conn):
    p = FakeProvider()
    aspect_sentence = "trẻ em khó phát âm tiếng Anh chuẩn"
    abstract = f"Nghiên cứu bài toán {aspect_sentence}. Đối tượng là học sinh tiểu học."
    english_ids, _ = _seed_six_works(conn, abstract_for_first=abstract)
    E.build_embeddings(conn, p)

    r = C.compare_topic(
        conn, p, title="học tiếng Anh cho trẻ em luyện phát âm", description="",
        aspects={"bai_toan": aspect_sentence}, k=6,
    )
    top = next(res for res in r["results"] if res["work_id"] == english_ids[0])
    assert top["aspects"]["bai_toan"] != "chua_du"
    # ba khía cạnh không nhập luôn là "chua_du", với mọi công trình trả về
    for res in r["results"]:
        assert res["aspects"]["doi_tuong"] == "chua_du"
        assert res["aspects"]["pham_vi"] == "chua_du"
        assert res["aspects"]["phuong_phap"] == "chua_du"


def test_no_aspects_given_all_results_are_chua_du(conn):
    p = FakeProvider()
    _seed_six_works(conn)
    E.build_embeddings(conn, p)

    r = C.compare_topic(conn, p, title="học tiếng Anh cho trẻ em", description="", aspects={}, k=6)
    for res in r["results"]:
        assert all(v == "chua_du" for v in res["aspects"].values())


def test_doc_types_filter_narrows_results(conn):
    p = FakeProvider()
    english_ids, other_ids = _seed_six_works(conn)
    q(conn, "UPDATE work SET doc_type='bai_bao' WHERE id = %s", other_ids[0])
    E.build_embeddings(conn, p)

    r = C.compare_topic(
        conn, p, title="học tiếng Anh cho trẻ em", description="", aspects={}, k=10,
        doc_types=["bai_bao"],
    )
    assert all(res["doc_type"] == "bai_bao" for res in r["results"])
    assert {res["work_id"] for res in r["results"]} == {other_ids[0]}


# ---- Đường lui khi provider=none ----

def test_provider_none_falls_back_to_keyword_match_without_raising(conn):
    _seed_six_works(conn)
    r = C.compare_topic(
        conn, NoneProvider(), title="học tiếng Anh cho trẻ em luyện phát âm", description="",
        aspects={"bai_toan": "phát âm"}, k=6,
    )
    assert r["fallback"] is True
    assert r["provider"] == "none"
    assert len(r["results"]) >= 1
    assert all(v == "chua_du" for res in r["results"] for v in res["aspects"].values())
    top_titles = {res["title"] for res in r["results"]}
    assert top_titles & set(ENGLISH_TITLES)


def test_provider_none_no_query_tokens_returns_empty_without_raising(conn):
    _seed_six_works(conn)
    r = C.compare_topic(conn, NoneProvider(), title="", description="", aspects={}, k=6)
    assert r["fallback"] is True
    assert r["results"] == []


# ---- ai_query được ghi ----

def test_ai_query_is_recorded_with_created_by(conn, user_id):
    p = FakeProvider()
    _seed_six_works(conn)
    E.build_embeddings(conn, p)

    r = C.compare_topic(
        conn, p, title="học tiếng Anh cho trẻ em", description="mô tả", aspects={}, k=6,
        actor_id=user_id,
    )
    row = q(conn, "SELECT provider, created_by, input, results FROM ai_query WHERE id = %s", r["query_id"])[0]
    assert row["provider"] == "fake"
    assert row["created_by"] == user_id
    assert row["input"]["title"] == "học tiếng Anh cho trẻ em"
    assert len(row["results"]) == len(r["results"])


def test_compare_topic_never_touches_business_tables(conn, user_id):
    """Rào chắn BR-18: AI chỉ ghi vào ai_query, không đụng work/author_link/...."""
    p = FakeProvider()
    _seed_six_works(conn)
    E.build_embeddings(conn, p)
    before = _counts(conn)
    C.compare_topic(conn, p, title="học tiếng Anh", description="", aspects={}, k=6, actor_id=user_id)
    C.compare_topic(conn, NoneProvider(), title="học tiếng Anh", description="", aspects={}, k=6, actor_id=user_id)
    assert _counts(conn) == before
