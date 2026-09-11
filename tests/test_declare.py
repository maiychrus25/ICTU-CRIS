# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Nghiệp vụ kê khai công trình vào kỳ (`cris.declare`, lát cắt K, G3): mở kỳ
qua `cris.period` (không sửa module đó), rồi kê khai/đổi trạng thái/minh
chứng qua `cris.declare` trên PostgreSQL thật (fixture `conn`)."""
from datetime import UTC, datetime, timedelta

import pytest

from cris import declare, period, rules


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def mk_work(conn, title="Bài báo kê khai", doc_type="bai_bao"):
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (currval('sync_run_id_seq'),'manual',%s,%s,'h','{}')", title, doc_type)
    wid = q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) "
                  "VALUES (%s, currval('source_record_id_seq'), %s, %s, 'DaChuanHoa') RETURNING id",
            doc_type, title, title.lower())[0]["id"]
    conn.commit()
    return wid


def due_soon(days=30):
    return datetime.now(UTC) + timedelta(days=days)


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


def open_basic(conn, user_id, code="K2026-DEC"):
    return period.open_period(
        conn, code=code, name="Kỳ báo cáo kê khai", scope={"doc_types": ["bai_bao"]},
        criteria=None, due_at=due_soon(), actor_id=user_id)


class TestAddDeclaration:
    def test_add_declaration_on_closed_period_raises(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-1")
        period.close_submissions(conn, pid, user_id)
        with pytest.raises(ValueError):
            declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)

    def test_add_declaration_duplicate_raises(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-2")
        declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        with pytest.raises(ValueError, match="đã kê khai"):
            declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)

    def test_add_declaration_dead_work_raises(self, conn, user_id):
        unit_id = mk_unit(conn)
        survivor = mk_work(conn, "Bản sống sót")
        merged = mk_work(conn, "Bản đã gộp")
        q(conn, "UPDATE work SET state='DaGop', merged_into_id=%s WHERE id=%s", survivor, merged)
        conn.commit()
        pid = open_basic(conn, user_id, code="K2026-DEC-3")
        with pytest.raises(ValueError):
            declare.add_declaration(conn, period_id=pid, work_id=merged, unit_id=unit_id, actor_id=user_id)

    def test_add_declaration_writes_nhap_event_and_audit(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-4")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id,
                                      note="ghi chú")
        row = q(conn, "SELECT state, note FROM declaration WHERE id=%s", did)[0]
        assert row["state"] == "Nhap" and row["note"] == "ghi chú"
        events = q(conn, "SELECT from_state, to_state FROM declaration_event WHERE declaration_id=%s", did)
        assert events == [{"from_state": None, "to_state": "Nhap"}]
        audit_rows = q(conn, "SELECT action FROM audit_log WHERE entity='declaration' AND entity_id=%s", did)
        assert [r["action"] for r in audit_rows] == ["declaration.add"]


class TestSetState:
    def test_transition_requires_reason(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-5")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        with pytest.raises(ValueError):
            declare.set_state(conn, did, "ChoBoSung", user_id)
        with pytest.raises(ValueError):
            declare.set_state(conn, did, "Rut", user_id)

    def test_valid_round_trip_nhap_chobosung_nhap_rut(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-6")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)

        declare.set_state(conn, did, "ChoBoSung", user_id, reason="thiếu minh chứng")
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "ChoBoSung"

        declare.set_state(conn, did, "Nhap", user_id)
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "Nhap"

        declare.set_state(conn, did, "Rut", user_id, reason="rút vì trùng")
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "Rut"

        events = q(conn, "SELECT from_state, to_state FROM declaration_event WHERE declaration_id=%s ORDER BY id", did)
        assert [(e["from_state"], e["to_state"]) for e in events] == [
            (None, "Nhap"), ("Nhap", "ChoBoSung"), ("ChoBoSung", "Nhap"), ("Nhap", "Rut")]
        actions = q(conn, "SELECT action FROM audit_log WHERE entity='declaration' AND entity_id=%s ORDER BY id", did)
        assert [a["action"] for a in actions] == [
            "declaration.add", "declaration.ChoBoSung", "declaration.Nhap", "declaration.Rut"]

    def test_invalid_transition_from_rut_raises(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-7")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        declare.set_state(conn, did, "Rut", user_id, reason="rút")
        with pytest.raises(ValueError):
            declare.set_state(conn, did, "Nhap", user_id)

    def test_period_closed_after_declaration_blocks_state_change(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-8")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        period.close_submissions(conn, pid, user_id)
        with pytest.raises(ValueError):
            declare.set_state(conn, did, "ChoBoSung", user_id, reason="quá hạn")


class TestEvidence:
    def test_invalid_kind_raises(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-9")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        with pytest.raises(ValueError):
            declare.add_evidence(conn, did, kind="pdf", actor_id=user_id)

    def test_add_evidence_writes_audit(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-DEC-10")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        eid = declare.add_evidence(conn, did, kind="link", url="https://doi.org/10.1/x", actor_id=user_id)
        row = q(conn, "SELECT kind, url FROM evidence WHERE id=%s", eid)[0]
        assert row["kind"] == "link" and row["url"] == "https://doi.org/10.1/x"
        actions = q(conn, "SELECT action FROM audit_log WHERE entity='declaration' AND entity_id=%s ORDER BY id", did)
        assert actions[-1]["action"] == "declaration.evidence"


class TestListDeclarations:
    def test_list_includes_work_title_unit_code_and_evidence_count(self, conn, user_id):
        unit_id = mk_unit(conn, "khoa-a", "Khoa A")
        work_id = mk_work(conn, "Bài báo liệt kê")
        pid = open_basic(conn, user_id, code="K2026-DEC-11")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        declare.add_evidence(conn, did, kind="note", note="đã kiểm tra", actor_id=user_id)
        declare.add_evidence(conn, did, kind="link", url="https://example.org", actor_id=user_id)

        rows = declare.list_declarations(conn, pid)
        assert len(rows) == 1
        row = rows[0]
        assert row["work_title"] == "Bài báo liệt kê"
        assert row["unit_code"] == "khoa-a"
        assert row["evidence_count"] == 2
        assert row["last_event_at"] is not None

    def test_list_filters_by_unit(self, conn, user_id):
        unit_a = mk_unit(conn, "khoa-x", "Khoa X")
        unit_b = mk_unit(conn, "khoa-y", "Khoa Y")
        work_a = mk_work(conn, "Bài A")
        work_b = mk_work(conn, "Bài B")
        pid = open_basic(conn, user_id, code="K2026-DEC-12")
        declare.add_declaration(conn, period_id=pid, work_id=work_a, unit_id=unit_a, actor_id=user_id)
        declare.add_declaration(conn, period_id=pid, work_id=work_b, unit_id=unit_b, actor_id=user_id)

        rows_a = declare.list_declarations(conn, pid, unit_id=unit_a)
        assert [r["unit_id"] for r in rows_a] == [unit_a]
        assert len(declare.list_declarations(conn, pid)) == 2
