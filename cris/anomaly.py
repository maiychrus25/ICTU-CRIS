# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Cảnh báo bất thường dữ liệu (K2, SC-10): quét sáu loại bất thường trên
`work`/`person` (chỉ đọc), ghi/đóng `quality_flag` — quét idempotent, không đụng
cờ đã `dismissed`. `python -m cris quality scan` gọi `scan()`; API
`cris/api/routes/anomalies.py` chỉ đọc lại bảng này và gọi `dismiss()`."""
import datetime
import json

from cris import audit
from cris.db import tx

# severity: 'cao' | 'vua' | 'thap'
KINDS = {
    "scopus_no_doi": "cao",
    "year_out_of_range": "vua",
    "thesis_title_equals_article": "vua",
    "orcid_duplicate": "cao",
    "doi_invalid": "vua",
    "missing_abstract_article": "thap",
}

_LABELS = {
    "scopus_no_doi": "Ghi Scopus/ISI nhưng không có DOI",
    "thesis_title_equals_article": "Luận văn/đồ án trùng tiêu đề chuẩn hoá với một bài báo",
    "orcid_duplicate": "Hai giảng viên cùng ORCID",
    "doi_invalid": "DOI sai định dạng 10.xxxx/…",
    "missing_abstract_article": "Bài báo không có tóm tắt",
}

YEAR_LOWER = 1990


def _year_upper():
    """Năm hiện tại + 1 — tính lại mỗi lần gọi, không đóng cứng theo ngày dựng."""
    return datetime.date.today().year + 1


def kind_label(kind):
    if kind == "year_out_of_range":
        return f"Năm ngoài khoảng {YEAR_LOWER}–{_year_upper()}"
    return _LABELS.get(kind, kind)


def _find_scopus_no_doi(cur):
    """Ghi Scopus/WoS (nhóm ISI, xem `cris.rules`) ở `indexes` nhưng không có DOI."""
    cur.execute(
        "SELECT id FROM work WHERE merged_into_id IS NULL AND doi IS NULL "
        "AND indexes && ARRAY['Scopus','WoS']"
    )
    return {(r["id"], None): {} for r in cur.fetchall()}


def _find_year_out_of_range(cur):
    cur.execute(
        "SELECT id, year_issue FROM work WHERE merged_into_id IS NULL AND year_issue IS NOT NULL "
        "AND (year_issue < %s OR year_issue > %s)",
        (YEAR_LOWER, _year_upper()),
    )
    return {(r["id"], None): {"year": r["year_issue"]} for r in cur.fetchall()}


def _find_thesis_title_equals_article(cur):
    """Luận văn/đồ án/luận án còn sống trùng `title_norm` với một bài báo còn sống;
    `article_id` lấy bài báo nhỏ nhất id cho ổn định."""
    cur.execute(
        "SELECT t.id AS thesis_id, min(a.id) AS article_id "
        "FROM work t JOIN work a ON a.title_norm = t.title_norm "
        "  AND a.doc_type = 'bai_bao' AND a.merged_into_id IS NULL "
        "WHERE t.doc_type IN ('do_an','luan_van','luan_an') AND t.merged_into_id IS NULL "
        "GROUP BY t.id"
    )
    return {(r["thesis_id"], None): {"article_id": r["article_id"]} for r in cur.fetchall()}


def _find_orcid_duplicate(cur):
    """Hai `person` khác nhau cùng ORCID — bình thường bị chặn bởi UNIQUE(orcid);
    cờ này chỉ để phòng khi ràng buộc bị nới hoặc dữ liệu lịch sử. Khoá theo
    `person_id`, không phải `work_id`."""
    cur.execute(
        "SELECT p.id AS person_id, p2.id AS other_id FROM person p "
        "JOIN person p2 ON p2.orcid = p.orcid AND p2.id <> p.id "
        "WHERE p.orcid IS NOT NULL"
    )
    return {(None, r["person_id"]): {"other_person_id": r["other_id"]} for r in cur.fetchall()}


def _find_doi_invalid(cur):
    cur.execute(
        r"SELECT id FROM work WHERE merged_into_id IS NULL AND doi IS NOT NULL "
        r"AND doi !~ '^10\.\d{4,9}/\S+$'"
    )
    return {(r["id"], None): {} for r in cur.fetchall()}


def _find_missing_abstract_article(cur):
    cur.execute(
        "SELECT id FROM work WHERE merged_into_id IS NULL AND doc_type = 'bai_bao' "
        "AND (abstract IS NULL OR btrim(abstract) = '')"
    )
    return {(r["id"], None): {} for r in cur.fetchall()}


FINDERS = {
    "scopus_no_doi": _find_scopus_no_doi,
    "year_out_of_range": _find_year_out_of_range,
    "thesis_title_equals_article": _find_thesis_title_equals_article,
    "orcid_duplicate": _find_orcid_duplicate,
    "doi_invalid": _find_doi_invalid,
    "missing_abstract_article": _find_missing_abstract_article,
}


def scan(conn):
    """Quét cả sáu loại, một giao dịch. Với mỗi loại: tính tập bất thường hiện
    tại; cờ chưa có -> chèn `open` (hoặc mở lại nếu trước đó `resolved`); cờ
    `open` đang có mà không còn đúng -> chuyển `resolved`; cờ `dismissed`
    không bao giờ bị đụng tới dù điều kiện còn đúng hay đã hết.
    Trả về `{kind: {found, new, resolved}}`."""
    out = {}
    with tx(conn), conn.cursor() as cur:
        for kind, severity in KINDS.items():
            current = FINDERS[kind](cur)  # {(work_id, person_id): detail}
            cur.execute("SELECT id, work_id, person_id, state FROM quality_flag WHERE kind=%s", (kind,))
            existing = {(r["work_id"], r["person_id"]): r for r in cur.fetchall()}
            new_count = 0
            for key, detail in current.items():
                work_id, person_id = key
                row = existing.get(key)
                detail_json = json.dumps(detail, ensure_ascii=False)
                if row is None:
                    cur.execute(
                        "INSERT INTO quality_flag(kind, work_id, person_id, detail, severity, state) "
                        "VALUES (%s,%s,%s,%s,%s,'open')",
                        (kind, work_id, person_id, detail_json, severity),
                    )
                    new_count += 1
                elif row["state"] == "resolved":
                    cur.execute(
                        "UPDATE quality_flag SET state='open', detail=%s, updated_at=now() WHERE id=%s",
                        (detail_json, row["id"]),
                    )
                    new_count += 1
                elif row["state"] == "open":
                    cur.execute(
                        "UPDATE quality_flag SET detail=%s, updated_at=now() WHERE id=%s",
                        (detail_json, row["id"]),
                    )
                # 'dismissed': không đụng, kể cả khi vẫn còn đúng.
            resolved_count = 0
            for key, row in existing.items():
                if row["state"] == "open" and key not in current:
                    cur.execute("UPDATE quality_flag SET state='resolved', updated_at=now() WHERE id=%s", (row["id"],))
                    resolved_count += 1
            out[kind] = {"found": len(current), "new": new_count, "resolved": resolved_count}
    return out


def dismiss(conn, flag_id, actor_id, reason):
    """Bỏ qua một cờ: lý do bắt buộc (`ValueError` nếu rỗng), cờ phải tồn tại
    (`LookupError` nếu không) — ghi audit `quality.dismiss`."""
    if not (reason or "").strip():
        raise ValueError("Bỏ qua cảnh báo bắt buộc phải nêu lý do.")
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT id, kind, work_id, person_id FROM quality_flag WHERE id=%s", (flag_id,))
        row = cur.fetchone()
        if row is None:
            raise LookupError(f"không tìm thấy cờ chất lượng #{flag_id}")
        cur.execute(
            "UPDATE quality_flag SET state='dismissed', dismissed_by=%s, reason=%s, updated_at=now() WHERE id=%s",
            (actor_id, reason, flag_id),
        )
        audit.log(conn, actor_id, "quality.dismiss", "quality_flag", flag_id,
                  after={"kind": row["kind"], "work_id": row["work_id"], "person_id": row["person_id"], "reason": reason})
