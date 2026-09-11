# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Nghiệp vụ kê khai công trình vào kỳ (`cris.declare`, lát cắt K, G3, nâng
cấp H1): mở kỳ qua `cris.period` (không sửa module đó), rồi kê khai/đổi trạng
thái/minh chứng qua `cris.declare` trên PostgreSQL thật (fixture `conn`)."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from cris import declare, period, rules


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def mk_actor(conn, roles, unit_id=None, email=None):
    """Tạo một `app_user` với vai trò/đơn vị cho các test kiểm quyền H1."""
    email = email or f"actor-{uuid.uuid4().hex[:10]}@ictu.test"
    return q(conn, "INSERT INTO app_user(email, display_name, roles, unit_id) VALUES (%s,%s,%s,%s) RETURNING id",
             email, "Người kiểm thử H1", roles, unit_id)[0]["id"]


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


# ---------- H1: duyệt hai cấp theo BA + phạm vi đơn vị (NFR-02) ----------

class TestTwoLevelReviewRoles:
    def test_full_round_trip_each_role_in_its_step(self, conn, user_id):
        unit_id = mk_unit(conn)
        officer = mk_actor(conn, ["faculty_officer"], unit_id)
        head = mk_actor(conn, ["faculty_head"], unit_id)
        rd = mk_actor(conn, ["rd_officer"])
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-1")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=officer,
                                      actor_roles=["faculty_officer"], actor_unit_id=unit_id)

        declare.set_state(conn, did, "ChoKhoaDuyet", officer, actor_roles=["faculty_officer"], actor_unit_id=unit_id)
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "ChoKhoaDuyet"

        declare.set_state(conn, did, "KhoaDaDuyet", head, actor_roles=["faculty_head"], actor_unit_id=unit_id)
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "KhoaDaDuyet"

        declare.set_state(conn, did, "ChoPhongKiemTra", head, actor_roles=["faculty_head"], actor_unit_id=unit_id)
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "ChoPhongKiemTra"

        declare.set_state(conn, did, "DatYeuCau", rd, actor_roles=["rd_officer"])
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "DatYeuCau"

        events = q(conn, "SELECT to_state FROM declaration_event WHERE declaration_id=%s ORDER BY id", did)
        assert [e["to_state"] for e in events] == [
            "Nhap", "ChoKhoaDuyet", "KhoaDaDuyet", "ChoPhongKiemTra", "DatYeuCau"]

    def test_faculty_officer_cannot_approve_at_khoa_level(self, conn, user_id):
        unit_id = mk_unit(conn)
        officer = mk_actor(conn, ["faculty_officer"], unit_id)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-2")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=officer)
        declare.set_state(conn, did, "ChoKhoaDuyet", officer)
        with pytest.raises(PermissionError):
            declare.set_state(conn, did, "KhoaDaDuyet", officer, actor_roles=["faculty_officer"],
                              actor_unit_id=unit_id)

    def test_faculty_head_other_unit_is_permission_error(self, conn, user_id):
        unit_a = mk_unit(conn, "khoa-a1", "Khoa A1")
        unit_b = mk_unit(conn, "khoa-b1", "Khoa B1")
        officer = mk_actor(conn, ["faculty_officer"], unit_a)
        head_b = mk_actor(conn, ["faculty_head"], unit_b)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-3")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_a, actor_id=officer)
        declare.set_state(conn, did, "ChoKhoaDuyet", officer)
        with pytest.raises(PermissionError):
            declare.set_state(conn, did, "KhoaDaDuyet", head_b, actor_roles=["faculty_head"], actor_unit_id=unit_b)

    def test_rd_officer_acts_school_wide_regardless_of_unit(self, conn, user_id):
        unit_id = mk_unit(conn, "khoa-c1", "Khoa C1")
        rd = mk_actor(conn, ["rd_officer"])
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-4")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=rd,
                                      actor_roles=["rd_officer"], actor_unit_id=None)
        declare.set_state(conn, did, "ChoKhoaDuyet", rd, actor_roles=["rd_officer"])
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "ChoKhoaDuyet"

    def test_khoa_returns_to_nhap_requires_reason(self, conn, user_id):
        unit_id = mk_unit(conn)
        head = mk_actor(conn, ["faculty_head"], unit_id)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-5")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        declare.set_state(conn, did, "ChoKhoaDuyet", user_id)
        with pytest.raises(ValueError):
            declare.set_state(conn, did, "Nhap", head, actor_roles=["faculty_head"], actor_unit_id=unit_id)
        declare.set_state(conn, did, "Nhap", head, reason="thiếu minh chứng",
                          actor_roles=["faculty_head"], actor_unit_id=unit_id)
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "Nhap"

    def test_phong_returns_to_nhap_requires_reason_and_role(self, conn, user_id):
        unit_id = mk_unit(conn)
        head = mk_actor(conn, ["faculty_head"], unit_id)
        rd = mk_actor(conn, ["rd_officer"])
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-6")
        did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)
        declare.set_state(conn, did, "ChoKhoaDuyet", user_id)
        declare.set_state(conn, did, "KhoaDaDuyet", head, actor_roles=["faculty_head"], actor_unit_id=unit_id)
        declare.set_state(conn, did, "ChoPhongKiemTra", head, actor_roles=["faculty_head"], actor_unit_id=unit_id)
        with pytest.raises(PermissionError):
            declare.set_state(conn, did, "Nhap", head, reason="thiếu", actor_roles=["faculty_head"],
                              actor_unit_id=unit_id)
        declare.set_state(conn, did, "Nhap", rd, reason="số liệu sai", actor_roles=["rd_officer"])
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did)[0]["state"] == "Nhap"


class TestFinalizePeriod:
    def test_finalize_requires_period_da_dong_nop(self, conn, user_id):
        pid = open_basic(conn, user_id, code="K2026-H1-7")
        with pytest.raises(ValueError):
            declare.finalize_period(conn, pid, user_id)

    def test_finalize_moves_dat_yeu_cau_to_da_chot_and_lists_skipped(self, conn, user_id):
        unit_id = mk_unit(conn)
        work_ready = mk_work(conn, "Bài đạt yêu cầu")
        work_pending = mk_work(conn, "Bài chưa xong")
        pid = open_basic(conn, user_id, code="K2026-H1-8")
        did_ready = declare.add_declaration(conn, period_id=pid, work_id=work_ready, unit_id=unit_id,
                                            actor_id=user_id)
        did_pending = declare.add_declaration(conn, period_id=pid, work_id=work_pending, unit_id=unit_id,
                                              actor_id=user_id)
        for to_state in ("ChoKhoaDuyet", "KhoaDaDuyet", "ChoPhongKiemTra", "DatYeuCau"):
            declare.set_state(conn, did_ready, to_state, user_id)
        declare.set_state(conn, did_pending, "ChoKhoaDuyet", user_id)

        period.close_submissions(conn, pid, user_id)
        result = declare.finalize_period(conn, pid, user_id)

        assert result["finalized"] == 1
        assert result["skipped"] == [{"id": did_pending, "state": "ChoKhoaDuyet"}]
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did_ready)[0]["state"] == "DaChot"
        assert q(conn, "SELECT state FROM declaration WHERE id=%s", did_pending)[0]["state"] == "ChoKhoaDuyet"
        actions = q(conn, "SELECT action FROM audit_log WHERE entity='declaration' AND entity_id=%s ORDER BY id",
                   did_ready)
        assert actions[-1]["action"] == "declaration.DaChot"
        period_actions = q(conn, "SELECT action FROM audit_log WHERE entity='period' AND entity_id=%s", pid)
        assert "period.finalize" in [a["action"] for a in period_actions]


class TestUnitScopedListing:
    def test_list_scoped_to_actor_unit_ignores_requested_unit(self, conn, user_id):
        unit_a = mk_unit(conn, "khoa-d1", "Khoa D1")
        unit_b = mk_unit(conn, "khoa-e1", "Khoa E1")
        work_a = mk_work(conn, "Bài khoa D1")
        work_b = mk_work(conn, "Bài khoa E1")
        pid = open_basic(conn, user_id, code="K2026-H1-9")
        declare.add_declaration(conn, period_id=pid, work_id=work_a, unit_id=unit_a, actor_id=user_id)
        declare.add_declaration(conn, period_id=pid, work_id=work_b, unit_id=unit_b, actor_id=user_id)

        rows = declare.list_declarations(conn, pid, unit_id=unit_b, actor_roles=["faculty_officer"],
                                         actor_unit_id=unit_a)
        assert [r["unit_id"] for r in rows] == [unit_a]

    def test_rd_officer_sees_every_unit(self, conn, user_id):
        unit_a = mk_unit(conn, "khoa-f1", "Khoa F1")
        unit_b = mk_unit(conn, "khoa-g1", "Khoa G1")
        work_a = mk_work(conn, "Bài F1")
        work_b = mk_work(conn, "Bài G1")
        pid = open_basic(conn, user_id, code="K2026-H1-10")
        declare.add_declaration(conn, period_id=pid, work_id=work_a, unit_id=unit_a, actor_id=user_id)
        declare.add_declaration(conn, period_id=pid, work_id=work_b, unit_id=unit_b, actor_id=user_id)

        rows = declare.list_declarations(conn, pid, actor_roles=["rd_officer"], actor_unit_id=None)
        assert len(rows) == 2


class TestAddDeclarationRoles:
    def test_faculty_head_cannot_add_declaration(self, conn, user_id):
        unit_id = mk_unit(conn)
        head = mk_actor(conn, ["faculty_head"], unit_id)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-11")
        with pytest.raises(PermissionError):
            declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=head,
                                    actor_roles=["faculty_head"], actor_unit_id=unit_id)

    def test_faculty_officer_cannot_add_for_other_unit(self, conn, user_id):
        unit_a = mk_unit(conn, "khoa-h1", "Khoa H1")
        unit_b = mk_unit(conn, "khoa-i1", "Khoa I1")
        officer = mk_actor(conn, ["faculty_officer"], unit_a)
        work_id = mk_work(conn)
        pid = open_basic(conn, user_id, code="K2026-H1-12")
        with pytest.raises(PermissionError):
            declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_b, actor_id=officer,
                                    actor_roles=["faculty_officer"], actor_unit_id=unit_a)


class TestPeriodProgressAllStates:
    def test_progress_counts_all_eight_states(self, conn, user_id):
        unit_id = mk_unit(conn)
        titles = ["Bài 1", "Bài 2", "Bài 3", "Bài 4", "Bài 5", "Bài 6", "Bài 7", "Bài 8"]
        works = [mk_work(conn, t) for t in titles]
        pid = open_basic(conn, user_id, code="K2026-H1-13")
        dids = [declare.add_declaration(conn, period_id=pid, work_id=w, unit_id=unit_id, actor_id=user_id)
               for w in works]
        # dids[0] ở lại Nhap
        declare.set_state(conn, dids[1], "ChoBoSung", user_id, reason="thiếu")
        declare.set_state(conn, dids[2], "ChoKhoaDuyet", user_id)
        declare.set_state(conn, dids[3], "ChoKhoaDuyet", user_id)
        declare.set_state(conn, dids[3], "KhoaDaDuyet", user_id)
        declare.set_state(conn, dids[4], "ChoKhoaDuyet", user_id)
        declare.set_state(conn, dids[4], "KhoaDaDuyet", user_id)
        declare.set_state(conn, dids[4], "ChoPhongKiemTra", user_id)
        declare.set_state(conn, dids[5], "ChoKhoaDuyet", user_id)
        declare.set_state(conn, dids[5], "KhoaDaDuyet", user_id)
        declare.set_state(conn, dids[5], "ChoPhongKiemTra", user_id)
        declare.set_state(conn, dids[6], "Rut", user_id, reason="trùng")
        # dids[7]: đưa lên DatYeuCau rồi chốt kỳ — finalize_period chốt MỌI hồ sơ
        # đang DatYeuCau, nên đưa dids[5] lên DatYeuCau sau khi đã chốt để hồ sơ
        # đó còn lại đúng ở DatYeuCau (không bị chốt theo).
        declare.set_state(conn, dids[7], "ChoKhoaDuyet", user_id)
        declare.set_state(conn, dids[7], "KhoaDaDuyet", user_id)
        declare.set_state(conn, dids[7], "ChoPhongKiemTra", user_id)
        declare.set_state(conn, dids[7], "DatYeuCau", user_id)
        period.close_submissions(conn, pid, user_id)
        declare.finalize_period(conn, pid, user_id)
        declare.set_state(conn, dids[5], "DatYeuCau", user_id)

        progress = period.period_progress(conn, pid)
        counts = next(u["counts"] for u in progress["units"] if u["unit_id"] == unit_id)
        assert counts == {
            "Nhap": 1, "ChoBoSung": 1, "ChoKhoaDuyet": 1, "KhoaDaDuyet": 1,
            "ChoPhongKiemTra": 1, "DatYeuCau": 1, "DaChot": 1, "Rut": 1,
        }
        assert sum(counts.values()) == 8


class TestUserCreateCli:
    def test_cli_user_create_and_set_unit(self, conn, user_id, capsys):
        # cli.main() mở một kết nối DB riêng (DATABASE_URL) — phải commit trước
        # khi gọi CLI để nó thấy được các bản ghi vừa tạo qua fixture `conn`.
        from cris import cli
        unit_id = mk_unit(conn, "khoa-cli1", "Khoa CLI 1")
        conn.commit()
        cli.main(["user", "create", "--email", "khoa.cli@ictu.test", "--name", "Chuyên viên CLI",
                 "--roles", "faculty_officer,lecturer", "--unit", "khoa-cli1"])
        row = q(conn, "SELECT roles, unit_id, active FROM app_user WHERE email=%s", "khoa.cli@ictu.test")[0]
        assert set(row["roles"]) == {"faculty_officer", "lecturer"} and row["unit_id"] == unit_id

        other_unit = mk_unit(conn, "khoa-cli2", "Khoa CLI 2")
        conn.commit()
        cli.main(["user", "set-unit", "--email", "khoa.cli@ictu.test", "--unit", "khoa-cli2"])
        row2 = q(conn, "SELECT unit_id FROM app_user WHERE email=%s", "khoa.cli@ictu.test")[0]
        assert row2["unit_id"] == other_unit
