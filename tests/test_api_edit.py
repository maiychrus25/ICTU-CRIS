# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""API chỉnh tay có xuất xứ (`PATCH /api/works/{id}/fields`) và tìm kiếm không
dấu trong `/api/works` (lát cắt H2) trên PostgreSQL thật (fixture `conn`),
theo khuôn `test_api_ext.py`/`test_api_declarations.py`."""
import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import edit, rules
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


def test_patch_field_updates_value_and_detail_shows_manual_source(client, conn, user_id):
    wid = mk_work(conn, "Xây dựng website bán hàng")
    r = client.patch(f"/api/works/{wid}/fields",
                      json={"field": "journal", "value": "Tạp chí Khoa học ICTU", "reason": "nguồn ghi sai tên tạp chí"})
    assert r.status_code == 200, r.text
    assert r.json() == {"field": "journal", "old": None, "new": "Tạp chí Khoa học ICTU"}

    d = client.get(f"/api/works/{wid}").json()
    assert d["has_manual"] is True
    row = next(f for f in d["fields"] if f["field"] == "journal")
    assert row["value"] == "Tạp chí Khoa học ICTU"
    assert row["raw"] is None
    assert row["source"].startswith("Chỉnh tay bởi Chuyên viên phòng, lúc")


def test_patch_field_outside_editable_is_400_with_list(client, conn, user_id):
    wid = mk_work(conn, "Một công trình")
    r = client.patch(f"/api/works/{wid}/fields", json={"field": "authors", "value": "Ai đó", "reason": "vì lý do"})
    assert r.status_code == 400
    for f in edit.EDITABLE:
        assert f in r.text


def test_patch_field_unknown_work_is_404(client, conn, user_id):
    r = client.patch("/api/works/999999/fields", json={"field": "journal", "value": "x", "reason": "vì lý do"})
    assert r.status_code == 404


def test_patch_field_empty_reason_is_409(client, conn, user_id):
    wid = mk_work(conn, "Một công trình")
    r = client.patch(f"/api/works/{wid}/fields", json={"field": "journal", "value": "Tạp chí mới", "reason": "  "})
    assert r.status_code == 409


def test_patch_field_invalid_year_is_409(client, conn, user_id):
    wid = mk_work(conn, "Một công trình")
    r = client.patch(f"/api/works/{wid}/fields",
                      json={"field": "year_issue", "value": "không phải năm", "reason": "sửa năm"})
    assert r.status_code == 409


def test_patch_field_merged_work_is_409(client, conn, user_id):
    survivor = mk_work(conn, "Bản còn lại")
    wid = mk_work(conn, "Bản đã gộp")
    q(conn, "UPDATE work SET merged_into_id=%s, state='DaGop' WHERE id=%s", survivor, wid)
    conn.commit()
    r = client.patch(f"/api/works/{wid}/fields", json={"field": "journal", "value": "Tạp chí mới", "reason": "vì lý do"})
    assert r.status_code == 409


def test_search_title_is_accent_insensitive(client, conn, user_id):
    # `mk_work` (test_api_core) không tự tính title_norm chuẩn hoá — cập nhật bằng
    # đúng hàm sản xuất (`rules.norm_title`) để mô phỏng bản ghi đã qua `cris.normalize`.
    wid = mk_work(conn, "Xây dựng website bán hàng")
    q(conn, "UPDATE work SET title_norm=%s WHERE id=%s", rules.norm_title("Xây dựng website bán hàng"), wid)
    conn.commit()
    r = client.get("/api/works", params={"q": "xay dung website"}).json()
    assert r["page"]["total"] == 1
    assert r["items"][0]["id"] == wid
