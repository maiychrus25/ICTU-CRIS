# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
def report(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM v_data_quality")
        r = dict(cur.fetchone())
        cur.execute("SELECT doc_type, count(*) AS n FROM work WHERE merged_into_id IS NULL GROUP BY doc_type")
        r["works_by_type"] = {x["doc_type"]: x["n"] for x in cur.fetchall()}
        r["works_with_link_pct"] = round(100.0 * r["works_with_link"] / r["works"], 1) if r["works"] else 0.0
        cur.execute("SELECT id, source, scope, status, started_at, finished_at, added, changed, vanished, warnings FROM sync_run ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()
        r["last_sync"] = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in last.items()} if last else None
    return r
