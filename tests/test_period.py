# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime, timedelta, timezone

import pytest

from cris import period, rules


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk_unit(conn, code="khoa-cntt", name="Khoa Công nghệ thông tin"):
    return q(conn, "INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", code, name)[0]["id"]


def due_soon(days=30):
    return datetime.now(timezone.utc) + timedelta(days=days)


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


def open_basic(conn, user_id, code="K2026-01"):
    return period.open_period(
        conn, code=code, name="Kỳ báo cáo 2026 đợt 1",
        scope={"doc_types": ["bai_bao"], "year_from": 2025, "year_to": 2026},
        criteria="Bài báo khoa học năm 2025-2026", due_at=due_soon(), actor_id=user_id)


class TestOpenPeriod:
    def test_open_period_snapshots_active_rule_set_and_is_immutable_after_change(self, conn, user_id):
        old_id = q(conn, "SELECT id FROM rule_set WHERE kind='year_rule' AND active")[0]["id"]
        pid = open_basic(conn, user_id)
        row = q(conn, "SELECT rule_set_id, state FROM period WHERE id=%s", pid)[0]
        assert row["rule_set_id"] == old_id
        assert row["state"] == "DangMo"

        # Kích hoạt một phiên bản mới của bộ quy tắc "year_rule" — BR-05 yêu cầu
        # kỳ đã mở KHÔNG được đổi theo.
        with conn.cursor() as cur:
            cur.execute("UPDATE rule_set SET active=false WHERE kind='year_rule'")
            cur.execute(
                "INSERT INTO rule_set(kind, version, body, active, created_by) "
                "VALUES ('year_rule', 2, '{}', true, %s)", (user_id,))
        conn.commit()
        new_id = q(conn, "SELECT id FROM rule_set WHERE kind='year_rule' AND active")[0]["id"]
        assert new_id != old_id

        row_after = q(conn, "SELECT rule_set_id FROM period WHERE id=%s", pid)[0]
        assert row_after["rule_set_id"] == old_id

    def test_open_period_with_explicit_rule_set_id_overrides_active_one(self, conn, user_id):
        other = q(conn, "SELECT id FROM rule_set WHERE kind='dedup' AND active")[0]["id"]
        pid = period.open_period(
            conn, code="K2026-02", name="Kỳ khác", scope={}, criteria=None,
            due_at=due_soon(), actor_id=user_id, rule_set_id=other)
        row = q(conn, "SELECT rule_set_id FROM period WHERE id=%s", pid)[0]
        assert row["rule_set_id"] == other

    def test_duplicate_code_raises_value_error(self, conn, user_id):
        open_basic(conn, user_id, code="K2026-DUP")
        with pytest.raises(ValueError):
            open_basic(conn, user_id, code="K2026-DUP")


class TestTransitions:
    def test_valid_transition_close_submissions(self, conn, user_id):
        pid = open_basic(conn, user_id)
        period.close_submissions(conn, pid, user_id)
        row = q(conn, "SELECT state FROM period WHERE id=%s", pid)[0]
        assert row["state"] == "DaDongNop"

    def test_invalid_transition_rejected(self, conn, user_id):
        pid = open_basic(conn, user_id)
        period.close_submissions(conn, pid, user_id)
        # Kỳ đã đóng nộp (DaDongNop): không có đường quay lại DangMo trong lát cắt
        # này, và cũng không được huỷ nữa — mọi chuyển trạng thái tiếp theo phải
        # bị từ chối.
        with pytest.raises(ValueError):
            period.close_submissions(conn, pid, user_id)
        with pytest.raises(ValueError):
            period.cancel_period(conn, pid, user_id)
        row = q(conn, "SELECT state FROM period WHERE id=%s", pid)[0]
        assert row["state"] == "DaDongNop"

    def test_cancel_period_from_chuan_bi_or_dang_mo(self, conn, user_id):
        pid = open_basic(conn, user_id, code="K2026-CANCEL")
        period.cancel_period(conn, pid, user_id)
        row = q(conn, "SELECT state FROM period WHERE id=%s", pid)[0]
        assert row["state"] == "Huy"

    def test_each_transition_writes_one_audit_log_row(self, conn, user_id):
        pid = open_basic(conn, user_id, code="K2026-AUDIT")
        after_open = q(conn, "SELECT count(*) AS n FROM audit_log WHERE entity='period' AND entity_id=%s", pid)[0]["n"]
        assert after_open == 1
        period.close_submissions(conn, pid, user_id)
        after_close = q(conn, "SELECT count(*) AS n FROM audit_log WHERE entity='period' AND entity_id=%s", pid)[0]["n"]
        assert after_close == 2
        rows = q(conn, "SELECT action, actor_id FROM audit_log WHERE entity='period' AND entity_id=%s ORDER BY id", pid)
        assert [r["action"] for r in rows] == ["period.open", "period.close_submissions"]
        assert all(r["actor_id"] == user_id for r in rows)

        # Chuyển trạng thái bị từ chối không được sinh thêm dòng audit_log nào.
        with pytest.raises(ValueError):
            period.close_submissions(conn, pid, user_id)
        after_reject = q(conn, "SELECT count(*) AS n FROM audit_log WHERE entity='period' AND entity_id=%s", pid)[0]["n"]
        assert after_reject == 2


class TestProgress:
    def test_period_progress_on_empty_period_returns_zero_for_every_unit(self, conn, user_id):
        mk_unit(conn, "khoa-a", "Khoa A")
        mk_unit(conn, "khoa-b", "Khoa B")
        pid = open_basic(conn, user_id, code="K2026-PROGRESS")

        progress = period.period_progress(conn, pid)

        assert progress["period_id"] == pid
        assert progress["state"] == "DangMo"
        assert progress["days_remaining"] is not None and progress["days_remaining"] >= 0
        assert len(progress["units"]) == 2
        for u in progress["units"]:
            assert u["total"] == 0
            assert u["counts"] == {s: 0 for s in period.DECLARATION_STATES}

    def test_period_progress_unknown_period_raises(self, conn):
        with pytest.raises(ValueError):
            period.period_progress(conn, 999999)


class TestListPeriods:
    def test_list_periods_without_unit_returns_all(self, conn, user_id):
        open_basic(conn, user_id, code="K2026-L1")
        open_basic(conn, user_id, code="K2026-L2")
        rows = period.list_periods(conn)
        assert {r["code"] for r in rows} == {"K2026-L1", "K2026-L2"}

    def test_list_periods_filtered_by_unit_only_includes_units_with_declarations(self, conn, user_id):
        unit_a = mk_unit(conn, "khoa-x", "Khoa X")
        unit_b = mk_unit(conn, "khoa-y", "Khoa Y")
        pid_with = open_basic(conn, user_id, code="K2026-WITH")
        open_basic(conn, user_id, code="K2026-WITHOUT")

        w = q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t') RETURNING id")[0]["id"]
        sr = q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
                     "VALUES (%s,'manual','k1','bai_bao','h','{}') RETURNING id", w)[0]["id"]
        work_id = q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) "
                          "VALUES ('bai_bao',%s,'t','t','DaChuanHoa') RETURNING id", sr)[0]["id"]
        q(conn, "INSERT INTO declaration(period_id, work_id, unit_id, created_by) VALUES (%s,%s,%s,%s)",
          pid_with, work_id, unit_a, user_id)
        conn.commit()

        rows = period.list_periods(conn, unit_id=unit_a)
        assert [r["code"] for r in rows] == ["K2026-WITH"]
        assert period.list_periods(conn, unit_id=unit_b) == []
