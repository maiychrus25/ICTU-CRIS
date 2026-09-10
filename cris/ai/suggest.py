# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Gợi ý cho hàng đợi tác giả (FR-AI-06) và hàng đợi nghi trùng (FR-AI-07).

Chỉ ghi vào `ai_suggestion` — không bao giờ đổi `author_link`, `duplicate_group`
hay `work`. Người dùng vẫn tự quyết định qua `cris.link.decide_link` /
`cris.dedup.decide_group`; mã ở đây chỉ đọc và xếp hạng.
"""
import json
from cris.ai.embed import build_embeddings, load_matrix
from cris.db import tx

_UPSERT = (
    "INSERT INTO ai_suggestion(kind, target_id, payload, model) VALUES (%s,%s,%s,%s) "
    "ON CONFLICT (kind, target_id, model) DO UPDATE SET payload=EXCLUDED.payload, built_at=now()"
)


def suggest_author_links(conn, provider):
    """Xếp hạng ứng viên của mỗi lượt tên có ≥2 `author_link` đang `ChoXacNhan`.

    Điểm ứng viên = trung bình cosine giữa vector công trình đang xét và vector
    các công trình `DaXacNhan` của ứng viên đó. Ứng viên chưa có công trình xác
    nhận nào thì không có điểm, chỉ có lý do. Ghi
    `ai_suggestion(kind='author_link', target_id=link_id, payload={rank,score,reason})`.
    """
    build_embeddings(conn, provider)
    ids, M = load_matrix(conn, provider.model_id)
    row_of = {wid: i for i, wid in enumerate(ids)}

    with conn.cursor() as cur:
        cur.execute(
            "SELECT l.id AS link_id, l.person_id, l.mention_id, m.work_id "
            "FROM author_link l JOIN author_mention m ON m.id = l.mention_id "
            "WHERE l.state='ChoXacNhan' AND l.mention_id IN ("
            "  SELECT mention_id FROM author_link WHERE state='ChoXacNhan' GROUP BY mention_id HAVING count(*) >= 2"
            ") ORDER BY l.mention_id, l.id"
        )
        candidates = cur.fetchall()
        cur.execute(
            "SELECT l.person_id, m.work_id FROM author_link l "
            "JOIN author_mention m ON m.id = l.mention_id WHERE l.state = 'DaXacNhan'"
        )
        confirmed = {}
        for r in cur.fetchall():
            confirmed.setdefault(r["person_id"], []).append(r["work_id"])

    by_mention = {}
    for c in candidates:
        by_mention.setdefault(c["mention_id"], []).append(c)

    n = 0
    with tx(conn), conn.cursor() as cur:
        for mention_id, cands in by_mention.items():
            work_row = row_of.get(cands[0]["work_id"])
            scored = []
            for c in cands:
                own = [row_of[w] for w in confirmed.get(c["person_id"], []) if w in row_of]
                if work_row is None or not own:
                    scored.append((c["link_id"], None, "chưa có công trình đã xác nhận"))
                    continue
                score = float((M[own] @ M[work_row]).mean())
                reason = f"{len(own)} công trình đã xác nhận của người này cùng chủ đề"
                scored.append((c["link_id"], score, reason))
            scored.sort(key=lambda t: (t[1] is None, -(t[1] or 0.0)))
            for rank, (link_id, score, reason) in enumerate(scored, start=1):
                payload = json.dumps({"rank": rank, "score": score, "reason": reason}, ensure_ascii=False)
                cur.execute(_UPSERT, ("author_link", link_id, payload, provider.model_id))
                n += 1
    return {"model": provider.model_id, "suggestions": n}


def suggest_duplicates(conn, provider):
    """Tương đồng tóm tắt giữa các thành viên của mỗi nhóm nghi trùng ghép theo
    tiêu đề (`basis` là `title_norm`/`title_student_cohort`, `state='NghiTrung'`).

    KHÔNG đổi `duplicate_group.hint` hay gợi ý mặc định Giữ riêng của FR-N-10 —
    chỉ ghi `ai_suggestion(kind='duplicate', target_id=group_id, payload={pairs,min,max})`.
    """
    build_embeddings(conn, provider)
    ids, M = load_matrix(conn, provider.model_id)
    row_of = {wid: i for i, wid in enumerate(ids)}

    with conn.cursor() as cur:
        cur.execute(
            "SELECT g.id AS group_id, m.work_id FROM duplicate_group g "
            "JOIN duplicate_member m ON m.group_id = g.id "
            "WHERE g.state='NghiTrung' AND g.basis IN ('title_norm','title_student_cohort') "
            "ORDER BY g.id, m.work_id"
        )
        rows = cur.fetchall()

    by_group = {}
    for r in rows:
        by_group.setdefault(r["group_id"], []).append(r["work_id"])

    n = 0
    with tx(conn), conn.cursor() as cur:
        for gid, wids in by_group.items():
            pairs = []
            for i in range(len(wids)):
                for j in range(i + 1, len(wids)):
                    a, b = wids[i], wids[j]
                    if a not in row_of or b not in row_of:
                        continue
                    pairs.append([a, b, float(M[row_of[a]] @ M[row_of[b]])])
            if not pairs:
                continue
            scores = [p[2] for p in pairs]
            payload = json.dumps({"pairs": pairs, "min": min(scores), "max": max(scores)}, ensure_ascii=False)
            cur.execute(_UPSERT, ("duplicate", gid, payload, provider.model_id))
            n += 1
    return {"model": provider.model_id, "suggestions": n}
