# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
def test_migrate_creates_tables(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        names = {r["table_name"] for r in cur.fetchall()}
    for t in ["sync_run", "source_record", "work", "field_provenance", "author_mention",
              "person", "author_link", "unit", "duplicate_group", "duplicate_member",
              "catalog", "rule_set", "app_user", "audit_log", "schema_migration"]:
        assert t in names, t

def test_migrate_is_idempotent(conn):
    from cris import db
    assert db.migrate(conn) == []

def test_audit_log_has_no_update(conn):
    import psycopg
    with conn.cursor() as cur:
        cur.execute("INSERT INTO audit_log(action, entity, entity_id) VALUES ('t','work',1)")
        try:
            cur.execute("UPDATE audit_log SET action='x'")
            assert False, "UPDATE phải bị chặn"
        except psycopg.errors.RaiseException:
            pass
    conn.rollback()
