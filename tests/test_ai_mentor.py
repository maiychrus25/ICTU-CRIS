# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Gợi ý người hướng dẫn cho đồ án ICTU_TEACHER (lát cắt I3):

`cris.ai.mentor.suggest_mentors` và `/api/ai/mentors`, `/api/ai/mentors/{id}/accept`."""
import itertools

import pytest
from fastapi.testclient import TestClient

from cris.ai import embed as E
from cris.ai import mentor as M
from cris.ai.provider import (
    AIDisabled,
    FakeProvider,
    NoneProvider,
    clear_provider_cache,
)
from cris.api.app import create_app

_seq = itertools.count()

TITLE = "Xây dựng website bán hàng trực tuyến cho cửa hàng thời trang"


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_work(conn, title=TITLE, abstract=None, doc_type="do_an"):
    source_key = f"{title} #{next(_seq)}"
    abstract = title if abstract is None else abstract
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,'h','{}')", source_key, doc_type)
    return q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, abstract, state) "
                   "VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, 'DaChuanHoa') RETURNING id",
             doc_type, title, title.lower(), abstract)[0]["id"]


def mk_mention(conn, work_id, raw, role="mentor", position=0, is_placeholder=False, degree=None):
    return q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, "
                   "degree_raw, is_placeholder) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
             work_id, role, position, raw, raw.lower(), raw.lower(), degree, is_placeholder)[0]["id"]


def mk_person(conn, name, degree=None):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys, degree_raw) "
                   "VALUES ('lecturer',%s,%s,%s,%s) RETURNING id",
             name, name.lower(), [name.lower()], degree)[0]["id"]


def mk_link(conn, mention_id, person_id, state, confidence="ten_day_du_duy_nhat"):
    return q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, basis, state) "
                   "VALUES (%s,%s,%s,'{}',%s) RETURNING id",
             mention_id, person_id, confidence, state)[0]["id"]


def _counts(conn):
    return {t: q(conn, f"SELECT count(*) AS n FROM {t}")[0]["n"]
            for t in ("work", "author_link", "person", "duplicate_group", "declaration")}


def _mentor_payload(conn, work_id):
    rows = q(conn, "SELECT payload FROM ai_suggestion WHERE kind='mentor' AND target_id=%s", work_id)
    return rows[0]["payload"] if rows else None


# ---------- cris.ai.mentor.suggest_mentors ----------

def test_placeholder_mentor_suggested_from_two_confirmed_neighbours(conn):
    p = mk_person(conn, "Nguyễn Văn An", degree="ThS")
    w1 = mk_work(conn); m1 = mk_mention(conn, w1, "Nguyễn Văn An")
    mk_link(conn, m1, p, "DaXacNhan")
    w2 = mk_work(conn); m2 = mk_mention(conn, w2, "Nguyễn Văn An")
    mk_link(conn, m2, p, "DaNoiTuDong")
    w3 = mk_work(conn); m3 = mk_mention(conn, w3, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = M.suggest_mentors(conn, prov)
    assert out == {"scanned": 1, "suggested": 1}

    payload = _mentor_payload(conn, w3)
    assert payload["mention_id"] == m3
    assert len(payload["candidates"]) == 1
    c = payload["candidates"][0]
    assert c["person_id"] == p
    assert c["display_name"] == "Nguyễn Văn An"
    assert c["degree"] == "ThS"
    assert c["votes"] == 2
    assert c["score"] == pytest.approx(2.0)
    evidence_ids = {e["work_id"] for e in c["evidence"]}
    assert evidence_ids == {w1, w2}


def test_below_min_votes_not_suggested(conn):
    p = mk_person(conn, "Trần Thị Bình")
    w1 = mk_work(conn); m1 = mk_mention(conn, w1, "Trần Thị Bình")
    mk_link(conn, m1, p, "DaXacNhan")
    w2 = mk_work(conn); mk_mention(conn, w2, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = M.suggest_mentors(conn, prov)
    assert out == {"scanned": 1, "suggested": 0}
    assert _mentor_payload(conn, w2) is None


def test_unlinked_mentor_neighbour_is_ignored(conn):
    """Lượt tên vai mentor không giữ chỗ nhưng chưa liên kết (không có
    author_link, hoặc chỉ ChoXacNhan — chưa "đã liên kết thật") không được
    tính vào tập láng giềng, dù trùng đề tài."""
    w1 = mk_work(conn); mk_mention(conn, w1, "Lê Văn Cường")  # không author_link nào
    p2 = mk_person(conn, "Phạm Thị Dung")
    w1b = mk_work(conn); m1b = mk_mention(conn, w1b, "Phạm Thị Dung")
    mk_link(conn, m1b, p2, "ChoXacNhan")  # đang chờ, chưa phải "đã liên kết thật"
    w2 = mk_work(conn); mk_mention(conn, w2, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    out = M.suggest_mentors(conn, prov)
    assert out == {"scanned": 1, "suggested": 0}
    assert _mentor_payload(conn, w2) is None


def test_rerun_upsert_is_idempotent(conn):
    p = mk_person(conn, "Nguyễn Văn An")
    w1 = mk_work(conn); m1 = mk_mention(conn, w1, "Nguyễn Văn An")
    mk_link(conn, m1, p, "DaXacNhan")
    w2 = mk_work(conn); m2 = mk_mention(conn, w2, "Nguyễn Văn An")
    mk_link(conn, m2, p, "DaNoiTuDong")
    w3 = mk_work(conn); mk_mention(conn, w3, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    M.suggest_mentors(conn, prov)
    first = _mentor_payload(conn, w3)
    M.suggest_mentors(conn, prov)
    second = _mentor_payload(conn, w3)
    assert q(conn, "SELECT count(*) AS n FROM ai_suggestion WHERE kind='mentor'")[0]["n"] == 1
    assert first == second


def test_stale_suggestion_removed_when_candidate_no_longer_qualifies(conn):
    p = mk_person(conn, "Nguyễn Văn An")
    w1 = mk_work(conn); m1 = mk_mention(conn, w1, "Nguyễn Văn An")
    mk_link(conn, m1, p, "DaXacNhan")
    w2 = mk_work(conn); m2 = mk_mention(conn, w2, "Nguyễn Văn An")
    l2 = mk_link(conn, m2, p, "DaNoiTuDong")
    w3 = mk_work(conn); mk_mention(conn, w3, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    assert M.suggest_mentors(conn, prov) == {"scanned": 1, "suggested": 1}
    assert _mentor_payload(conn, w3) is not None

    q(conn, "UPDATE author_link SET state='DaBacBo', reason='thu hồi' WHERE id=%s", l2)
    conn.commit()
    assert M.suggest_mentors(conn, prov) == {"scanned": 1, "suggested": 0}
    assert _mentor_payload(conn, w3) is None


def test_provider_none_raises_ai_disabled(conn):
    w = mk_work(conn)
    mk_mention(conn, w, "ICTU_TEACHER", is_placeholder=True)
    with pytest.raises(AIDisabled):
        M.suggest_mentors(conn, NoneProvider())


def test_suggest_mentors_never_touches_business_tables(conn):
    p = mk_person(conn, "Nguyễn Văn An")
    w1 = mk_work(conn); m1 = mk_mention(conn, w1, "Nguyễn Văn An")
    mk_link(conn, m1, p, "DaXacNhan")
    w2 = mk_work(conn); m2 = mk_mention(conn, w2, "Nguyễn Văn An")
    mk_link(conn, m2, p, "DaNoiTuDong")
    w3 = mk_work(conn); mk_mention(conn, w3, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()

    before = _counts(conn)
    M.suggest_mentors(conn, prov)
    assert _counts(conn) == before


# ---------- /api/ai/mentors, /api/ai/mentors/{id}/accept ----------

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


def _seed_suggestion(conn):
    """2 đồ án đã có Nguyễn Văn An hướng dẫn (đã xác nhận), 1 đồ án giữ chỗ
    ICTU_TEACHER cùng đề tài — trả (work_id đích, mention_id, person_id)."""
    p = mk_person(conn, "Nguyễn Văn An", degree="ThS")
    w1 = mk_work(conn); m1 = mk_mention(conn, w1, "Nguyễn Văn An")
    mk_link(conn, m1, p, "DaXacNhan")
    w2 = mk_work(conn); m2 = mk_mention(conn, w2, "Nguyễn Văn An")
    mk_link(conn, m2, p, "DaNoiTuDong")
    w3 = mk_work(conn); m3 = mk_mention(conn, w3, "ICTU_TEACHER", is_placeholder=True)
    prov = FakeProvider()
    E.build_embeddings(conn, prov)
    conn.commit()
    M.suggest_mentors(conn, prov)
    conn.commit()
    return w3, m3, p


def test_api_list_mentors_and_filters_by_min_votes(client, conn):
    w3, m3, p = _seed_suggestion(conn)

    r = client.get("/api/ai/mentors").json()
    assert r["page"]["total"] == 1
    item = r["items"][0]
    assert item["work_id"] == w3 and item["mention_id"] == m3
    assert item["pending_link"] is None
    cand = item["candidates"][0]
    assert cand["person_id"] == p and cand["votes"] == 2 and set(cand.keys()) >= {"display_name", "degree", "score", "evidence"}

    assert client.get("/api/ai/mentors", params={"min_votes": 3}).json()["items"] == []
    assert client.get("/api/ai/mentors", params={"min_votes": 2}).json()["page"]["total"] == 1


def test_accept_creates_pending_link_visible_in_author_queue(client, conn, user_id):
    w3, _m3, p = _seed_suggestion(conn)

    r = client.post(f"/api/ai/mentors/{w3}/accept", json={"person_id": p})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True and body["person_id"] == p and body["state"] == "ChoXacNhan"
    link_id = body["link_id"]

    items = client.get("/api/queue/authors", params={"state": "ChoXacNhan"}).json()["items"]
    row = next(x for x in items if x["link_id"] == link_id)
    assert row["candidate_person_id"] == p and row["confidence"] == "ai_mentor" and row["work_id"] == w3

    actions = [a["action"] for a in q(conn, "SELECT action FROM audit_log")]
    assert "link.ai_candidate" in actions


def test_accept_twice_returns_409(client, conn, user_id):
    w3, _m3, p = _seed_suggestion(conn)
    assert client.post(f"/api/ai/mentors/{w3}/accept", json={"person_id": p}).status_code == 200
    r = client.post(f"/api/ai/mentors/{w3}/accept", json={"person_id": p})
    assert r.status_code == 409


def test_accept_unknown_candidate_returns_404(client, conn, user_id):
    w3, _m3, _p = _seed_suggestion(conn)
    other = mk_person(conn, "Người Khác")
    conn.commit()
    r = client.post(f"/api/ai/mentors/{w3}/accept", json={"person_id": other})
    assert r.status_code == 404


def test_accept_without_suggestion_returns_404(client, conn, user_id):
    w = mk_work(conn)
    conn.commit()
    r = client.post(f"/api/ai/mentors/{w}/accept", json={"person_id": 1})
    assert r.status_code == 404


def test_accept_writes_only_author_link_and_audit_log(client, conn, user_id):
    w3, _m3, p = _seed_suggestion(conn)
    before = _counts(conn)
    before_audit = q(conn, "SELECT count(*) AS n FROM audit_log")[0]["n"]

    r = client.post(f"/api/ai/mentors/{w3}/accept", json={"person_id": p})
    assert r.status_code == 200

    after = _counts(conn)
    assert after["author_link"] == before["author_link"] + 1
    for t in ("work", "person", "duplicate_group", "declaration"):
        assert after[t] == before[t]
    after_audit = q(conn, "SELECT count(*) AS n FROM audit_log")[0]["n"]
    assert after_audit == before_audit + 1
