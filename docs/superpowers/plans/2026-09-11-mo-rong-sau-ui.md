# Kế hoạch: mở rộng sau khi có giao diện mới (lát cắt E)

Ngày 11/09/2026. Tiền đề: API FastAPI (`ea9f847`) và giao diện Next.js đợt A/B đã ngang
màn với UI cũ. Mục tiêu của lát cắt E: tăng điểm **hoàn thiện, khả dụng và tích hợp AI**
trong 50đ sản phẩm, không mở rộng phạm vi nghiệp vụ ngoài BRD.

Thứ tự ưu tiên theo giá trị/chi phí. Mỗi task độc lập, có thể giao cho một agent riêng;
UI luôn giao Codex, backend giao subagent sonnet.

## Ràng buộc chung

1. Không sửa tầng nghiệp vụ hiện có (`link`, `dedup`, `normalize`, `people`, `sync`,
   `quality`, `period`, `cris/ai/*`) trừ khi task nói rõ; thêm module mới thay vì sửa.
2. Mọi endpoint mới có `response_model`, test bằng `TestClient` trên PostgreSQL thật
   (fixture `conn`, `user_id`), provider AI `fake`. Cả hai biến DB, DB riêng mỗi tác vụ,
   pytest tiền cảnh trong Docker (xem `BUILDING.md` §9).
3. AI chỉ ghi `ai_*`; mọi quyết định của người đi qua hàm nghiệp vụ có `actor_id`.
4. Commit tiếng Anh, conventional-commit, không trailer AI. Không push (người dùng push).
5. UI: tiếng Việt có dấu, SPDX ở `.ts/.tsx`, trạng thái tải/rỗng/lỗi, `lint`/`tsc`/`build`/
   Playwright xanh. Đọc `frontend/AGENTS.md`.

## E1 — Tổng quan cho lãnh đạo (`/tong-quan/`)

Backend `cris/api/routes/stats.py`, `GET /api/stats?years=5`:
- `by_year_type`: `[{year, bai_bao, do_an, luan_van, luan_an, hoc_lieu}]` 5 năm gần nhất
  từ `v_work_current` (năm NULL gộp vào `"khong_ro"` ở trường riêng `unknown_year`).
- `by_unit`: `[{unit_id, code, name, works}]` từ `v_work_unit` + `unit`.
- `top_persons`: 10 người nhiều công trình nhất theo `v_person_publications` (chỉ
  `DaNoiTuDong`/`DaXacNhan`), kèm `unit_code`.
- `queues`: `{authors_pending, dup_groups_open}` từ `v_data_quality`.
- `coverage`: `works_with_link_pct`, `works_without_unit`.
- `last_sync`.
Test: DB rỗng → mảng rỗng, không lỗi chia 0; 3 công trình 2 năm → đúng đếm.

UI: một trang, hàng thẻ số (tổng công trình, % đã liên kết, chờ xác nhận, nghi trùng),
biểu đồ cột chồng theo năm × loại (Recharts, màu theo loại cố định, legend), bảng đơn vị,
bảng top giảng viên (link hồ sơ). Sidebar thêm mục "Tổng quan" đứng đầu; `/` chuyển
hướng sang `/tong-quan/` thay vì `/tra-cuu/`.

## E2 — Xuất CSV (SC-05, UX-07)

Backend: `GET /api/works.csv` (cùng tham số lọc `/api/works`, không phân trang, tối đa
20.000 dòng, cột: id, doc_type, title, year, doi, journal, authors (raw_name nối `; `),
state) và `GET /api/persons/{id}/publications.csv`. UTF-8 có BOM, `Content-Disposition:
attachment; filename="cong-trinh-YYYYMMDD.csv"`, dùng `csv` stdlib, `StreamingResponse`.
Test: BOM ở đầu, số dòng, dấu tiếng Việt nguyên vẹn, lọc `doc_type` áp dụng.

UI: nút "Tải CSV" ở trang tra cứu (giữ bộ lọc hiện tại) và hồ sơ giảng viên — thẻ `<a>`
tới URL API (không fetch qua JS).

## E3 — Nhật ký thao tác (SC-08, minh bạch)

Backend `cris/api/routes/audit.py`: `GET /api/audit?entity&entity_id&actor&page` đọc
`audit_log` JOIN `app_user`, mới nhất trước, 50/trang; trả `{items:[{id, at, actor_name,
action, action_label, entity, entity_id, before, after}], page}`. `action_label` tiếng
Việt cho các action đã có: `link.confirm/reject/reassign`, `dup.merge/keep/skip`,
`period.open/close_submissions/cancel`, `source_record.new_version`, `mention.orphaned`.
Test: sau `decide_link` confirm có 1 dòng `link.confirm` với actor đúng; lọc `entity`.

UI: trang `/nhat-ky/` (bảng, lọc theo loại thực thể) và tab "Lịch sử" ở chi tiết công
trình (audit của `author_link`/`duplicate_group` liên quan tới work — dùng `entity_id` của
link/group; đơn giản: chỉ hiển thị khi bản ghi có `has_manual`).

## E4 — Kỳ báo cáo (lát cắt K, phần đọc + mở/đóng)

Backend `cris/api/routes/periods.py` gọi `cris/period.py`: `GET /api/periods`,
`GET /api/periods/{id}/progress`, `POST /api/periods` (body `{code, name, scope, criteria,
due_at}` → `open_period`), `POST /api/periods/{id}/close`, `POST /api/periods/{id}/cancel`.
`ValueError` → 409. Test: mở → có trong danh sách trạng thái `DangMo`; đóng hai lần → 409;
progress liệt kê mọi đơn vị active kể cả 0.

UI: `/ky-bao-cao/` danh sách + form mở kỳ (Dialog), `/ky-bao-cao/chi-tiet/?id=` bảng tiến
độ theo đơn vị (thanh tiến độ), nút đóng/huỷ có xác nhận; `days_remaining` nổi bật.
Kê khai từng công trình (declaration) để lát cắt sau.

## E5 — AI: rà soát trùng đề tài theo lô (điểm AI)

Bối cảnh: `dang_ky_do_an` không có ở nguồn (chỉ có trong schema). Thay vào đó rà theo lô
**đồ án của khoá mới nhất** với toàn kho trước đó: phát hiện đề tài lặp lại giữa các khoá
(đúng nỗi đau của giảng viên hướng dẫn, BRD mục "đề tài trùng lặp qua các năm").

Backend `cris/ai/screen.py`: `screen_cohort(conn, provider, *, cohort, k=3, thresholds)`:
với mỗi đồ án có `cohort` = giá trị đã cho, lấy top-k láng giềng có `cohort` khác (dùng
`load_matrix`/`top_k` sẵn có), tính mức 4 khía cạnh như `compare_topic` (tái dùng hàm
nội bộ, không sửa `compare.py` — nếu hàm cần dùng là private thì import có chú thích),
ghi `ai_suggestion(kind='topic_overlap', target_id=work_id, payload={cohort, neighbours:[{work_id, score, aspects}]})`
(UPSERT theo UNIQUE(kind,target_id,model)). CLI `python -m cris ai screen --cohort K18`.
`GET /api/ai/screen?cohort&min=cao&page` trả danh sách đồ án có ít nhất một láng giềng
mức `cao` ở khía cạnh `bai_toan`, kèm láng giềng. Test với provider fake: 2 đồ án cùng
tiêu đề khác khoá → có gợi ý; khác hẳn → không.

UI: trang `/doi-chieu/ra-soat/` chọn khoá (từ facet có sẵn hoặc nhập), bảng đồ án ↔ láng
giềng với ma trận khía cạnh (tái dùng component AspectMatrix), nút "Mở đối chiếu chi tiết"
→ `/doi-chieu/` điền sẵn tiêu đề. Dòng chú thích "AI gợi ý, người quyết; so trên tóm tắt".

## E6 — Đóng gói một container, gỡ UI cũ (Task 4 của kế hoạch UI)

- `Dockerfile` đa tầng: `node:24-alpine` build `frontend/` (`npm ci && npm run build`) →
  tầng python copy `frontend/out` vào `/app/frontend/out` (FastAPI mount tại `/`).
  `CMD ["serve","--host","0.0.0.0"]`. `deploy/docker-compose.yml` không đổi cổng.
- Gỡ `cris/web/`, `tests/test_web_*.py`, cờ `--legacy`; `BUILDING.md`, `README.md`,
  `docs/SRS.md` (mục giao diện) cập nhật; CHANGELOG `[Unreleased]`.
- CI: job `frontend` đã có; job `build` dựng ảnh đa tầng (kiểm tra `out/index.html` có
  trong ảnh bằng `docker run --rm cris:ci python -c "import pathlib; assert pathlib.Path('/app/frontend/out/index.html').exists()"`).

## Ngoài kế hoạch

Đăng nhập (NFR-01), kê khai từng công trình + minh chứng, xuất Excel định dạng biểu mẫu
Bộ, thông báo email. Ghi vào "Đã biết" của CHANGELOG khi phát hành 0.2.0.
