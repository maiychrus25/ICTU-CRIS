# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Quản lý đơn vị thật (lát cắt M): liệt kê, đổi tên, thêm bí danh, gán tay
một giảng viên — mọi thay đổi ghi `audit_log`.

Chú ý: `unit` không phải bảng "hạt giống bất biến" trong bộ test — fixture
`clean` (tests/conftest.py, dùng chung mọi test) TRUNCATE nó trước mỗi test,
kể cả những đơn vị migration `0020_units_from_source.sql` seed. Vì vậy mọi
test ở đây tự tạo đơn vị của mình (`_mk_unit`) thay vì giả định "CNTT"/"ĐTTT"…
đã có sẵn — hành vi thật của migration 0020 được xác nhận riêng, ngoài bộ test
này (đọc trực tiếp SQL migration, và chạy thử trên DB thật)."""
from cris import units


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall()


def _mk_unit(conn, code, name=None, aliases=None, active=True):
    return q(conn, "INSERT INTO unit(code, name, aliases, active) VALUES (%s,%s,%s,%s) RETURNING id",
             code, name or code, aliases or [], active)[0]["id"]


def _mk_person(conn, name="Nguyễn Văn A"):
    return q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) VALUES ('lecturer',%s,%s,%s) RETURNING id",
             name, name.lower(), [name.lower()])[0]["id"]


def test_list_units_counts_works_and_persons(conn):
    cntt = _mk_unit(conn, "CNTT", "Khoa Công nghệ thông tin")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
        cur.execute("INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
                    "VALUES (currval('sync_run_id_seq'),'manual','k1','bai_bao','h','{}') RETURNING id")
        sr_id = cur.fetchone()["id"]
        cur.execute("INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) "
                    "VALUES ('bai_bao',%s,'T','t','DaChuanHoa') RETURNING id", (sr_id,))
        wid = cur.fetchone()["id"]
        cur.execute("INSERT INTO work_unit(work_id, unit_id, source) VALUES (%s,%s,'source')", (wid, cntt))
    pid = _mk_person(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE person SET unit_id=%s WHERE id=%s", (cntt, pid))
    conn.commit()
    rows = units.list_units(conn)
    row = next(r for r in rows if r["code"] == "CNTT")
    assert row["works"] == 1 and row["persons"] == 1 and row["active"] is True


def test_list_units_excludes_inactive_by_default(conn):
    _mk_unit(conn, "CNTT", "Khoa Công nghệ thông tin")
    _mk_unit(conn, "KHCB", "Khoa Khoa học cơ bản", active=False)
    conn.commit()
    codes = {r["code"] for r in units.list_units(conn)}
    assert "KHCB" not in codes and "CNTT" in codes
    codes_all = {r["code"] for r in units.list_units(conn, include_inactive=True)}
    assert "KHCB" in codes_all


def test_rename_unit_updates_name_and_logs_audit(conn):
    _mk_unit(conn, "DTTT", "DTTT")
    conn.commit()
    uid = units.rename_unit(conn, "DTTT", "Khoa Điện tử viễn thông", reason="xác nhận với phòng đào tạo")
    row = q(conn, "SELECT name FROM unit WHERE id=%s", uid)[0]
    assert row["name"] == "Khoa Điện tử viễn thông"
    log = q(conn, "SELECT action, after FROM audit_log WHERE entity='unit' AND entity_id=%s", uid)[0]
    assert log["action"] == "unit.rename" and log["after"]["reason"] == "xác nhận với phòng đào tạo"


def test_rename_unit_unknown_code_raises(conn):
    try:
        units.rename_unit(conn, "KHONGTONTAI", "X")
        raise AssertionError("phải ném ValueError")
    except ValueError:
        pass


def test_add_alias_dedups_and_logs_audit(conn):
    uid0 = _mk_unit(conn, "HTTTKT", "Khoa Hệ thống thông tin kinh tế", aliases=["HTTKT"])
    conn.commit()
    uid = units.add_alias(conn, "HTTTKT", "HTTKT2")
    assert uid == uid0
    row = q(conn, "SELECT aliases FROM unit WHERE id=%s", uid)[0]
    assert "HTTKT2" in row["aliases"] and "HTTKT" in row["aliases"]     # bí danh cũ vẫn còn
    same_uid = units.add_alias(conn, "HTTTKT", "HTTKT2")                # thêm lại: không trùng lặp
    row2 = q(conn, "SELECT aliases FROM unit WHERE id=%s", same_uid)[0]
    assert row2["aliases"].count("HTTKT2") == 1
    log = q(conn, "SELECT action, after FROM audit_log WHERE entity='unit' AND entity_id=%s AND action='unit.alias'", uid)
    assert len(log) == 1     # lần gọi lặp (đã có bí danh) không ghi audit lần hai


def test_add_alias_unknown_code_raises(conn):
    try:
        units.add_alias(conn, "KHONGTONTAI", "X")
        raise AssertionError("phải ném ValueError")
    except ValueError:
        pass


def test_set_person_unit_marks_manual_and_logs_audit(conn):
    cntt = _mk_unit(conn, "CNTT", "Khoa Công nghệ thông tin")
    pid = _mk_person(conn)
    conn.commit()
    units.set_person_unit(conn, pid, cntt, reason="phân công lại theo quyết định")
    row = q(conn, "SELECT unit_id, unit_source FROM person WHERE id=%s", pid)[0]
    assert row["unit_id"] == cntt and row["unit_source"] == "manual"
    log = q(conn, "SELECT action FROM audit_log WHERE entity='person' AND entity_id=%s", pid)[0]
    assert log["action"] == "person.unit_manual"


def test_set_person_unit_unknown_person_raises(conn):
    cntt = _mk_unit(conn, "CNTT", "Khoa Công nghệ thông tin")
    conn.commit()
    try:
        units.set_person_unit(conn, 999999, cntt)
        raise AssertionError("phải ném ValueError")
    except ValueError:
        pass
