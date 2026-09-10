from cris import people, rules, sync

def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a); return cur.fetchall()

GV = {"archive": {"url": "https://r/giang-vien/tao/", "name": "Nguyễn Văn Tảo", "display": "TS. Nguyễn Văn Tảo",
                  "degree": "TS", "rank": None, "position": "Giảng viên", "email": "tao@ictu.edu.vn",
                  "jobTitle": "Khoa Công nghệ thông tin", "knowsAbout": None, "honorificPrefix": "TS.",
                  "orcid": "0000-0002-1825-0097", "phone": "0900000000", "dob": "01/01/1980"}}

def test_import_creates_person_unit_and_keys(conn):
    rules.seed_rules(conn, None)
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/tao/", GV)], expected=1, full=True)
    assert people.import_people(conn) == {"created": 1, "updated": 0}
    p = q(conn, "SELECT * FROM person")[0]
    assert p["kind"] == "lecturer" and p["display_name"] == "Nguyễn Văn Tảo"
    assert p["name_keys"] == ["nguyen tao van"] and p["orcid"] == "0000-0002-1825-0097" and p["orcid_verified"] is False
    assert p["degree_raw"] == "TS" and p["email"] == "tao@ictu.edu.vn"
    assert p["dob"].isoformat() == "1980-01-01"
    u = q(conn, "SELECT code, name FROM unit WHERE id=%s", p["unit_id"])[0]
    assert u["name"] == "Khoa Công nghệ thông tin"

def test_import_is_idempotent_and_unit_alias_dedups(conn):
    rules.seed_rules(conn, None)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO unit(code, name, aliases) VALUES ('CNTT','Khoa CNTT', ARRAY['Khoa Công nghệ thông tin'])")
    conn.commit()
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/tao/", GV)], expected=1, full=True)
    people.import_people(conn)
    assert people.import_people(conn) == {"created": 0, "updated": 1}
    assert len(q(conn, "SELECT 1 FROM unit")) == 1
    assert q(conn, "SELECT code FROM unit")[0]["code"] == "CNTT"
