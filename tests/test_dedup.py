# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
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

def test_merge_rejects_non_mergeable_field(conn, user_id):
    a = mk(conn, "bai_bao", "Injection", doi="10.1/inj")
    mk(conn, "bai_bao", "Injection", doi="10.1/inj")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    with pytest.raises(ValueError):
        dedup.decide_group(conn, gid, "merge", user_id, survivor_id=a,
                            field_choices={"id; DROP TABLE work": a})

def test_merge_title_updates_title_norm(conn, user_id):
    a = mk(conn, "bai_bao", "Old Title", doi="10.1/tn")
    b = mk(conn, "bai_bao", "New Title", doi="10.1/tn")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    dedup.decide_group(conn, gid, "merge", user_id, survivor_id=a, field_choices={"title": b})
    w = q(conn, "SELECT title, title_norm FROM work WHERE id=%s", a)[0]
    assert w["title"] == "New Title" and w["title_norm"] == rules.norm_title("New Title")

def test_confirmed_survivor_is_regrouped_with_new_duplicate(conn, user_id):
    a = mk(conn, "bai_bao", "Regroup", doi="10.1/regroup")
    b = mk(conn, "bai_bao", "Regroup", doi="10.1/regroup")
    dedup.find_duplicates(conn)
    old_gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    dedup.decide_group(conn, old_gid, "merge", user_id, survivor_id=a)
    c = mk(conn, "bai_bao", "Regroup", doi="10.1/regroup")
    out = dedup.find_duplicates(conn)
    assert out["groups"] == 1
    new_groups = q(conn, "SELECT id FROM duplicate_group WHERE id <> %s", old_gid)
    assert len(new_groups) == 1
    members = {r["work_id"] for r in q(conn, "SELECT work_id FROM duplicate_member WHERE group_id=%s", new_groups[0]["id"])}
    assert members == {a, c}
    ws = {w["id"]: w["state"] for w in q(conn, "SELECT id, state FROM work")}
    assert ws[a] == "DaXacNhan" and ws[c] == "NghiTrung" and ws[b] == "DaGop"

def test_diff_compares_against_all_other_members(conn):
    a = mk(conn, "bai_bao", "Same Title Three", journal="J1")
    mk(conn, "bai_bao", "same title three", journal="J1")
    mk(conn, "bai_bao", "Same title three", journal="J2")
    dedup.find_duplicates(conn)
    diffs = {r["work_id"]: r["diff"] for r in q(conn, "SELECT work_id, diff FROM duplicate_member")}
    assert "journal" in diffs[a]

def test_title_bucket_includes_doi_bearing_work(conn):
    a = mk(conn, "bai_bao", "Same Title Doi Mix", doi="10.1/x")
    b = mk(conn, "bai_bao", "Same title doi mix")
    dedup.find_duplicates(conn)
    gs = q(conn, "SELECT id, basis FROM duplicate_group")
    assert len(gs) == 1 and gs[0]["basis"] == "title_norm"
    members = {r["work_id"] for r in q(conn, "SELECT work_id FROM duplicate_member WHERE group_id=%s", gs[0]["id"])}
    assert members == {a, b}

def test_thesis_same_title_absent_student_no_false_hint(conn):
    mk(conn, "do_an", "Đề tài không sinh viên", student=None, cohort="K14")
    mk(conn, "do_an", "Đề tài không sinh viên", student="Nguyễn A", cohort="K14")
    out = dedup.find_duplicates(conn)
    assert out == {"groups": 1, "group_hint": 0}
    assert q(conn, "SELECT hint FROM duplicate_group")[0]["hint"] is None

def test_new_duplicate_of_giu_rieng_pair_is_surfaced(conn, user_id):
    a = mk(conn, "bai_bao", "Giu Rieng Regroup")
    b = mk(conn, "bai_bao", "Giu rieng regroup")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    dedup.decide_group(conn, gid, "keep", user_id, reason="khác nhau")
    c = mk(conn, "bai_bao", "giu rieng regroup")
    out = dedup.find_duplicates(conn)
    assert out["groups"] == 1
    new_gid = q(conn, "SELECT id FROM duplicate_group WHERE id <> %s", gid)[0]["id"]
    members = {r["work_id"] for r in q(conn, "SELECT work_id FROM duplicate_member WHERE group_id=%s", new_gid)}
    assert members == {a, b, c}
    ws = {w["id"]: w["state"] for w in q(conn, "SELECT id, state FROM work")}
    assert ws[a] == "GiuRieng" and ws[b] == "GiuRieng" and ws[c] == "NghiTrung"

def test_decide_group_twice_raises(conn, user_id):
    mk(conn, "do_an", "Dup", student="A B", cohort="K1")
    mk(conn, "do_an", "Dup", student="A B", cohort="K1")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]
    dedup.decide_group(conn, gid, "keep", user_id, reason="r1")
    with pytest.raises(ValueError):
        dedup.decide_group(conn, gid, "keep", user_id, reason="r2")
