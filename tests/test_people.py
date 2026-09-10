# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import hashlib
from cris import people, rules, sync

def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a); return cur.fetchall()

GV = {"archive": {"url": "https://r/giang-vien/mau/", "name": "Nguyễn Văn Mẫu", "display": "TS. Nguyễn Văn Mẫu",
                  "degree": "TS", "rank": None, "position": "Giảng viên", "email": "mau@example.invalid",
                  "jobTitle": "Khoa Công nghệ thông tin", "knowsAbout": None, "honorificPrefix": "TS.",
                  "orcid": "0000-0002-1825-0097", "phone": "0900000000", "dob": "01/01/1980"}}

def test_import_creates_person_unit_and_keys(conn):
    rules.seed_rules(conn, None)
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", GV)], expected=1, full=True)
    assert people.import_people(conn) == {"created": 1, "updated": 0, "errors": []}
    p = q(conn, "SELECT * FROM person")[0]
    assert p["kind"] == "lecturer" and p["display_name"] == "Nguyễn Văn Mẫu"
    assert p["name_keys"] == ["mau nguyen van"] and p["orcid"] == "0000-0002-1825-0097" and p["orcid_verified"] is False
    assert p["degree_raw"] == "TS" and p["email"] == "mau@example.invalid"
    assert p["dob"].isoformat() == "1980-01-01"
    u = q(conn, "SELECT code, name FROM unit WHERE id=%s", p["unit_id"])[0]
    assert u["name"] == "Khoa Công nghệ thông tin"

def test_import_is_idempotent_and_unit_alias_dedups(conn):
    rules.seed_rules(conn, None)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO unit(code, name, aliases) VALUES ('CNTT','Khoa CNTT', ARRAY['Khoa Công nghệ thông tin'])")
    conn.commit()
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", GV)], expected=1, full=True)
    people.import_people(conn)
    assert people.import_people(conn) == {"created": 0, "updated": 1, "errors": []}
    assert len(q(conn, "SELECT 1 FROM unit")) == 1
    assert q(conn, "SELECT code FROM unit")[0]["code"] == "CNTT"

def test_ensure_unit_collision_gets_deterministic_suffix(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO unit(code, name) VALUES ('KHOAX', 'Khoa X cũ')")
    conn.commit()
    uid1 = people.ensure_unit(conn, "Khoa X")
    conn.commit()
    expected_code = "KHOAX" + hashlib.sha1("Khoa X".encode("utf-8")).hexdigest()[:4].upper()
    row = q(conn, "SELECT code FROM unit WHERE id=%s", uid1)[0]
    assert row["code"] == expected_code and row["code"] != "KHOAX"
    uid2 = people.ensure_unit(conn, "Khoa X")
    conn.commit()
    assert uid2 == uid1

def test_ensure_unit_prefers_exact_name_then_code_over_alias(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO unit(code, name) VALUES ('CNTT','Khoa CNTT') RETURNING id")
        a_id = cur.fetchone()["id"]
        cur.execute("INSERT INTO unit(code, name, aliases) VALUES ('B','Khoa B', ARRAY['CNTT'])")
    conn.commit()
    assert people.ensure_unit(conn, "CNTT") == a_id

def test_import_continues_after_unique_violation_and_reports_error(conn):
    rules.seed_rules(conn, None)
    gv2 = {"archive": {**GV["archive"], "url": "https://r/giang-vien/binh/",
                        "name": "Trần Thị Bình", "display": "Trần Thị Bình", "orcid": None}}
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", GV), ("https://r/giang-vien/binh/", gv2)],
                  expected=2, full=True)
    result = people.import_people(conn)
    assert result["created"] == 1
    assert len(result["errors"]) == 1
    assert result["errors"][0]["source_key"] == "https://r/giang-vien/binh/"
    assert len(q(conn, "SELECT 1 FROM person")) == 1
