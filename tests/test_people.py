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

def test_import_creates_person_position_and_keys(conn):
    """jobTitle (lát cắt M) là CHỨC VỤ → person.position; import không còn gán/tạo
    đơn vị (đơn vị nay đến từ assign_units_by_works hoặc gán tay)."""
    rules.seed_rules(conn, None)
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", GV)], expected=1, full=True)
    assert people.import_people(conn) == {"created": 1, "updated": 0, "errors": []}
    p = q(conn, "SELECT * FROM person")[0]
    assert p["kind"] == "lecturer" and p["display_name"] == "Nguyễn Văn Mẫu"
    assert p["name_keys"] == ["mau nguyen van"] and p["orcid"] == "0000-0002-1825-0097" and p["orcid_verified"] is False
    assert p["degree_raw"] == "TS" and p["email"] == "mau@example.invalid"
    assert p["dob"].isoformat() == "1980-01-01"
    assert p["position"] == "Khoa Công nghệ thông tin"     # giữ nguyên văn (không khớp bảng chuẩn hoá)
    assert p["unit_id"] is None and p["unit_source"] == "auto"

def test_import_never_creates_or_touches_unit_from_job_title(conn):
    """Khác hành vi cũ (unit_from_job_title): import không đụng tới bảng `unit`
    dù trước/sau khi có sẵn đơn vị trùng tên với jobTitle."""
    rules.seed_rules(conn, None)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO unit(code, name, aliases) VALUES ('CNTT','Khoa CNTT', ARRAY['Khoa Công nghệ thông tin'])")
    conn.commit()
    before = len(q(conn, "SELECT 1 FROM unit"))
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", GV)], expected=1, full=True)
    people.import_people(conn)
    assert people.import_people(conn) == {"created": 0, "updated": 1, "errors": []}
    assert len(q(conn, "SELECT 1 FROM unit")) == before
    p = q(conn, "SELECT unit_id FROM person")[0]
    assert p["unit_id"] is None

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


def test_lowercase_source_name_is_title_cased_for_display(conn):
    """Kho nguồn ghi `name` toàn chữ thường (slug); tên hiển thị phải viết hoa có dấu."""
    rules.seed_rules(conn, None)
    gv = {"archive": dict(GV["archive"], url="https://r/giang-vien/vinh/", name="nguyễn thế vịnh",
                           display="TS. nguyễn thế vịnh", email="vinh@example.invalid", orcid=None)}
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/vinh/", gv)], expected=1, full=True)
    people.import_people(conn)
    p = q(conn, "SELECT display_name, name_keys FROM person")[0]
    assert p["display_name"] == "Nguyễn Thế Vịnh"
    assert p["name_keys"] == ["nguyen the vinh"]
    assert rules.title_case_name("trần thị xuân-hà") == "Trần Thị Xuân-Hà"
    assert rules.title_case_name("NGUYỄN VĂN A") == "NGUYỄN VĂN A"


def test_job_title_positions_are_not_units(conn):
    """`jobTitle` là chức vụ (lát cắt M): hiệu trưởng/hiệu phó/trưởng khoa/tên khoa
    tự do đều chỉ ghi vào `person.position`, KHÔNG bao giờ gán/tạo đơn vị — Ban
    Giám hiệu (BGH) đã bị tắt ở migration 0020, không còn được suy ra ở đây nữa."""
    rules.seed_rules(conn, None)
    recs = []
    for i, jt in enumerate(["Hiệu trưởng", "Hiệu phó", "Trưởng khoa", "Khoa Công nghệ thông tin"]):
        a = dict(GV["archive"], url=f"https://r/giang-vien/p{i}/", name=f"Người Số {i}", display=f"TS. Người Số {i}",
                 email=f"p{i}@example.invalid", orcid=None, jobTitle=jt)
        recs.append((a["url"], {"archive": a}))
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien", records=recs, expected=4, full=True)
    people.import_people(conn)
    rows = {r["display_name"]: (r["code"], r["position"]) for r in
            q(conn, "SELECT p.display_name, p.position, u.code FROM person p LEFT JOIN unit u ON u.id=p.unit_id")}
    assert rows["Người Số 0"] == (None, "Hiệu trưởng")
    assert rows["Người Số 1"] == (None, "Phó Hiệu trưởng")
    assert rows["Người Số 2"] == (None, "Trưởng khoa")
    assert rows["Người Số 3"] == (None, "Khoa Công nghệ thông tin")
    assert len(q(conn, "SELECT 1 FROM unit WHERE code='BGH'")) == 0


def test_position_from_job_title_normalizes_known_variants():
    assert people.position_from_job_title("Hiệu phó") == "Phó Hiệu trưởng"
    assert people.position_from_job_title("  hiệu   trưởng ") == "Hiệu trưởng"
    assert people.position_from_job_title("Giảng viên chính") == "Giảng viên chính"
    assert people.position_from_job_title(None) is None
    assert people.position_from_job_title("") is None
    assert people.position_from_job_title("Chuyên viên") == "Chuyên viên"   # giữ nguyên, không có trong bảng chuẩn hoá


# ---------- lát cắt N: ảnh đại diện + lĩnh vực từ kho nguồn ----------
def test_avatar_url_from_archive_accepts_only_repository_domain():
    good = "https://repository.ictu.edu.vn/wp-content/uploads/2026/06/unnamed-150x150.webp"
    assert people.avatar_url_from_archive(good) == good
    assert people.avatar_url_from_archive("https://ui-avatars.com/api/?name=X") is None
    assert people.avatar_url_from_archive(None) is None
    assert people.avatar_url_from_archive("") is None
    assert people.avatar_url_from_archive("  ") is None


def test_field_from_archive_trims_and_keeps_raw_codes():
    assert people.field_from_archive("  CNTT  ") == "CNTT"
    assert people.field_from_archive("Toán học tính toán, Khoa học máy tính") == "Toán học tính toán, Khoa học máy tính"
    assert people.field_from_archive(None) is None
    assert people.field_from_archive("") is None


def test_import_sets_avatar_url_and_field(conn):
    rules.seed_rules(conn, None)
    gv = {"archive": dict(GV["archive"],
                          avatar="https://repository.ictu.edu.vn/wp-content/uploads/2026/06/mau.webp",
                          knowsAbout="CNTT")}
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", gv)], expected=1, full=True)
    people.import_people(conn)
    p = q(conn, "SELECT avatar_url, field FROM person")[0]
    assert p["avatar_url"] == "https://repository.ictu.edu.vn/wp-content/uploads/2026/06/mau.webp"
    assert p["field"] == "CNTT"


def test_import_drops_avatar_from_unknown_domain_and_missing_field(conn):
    rules.seed_rules(conn, None)
    gv = {"archive": dict(GV["archive"], avatar="https://ui-avatars.com/api/?name=X", knowsAbout=None)}
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", gv)], expected=1, full=True)
    people.import_people(conn)
    p = q(conn, "SELECT avatar_url, field FROM person")[0]
    assert p["avatar_url"] is None and p["field"] is None


def test_import_avatar_and_field_update_is_idempotent(conn):
    """Chạy lại `import_people` với cùng dữ liệu không đổi kết quả (410 hồ sơ
    thật ở sản xuất phải cập nhật lại an toàn nhiều lần)."""
    rules.seed_rules(conn, None)
    gv = {"archive": dict(GV["archive"],
                          avatar="https://repository.ictu.edu.vn/x.webp", knowsAbout="CNTT")}
    sync.run_sync(conn, source="repository", scope="giang-vien", doc_type="giang_vien",
                  records=[("https://r/giang-vien/mau/", gv)], expected=1, full=True)
    people.import_people(conn)
    people.import_people(conn)
    rows = q(conn, "SELECT avatar_url, field FROM person")
    assert len(rows) == 1
    assert rows[0]["avatar_url"] == "https://repository.ictu.edu.vn/x.webp" and rows[0]["field"] == "CNTT"


def _mk_unit(conn, code, name=None):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO unit(code, name) VALUES (%s,%s) ON CONFLICT (code) DO NOTHING RETURNING id",
                    (code, name or code))
        row = cur.fetchone()
        if row is None:
            cur.execute("SELECT id FROM unit WHERE code=%s", (code,))
            row = cur.fetchone()
    return row["id"]


def _mk_lecturer(conn, name):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO person(kind, display_name, name_norm, name_keys) VALUES ('lecturer',%s,%s,%s) RETURNING id",
                    (name, name.lower(), [name.lower()]))
        return cur.fetchone()["id"]


def _mk_bai_bao(conn, title):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO sync_run(source, scope) VALUES ('manual','t')")
        cur.execute("INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
                    "VALUES (currval('sync_run_id_seq'),'manual',%s,'bai_bao','h','{}') RETURNING id", (title,))
        sr_id = cur.fetchone()["id"]
        cur.execute("INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) "
                    "VALUES ('bai_bao',%s,%s,%s,'DaChuanHoa') RETURNING id", (sr_id, title, title.lower()))
        return cur.fetchone()["id"]


def _link_author(conn, work_id, person_id, state="DaXacNhan"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                    "VALUES (%s,'author',1,'X','x','x') RETURNING id", (work_id,))
        mid = cur.fetchone()["id"]
        cur.execute("INSERT INTO author_link(mention_id, person_id, confidence, state) VALUES (%s,%s,'ten_day_du_duy_nhat',%s)",
                    (mid, person_id, state))


def _set_work_unit(conn, work_id, unit_id, source="source"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO work_unit(work_id, unit_id, source) VALUES (%s,%s,%s)", (work_id, unit_id, source))


def test_assign_units_by_works_picks_majority(conn):
    cntt = _mk_unit(conn, "CNTT")
    khcb = _mk_unit(conn, "KHCB")
    pid = _mk_lecturer(conn, "Nguyễn Văn A")
    for title, unit_id in [("W1", cntt), ("W2", cntt), ("W3", khcb)]:
        wid = _mk_bai_bao(conn, title)
        _set_work_unit(conn, wid, unit_id)
        _link_author(conn, wid, pid)
    conn.commit()
    out = people.assign_units_by_works(conn)
    assert out["assigned"] == 1 and out["tied"] == 0
    row = q(conn, "SELECT unit_id, unit_source FROM person WHERE id=%s", pid)[0]
    assert row["unit_id"] == cntt and row["unit_source"] == "auto"


def test_assign_units_by_works_tie_clears_unit(conn):
    cntt = _mk_unit(conn, "CNTT")
    khcb = _mk_unit(conn, "KHCB")
    pid = _mk_lecturer(conn, "Trần Thị B")
    for title, unit_id in [("W1", cntt), ("W2", khcb)]:
        wid = _mk_bai_bao(conn, title)
        _set_work_unit(conn, wid, unit_id)
        _link_author(conn, wid, pid)
    with conn.cursor() as cur:
        cur.execute("UPDATE person SET unit_id=%s WHERE id=%s", (cntt, pid))
    conn.commit()
    out = people.assign_units_by_works(conn)
    assert out["cleared"] == 1 and out["tied"] == 1
    row = q(conn, "SELECT unit_id FROM person WHERE id=%s", pid)[0]
    assert row["unit_id"] is None


def test_assign_units_by_works_skips_manual_unit_source(conn):
    cntt = _mk_unit(conn, "CNTT")
    khcb = _mk_unit(conn, "KHCB")
    pid = _mk_lecturer(conn, "Lê Văn C")
    wid = _mk_bai_bao(conn, "W1")
    _set_work_unit(conn, wid, khcb)
    _link_author(conn, wid, pid)
    with conn.cursor() as cur:
        cur.execute("UPDATE person SET unit_id=%s, unit_source='manual' WHERE id=%s", (cntt, pid))
    conn.commit()
    out = people.assign_units_by_works(conn)
    assert out == {"assigned": 0, "cleared": 0, "unchanged": 0, "tied": 0}
    row = q(conn, "SELECT unit_id, unit_source FROM person WHERE id=%s", pid)[0]
    assert row["unit_id"] == cntt and row["unit_source"] == "manual"

