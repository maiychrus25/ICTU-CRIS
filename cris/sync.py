# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import hashlib
import json
from cris import audit
from cris.db import tx
from cris.source import repository as R

def _hash(raw):
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def run_sync(conn, *, source, scope, doc_type, records, expected, full, triggered_by=None):
    with tx(conn), conn.cursor() as cur:
        cur.execute("INSERT INTO sync_run(source, scope, triggered_by, expected_count) VALUES (%s,%s,%s,%s) RETURNING id",
                    (source, scope, triggered_by, json.dumps({doc_type: expected}) if expected is not None else None))
        run_id = cur.fetchone()["id"]
        seen, added, changed = set(), 0, 0
        for key, raw in records:
            seen.add(key)
            h = _hash(raw)
            cur.execute("SELECT id, version, content_hash FROM source_record WHERE source=%s AND source_key=%s ORDER BY version DESC LIMIT 1",
                        (source, key))
            cur_row = cur.fetchone()
            if cur_row and cur_row["content_hash"] == h:
                cur.execute("UPDATE source_record SET last_seen_at=now(), status='active' WHERE id=%s", (cur_row["id"],))
                continue
            version = (cur_row["version"] + 1) if cur_row else 1
            cur.execute(
                "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, version, content_hash, raw) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (run_id, source, key, doc_type, version, h, json.dumps(raw, ensure_ascii=False)))
            new_id = cur.fetchone()["id"]
            if cur_row:
                changed += 1
                audit.log(conn, triggered_by, "source_record.new_version", "source_record", new_id,
                          before={"id": cur_row["id"]}, sync_run_id=run_id)
            else:
                added += 1
        vanished = 0
        if full:
            cur.execute("SELECT DISTINCT source_key FROM source_record WHERE source=%s AND doc_type=%s AND status='active'",
                        (source, doc_type))
            for r in cur.fetchall():
                if r["source_key"] not in seen:
                    cur.execute("UPDATE source_record SET status='vanished' WHERE source=%s AND source_key=%s",
                                (source, r["source_key"]))
                    vanished += 1
        fetched = len(seen)
        warnings, status = [], "ok"
        if expected is not None and fetched != expected:
            warnings.append({"doc_type": doc_type, "expected": expected, "fetched": fetched})
            status = "warning"
        cur.execute(
            "UPDATE sync_run SET finished_at=now(), fetched_count=%s, added=%s, changed=%s, vanished=%s, warnings=%s, status=%s WHERE id=%s",
            (json.dumps({doc_type: fetched}), added, changed, vanished, json.dumps(warnings), status, run_id))
    return run_id

def sync_repository(conn, path, fetch=None, with_details=True, triggered_by=None):
    fetch = fetch or R.get
    doc_type = R.DOC_TYPES[path]["doc_type"]
    first_page = fetch(f"{R.BASE}/{path}/")
    expected = R.archive_total(first_page)

    def records():
        for arc in R.iter_archive(path, fetch=fetch):
            raw = {"archive": arc}
            if with_details:
                try:
                    page = fetch(arc["url"])
                    raw["detail"] = R.parse_detail(page, arc["url"])
                    if doc_type == "giang_vien":
                        raw["detail"]["orcid"] = R.extract_orcid(page)
                except Exception as e:      # trang chi tiết lỗi: ghi nhận, tiếp tục (UC-01 3a)
                    with conn.cursor() as c2:
                        c2.execute("SELECT raw FROM source_record WHERE source='repository' AND source_key=%s ORDER BY version DESC LIMIT 1",
                                   (arc["url"],))
                        prev = c2.fetchone()
                    prev_detail = prev["raw"].get("detail") if prev else None
                    if prev_detail:
                        raw["detail"] = prev_detail
                        # bản lưu trữ (archive) không đổi so với phiên bản trước: coi như phục hồi
                        # hoàn toàn, không đánh dấu lỗi/cũ để tránh tạo version giả (hash không đổi)
                        if prev["raw"].get("archive") != arc:
                            raw["detail_error"] = str(e)
                            raw["detail_stale"] = True
                    else:
                        raw["detail_error"] = str(e)
            yield arc["url"], raw

    return run_sync(conn, source="repository", scope=path, doc_type=doc_type,
                    records=records(), expected=expected, full=True, triggered_by=triggered_by)
