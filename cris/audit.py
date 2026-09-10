import json

def log(conn, actor_id, action, entity, entity_id, before=None, after=None, sync_run_id=None):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO audit_log(actor_id, action, entity, entity_id, before, after, sync_run_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (actor_id, action, entity, entity_id,
             json.dumps(before, ensure_ascii=False) if before is not None else None,
             json.dumps(after, ensure_ascii=False) if after is not None else None,
             sync_run_id))
        return cur.fetchone()["id"]
