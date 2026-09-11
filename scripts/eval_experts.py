#!/usr/bin/env python3
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đo tìm chuyên gia (J1) trên dữ liệu thật: 30 đồ án ngẫu nhiên (seed 0) đã
có người hướng dẫn (GVHD) thật liên kết — che GVHD (không cho thuật toán
biết trước), hỏi `find_experts(title, abstract)`, xem GVHD thật có nằm
top-1/top-5 hay không. Không ghi `ai_query` (`save=False`).

Chạy (DB local `cris` đã `ai embed` + `normalize --redo --doc-type do_an`
từ trước, xem docs/ai.md mục 6 "Gợi ý người hướng dẫn"):

    python -m cris migrate   # áp 0014_ai_query_kind.sql nếu DB tạo trước lát cắt này
    python scripts/eval_experts.py

Kết quả in ra bảng từng đồ án và tỷ lệ top-1/top-5 tổng hợp — chép vào
docs/ai.md mục "Tìm chuyên gia".
"""
import os
import random
import sys
import time

from cris import db
from cris.ai import expert as ai_expert
from cris.ai import provider as ai_provider

SEED = 0
SAMPLE_SIZE = 30

_QUERY = (
    "SELECT DISTINCT ON (w.id) w.id AS work_id, w.title AS title, w.abstract AS abstract, "
    "l.person_id AS mentor_id, p.display_name AS mentor_name "
    "FROM work w "
    "JOIN author_mention m ON m.work_id = w.id AND m.role = 'mentor' AND m.is_placeholder = false "
    "JOIN author_link l ON l.mention_id = m.id AND l.state IN ('DaNoiTuDong','DaXacNhan') "
    "JOIN person p ON p.id = l.person_id "
    "WHERE w.doc_type = 'do_an' AND w.merged_into_id IS NULL AND w.title IS NOT NULL "
    "ORDER BY w.id, l.id DESC"
)


def _truncate(s, n=48):
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    conn = db.connect()
    with conn.cursor() as cur:
        cur.execute(_QUERY)
        rows = cur.fetchall()
    if not rows:
        print("Không có đồ án nào có GVHD thật đã liên kết — chạy `python -m cris ai mentors` "
              "và xác nhận vài gợi ý trước, hoặc kiểm tra normalize --redo --doc-type do_an.",
              file=sys.stderr)
        sys.exit(1)

    random.seed(SEED)
    sample = random.sample(rows, min(SAMPLE_SIZE, len(rows)))

    prov = ai_provider.get_provider()
    print(f"provider={prov.name} model={getattr(prov, 'model_id', '?')} "
          f"ứng viên={len(rows)} mẫu={len(sample)} (seed={SEED})", file=sys.stderr)

    top1_hits = 0
    top5_hits = 0
    durations = []
    print(f"{'work_id':>8}  {'top1':>4}  {'top5':>4}  {'hạng':>4}  GVHD thật  ·  tiêu đề")
    for r in sample:
        t0 = time.monotonic()
        result = ai_expert.find_experts(
            conn, prov, title=r["title"] or "", description=r["abstract"] or "", k=10, save=False,
        )
        durations.append(time.monotonic() - t0)
        person_ids = [c["person_id"] for c in result["results"]]
        rank = person_ids.index(r["mentor_id"]) + 1 if r["mentor_id"] in person_ids else None
        is_top1 = rank == 1
        is_top5 = rank is not None and rank <= 5
        top1_hits += int(is_top1)
        top5_hits += int(is_top5)
        print(f"{r['work_id']:>8}  {'x' if is_top1 else '.':>4}  {'x' if is_top5 else '.':>4}  "
              f"{rank if rank else '-':>4}  {r['mentor_name']}  ·  {_truncate(r['title'])}")

    n = len(sample)
    avg_s = sum(durations) / len(durations) if durations else 0.0
    print()
    print(f"top-1: {top1_hits}/{n} ({top1_hits / n:.1%})" if n else "top-1: n/a")
    print(f"top-5: {top5_hits}/{n} ({top5_hits / n:.1%})" if n else "top-5: n/a")
    print(f"thời gian trung bình mỗi lượt find_experts: {avg_s:.2f}s (k=10, top_works=200)")
    conn.close()


if __name__ == "__main__":
    os.environ.setdefault("CRIS_AI_PROVIDER", "local")
    main()
