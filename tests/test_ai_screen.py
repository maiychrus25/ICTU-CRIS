# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Rà soát trùng đề tài theo khoá (E5): `cris.ai.screen.screen_cohort` và `/api/ai/screen*`."""
import itertools

import pytest
from fastapi.testclient import TestClient

from cris.ai import embed as E
from cris.ai import screen as S
from cris.ai.provider import (
    AIDisabled,
    FakeProvider,
    NoneProvider,
    clear_provider_cache,
)
from cris.api.app import create_app

_seq = itertools.count()


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title, abstract=None, cohort=None, doc_type="do_an"):
    """`source_key` mang thêm số thứ tự — nhiều công trình trong test cố ý cùng
    `title` (để mô phỏng đề tài trùng qua các khoá) nhưng `source_key` phải khác
    nhau để không đụng `source_record_version_unique`."""
    source_key = f"{title} #{next(_seq)}"
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,'h','{}')", source_key, doc_type)
    wid = q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, cohort, state) "
                  "VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, 'DaChuanHoa') RETURNING id",
            doc_type, title, title.lower(), abstract, cohort)[0]["id"]
    conn.commit()
    return wid


def _counts(conn):
    return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"] for t in ("work", "author_link")}


SAME_TITLE = "Xây dựng website bán hàng trực tuyến"
OTHER_TITLE = "Thiết kế hệ thống đèn chiếu sáng thông minh IoT"
# Chung phần lớn từ với SAME_TITLE ("xây dựng", "bán hàng", "trực tuyến") nhưng đổi
# "website" -> "ứng dụng": cosine đo được với FakeProvider ~0.8007 — vừa qua ngưỡng
# MID=0.80 (mức "vua"), dưới HIGH=0.90 (mức "cao") — dùng để kiểm mức giữa và sắp xếp.
MID_TITLE = "Xây dựng ứng dụng bán hàng trực tuyến"


# ---------- cris.ai.screen.screen_cohort ----------

def test_same_title_across_cohorts_is_flagged(conn):
    w17 = mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    w18 = mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    out = S.screen_cohort(conn, p, cohort="K18")
    assert out == {"screened": 1, "flagged": 1}

    row = q(conn, "SELECT payload FROM ai_suggestion WHERE kind='topic_overlap' AND target_id=%s", w18)[0]
    payload = row["payload"]
    assert payload["cohort"] == "K18"
    assert payload["level"] == "cao"
    assert payload["max_score"] == pytest.approx(1.0)
    neighbour_ids = {n["work_id"] for n in payload["neighbours"]}
    assert w17 in neighbour_ids
    n17 = next(n for n in payload["neighbours"] if n["work_id"] == w17)
    assert n17["cohort"] == "K17"
    assert n17["aspects"]["bai_toan"] == "cao"
    for a in ("doi_tuong", "pham_vi", "phuong_phap"):
        assert n17["aspects"][a] == "khong_du_du_lieu"


def test_dissimilar_work_is_not_flagged(conn):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    w18 = mk_work(conn, OTHER_TITLE, abstract=OTHER_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    out = S.screen_cohort(conn, p, cohort="K18")
    assert out["screened"] == 1
    assert out["flagged"] == 0

    payload = q(conn, "SELECT payload FROM ai_suggestion WHERE kind='topic_overlap' AND target_id=%s", w18)[0]["payload"]
    assert payload["level"] == "thap"
    assert payload["max_score"] < 0.80


def test_mid_similarity_is_vua_not_flagged(conn):
    """MID_TITLE chia phần lớn từ với SAME_TITLE (~0.80, vừa qua MID) nhưng dưới HIGH
    (0.90) — mức "vua": đáng chú ý nhưng chưa đủ để gắn cờ "cao"."""
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    w18 = mk_work(conn, MID_TITLE, abstract=MID_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    out = S.screen_cohort(conn, p, cohort="K18")
    assert out == {"screened": 1, "flagged": 0}

    payload = q(conn, "SELECT payload FROM ai_suggestion WHERE kind='topic_overlap' AND target_id=%s", w18)[0]["payload"]
    assert payload["level"] == "vua"
    assert 0.80 <= payload["max_score"] < 0.90


def test_same_cohort_neighbour_is_excluded(conn):
    w18a = mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")  # cùng khoá — phải bị loại làm láng giềng
    w17 = mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    out = S.screen_cohort(conn, p, cohort="K18")
    assert out["screened"] == 2

    payload_a = q(conn, "SELECT payload FROM ai_suggestion WHERE kind='topic_overlap' AND target_id=%s", w18a)[0]["payload"]
    neighbour_ids = {n["work_id"] for n in payload_a["neighbours"]}
    assert w17 in neighbour_ids
    assert all(n["cohort"] != "K18" for n in payload_a["neighbours"])


def test_rerun_does_not_duplicate_rows(conn):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    S.screen_cohort(conn, p, cohort="K18")
    S.screen_cohort(conn, p, cohort="K18")
    assert q(conn, "SELECT count(*) AS n FROM ai_suggestion WHERE kind='topic_overlap'")[0]["n"] == 1


def test_provider_none_raises_ai_disabled(conn):
    mk_work(conn, SAME_TITLE, cohort="K18")
    with pytest.raises(AIDisabled):
        S.screen_cohort(conn, NoneProvider(), cohort="K18")


def test_screen_cohort_never_touches_business_tables(conn):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()

    before = _counts(conn)
    S.screen_cohort(conn, p, cohort="K18")
    assert _counts(conn) == before


# ---------- /api/ai/screen, /api/ai/screen/cohorts ----------

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


def test_api_screen_filters_by_cohort_and_min(client, conn, user_id):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    w18 = mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()
    S.screen_cohort(conn, p, cohort="K18")
    conn.commit()

    r = client.get("/api/ai/screen", params={"cohort": "K18"}).json()
    assert r["page"]["total"] == 1
    assert r["items"][0]["work_id"] == w18
    assert r["items"][0]["level"] == "cao"
    assert r["items"][0]["max_score"] == pytest.approx(1.0)
    assert "K18" in r["cohorts"]

    r_min_cao = client.get("/api/ai/screen", params={"min": "cao"}).json()
    assert any(it["work_id"] == w18 for it in r_min_cao["items"])

    r_other_cohort = client.get("/api/ai/screen", params={"cohort": "K17"}).json()
    assert r_other_cohort["items"] == []


def test_api_screen_min_excludes_low_level(client, conn, user_id):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    mk_work(conn, OTHER_TITLE, abstract=OTHER_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()
    S.screen_cohort(conn, p, cohort="K18")
    conn.commit()

    r = client.get("/api/ai/screen", params={"min": "cao"}).json()
    assert r["items"] == []


def test_api_screen_cohorts_summary(client, conn, user_id):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()
    S.screen_cohort(conn, p, cohort="K18")
    conn.commit()

    r = client.get("/api/ai/screen/cohorts").json()
    assert {"cohort": "K18", "screened": 1, "flagged": 1} in r


def test_api_screen_min_score_and_sorted_by_max_score_desc(client, conn, user_id):
    mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K17")
    w_high = mk_work(conn, SAME_TITLE, abstract=SAME_TITLE, cohort="K18")
    w_mid = mk_work(conn, MID_TITLE, abstract=MID_TITLE, cohort="K18")
    w_low = mk_work(conn, OTHER_TITLE, abstract=OTHER_TITLE, cohort="K18")
    p = FakeProvider()
    E.build_embeddings(conn, p)
    conn.commit()
    S.screen_cohort(conn, p, cohort="K18")
    conn.commit()

    r = client.get("/api/ai/screen", params={"cohort": "K18"}).json()
    assert [it["work_id"] for it in r["items"]] == [w_high, w_mid, w_low]
    scores = {it["work_id"]: it["max_score"] for it in r["items"]}
    assert scores[w_high] == pytest.approx(1.0)
    assert 0.80 <= scores[w_mid] < 0.90
    assert scores[w_low] < 0.80

    r_min_score = client.get("/api/ai/screen", params={"cohort": "K18", "min_score": 0.85}).json()
    assert [it["work_id"] for it in r_min_score["items"]] == [w_high]
