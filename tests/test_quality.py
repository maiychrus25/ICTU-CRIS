# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json
import subprocess
import sys
from cris import quality, rules

def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None

def test_report_counts_and_percent(conn):
    rules.seed_rules(conn, None)
    q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) VALUES ('manual','t','ok',now())")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) VALUES (1,'manual','a','bai_bao','h','{}'),(1,'manual','b','bai_bao','h','{}')")
    q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state, needs_review) VALUES ('bai_bao',1,'A','a','DaChuanHoa',true),('bai_bao',2,'B','b','DaChuanHoa',false)")
    q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key, is_placeholder) VALUES (1,'author',1,'X Y','x y','x y',false),(2,'mentor',1,'ICTU_TEACHER','ictu_teacher','ictu_teacher',true)")
    q(conn, "INSERT INTO person(kind, display_name, name_norm, name_keys) VALUES ('lecturer','X Y','x y', ARRAY['x y'])")
    q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) VALUES (1,1,'ten_day_du_duy_nhat','DaNoiTuDong')")
    conn.commit()
    r = quality.report(conn)
    assert r["works"] == 2 and r["works_by_type"] == {"bai_bao": 2} and r["works_needs_review"] == 1
    assert r["mentions_placeholder"] == 1 and r["links_auto"] == 1
    assert r["works_with_link_pct"] == 50.0 and r["works_without_unit"] == 2
    assert r["last_sync"]["status"] == "ok"

def test_merged_work_link_not_double_counted(conn):
    rules.seed_rules(conn, None)
    q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) VALUES ('manual','t','ok',now())")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) VALUES (1,'manual','a','bai_bao','h1','{}'),(1,'manual','b','bai_bao','h2','{}')")
    q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) VALUES ('bai_bao',1,'A','a','DaChuanHoa')")
    survivor = q(conn, "SELECT id FROM work WHERE title='A'")[0]["id"]
    q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state, merged_into_id) VALUES ('bai_bao',2,'B','b','DaGop',%s)", survivor)
    merged = q(conn, "SELECT id FROM work WHERE title='B'")[0]["id"]
    q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) VALUES (%s,'author',1,'X Y','x y','x y'),(%s,'author',1,'Z T','z t','z t')", survivor, merged)
    m1 = q(conn, "SELECT id FROM author_mention WHERE work_id=%s", survivor)[0]["id"]
    m2 = q(conn, "SELECT id FROM author_mention WHERE work_id=%s", merged)[0]["id"]
    q(conn, "INSERT INTO person(kind, display_name, name_norm) VALUES ('external','X Y','x y'),('external','Z T','z t')")
    p1 = q(conn, "SELECT id FROM person WHERE display_name='X Y'")[0]["id"]
    p2 = q(conn, "SELECT id FROM person WHERE display_name='Z T'")[0]["id"]
    q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) VALUES (%s,%s,'ten_day_du_duy_nhat','DaXacNhan'),(%s,%s,'ten_day_du_duy_nhat','DaXacNhan')", m1, p1, m2, p2)
    conn.commit()
    r = quality.report(conn)
    assert r["works"] == 1
    assert r["works_with_link"] == 1
    assert r["works_with_link_pct"] == 100.0

def test_orphaned_only_mention_excluded_from_work_unit_and_link_count(conn):
    rules.seed_rules(conn, None)
    q(conn, "INSERT INTO sync_run(source, scope, status, finished_at) VALUES ('manual','t','ok',now())")
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) VALUES (1,'manual','a','bai_bao','h1','{}')")
    q(conn, "INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, state) VALUES ('bai_bao',1,'A','a','DaChuanHoa')")
    wid = q(conn, "SELECT id FROM work")[0]["id"]
    q(conn, "INSERT INTO unit(code, name) VALUES ('U1','Unit 1')")
    unit_id = q(conn, "SELECT id FROM unit")[0]["id"]
    q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) VALUES (%s,'author',-99,'X Y','x y','x y')", wid)
    mid = q(conn, "SELECT id FROM author_mention")[0]["id"]
    q(conn, "INSERT INTO person(kind, display_name, name_norm, unit_id) VALUES ('lecturer','X Y','x y',%s)", unit_id)
    pid = q(conn, "SELECT id FROM person")[0]["id"]
    q(conn, "INSERT INTO author_link(mention_id, person_id, confidence, state) VALUES (%s,%s,'ten_day_du_duy_nhat','DaXacNhan')", mid, pid)
    conn.commit()
    assert q(conn, "SELECT 1 FROM v_work_unit WHERE work_id=%s", wid) == []
    r = quality.report(conn)
    assert r["works"] == 1
    assert r["works_with_link"] == 0
    assert r["works_without_unit"] == 1

def test_cli_quality_json(conn):
    rules.seed_rules(conn, None)
    import os
    env = {**os.environ, "DATABASE_URL": os.environ.get("TEST_DATABASE_URL", "postgresql://cris:cris@localhost:5432/cris_test")}
    out = subprocess.run([sys.executable, "-m", "cris", "quality", "--json"], capture_output=True, text=True, env=env, check=True)
    assert json.loads(out.stdout)["works"] == 0
