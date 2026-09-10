import itertools
import pytest
from cris import dedup, rules

def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None

_seq = itertools.count()

@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")

def mk(conn, doc_type, title, doi=None, year=None, journal=None, student=None, cohort=None):
    key = f"{doc_type}/{title}/{student}/{doi}/{next(_seq)}"
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) VALUES (1,'manual',%s,%s,'h','{}')", key, doc_type)
    wid = q(conn, """INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, doi, year_issue, journal, cohort, state)
                     VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, %s, %s, 'DaChuanHoa') RETURNING id""",
            doc_type, title, rules.norm_title(title), doi, year, journal, cohort)[0]["id"]
    for f, v in (("year_issue", year), ("journal", journal)):
        if v is not None:
            q(conn, "INSERT INTO field_provenance(work_id, field, value, set_kind) VALUES (%s,%s,%s,'normalize')", wid, f, str(v))
    if student:
        nn, _ = rules.norm_name(student, rules.RULES_V1["name_norm"])
        q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) VALUES (%s,'student',1,%s,%s,%s)", wid, student, nn, rules.name_key(nn))
    return wid

def test_same_doi_groups_with_diff(conn):
    a = mk(conn, "bai_bao", "Cocktail Party Effect", doi="10.1/x", year=2025, journal="ACS Omega")
    b = mk(conn, "bai_bao", "Cocktail party effect", doi="10.1/x", year=2024, journal="ACS omega")
    assert dedup.find_duplicates(conn)["groups"] == 1
    g = q(conn, "SELECT * FROM duplicate_group")[0]
    assert g["basis"] == "doi" and g["state"] == "NghiTrung" and g["hint"] is None
    d = {r["work_id"]: r["diff"] for r in q(conn, "SELECT work_id, diff FROM duplicate_member")}
    assert set(d) == {a, b} and "year_issue" in d[a] and "journal" in d[a]

def test_same_title_no_doi_groups_by_title(conn):
    mk(conn, "bai_bao", "A Large Language Model QA System", journal="J1")
    mk(conn, "bai_bao", "A large language model QA system", journal="Bộ TTTT")
    dedup.find_duplicates(conn)
    assert q(conn, "SELECT basis FROM duplicate_group")[0]["basis"] == "title_norm"

def test_group_thesis_same_title_different_students_gets_hint(conn):
    for s in ["Nguyễn A", "Trần B", "Lê C"]:
        mk(conn, "do_an", "Xây dựng chuỗi sản phẩm truyền thông", student=s, cohort="K14")
    out = dedup.find_duplicates(conn)
    assert out == {"groups": 1, "group_hint": 1}
    g = q(conn, "SELECT hint, basis FROM duplicate_group")[0]
    assert g["basis"] == "title_student_cohort" and "đồ án nhóm" in g["hint"]

def test_thesis_same_title_same_student_no_hint(conn):
    mk(conn, "do_an", "Website bán hàng", student="Nguyễn A", cohort="K14")
    mk(conn, "do_an", "Website bán hàng", student="Nguyen A", cohort="K14")
    assert dedup.find_duplicates(conn) == {"groups": 1, "group_hint": 0}

def test_different_titles_not_grouped(conn):
    mk(conn, "bai_bao", "Alpha"); mk(conn, "bai_bao", "Beta")
    assert dedup.find_duplicates(conn)["groups"] == 0

def test_merge_keeps_both_originals_and_writes_provenance(conn, user_id):
    a = mk(conn, "bai_bao", "X", doi="10.1/y", year=2025, journal="ACS Omega")
    b = mk(conn, "bai_bao", "X", doi="10.1/y", year=2024, journal="ACS omega")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    dedup.decide_group(conn, gid, "merge", user_id, survivor_id=a, field_choices={"year_issue": b, "journal": a})
    ws = {w["id"]: w for w in q(conn, "SELECT id, state, merged_into_id, year_issue, journal FROM work")}
    assert ws[b]["state"] == "DaGop" and ws[b]["merged_into_id"] == a
    assert ws[a]["state"] == "DaXacNhan" and ws[a]["year_issue"] == 2024 and ws[a]["journal"] == "ACS Omega"
    pv = q(conn, "SELECT field, value, set_kind, set_by FROM field_provenance WHERE work_id=%s AND set_kind='merge'", a)
    assert {(p["field"], p["value"]) for p in pv} == {("year_issue", "2024")} and pv[0]["set_by"] == user_id
    assert q(conn, "SELECT state, survivor_work_id FROM duplicate_group")[0] == {"state": "DaGop", "survivor_work_id": a}
    assert len(q(conn, "SELECT 1 FROM work")) == 2       # không xoá bản gốc

def test_keep_requires_reason_and_marks_giu_rieng(conn, user_id):
    mk(conn, "do_an", "T", student="A B", cohort="K1"); mk(conn, "do_an", "T", student="C D", cohort="K1")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    with pytest.raises(ValueError):
        dedup.decide_group(conn, gid, "keep", user_id)
    dedup.decide_group(conn, gid, "keep", user_id, reason="đồ án nhóm")
    assert q(conn, "SELECT state FROM duplicate_group")[0]["state"] == "GiuRieng"
    assert {w["state"] for w in q(conn, "SELECT state FROM work")} == {"GiuRieng"}
    assert dedup.find_duplicates(conn)["groups"] == 0    # đã quyết, không ghép lại
