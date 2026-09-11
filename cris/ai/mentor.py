# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Gợi ý người hướng dẫn thật cho đồ án đang ghi `ICTU_TEACHER` (lát cắt I3,

xem docs/superpowers/plans/2026-09-11-lat-cat-i.md mục I3) — nỗi đau đo được
lớn nhất của kho: 4.621/5.375 đồ án (86%, xem README mục "Ba số liệu") ghi
người hướng dẫn là `ICTU_TEACHER`, một tên giữ chỗ do nguồn không tách được
tên thật (`cris/source/repository.py`), không phải tên một giảng viên.

Chỉ ghi vào `ai_suggestion` — không bao giờ tự tạo/đổi `author_link`. Người
dùng đưa ứng viên vào hàng đợi tác giả (`POST /api/ai/mentors/{work_id}/accept`,
qua `cris.link.add_candidate`) rồi tự quyết định qua `cris.link.decide_link`
như mọi liên kết khác (BR-18) — xem `cris/api/routes/mentors.py`.

**Giả định** (ghi rõ để không ai tưởng là suy luận chắc chắn, chỉ là gợi ý
thống kê): đồ án cùng đề tài (gần nhau về ngữ nghĩa trên tiêu đề + tóm tắt +
từ khoá, cùng vector `cris.ai.embed`) thường có cùng giảng viên hướng dẫn —
vì một giảng viên thường nhận nhiều đồ án cùng hướng nghiên cứu qua các
khoá/nhóm sinh viên. Đây **không** phải suy luận từ hồ sơ phân công giảng
dạy (kho không có `dang_ky_do_an`, xem `cris/ai/screen.py`) — chỉ là tương
quan đề tài, có thể sai (một đề tài phổ biến — "xây dựng website bán hàng" —
có thể do nhiều giảng viên khác nhau hướng dẫn ở các khoá khác nhau); vì vậy
đây chỉ là gợi ý xếp vào hàng đợi, không bao giờ tự xác nhận.
"""
import json

from cris.ai.embed import load_matrix, top_k
from cris.ai.provider import AIDisabled
from cris.db import tx

_UPSERT = (
    "INSERT INTO ai_suggestion(kind, target_id, payload, model) VALUES (%s,%s,%s,%s) "
    "ON CONFLICT (kind, target_id, model) DO UPDATE SET payload=EXCLUDED.payload, built_at=now()"
)
_DELETE = "DELETE FROM ai_suggestion WHERE kind=%s AND target_id=%s AND model=%s"


def suggest_mentors(conn, provider, *, k=5, min_votes=2, min_score=0.70):
    """Gợi ý người hướng dẫn cho mỗi đồ án sống có lượt tên vai `mentor` đang
    giữ chỗ và chưa có liên kết nào đang chờ hay đã sống.

    **Đích** (đồ án cần gợi ý): `work.doc_type='do_an'`, `merged_into_id IS
    NULL`, có `author_mention` vai `mentor` với `is_placeholder=true`, và lượt
    tên đó **chưa** có `author_link` ở trạng thái `DaNoiTuDong`/`DaXacNhan`
    (đã sống) hay `ChoXacNhan` (đang chờ) — đã có liên kết rồi thì không cần
    gợi ý thêm.

    **Láng giềng** (nguồn ứng viên): đồ án sống khác có lượt tên vai `mentor`
    **không** giữ chỗ (`is_placeholder=false`) và **đã liên kết thật**
    (`author_link.state IN ('DaNoiTuDong','DaXacNhan')`) → ánh xạ sang
    `person_id` của người hướng dẫn đó. Chỉ đồ án trong tập này mới được coi
    là "biết người hướng dẫn thật".

    Với mỗi đích, lấy `k` láng giềng gần nhất theo cosine (ma trận từ
    `load_matrix`, giới hạn trước vào tập láng giềng hợp lệ — cùng cách
    `cris.ai.screen.screen_cohort` giới hạn không gian tìm trước khi gọi
    `top_k`). Trong `k` láng giềng đó, gộp theo `person_id`: `votes` = số láng
    giềng thuộc về người này, `score` = tổng cosine của các láng giềng đó
    (không phải trung bình — một người có nhiều láng giềng gần thì đáng tin
    hơn, `votes` một mình không phân biệt được điểm gần hay chỉ vừa qua
    ngưỡng top-k). Ứng viên vào gợi ý khi `votes >= min_votes` **và**
    `score >= min_score`; nhiều ứng viên có thể cùng qua ngưỡng (vd hai giảng
    viên khác nhau cùng hướng các nhóm khác nhau của một đề tài phổ biến) —
    payload liệt kê hết, sắp theo `score` giảm dần.

    Ghi `ai_suggestion(kind='mentor', target_id=work_id, model=provider.model_id,
    payload={mention_id, candidates:[{person_id, display_name, degree, votes,
    score, evidence:[{work_id, title, score}]}]})` — UPSERT theo
    `UNIQUE(kind, target_id, model)`, chạy lại không nhân đôi dòng. Đồ án
    không có ứng viên nào qua ngưỡng ở lần chạy này thì gợi ý cũ (nếu có, từ
    lần chạy trước với dữ liệu khác) bị xoá — không để lại gợi ý đã lỗi thời.

    `provider` là `NoneProvider` (`CRIS_AI_PROVIDER=none`) → ném `AIDisabled`,
    như mọi hàm khác trong `cris/ai/` cần vector thật.

    Trả `{"scanned": n, "suggested": m}`; `scanned` đếm đồ án đích đã xét,
    `suggested` đếm đồ án có ít nhất một ứng viên qua ngưỡng.
    """
    if getattr(provider, "name", None) == "none":
        raise AIDisabled("AI chưa bật: đặt CRIS_AI_PROVIDER=local (hoặc fake để kiểm thử) trước khi gợi ý người hướng dẫn")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT m.id AS mention_id, m.work_id FROM author_mention m "
            "JOIN work w ON w.id = m.work_id "
            "WHERE m.role = 'mentor' AND m.is_placeholder AND w.doc_type = 'do_an' AND w.merged_into_id IS NULL "
            "AND NOT EXISTS (SELECT 1 FROM author_link l WHERE l.mention_id = m.id "
            "AND l.state IN ('DaNoiTuDong','DaXacNhan','ChoXacNhan')) "
            "ORDER BY m.id"
        )
        targets = cur.fetchall()
    if not targets:
        return {"scanned": 0, "suggested": 0}

    with conn.cursor() as cur:
        cur.execute(
            "SELECT m.work_id, l.person_id, p.display_name, p.degree_raw FROM author_mention m "
            "JOIN author_link l ON l.mention_id = m.id AND l.state IN ('DaNoiTuDong','DaXacNhan') "
            "JOIN person p ON p.id = l.person_id "
            "JOIN work w ON w.id = m.work_id "
            "WHERE m.role = 'mentor' AND NOT m.is_placeholder AND w.doc_type = 'do_an' AND w.merged_into_id IS NULL"
        )
        mentor_rows = cur.fetchall()
    # Một đồ án có thể có nhiều lượt tên vai mentor đã liên kết (hiếm, đồng
    # hướng dẫn) — giữ người đầu tiên, đủ cho một gợi ý thống kê.
    mentor_of = {}
    for r in mentor_rows:
        mentor_of.setdefault(r["work_id"], r)

    scanned = len(targets)
    if not mentor_of:
        return {"scanned": scanned, "suggested": 0}

    ids, M = load_matrix(conn, provider.model_id)
    row_of = {wid: i for i, wid in enumerate(ids)}

    neighbour_ids = [wid for wid in mentor_of if wid in row_of]
    if not neighbour_ids:
        return {"scanned": scanned, "suggested": 0}
    sub_M = M[[row_of[wid] for wid in neighbour_ids]]

    with conn.cursor() as cur:
        cur.execute("SELECT id, title FROM work WHERE id = ANY(%s)", (neighbour_ids,))
        titles = {r["id"]: r["title"] for r in cur.fetchall()}

    suggested = 0
    with tx(conn), conn.cursor() as cur:
        for t in targets:
            row = row_of.get(t["work_id"])
            if row is None:
                cur.execute(_DELETE, ("mentor", t["work_id"], provider.model_id))
                continue  # đồ án chưa `ai embed` — không có vector để tìm láng giềng
            by_person = {}
            for idx, score in top_k(sub_M, M[row], k=k):
                wid = neighbour_ids[idx]
                info = mentor_of[wid]
                pid = info["person_id"]
                agg = by_person.setdefault(pid, {
                    "person_id": pid, "display_name": info["display_name"], "degree": info["degree_raw"],
                    "votes": 0, "score": 0.0, "evidence": [],
                })
                agg["votes"] += 1
                agg["score"] += score
                agg["evidence"].append({"work_id": wid, "title": titles.get(wid), "score": score})
            candidates = [c for c in by_person.values() if c["votes"] >= min_votes and c["score"] >= min_score]
            if not candidates:
                cur.execute(_DELETE, ("mentor", t["work_id"], provider.model_id))
                continue
            candidates.sort(key=lambda c: c["score"], reverse=True)
            payload = json.dumps({"mention_id": t["mention_id"], "candidates": candidates}, ensure_ascii=False)
            cur.execute(_UPSERT, ("mentor", t["work_id"], payload, provider.model_id))
            suggested += 1
    return {"scanned": scanned, "suggested": suggested}
