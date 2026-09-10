# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import os
import pytest
from cris import db

TABLES = [
    "audit_log", "declaration_event", "evidence", "declaration", "period",
    "duplicate_member", "duplicate_group", "author_link",
    "author_mention", "field_provenance", "work", "person", "unit",
    "source_record", "sync_run", "rule_set", "catalog", "app_user",
]

@pytest.fixture(scope="session")
def conn():
    url = os.environ.get("TEST_DATABASE_URL", "postgresql://cris:cris@localhost:5432/cris_test")
    c = db.connect(url)
    db.migrate(c)
    c.commit()
    yield c
    c.close()

@pytest.fixture(autouse=True)
def clean(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE " + ", ".join(TABLES) + " RESTART IDENTITY CASCADE")
    conn.commit()
    yield
    conn.rollback()

@pytest.fixture
def user_id(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO app_user(email, display_name, roles) VALUES (%s,%s,%s) RETURNING id",
                    ("rd@ictu.test", "Chuyên viên phòng", ["rd_officer"]))
        uid = cur.fetchone()["id"]
    conn.commit()
    return uid
