# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Minh chứng dạng tệp thật (lát cắt I2): nhận diện loại qua chữ ký byte
(`cris.declare.sniff_content_type`), lưu tệp vào `CRIS_DATA_DIR` (ở đây trỏ
vào `tmp_path` qua `monkeypatch`), kiểm kích thước/loại, và tải về có kiểm
phạm vi đơn vị (NFR-02) — theo khuôn `test_api_declarations.py`."""
import hashlib
import io
import zipfile
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_api_core import mk_work, q
from test_api_declarations import as_user, mk_actor, mk_unit, open_period

from cris import declare, rules
from cris import period as period_mod
from cris.ai.provider import clear_provider_cache
from cris.api.app import create_app

PDF_BYTES = b"%PDF-1.4\n" + b"0" * 64
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 64
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"0" * 64
EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00" + b"0" * 64


def docx_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<w:document/>")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CRIS_AI_PROVIDER", "fake")
    clear_provider_cache()
    return TestClient(create_app(static_dir="/nonexistent"))


@pytest.fixture(autouse=True)
def data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("CRIS_DATA_DIR", str(tmp_path))
    return tmp_path


def mk_declaration(client, conn, user_id, code, unit_id=None, actor_headers=None):
    unit_id = unit_id or mk_unit(conn, f"khoa-{code.lower()}", f"Khoa {code}")
    work_id = mk_work(conn, f"Bài minh chứng {code}", doc_type="bai_bao")
    pid = open_period(client, code)
    r = client.post(f"/api/periods/{pid}/declarations", json={"work_id": work_id, "unit_id": unit_id},
                    headers=actor_headers or {})
    assert r.status_code == 201, r.text
    return r.json()["id"], unit_id


# ---------- sniff_content_type ----------

def test_sniff_recognises_pdf_png_jpeg_docx_and_rejects_unknown():
    assert declare.sniff_content_type(PDF_BYTES) == "application/pdf"
    assert declare.sniff_content_type(PNG_BYTES) == "image/png"
    assert declare.sniff_content_type(JPEG_BYTES) == "image/jpeg"
    assert declare.sniff_content_type(docx_bytes()) == \
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert declare.sniff_content_type(EXE_BYTES) is None
    assert declare.sniff_content_type(b"plain text, not a real file") is None


# ---------- add_evidence_file (tầng nghiệp vụ) ----------

def test_add_evidence_file_writes_to_disk_hash_and_db(conn, user_id, data_dir):
    unit_id = mk_unit(conn, "khoa-tep-1", "Khoa Tệp 1")
    work_id = mk_work(conn, "Bài tệp 1")
    pid = period_mod.open_period(conn, code="K2026-EV-1", name="Kỳ minh chứng 1",
                                  scope={"doc_types": ["bai_bao"]}, criteria=None,
                                  due_at=datetime.now(UTC) + timedelta(days=30), actor_id=user_id)
    did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_id, actor_id=user_id)

    eid = declare.add_evidence_file(conn, did, data=PDF_BYTES, original_name="bao-cao.pdf", actor_id=user_id)

    sha256 = hashlib.sha256(PDF_BYTES).hexdigest()
    row = q(conn, "SELECT * FROM evidence WHERE id=%s", eid)[0]
    assert row["kind"] == "file"
    assert row["sha256"] == sha256
    assert row["size_bytes"] == len(PDF_BYTES)
    assert row["content_type"] == "application/pdf"
    assert row["file_name"] == "bao-cao.pdf"

    stored_path = data_dir / "evidence" / str(did) / f"{sha256[:16]}.pdf"
    assert row["storage_path"] == str(stored_path)
    assert stored_path.is_file()
    assert stored_path.read_bytes() == PDF_BYTES

    actions = q(conn, "SELECT action FROM audit_log WHERE entity='declaration' AND entity_id=%s ORDER BY id", did)
    assert actions[-1]["action"] == "declaration.evidence"


def test_add_evidence_file_missing_declaration_raises(conn, user_id, data_dir):
    with pytest.raises(ValueError):
        declare.add_evidence_file(conn, 999999, data=PDF_BYTES, original_name="x.pdf", actor_id=user_id)


def test_get_evidence_unit_scope_permission_error(conn, user_id, data_dir):
    unit_a = mk_unit(conn, "khoa-tep-2a", "Khoa Tệp 2A")
    unit_b = mk_unit(conn, "khoa-tep-2b", "Khoa Tệp 2B")
    work_id = mk_work(conn, "Bài tệp 2")
    pid = period_mod.open_period(conn, code="K2026-EV-2", name="Kỳ minh chứng 2",
                                  scope={"doc_types": ["bai_bao"]}, criteria=None,
                                  due_at=datetime.now(UTC) + timedelta(days=30), actor_id=user_id)
    did = declare.add_declaration(conn, period_id=pid, work_id=work_id, unit_id=unit_a, actor_id=user_id)
    eid = declare.add_evidence_file(conn, did, data=PDF_BYTES, original_name="a.pdf", actor_id=user_id)

    with pytest.raises(PermissionError):
        declare.get_evidence(conn, eid, actor_roles=["faculty_officer"], actor_unit_id=unit_b)

    row = declare.get_evidence(conn, eid, actor_roles=["faculty_officer"], actor_unit_id=unit_a)
    assert row["id"] == eid
    assert declare.get_evidence(conn, 999999) is None


# ---------- API ----------

def test_api_upload_pdf_returns_201_with_hash_and_size(client, conn, user_id):
    did, _ = mk_declaration(client, conn, user_id, "K2026-EVAPI-1")
    r = client.post(f"/api/declarations/{did}/evidence/file",
                    files={"file": ("bao-cao.pdf", PDF_BYTES, "application/pdf")})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["content_type"] == "application/pdf"
    assert body["size_bytes"] == len(PDF_BYTES)
    assert body["sha256"] == hashlib.sha256(PDF_BYTES).hexdigest()

    detail = client.get(f"/api/declarations/{did}").json()
    assert detail["evidence"][0]["sha256"] == body["sha256"]
    assert detail["evidence"][0]["content_type"] == "application/pdf"


def test_api_upload_oversized_file_is_413(client, conn, user_id):
    did, _ = mk_declaration(client, conn, user_id, "K2026-EVAPI-2")
    too_big = b"%PDF-1.4\n" + b"0" * (declare.EVIDENCE_MAX_BYTES + 1)
    r = client.post(f"/api/declarations/{did}/evidence/file",
                    files={"file": ("lon.pdf", too_big, "application/pdf")})
    assert r.status_code == 413, r.text


def test_api_upload_exe_renamed_pdf_is_415(client, conn, user_id):
    did, _ = mk_declaration(client, conn, user_id, "K2026-EVAPI-3")
    r = client.post(f"/api/declarations/{did}/evidence/file",
                    files={"file": ("gia-mao.pdf", EXE_BYTES, "application/pdf")})
    assert r.status_code == 415, r.text


def test_api_upload_to_unknown_declaration_is_404(client, conn, user_id):
    r = client.post("/api/declarations/999999/evidence/file",
                    files={"file": ("a.pdf", PDF_BYTES, "application/pdf")})
    assert r.status_code == 404


def test_api_download_returns_matching_content_and_disposition_header(client, conn, user_id):
    did, _ = mk_declaration(client, conn, user_id, "K2026-EVAPI-4")
    eid = client.post(f"/api/declarations/{did}/evidence/file",
                      files={"file": ("bao-cao.docx", docx_bytes(),
                                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                      ).json()["id"]

    r = client.get(f"/api/evidence/{eid}/file")
    assert r.status_code == 200
    assert r.content == docx_bytes()
    assert "attachment" in r.headers["content-disposition"]
    assert "bao-cao.docx" in r.headers["content-disposition"]


def test_api_download_from_other_faculty_unit_is_403(client, conn, user_id):
    unit_a = mk_unit(conn, "khoa-tep-5a", "Khoa Tệp 5A")
    unit_b = mk_unit(conn, "khoa-tep-5b", "Khoa Tệp 5B")
    officer_a = mk_actor(conn, ["faculty_officer"], unit_a)
    officer_b = mk_actor(conn, ["faculty_officer"], unit_b)
    did, _ = mk_declaration(client, conn, user_id, "K2026-EVAPI-5", unit_id=unit_a)
    eid = client.post(f"/api/declarations/{did}/evidence/file",
                      files={"file": ("bao-cao.pdf", PDF_BYTES, "application/pdf")}).json()["id"]

    ok = client.get(f"/api/evidence/{eid}/file", headers=as_user(client, officer_a))
    assert ok.status_code == 200

    forbidden = client.get(f"/api/evidence/{eid}/file", headers=as_user(client, officer_b))
    assert forbidden.status_code == 403


def test_api_download_unknown_evidence_is_404(client, conn, user_id):
    r = client.get("/api/evidence/999999/file")
    assert r.status_code == 404


def test_api_download_non_file_evidence_is_404(client, conn, user_id):
    did, _ = mk_declaration(client, conn, user_id, "K2026-EVAPI-6")
    eid = client.post(f"/api/declarations/{did}/evidence",
                      json={"kind": "link", "url": "https://example.org/x"}).json()["id"]
    r = client.get(f"/api/evidence/{eid}/file")
    assert r.status_code == 404
