# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

MIGRATIONS = pathlib.Path(__file__).parent / "migrations"

def connect(url=None):
    url = url or os.environ.get("DATABASE_URL", "postgresql://cris:cris@localhost:5432/cris")
    return psycopg.connect(url, row_factory=dict_row)

@contextmanager
def tx(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def migrate(conn):
    applied = []
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS schema_migration (name text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())")
        cur.execute("SELECT name FROM schema_migration")
        done = {r["name"] for r in cur.fetchall()}
        for path in sorted(MIGRATIONS.glob("*.sql")):
            if path.name in done:
                continue
            cur.execute(path.read_text(encoding="utf-8"))
            cur.execute("INSERT INTO schema_migration(name) VALUES (%s)", (path.name,))
            applied.append(path.name)
    conn.commit()
    return applied
