# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Rà soát trùng đề tài theo khoá (lát cắt E5): với đồ án của một khoá, tìm

láng giềng ngữ nghĩa ở các khoá khác — đúng nỗi đau "đề tài lặp lại qua các
năm" của giảng viên hướng dẫn (`dang_ky_do_an` không có ở nguồn nên không rà
được lúc đăng ký; rà theo lô sau khi đã có trong kho).

Nguyên tắc gợi ý-không-quyết (BR-18) như phần còn lại của `cris/ai/`: chỉ ghi
`ai_suggestion(kind='topic_overlap')`, không bao giờ đổi `work` hay các bảng
nghiệp vụ khác.

**Lựa chọn khía cạnh** (khác `compare_topic`, ghi rõ ở đây để không ai tưởng
nhầm là cùng một thang đo): `compare_topic` so một khía cạnh với mô tả khía
cạnh do người dùng gõ tay; ở đây không có mô tả tay cho từng khía cạnh — chỉ
có tiêu đề + tóm tắt + từ khoá của chính công trình. Vì vậy:

- `bai_toan` dùng cosine của **toàn văn bản công trình** (cùng vector đã
  đứng trong `ai_embedding`, chính là `score` trả kèm mỗi láng giềng) — cách
  chia ba mức tái dùng công thức của `compare._bucket` (hàm nội bộ, import
  có chú thích bên dưới, chỉ đổi tên nhãn để tránh lẫn với nhãn
  "giống/khác/chưa đủ" của đối chiếu đề tài), nhưng **ngưỡng khác hẳn**:
  0,55/0,35 của `compare.py` hiệu chỉnh cho so một khía cạnh với một câu
  tóm tắt; ở đây so toàn văn bản (tiêu đề+tóm tắt+từ khoá) hai công trình
  cùng loại — điểm nền cao hơn nhiều vì mọi đồ án cùng ngành dùng chung một
  lớp từ vựng ("xây dựng", "website", "hệ thống", "quản lý"...). Xem
  `SCREEN_THRESHOLDS` ngay dưới đây để biết số đo và ngưỡng chọn.
- `doi_tuong`, `pham_vi`, `phuong_phap` không có căn cứ để tách riêng khỏi
  toàn văn bản (không có mô tả khía cạnh, không có câu chú thích khía cạnh
  trong tóm tắt) nên để `"khong_du_du_lieu"` — khác `"chua_du"` của
  `compare_topic` (nghĩa là "đã so nhưng không đủ câu"), ở đây nghĩa là
  "chưa thử so" để không gây hiểu nhầm là đã tính mà không ra kết quả.

**Hiệu chỉnh ngưỡng (10/09/2026, DB thật, cohort 21, 529 đồ án, mô hình
`local`)**: lấy điểm láng giềng cao nhất mỗi đồ án (`max_score`), phân vị đo
được — p50=0,835 · p75=0,870 · p90=0,897 · p95=0,908 · p99=0,928. Ngưỡng
0,55/0,35 kế thừa từ `compare.py` gắn cờ 529/529 (100%) — vô dụng. Đọc từng
cặp quanh các mốc ứng viên: ở 0,80–0,85 phần lớn là trùng lớp từ vựng chung
của đồ án CNTT (VD: "MVC/ASP.NET xây website quản lý ... cho công ty ..."
so với một đề tài khác hẳn), không phải trùng đề tài; từ 0,90 trở lên các
cặp đọc lên là cùng đề tài thật (VD: "Xây dựng ứng dụng Android hỗ trợ du
lịch thông minh" ~ "Xây dựng ứng dụng du lịch trên nền tảng Android",
0,9503). Chọn `HIGH = 0.90` (gắn cờ 47/529 = 8,9%, nằm trong khoảng mục
tiêu 5–15%), `MID = 0.80` (ranh dưới của lớp "cùng vốn từ chung ngành" —
dưới đó coi là không liên quan). Đo lại nếu hiệu chỉnh trên khoá/mô hình
khác.
"""
import json

# _bucket là hàm nội bộ (tên bắt đầu "_") của compare.py — tái dùng cách chia ba mức
# (không tái dùng ngưỡng của nó, xem SCREEN_THRESHOLDS); xem docstring trên cho lý do
# đổi tên nhãn.
from cris.ai.compare import _bucket
from cris.ai.embed import load_matrix, top_k
from cris.ai.provider import AIDisabled
from cris.db import tx

OTHER_ASPECTS = ("doi_tuong", "pham_vi", "phuong_phap")

# Nhãn "giong"/"khac"/"chua_du" của compare._bucket đổi tên cho ngữ cảnh rà
# soát theo khoá (mức độ trùng, không phải so khía cạnh đề tài đề xuất).
_LEVEL_LABELS = {"giong": "cao", "chua_du": "vua", "khac": "thap"}
LEVELS = ("cao", "vua", "thap")

# Ngưỡng hiệu chỉnh trên DB thật (xem số đo trong docstring module ở trên) —
# thay cho 0.55/0.35 kế thừa nhầm từ compare.py, vốn hiệu chỉnh cho so một
# khía cạnh với một câu, không phải so toàn văn bản hai công trình cùng loại.
SCREEN_THRESHOLDS = (0.90, 0.80)  # (HIGH, MID)

_UPSERT = (
    "INSERT INTO ai_suggestion(kind, target_id, payload, model) VALUES (%s,%s,%s,%s) "
    "ON CONFLICT (kind, target_id, model) DO UPDATE SET payload=EXCLUDED.payload, built_at=now()"
)


def _level(score, thresholds):
    return _LEVEL_LABELS[_bucket(score, thresholds)]


def screen_cohort(conn, provider, *, cohort, k=3, thresholds=SCREEN_THRESHOLDS, doc_type="do_an"):
    """Rà soát trùng đề tài của một khoá với các khoá khác đã có trong kho.

    Với mỗi công trình sống (`merged_into_id IS NULL`) có `doc_type` và
    `cohort` đã cho, đã có vector của `provider.model_id` (như cách
    `compare.py` chọn model — chỉ những công trình đã `ai embed` mới được
    rà), lấy top-`k` láng giềng cùng `doc_type` có `cohort` khác hoặc NULL
    (tìm dư rồi lọc, vì `top_k` không biết lọc theo cột `cohort`). Ghi
    `ai_suggestion(kind='topic_overlap', target_id=work_id, payload=
    {cohort, max_score, level, neighbours:[{work_id, title, cohort, score,
    aspects}]})` (UPSERT theo `UNIQUE(kind, target_id, model)`, giống
    `cris.ai.suggest`). `max_score` là điểm của láng giềng cao nhất (0.0 nếu
    không có láng giềng nào qua được bộ lọc khoá); `level` là mức của
    `max_score` theo `thresholds` (mặc định `SCREEN_THRESHOLDS`) — cùng cách
    tính `aspects.bai_toan` của láng giềng đứng đầu, đưa lên cấp công trình để
    API sắp xếp/lọc không phải quét lại `neighbours`.

    `provider` là `NoneProvider` (`CRIS_AI_PROVIDER=none`) → ném `AIDisabled`,
    như mọi hàm khác trong `cris/ai/` cần vector thật.

    Trả `{"screened": n, "flagged": m}`; `flagged` đếm công trình có `level`
    (điểm láng giềng cao nhất) ở mức `"cao"`.
    """
    if getattr(provider, "name", None) == "none":
        raise AIDisabled("AI chưa bật: đặt CRIS_AI_PROVIDER=local (hoặc fake để kiểm thử) trước khi rà soát")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT w.id, w.title, w.cohort FROM work w "
            "JOIN ai_embedding e ON e.work_id = w.id AND e.model = %s "
            "WHERE w.merged_into_id IS NULL AND w.doc_type = %s AND w.cohort = %s "
            "ORDER BY w.id",
            (provider.model_id, doc_type, cohort),
        )
        works = cur.fetchall()
    if not works:
        return {"screened": 0, "flagged": 0}

    ids, M = load_matrix(conn, provider.model_id)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, cohort FROM work WHERE merged_into_id IS NULL AND doc_type = %s",
            (doc_type,),
        )
        meta = {r["id"]: r for r in cur.fetchall()}

    # Không gian tìm láng giềng: chỉ công trình cùng doc_type đã có vector —
    # cùng cách compare._semantic_results giới hạn ma trận trước khi top_k.
    keep = [i for i, wid in enumerate(ids) if wid in meta]
    sub_ids = [ids[i] for i in keep]
    sub_M = M[keep]
    row_of = {wid: i for i, wid in enumerate(sub_ids)}

    k_search = max(k * 5, k + 20)
    screened = 0
    flagged = 0
    with tx(conn), conn.cursor() as cur:
        for w in works:
            row = row_of.get(w["id"])
            if row is None:
                continue  # phòng thân: không có trong ma trận dù JOIN ai_embedding đã lọc ở trên
            ranked = top_k(sub_M, sub_M[row], k=k_search)
            neighbours = []
            for idx, score in ranked:
                wid = sub_ids[idx]
                if wid == w["id"]:
                    continue
                info = meta.get(wid)
                if info is None or info["cohort"] == cohort:
                    continue  # chỉ láng giềng khoá khác hoặc NULL
                neighbours.append({
                    "work_id": wid,
                    "title": info["title"],
                    "cohort": info["cohort"],
                    "score": score,
                    "aspects": {"bai_toan": _level(score, thresholds),
                                **{a: "khong_du_du_lieu" for a in OTHER_ASPECTS}},
                })
                if len(neighbours) >= k:
                    break
            # neighbours giữ nguyên thứ tự giảm dần theo score (từ top_k) nên
            # láng giềng đầu tiên, nếu có, luôn là max_score.
            max_score = neighbours[0]["score"] if neighbours else 0.0
            level = _level(max_score, thresholds)
            payload = json.dumps(
                {"cohort": cohort, "max_score": max_score, "level": level, "neighbours": neighbours},
                ensure_ascii=False,
            )
            cur.execute(_UPSERT, ("topic_overlap", w["id"], payload, provider.model_id))
            screened += 1
            if level == "cao":
                flagged += 1
    return {"screened": screened, "flagged": flagged}
