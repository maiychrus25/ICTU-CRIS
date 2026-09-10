#!/usr/bin/env python3
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Chuẩn hoá trường 'Loại bài' (pub_type) của bài báo.

Vấn đề: 48 giá trị free-text trộn 2 chiều độc lập vào 1 ô:
  (a) nguồn/chỉ mục  : Scopus, WoS(+quartile), SCIE/ESCI, DOAJ, ISSN, kỷ yếu HT QG/QT...
  (b) điểm HĐGSNN    : 0,5 / 0,75 / 1,0
kèm lỗi gõ: 'KYHTGQ' (đảo chữ), 'KYHTQT.' (thừa dấu chấm),
'0,5' / '0.5' / '0,5đ' / '0,5 điểm' / 'TC 0,5 điểm' (cùng 1 nghĩa).

Đầu ra chuẩn: {indexes[], quartile, venue_kind, score, raw, needs_review}
"""
import re, json, unicodedata, collections, pathlib, sys

def _norm(s):
    s = unicodedata.normalize("NFC", (s or "").strip())
    return re.sub(r"\s+", " ", s).rstrip(" .").strip()

# --- (b) điểm: 0,5 / 0.5 / 0,5đ / 0,5 điểm / TC 0,5 điểm / 1 / 1,0 / 1điểm
SCORE = re.compile(r"(?<!\d)([01](?:[.,]\d+)?)\s*(?:đ|điểm)?(?!\d)", re.I)

# --- (a) nguồn/chỉ mục
INDEX_RULES = [
    (r"\bscopus\b",                    "Scopus"),
    (r"\bwos\b|\bisi\b|\bscie\b|\bssci\b|\besci\b", "WoS"),
    (r"\bscie\b",                      "SCIE"),
    (r"\bssci\b",                      "SSCI"),
    (r"\besci\b",                      "ESCI"),
    (r"\bdoaj\b",                      "DOAJ"),
    (r"\bissn\b",                      "ISSN"),
]
QUARTILE = re.compile(r"\bq([1-4])\b", re.I)

# kỷ yếu hội thảo: KYHTQG (quốc gia) / KYHTQT (quốc tế); 'KYHTGQ' là lỗi gõ của KYHTQG
VENUE_RULES = [
    (r"kyhtqt|hội thảo quốc tế",                    "conference_intl"),
    (r"kyhtqg|kyhtgq|hội thảo quốc gia|hội thảo trong nước", "conference_natl"),
    (r"tạp chí trong nước|\btc\b(?!.*(quốc tế|qt))", "journal_domestic"),
    (r"tạp chí quốc tế|\bqt\b|quốc tế|research article|báo quốc tế", "journal_intl"),
]

UNKNOWN = {"chưa xác định", "—", "-", "", "n/a"}

def normalize(raw):
    s = _norm(raw)
    low = s.lower()
    out = {"raw": raw, "indexes": [], "quartile": None,
           "venue_kind": None, "score": None, "needs_review": False}
    if low in UNKNOWN:
        out["needs_review"] = True
        return out
    for pat, name in INDEX_RULES:
        if re.search(pat, low) and name not in out["indexes"]:
            out["indexes"].append(name)
    q = QUARTILE.search(low)
    if q:
        out["quartile"] = "Q" + q.group(1)
    for pat, kind in VENUE_RULES:
        if re.search(pat, low):
            out["venue_kind"] = kind
            break
    m = SCORE.search(low)
    if m and not q:                       # tránh nhận nhầm 'Q1' thành điểm 1
        out["score"] = float(m.group(1).replace(",", "."))
    if out["indexes"] and not out["venue_kind"]:
        out["venue_kind"] = "journal_intl"
    if not any([out["indexes"], out["venue_kind"], out["score"]]):
        out["needs_review"] = True
    return out

if __name__ == "__main__":
    D = pathlib.Path(__file__).parent / "out"
    rows = [json.loads(l) for l in (D / "bai-bao.jsonl").open(encoding="utf-8")]
    for r in rows:
        r["pub_type_norm"] = normalize(r.get("pub_type"))
    with (D / "bai-bao.normalized.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Đã chuẩn hoá {len(rows)} bài báo -> out/bai-bao.normalized.jsonl\n")
    idx  = collections.Counter(i for r in rows for i in r["pub_type_norm"]["indexes"])
    ven  = collections.Counter(r["pub_type_norm"]["venue_kind"] for r in rows)
    sc   = collections.Counter(r["pub_type_norm"]["score"] for r in rows)
    quar = collections.Counter(r["pub_type_norm"]["quartile"] for r in rows if r["pub_type_norm"]["quartile"])
    rev  = sum(1 for r in rows if r["pub_type_norm"]["needs_review"])
    print("Chỉ mục :", dict(idx))
    print("Quartile:", dict(quar))
    print("Loại nơi công bố:", {k or "(không rõ)": v for k, v in ven.most_common()})
    print("Điểm    :", {k if k is not None else "(không có)": v for k, v in sorted(sc.items(), key=lambda x: (x[0] is None, x[0]))})
    print(f"\nCần rà tay: {rev} bài ({rev/len(rows)*100:.1f}%)")
    print(f"48 giá trị thô -> {len(idx)} chỉ mục + {len([k for k in ven if k])} loại nơi công bố + {len([k for k in sc if k])} mức điểm")
