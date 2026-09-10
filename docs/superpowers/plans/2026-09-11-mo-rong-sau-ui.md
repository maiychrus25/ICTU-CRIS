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

## Kết quả (11/09/2026)

Đối chiếu với `git log --oneline b3c3436..HEAD` (11 commit, từ cũ tới mới). Các task E1–E6
chạy xen kẽ với Task 3/4 của `2026-09-11-giao-dien-nextjs.md` chứ không tách hẳn thành một
đợt riêng sau khi UI ngang màn, như phần mở đầu của kế hoạch này giả định.

| Task kế hoạch | Xong ở commit | Ghi chú |
|---|---|---|
| E1 — Tổng quan cho lãnh đạo | backend `0eb0814` feat(api): stats, CSV export, audit log and reporting-period endpoints · frontend `81cf5dd` feat(frontend): batch C — leadership overview, CSV export links, audit log, reporting periods | `GET /api/stats` + trang `/tong-quan/` đúng như đặc tả: thẻ số, biểu đồ theo năm × loại, bảng đơn vị, top giảng viên |
| E2 — Xuất CSV | `0eb0814` (backend) · `81cf5dd` (nút "Tải CSV") | Đúng kế hoạch |
| E3 — Nhật ký thao tác | `0eb0814` (backend `/api/audit`) · `81cf5dd` (trang `/nhat-ky/`) | Đúng kế hoạch |
| E4 — Kỳ báo cáo (đọc + mở/đóng) | `0eb0814` (backend `/api/periods*`) · `81cf5dd` (trang `/ky-bao-cao/`, `/ky-bao-cao/chi-tiet/`) | Kê khai từng công trình vẫn để lại cho lát cắt sau, đúng như kế hoạch đã ghi rõ từ đầu |
| E5 — AI rà soát trùng đề tài theo lô | `140fb08` feat(ai): cohort topic-overlap screening with suggestions, CLI and API · `86de610` fix(ai): calibrate cohort screening thresholds on real score distribution · `151e6f5` feat(frontend): batch D — cohort topic-overlap screening with aspect matrix and prefilled comparison | Xem "Điều lệch" bên dưới — ngưỡng phải hiệu chuẩn lại sau khi đo trên dữ liệu thật |
| E6 — Đóng gói một container, gỡ UI cũ | `06f977e` refactor: remove the legacy stdlib web UI · `16b498f` build: multi-stage image serving the Next.js export; docs for the new architecture | Kiểm tra `frontend/out/index.html` trong ảnh CI đúng như kế hoạch; QA dữ liệu thật bổ sung thêm ở `d3e607e` (ngoài phạm vi E6 gốc) |

### Điều lệch so với kế hoạch

- **Ngưỡng rà soát (E5) phải hiệu chuẩn lại, không dùng lại ngưỡng của `compare_topic`.**
  Kế hoạch viết: "tính mức 4 khía cạnh như `compare_topic` (tái dùng hàm nội bộ...)" — ngụ
  ý dùng chung ngưỡng khía cạnh 0,55/0,35 đã có. Khi chạy thật trên cohort 21 (529 đồ án),
  ngưỡng đó gắn cờ **529/529 (100%)** — vô dụng, vì nó được hiệu chuẩn cho việc so một khía
  cạnh với một câu, không phải so toàn văn bản hai công trình cùng loại. Commit `86de610`
  thêm hằng số riêng `SCREEN_THRESHOLDS = (0.90, 0.80)` sau khi đo phân vị điểm thật
  (p50=0,835 · p90=0,897 · p99=0,928) và đọc thủ công các cặp quanh từng mức — kết quả gắn
  cờ 47/529 (8,9%), nằm trong khoảng mục tiêu 5–15% mà kế hoạch không hề đặt ra trước (vì
  chưa có số đo lúc viết kế hoạch). Xem phương pháp đầy đủ ở `docs/ai.md` §5.
- **E5 rà theo cohort do người vận hành truyền vào (`--cohort <mã>`), không tự động chọn
  "khoá mới nhất".** Mục "Bối cảnh" của E5 mô tả rà "đồ án của khoá mới nhất" — bản dựng
  thật để `screen_cohort(conn, provider, *, cohort, k=3, thresholds)` nhận `cohort` bất kỳ
  làm tham số bắt buộc, và trang `/doi-chieu/ra-soat/` cho chọn khoá từ danh sách các khoá
  đã rà (`GET /api/ai/screen/cohorts`) thay vì tự suy khoá mới nhất. Tổng quát hơn kế hoạch
  gốc: dùng được cho bất kỳ khoá nào đã `ai embed`, không chỉ khoá gần nhất.
  `dang_ky_do_an` vẫn đúng như kế hoạch nêu — không có ở nguồn, chỉ tồn tại trong schema —
  nên hướng "rà theo lô sau khi có dữ liệu" là lựa chọn đúng, không phải điều lệch.
  Migration cho tính năng này (`0008_ai_screen.sql`, thêm `'topic_overlap'` vào
  `ai_suggestion.kind`) không được nêu tên trong kế hoạch nhưng là hệ quả tất yếu của việc
  thêm `kind` mới — không phải sai lệch, chỉ là chi tiết kế hoạch bỏ sót.
- **E1 — biểu đồ theo năm chỉ vẽ được cho bài báo, không phải mọi loại tài liệu.** Kế
  hoạch mô tả `by_year_type` gồm đủ `bai_bao, do_an, luan_van, luan_an, hoc_lieu` theo năm,
  ngụ ý biểu đồ có đủ dữ liệu cho mọi loại. Trên dữ liệu thật, đồ án/luận văn/luận án không
  có năm xuất bản đáng tin ở nguồn nên phần lớn rơi vào `unknown_year` (5.734 công trình) —
  biểu đồ theo năm trên `/tong-quan/` vì vậy hiển thị chủ yếu là bài báo. API vẫn trả đúng
  cấu trúc kế hoạch yêu cầu; đây là giới hạn của dữ liệu nguồn, không phải lỗi triển khai —
  ghi vào mục "Đã biết" của `docs/release-notes/v0.2.0.md`.
- **Thứ tự chạy thực tế không tách bạch "trước/sau UI ngang màn"** như câu mở đầu kế hoạch
  giả định ("Tiền đề: ... đã ngang màn với UI cũ"). Nhìn theo lịch sử commit, E1–E4 backend
  (`0eb0814`) chạy ngay sau Task 3 của kế hoạch UI (`296db38`) và trước khi UI cũ bị gỡ
  (`06f977e`), tức là các lát cắt E và Task 4 của kế hoạch UI đan xen nhau thay vì nối tiếp
  tuần tự như hai kế hoạch riêng biệt ngụ ý.
- Phân công "UI luôn giao Codex, backend giao subagent sonnet" ghi trong Ràng buộc chung
  không kiểm chứng được từ lịch sử Git (tác giả commit là một tài khoản duy nhất); không
  tính là điều lệch vì đây là chi tiết quy trình nội bộ, không phải kết quả kỹ thuật.
