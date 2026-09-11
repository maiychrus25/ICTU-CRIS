# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Tìm chuyên gia (J1): gợi ý giảng viên gần chuyên môn nhất với một đề tài đề
xuất, dựa trên các công trình đã liên kết (sống) trong kho.

Nguyên tắc gợi ý-không-quyết (BR-18) như phần còn lại của `cris/ai/`: hàm ở
đây chỉ ghi vào `ai_query` (`kind='experts'`), không bao giờ ghi vào `work`,
`author_link`, `duplicate_group`, `person` hay `field_provenance` — không có
hành động nào tự động, chỉ trả danh sách gợi ý để người dùng tự đọc bằng
chứng và liên hệ.

**Thuật toán** (điểm mỗi giảng viên): lấy top-`top_works` công trình gần
nghĩa nhất với đề tài (cosine trên `cris.ai.embed`), gộp theo `person_id` qua
`v_person_publications` (liên kết sống — mọi trạng thái trừ `DaBacBo`, cùng
cách `cris.ai.mentor` coi là "công trình của người này"). Với mỗi người, sắp
các công trình khớp theo điểm giảm dần rồi cộng:

    score = Σ s_i · 0,8^hạng_i · (1,1 nếu năm công bố cách năm hiện tại
                                    không quá `recent_years`, ngược lại 1)

`0,8^hạng` (hạng tính riêng trong các công trình khớp của người đó, bắt đầu
từ 0) làm công trình khớp mạnh nhất đóng góp nhiều nhất, các công trình sau
đóng góp giảm dần theo cấp số nhân — một người có nhiều công trình gần đề
tài, dù mỗi công trình không phải khớp mạnh nhất, vẫn được ưu tiên hơn một
người chỉ có đúng một công trình rất khớp một lần rồi thôi khớp cả kho.
"""
import datetime
import json
import re

from cris.ai.embed import load_matrix, top_k
from cris.ai.provider import AIDisabled
from cris.db import tx

RANK_DECAY = 0.8
RECENT_BONUS = 1.1

NOTE = (
    "Gợi ý dựa trên tóm tắt các công trình đã liên kết trong kho — không phải toàn văn, "
    "không phải đánh giá năng lực; người quyết."
)
DISABLED_NOTE = "AI chưa bật: đặt CRIS_AI_PROVIDER=local (hoặc fake để kiểm thử) trước khi tìm chuyên gia — chưa có gợi ý."

_DEGREE_SPLIT = re.compile(r"[.\s/,;]+")
# "TS" nhận TS/PGS/GS (PGS, GS thường đi kèm TS — "PGS.TS", "GS.TS" — nhưng
# giữ cả dạng đứng riêng "PGS"/"GS" không có "TS" kèm theo, vẫn là học vị từ
# tiến sĩ trở lên); "ThS" nhận cả nhóm trên cộng thêm ThS. Tách theo dấu chấm/
# khoảng trắng trước khi so — "PGS.TS" phải tách thành hai token "PGS","TS",
# không gộp thành "PGSTS" rồi so chuỗi con (dễ sai: "THS" chứa "TS").
_TS_PLUS = {"TS", "PGS", "GS"}
_THS_PLUS = _TS_PLUS | {"THS"}


def _degree_tokens(raw):
    if not raw:
        return set()
    return {t.strip().upper() for t in _DEGREE_SPLIT.split(raw) if t.strip()}


def _degree_ok(degree_raw, min_degree):
    if not min_degree:
        return True
    wanted = _TS_PLUS if min_degree == "TS" else _THS_PLUS
    return bool(_degree_tokens(degree_raw) & wanted)


def _rank_experts(conn, provider, title, description, k, exclude, min_degree, unit_id, recent_years, top_works):
    query_text = (title + "\n" + description).strip()
    qv = provider.embed([query_text])[0]  # có thể ném AIDisabled, không bắt ở đây
    work_ids, M = load_matrix(conn, provider.model_id)
    if not work_ids:
        return []
    ranked = top_k(M, qv, k=top_works)
    if not ranked:
        return []
    top_ids = [work_ids[i] for i, _ in ranked]
    score_of = {work_ids[i]: score for i, score in ranked}

    with conn.cursor() as cur:
        cur.execute(
            "SELECT vp.person_id, vp.work_id, w.title, w.doc_type, w.year_issue "
            "FROM v_person_publications vp JOIN work w ON w.id = vp.work_id "
            "WHERE vp.work_id = ANY(%s)",
            (top_ids,),
        )
        links = cur.fetchall()

    by_person: dict[int, list] = {}
    for r in links:
        if r["person_id"] in exclude:
            continue
        score = score_of.get(r["work_id"])
        if score is None:
            continue
        by_person.setdefault(r["person_id"], []).append({
            "work_id": r["work_id"], "title": r["title"], "doc_type": r["doc_type"],
            "year": r["year_issue"], "score": score,
        })
    if not by_person:
        return []

    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.id, p.display_name, p.degree_raw, p.unit_id, u.code AS unit_code "
            "FROM person p LEFT JOIN unit u ON u.id = p.unit_id WHERE p.id = ANY(%s)",
            (list(by_person),),
        )
        people = {r["id"]: r for r in cur.fetchall()}

    current_year = datetime.date.today().year
    scored = []
    for pid, works in by_person.items():
        info = people.get(pid)
        if info is None:
            continue
        if unit_id is not None and info["unit_id"] != unit_id:
            continue
        if not _degree_ok(info["degree_raw"], min_degree):
            continue
        ranked_works = sorted(works, key=lambda w: w["score"], reverse=True)
        total = 0.0
        for rank, w in enumerate(ranked_works):
            recent = w["year"] is not None and (current_year - w["year"]) <= recent_years
            total += w["score"] * (RANK_DECAY ** rank) * (RECENT_BONUS if recent else 1.0)
        scored.append({
            "person_id": pid,
            "display_name": info["display_name"],
            "degree": info["degree_raw"],
            "unit_code": info["unit_code"],
            "score": total,
            "works_matched": len(ranked_works),
            "evidence": [
                {"work_id": w["work_id"], "title": w["title"], "doc_type": w["doc_type"],
                 "year": w["year"], "score": w["score"]}
                for w in ranked_works[:3]
            ],
        })
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:k]


def _save_query(conn, *, title, description, aspects, k, exclude_person_ids, min_degree, unit_id,
                 recent_years, provider_name, results, actor_id):
    input_payload = {
        "title": title, "description": description, "aspects": aspects, "k": k,
        "exclude_person_ids": list(exclude_person_ids), "min_degree": min_degree,
        "unit_id": unit_id, "recent_years": recent_years,
    }
    with tx(conn), conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ai_query(kind, input, results, provider, created_by) VALUES ('experts',%s,%s,%s,%s) "
            "RETURNING id",
            (
                json.dumps(input_payload, ensure_ascii=False, default=str),
                json.dumps(results, ensure_ascii=False, default=str),
                provider_name,
                actor_id,
            ),
        )
        return cur.fetchone()["id"]


def find_experts(conn, provider, *, title, description="", aspects=None, k=10, exclude_person_ids=(),
                  min_degree=None, unit_id=None, recent_years=3, top_works=200, actor_id=None, save=True):
    """Gợi ý `k` giảng viên gần chuyên môn nhất với đề tài (`title` + `description`).

    `min_degree`: `None` (không lọc), `"TS"` (nhận `TS`/`PGS`/`GS`) hay
    `"ThS"` (nhận cả nhóm trên cộng `ThS`) — so trên `person.degree_raw`,
    không phân biệt hoa/thường và dấu chấm. `unit_id` lọc theo
    `person.unit_id`. `exclude_person_ids` loại hẳn khỏi kết quả (vd giảng
    viên đã kín lịch, hoặc chính người đang hỏi).

    Lưu `ai_query(kind='experts', input, results, provider, created_by)` khi
    `save=True` (mặc định) — `results` là danh sách đã trả, giống cách
    `compare_topic` lưu, để `GET /api/ai/experts/{id}` đọc lại nguyên trạng.

    Không bao giờ ném ngoại lệ ra ngoài: `provider=none` (`AIDisabled`) →
    `results=[]`, `fallback=True`, `note` giải thích — khác `compare_topic`,
    ở đây **không có** đường lui khớp từ khoá (không có cách hợp lý để suy
    "gần chuyên môn" chỉ từ trùng từ).

    Trả `{"query_id", "provider", "fallback", "note", "results"}`.
    """
    title = title or ""
    description = description or ""
    aspects = dict(aspects or {})
    exclude = set(exclude_person_ids or ())
    try:
        results = _rank_experts(conn, provider, title, description, k, exclude, min_degree, unit_id,
                                 recent_years, top_works)
        fallback = False
        note = NOTE
    except AIDisabled:
        results = []
        fallback = True
        note = DISABLED_NOTE
    query_id = None
    if save:
        query_id = _save_query(
            conn, title=title, description=description, aspects=aspects, k=k,
            exclude_person_ids=exclude, min_degree=min_degree, unit_id=unit_id, recent_years=recent_years,
            provider_name=provider.name, results=results, actor_id=actor_id,
        )
    return {"query_id": query_id, "provider": provider.name, "fallback": fallback, "note": note, "results": results}
