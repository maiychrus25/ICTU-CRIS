# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Cảnh báo bất thường dữ liệu (K2): `cris.anomaly.scan`/`dismiss` trên
PostgreSQL thật (fixture `conn`, theo khuôn `test_quality.py`/`test_dedup.py`)
và API `/api/quality/anomalies` (theo khuôn `test_api_ext.py`)."""
import json
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q

from cris import anomaly
from cris.api.app import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "none")
    return TestClient(create_app(static_dir="/nonexistent"))


def _orcid_unique_constraint(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT tc.constraint_name FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu "
            "  ON kcu.constraint_name = tc.constraint_name AND kcu.table_name = tc.table_name "
            "WHERE tc.table_name='person' AND tc.constraint_type='UNIQUE' AND kcu.column_name='orcid'"
        )
        return cur.fetchone()["constraint_name"]


# ---------- từng loại bất thường ----------

def test_scan_detects_scopus_no_doi(conn):
    wid = mk_work(conn, "Bài Scopus không DOI", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    r = anomaly.scan(conn)
    assert r["scopus_no_doi"] == {"found": 1, "new": 1, "resolved": 0}
    row = q(conn, "SELECT * FROM quality_flag WHERE kind='scopus_no_doi'")[0]
    assert row["work_id"] == wid and row["person_id"] is None and row["severity"] == "cao" and row["state"] == "open"


def test_scan_detects_year_out_of_range(conn):
    wid = mk_work(conn, "Công trình năm lạ")
    q(conn, "UPDATE work SET year_issue=1899 WHERE id=%s", wid)
    conn.commit()
    r = anomaly.scan(conn)
    assert r["year_out_of_range"]["found"] == 1
    row = q(conn, "SELECT * FROM quality_flag WHERE kind='year_out_of_range'")[0]
    assert row["work_id"] == wid and row["severity"] == "vua" and row["detail"]["year"] == 1899


def test_scan_detects_thesis_title_equals_article(conn):
    # `source_key` (mã nguồn giả trong mk_work) trùng tiêu đề thô nên phải khác nhau
    # ở hoa/thường để không đụng UNIQUE(source, source_key, version); title_norm
    # (hạ chữ) vẫn trùng — đúng thứ cột mà thesis_title_equals_article so khớp.
    article = mk_work(conn, "Nghiên cứu về X", doc_type="bai_bao", abstract="Tóm tắt.")
    thesis = mk_work(conn, "NGHIÊN CỨU VỀ X", doc_type="do_an")
    conn.commit()
    r = anomaly.scan(conn)
    assert r["thesis_title_equals_article"]["found"] == 1
    row = q(conn, "SELECT * FROM quality_flag WHERE kind='thesis_title_equals_article'")[0]
    assert row["work_id"] == thesis and row["detail"]["article_id"] == article and row["severity"] == "vua"


def test_scan_detects_doi_invalid(conn):
    wid = mk_work(conn, "DOI sai định dạng", doc_type="bai_bao")
    q(conn, "UPDATE work SET doi=%s WHERE id=%s", "khong-phai-doi", wid)
    conn.commit()
    r = anomaly.scan(conn)
    assert r["doi_invalid"]["found"] == 1
    row = q(conn, "SELECT * FROM quality_flag WHERE kind='doi_invalid'")[0]
    assert row["work_id"] == wid and row["severity"] == "vua"


def test_doi_valid_format_not_flagged(conn):
    wid = mk_work(conn, "DOI đúng định dạng", doc_type="bai_bao")
    q(conn, "UPDATE work SET doi=%s WHERE id=%s", "10.1234/abc.2026", wid)
    conn.commit()
    r = anomaly.scan(conn)
    assert r["doi_invalid"] == {"found": 0, "new": 0, "resolved": 0}


def test_scan_detects_missing_abstract_article(conn):
    wid = mk_work(conn, "Bài báo không tóm tắt", doc_type="bai_bao", abstract=None)
    conn.commit()
    r = anomaly.scan(conn)
    assert r["missing_abstract_article"]["found"] == 1
    row = q(conn, "SELECT * FROM quality_flag WHERE kind='missing_abstract_article'")[0]
    assert row["work_id"] == wid and row["severity"] == "thap"


def test_scan_detects_orcid_duplicate(conn):
    """`person.orcid` có UNIQUE — hai hồ sơ trùng ORCID bình thường bị DB chặn
    (xem CHANGELOG: 10/410 hồ sơ giảng viên bị từ chối lúc nhập vì lý do này).
    Nới ràng buộc trong test để dựng lại tình huống lịch sử/khi ràng buộc bị
    nới, rồi phục hồi ràng buộc trước khi test kết thúc."""
    cname = _orcid_unique_constraint(conn)
    with conn.cursor() as cur:
        cur.execute(f"ALTER TABLE person DROP CONSTRAINT {cname}")
        cur.execute("INSERT INTO person(kind, display_name, name_norm, orcid) "
                    "VALUES ('lecturer','A','a','0000-0001-0000-0001') RETURNING id")
        p1 = cur.fetchone()["id"]
        cur.execute("INSERT INTO person(kind, display_name, name_norm, orcid) "
                    "VALUES ('lecturer','B','b','0000-0001-0000-0001') RETURNING id")
        p2 = cur.fetchone()["id"]
    conn.commit()
    try:
        r = anomaly.scan(conn)
        assert r["orcid_duplicate"] == {"found": 2, "new": 2, "resolved": 0}
        rows = q(conn, "SELECT person_id, detail, severity FROM quality_flag "
                       "WHERE kind='orcid_duplicate' ORDER BY person_id")
        assert [row["person_id"] for row in rows] == sorted([p1, p2])
        assert rows[0]["detail"]["other_person_id"] == p2
        assert rows[0]["severity"] == "cao"
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM quality_flag WHERE kind='orcid_duplicate'")
            cur.execute("DELETE FROM person WHERE id IN (%s,%s)", (p1, p2))
            cur.execute(f"ALTER TABLE person ADD CONSTRAINT {cname} UNIQUE (orcid)")
        conn.commit()


# ---------- quét idempotent, sửa dữ liệu, dismiss ----------

def test_scan_is_idempotent(conn):
    wid = mk_work(conn, "Bài Scopus không DOI 2", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    r1 = anomaly.scan(conn)
    assert r1["scopus_no_doi"]["new"] == 1
    r2 = anomaly.scan(conn)
    assert r2["scopus_no_doi"] == {"found": 1, "new": 0, "resolved": 0}
    assert len(q(conn, "SELECT id FROM quality_flag WHERE kind='scopus_no_doi'")) == 1


def test_fixing_data_resolves_flag(conn):
    wid = mk_work(conn, "Bài Scopus sẽ được sửa", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    anomaly.scan(conn)
    q(conn, "UPDATE work SET doi=%s WHERE id=%s", "10.1234/fixed.2026", wid)
    conn.commit()
    r = anomaly.scan(conn)
    assert r["scopus_no_doi"] == {"found": 0, "new": 0, "resolved": 1}
    row = q(conn, "SELECT state FROM quality_flag WHERE kind='scopus_no_doi'")[0]
    assert row["state"] == "resolved"


def test_dismissed_flag_kept_on_rescan(conn, user_id):
    wid = mk_work(conn, "Bài Scopus bị bỏ qua", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    anomaly.scan(conn)
    flag_id = q(conn, "SELECT id FROM quality_flag WHERE kind='scopus_no_doi'")[0]["id"]
    anomaly.dismiss(conn, flag_id, user_id, "đã báo khoa, đang chờ DOI chính thức")
    r = anomaly.scan(conn)
    assert r["scopus_no_doi"] == {"found": 1, "new": 0, "resolved": 0}
    row = q(conn, "SELECT state, reason, dismissed_by FROM quality_flag WHERE id=%s", flag_id)[0]
    assert row["state"] == "dismissed" and row["dismissed_by"] == user_id and row["reason"]


def test_dismiss_requires_reason(conn, user_id):
    wid = mk_work(conn, "Bài Scopus cần bỏ qua nhưng thiếu lý do", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    anomaly.scan(conn)
    flag_id = q(conn, "SELECT id FROM quality_flag WHERE kind='scopus_no_doi'")[0]["id"]
    with pytest.raises(ValueError):
        anomaly.dismiss(conn, flag_id, user_id, "")
    with pytest.raises(ValueError):
        anomaly.dismiss(conn, flag_id, user_id, "   ")


def test_dismiss_unknown_flag_raises_lookup_error(conn, user_id):
    with pytest.raises(LookupError):
        anomaly.dismiss(conn, 999999, user_id, "lý do")


def test_dismiss_writes_audit_log(conn, user_id):
    wid = mk_work(conn, "Bài Scopus cho audit", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    anomaly.scan(conn)
    flag_id = q(conn, "SELECT id FROM quality_flag WHERE kind='scopus_no_doi'")[0]["id"]
    anomaly.dismiss(conn, flag_id, user_id, "kiểm tra thủ công rồi")
    rows = q(conn, "SELECT * FROM audit_log WHERE action='quality.dismiss' AND entity_id=%s", flag_id)
    assert len(rows) == 1
    assert rows[0]["entity"] == "quality_flag" and rows[0]["actor_id"] == user_id
    assert rows[0]["after"]["reason"] == "kiểm tra thủ công rồi"


# ---------- API ----------

def test_api_list_anomalies_filters_kind_and_severity(client, conn):
    w1 = mk_work(conn, "Bài Scopus API 1", doc_type="bai_bao", abstract="Tóm tắt đầy đủ.")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], w1)
    w2 = mk_work(conn, "Bài không tóm tắt API", doc_type="bai_bao", abstract=None)
    conn.commit()
    anomaly.scan(conn)

    all_items = client.get("/api/quality/anomalies").json()
    assert all_items["page"]["total"] == 2
    assert all_items["summary"]["scopus_no_doi"]["open"] == 1
    assert all_items["summary"]["missing_abstract_article"]["open"] == 1

    by_kind = client.get("/api/quality/anomalies", params={"kind": "scopus_no_doi"}).json()
    assert [i["work_id"] for i in by_kind["items"]] == [w1]
    assert by_kind["items"][0]["kind_label"] == "Ghi Scopus/ISI nhưng không có DOI"

    by_sev = client.get("/api/quality/anomalies", params={"severity": "thap"}).json()
    assert [i["work_id"] for i in by_sev["items"]] == [w2]


def test_api_dismiss_missing_reason_400_and_unknown_404(client, conn, user_id):
    wid = mk_work(conn, "Bài Scopus API dismiss", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    anomaly.scan(conn)
    flag_id = q(conn, "SELECT id FROM quality_flag WHERE kind='scopus_no_doi'")[0]["id"]

    r = client.post(f"/api/quality/anomalies/{flag_id}/dismiss", json={"reason": ""})
    assert r.status_code == 400

    r = client.post("/api/quality/anomalies/999999/dismiss", json={"reason": "lý do"})
    assert r.status_code == 404

    r = client.post(f"/api/quality/anomalies/{flag_id}/dismiss", json={"reason": "đã xử lý"})
    assert r.status_code == 200 and r.json() == {"ok": True, "id": flag_id, "state": "dismissed"}


def test_api_quality_metric_anomalies_open(client, conn, user_id):
    wid = mk_work(conn, "Bài Scopus cho metric", doc_type="bai_bao", abstract="Tóm tắt đầy đủ.")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    anomaly.scan(conn)
    metrics = {m["key"]: m for m in client.get("/api/quality").json()["metrics"]}
    assert metrics["anomalies_open"]["value"] == 1
    assert metrics["anomalies_open"]["queue_url"] == "/chat-luong-du-lieu/canh-bao"


def test_cli_quality_scan(conn):
    import os
    wid = mk_work(conn, "Bài Scopus qua CLI", doc_type="bai_bao")
    q(conn, "UPDATE work SET indexes=%s WHERE id=%s", ["Scopus"], wid)
    conn.commit()
    env = {**os.environ, "DATABASE_URL": os.environ.get("TEST_DATABASE_URL", "postgresql://cris:cris@localhost:5432/cris_test")}
    out = subprocess.run([sys.executable, "-m", "cris", "quality", "scan"], capture_output=True, text=True, env=env, check=True)
    assert "scopus_no_doi: found=1 new=1 resolved=0" in out.stdout


def test_cli_quality_report_unchanged(conn):
    """`cris quality` (không tham số) vẫn phải chạy như trước K2 (`action` mặc
    định 'report'), không bị lệnh `scan` mới thêm vào làm hỏng."""
    import os
    env = {**os.environ, "DATABASE_URL": os.environ.get("TEST_DATABASE_URL", "postgresql://cris:cris@localhost:5432/cris_test")}
    out = subprocess.run([sys.executable, "-m", "cris", "quality", "--json"], capture_output=True, text=True, env=env, check=True)
    assert json.loads(out.stdout)["works"] == 0
