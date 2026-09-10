# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json
import re
import unicodedata

RULES_V1 = {
    "name_norm": {
        "prefixes": {
            "PGS.TS": ["pgs.ts", "pgs. ts", "pgs.ts."], "GS.TS": ["gs.ts", "gs. ts"],
            "TS": ["ts", "ts.", "t.s", "t.s."], "ThS": ["ths", "ths.", "th.s", "th.s.", "thạc sĩ"],
            "GS": ["gs", "gs."], "PGS": ["pgs", "pgs."], "KS": ["ks", "ks."], "CN": ["cn", "cn."],
        },
        "placeholders": ["ICTU_TEACHER", "ICTU_STUDENT", "ICTU"],
        "separators": [",", ";"],
        "truncation_marks": ["…", "..."],
    },
    "pub_type_map": {
        "index_rules": [
            [r"\bscopus\b", "Scopus"], [r"\bwos\b|\bisi\b|\bscie\b|\bssci\b|\besci\b", "WoS"],
            [r"\bscie\b", "SCIE"], [r"\bssci\b", "SSCI"], [r"\besci\b", "ESCI"],
            [r"\bdoaj\b", "DOAJ"], [r"\bissn\b", "ISSN"],
        ],
        "venue_rules": [
            [r"kyhtqt|hội thảo quốc tế", "conference_intl"],
            [r"kyhtqg|kyhtgq|hội thảo quốc gia|hội thảo trong nước", "conference_natl"],
            [r"tạp chí trong nước|\btc\b(?!.*(quốc tế|qt))", "journal_domestic"],
            [r"tạp chí quốc tế|\bqt\b|quốc tế|research article|báo quốc tế", "journal_intl"],
        ],
        "score_regex": r"(?<!\d)([01](?:[.,]\d+)?)\s*(?:đ|điểm)?(?!\d)",
        "quartile_regex": r"\bq([1-4])\b",
        "unknown": ["chưa xác định", "—", "-", "", "n/a"],
    },
    "dedup": {
        "bai_bao": ["doi", "title_norm"],
        "do_an": ["title_student_cohort"],
        "luan_van": ["title_student_cohort"],
        "luan_an": ["title_student_cohort"],
    },
    "field_map": {
        "student": ["Sinh viên", "Học viên", "Nghiên cứu sinh", "Tác giả"],
        "cohort": ["Khóa", "Khoá", "Lớp"],
        "year": ["Năm", "Năm bảo vệ", "Năm XB", "Năm xuất bản"],
        "mentor": ["GVHD", "Giảng viên hướng dẫn", "Người hướng dẫn"],
    },
    "year_rule": {},
}

def strip_accents(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")

def _squash(s):
    return re.sub(r"\s+", " ", s).strip()

def norm_title(s):
    s = strip_accents(s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return _squash(s)

def norm_name(raw, body):
    s = _squash((raw or "").replace("-", " "))
    degree = None
    low = s.lower()
    for canon, variants in body["prefixes"].items():
        for v in sorted(variants, key=len, reverse=True):
            if low.startswith(v + " ") or low == v:
                degree, s = canon, s[len(v):].strip()
                low = s.lower()
                break
        if degree:
            break
    name_norm = _squash(strip_accents(s).lower())
    return name_norm, degree

def name_key(name_norm):
    return " ".join(sorted(name_norm.split()))

def split_names(raw, body):
    raw = raw or ""
    trunc = any(raw.rstrip().endswith(m) for m in body["truncation_marks"])
    for m in body["truncation_marks"]:
        raw = raw.replace(m, "")
    sep_pattern = "[" + "".join(re.escape(s) for s in body["separators"]) + "]"
    parts = [p.strip() for p in re.split(sep_pattern, raw)]
    return [p for p in parts if p], trunc

def is_placeholder(raw, body):
    return (raw or "").strip() in body["placeholders"]

def map_pub_type(raw, body):
    out = {"indexes": [], "quartile": None, "venue_kind": None, "score": None, "needs_review": False}
    s = _squash(unicodedata.normalize("NFC", raw or "")).rstrip(" .")
    low = s.lower()
    if low in body["unknown"]:
        out["needs_review"] = True
        return out
    for pat, name in body["index_rules"]:
        if re.search(pat, low) and name not in out["indexes"]:
            out["indexes"].append(name)
    q = re.search(body["quartile_regex"], low)
    if q:
        out["quartile"] = "Q" + q.group(1)
    for pat, kind in body["venue_rules"]:
        if re.search(pat, low):
            out["venue_kind"] = kind
            break
    m = re.search(body["score_regex"], low)
    if m and not q:
        out["score"] = float(m.group(1).replace(",", "."))
    if out["indexes"] and not out["venue_kind"]:
        out["venue_kind"] = "journal_intl"
    if not any([out["indexes"], out["venue_kind"], out["score"]]):
        out["needs_review"] = True
    return out

def seed_rules(conn, created_by):
    ids = {}
    with conn.cursor() as cur:
        for kind, body in RULES_V1.items():
            cur.execute("SELECT id FROM rule_set WHERE kind=%s AND version=1", (kind,))
            row = cur.fetchone()
            if row:
                ids[kind] = row["id"]
                continue
            cur.execute(
                "INSERT INTO rule_set(kind, version, body, active, created_by) VALUES (%s,1,%s,true,%s) RETURNING id",
                (kind, json.dumps(body, ensure_ascii=False), created_by))
            ids[kind] = cur.fetchone()["id"]
    conn.commit()
    return ids

def load_active(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, kind, body FROM rule_set WHERE active")
        return {r["kind"]: (r["id"], r["body"]) for r in cur.fetchall()}
