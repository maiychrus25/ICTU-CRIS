# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Nghiệp vụ chỉnh tay có xuất xứ (`cris.edit`, lát cắt H2) trên PostgreSQL
thật (fixture `conn`), theo khuôn `test_declare.py`/`test_normalize.py`."""
import pytest
from test_api_core import mk_work, q
from test_normalize import BAI_BAO, load

from cris import edit, normalize, rules


def test_set_field_title_updates_title_norm_provenance_and_audit(conn, user_id):
    wid = mk_work(conn, "Xay dung website ban hang")
    out = edit.set_field(conn, wid, "title", "Xây dựng website bán hàng mới", user_id, "sửa lỗi chính tả")
    assert out == {"field": "title", "old": "Xay dung website ban hang", "new": "Xây dựng website bán hàng mới"}

    w = q(conn, "SELECT title, title_norm FROM work WHERE id=%s", wid)[0]
    assert w["title"] == "Xây dựng website bán hàng mới"
    assert w["title_norm"] == rules.norm_title("Xây dựng website bán hàng mới")

    prov = q(conn, "SELECT * FROM field_provenance WHERE work_id=%s AND field='title'", wid)[0]
    assert prov["set_kind"] == "manual" and prov["set_by"] == user_id
    assert prov["raw_value"] == "Xay dung website ban hang"
    assert prov["value"] == "Xây dựng website bán hàng mới"

    row = q(conn, "SELECT * FROM audit_log WHERE entity='work' AND entity_id=%s AND action='work.edit'", wid)[0]
    assert row["actor_id"] == user_id
    assert row["before"]["title"] == "Xay dung website ban hang"
    assert row["after"]["title"] == "Xây dựng website bán hàng mới" and row["after"]["reason"] == "sửa lỗi chính tả"


def test_set_field_rejects_field_outside_editable(conn, user_id):
    wid = mk_work(conn, "Một công trình")
    with pytest.raises(ValueError):
        edit.set_field(conn, wid, "authors", "Ai đó", user_id, "vì lý do")


def test_set_field_requires_reason(conn, user_id):
    wid = mk_work(conn, "Một công trình")
    with pytest.raises(ValueError):
        edit.set_field(conn, wid, "journal", "Tạp chí mới", user_id, "   ")


def test_set_field_year_issue_invalid_raises(conn, user_id):
    wid = mk_work(conn, "Một công trình")
    with pytest.raises(ValueError):
        edit.set_field(conn, wid, "year_issue", "không phải năm", user_id, "sửa năm")


def test_set_field_year_issue_empty_becomes_null(conn, user_id):
    wid = mk_work(conn, "Một công trình")
    q(conn, "UPDATE work SET year_issue=2020 WHERE id=%s", wid)
    conn.commit()
    out = edit.set_field(conn, wid, "year_issue", "", user_id, "năm sai, xoá đi")
    assert out == {"field": "year_issue", "old": 2020, "new": None}
    assert q(conn, "SELECT year_issue FROM work WHERE id=%s", wid)[0]["year_issue"] is None


def test_set_field_rejects_merged_work(conn, user_id):
    survivor = mk_work(conn, "Bản còn lại")
    wid = mk_work(conn, "Bản đã gộp")
    q(conn, "UPDATE work SET merged_into_id=%s, state='DaGop' WHERE id=%s", survivor, wid)
    conn.commit()
    with pytest.raises(ValueError):
        edit.set_field(conn, wid, "journal", "Tạp chí mới", user_id, "vì lý do")


def test_normalize_rerun_does_not_overwrite_manual_edit(conn, user_id):
    rules.seed_rules(conn, None)
    load(conn, "bai_bao", BAI_BAO, "https://r/bai-bao/edit/")
    normalize.normalize_pending(conn)
    work_id = q(conn, "SELECT id FROM work")[0]["id"]

    edit.set_field(conn, work_id, "journal", "Sửa tay", user_id, "tạp chí nguồn sai")

    import json
    changed = json.loads(json.dumps(BAI_BAO))
    changed["archive"]["journal"] = "Tạp chí mới"
    changed["archive"]["year"] = "2030"
    load(conn, "bai_bao", changed, "https://r/bai-bao/edit/")
    normalize.normalize_pending(conn)

    w = q(conn, "SELECT journal, year_issue FROM work WHERE id=%s", work_id)[0]
    assert w["journal"] == "Sửa tay"          # trường đã chỉnh tay không bị ghi đè
    assert w["year_issue"] == 2030            # trường chưa chỉnh tay vẫn cập nhật theo nguồn mới
    kinds = [r["set_kind"] for r in q(
        conn, "SELECT set_kind FROM field_provenance WHERE work_id=%s AND field='journal' ORDER BY set_at", work_id)]
    assert kinds == ["normalize", "manual"]
