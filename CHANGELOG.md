# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/); dự
án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

### Added

- `GET /api/persons?q=&kind=&limit=` (lát cắt G, G1): tìm giảng viên/sinh
  viên theo tên, khớp qua `person.name_keys` (có/không dấu, đủ họ tên) hoặc
  `display_name ILIKE` (một phần); `works` đếm trên `v_person_publications`
  ở trạng thái liên kết sống (`cris/api/routes/persons.py`).
- `GET /api/topics` thêm `keywords` (8 từ khoá nặng nhất) và `built_at`;
  `GET /api/topics/{id}` (mới): từ khoá đầy đủ kèm trọng số và tối đa 50
  công trình khớp cụm, cùng cách khớp với bộ lọc `topic` ở `/api/works`
  (`cris/api/routes/search.py`).
- `GET /api/sync/runs?page=` và `GET /api/sync/runs/{id}`: lịch sử các lượt
  đồng bộ (mới nhất trước) với số thêm/đổi/mất, thời lượng, cảnh báo, và 20
  `source_record` mới/đổi gần nhất của lượt (`cris/api/routes/sync.py`).

## [0.2.0] - 2026-09-11

### Added

- API JSON FastAPI 13 endpoint (`/api/*`, OpenAPI tại `/docs`): tra cứu công
  trình và hồ sơ giảng viên, hàng đợi liên kết tác giả, hàng đợi nghi trùng,
  đối chiếu đề tài, chất lượng dữ liệu — lớp mỏng gọi vào tầng nghiệp vụ hiện
  có (`cris/api/`).
- `GET /api/stats` (tổng quan cho lãnh đạo): công trình theo năm × loại, theo
  đơn vị, top giảng viên, hàng đợi và tỉ lệ đã liên kết tác giả
  (`cris/api/routes/stats.py`).
- `GET /api/works.csv` và `GET /api/persons/{id}/publications.csv` (SC-05,
  UX-07): xuất danh sách công trình đã lọc ra CSV UTF-8 có BOM, tối đa 20.000
  dòng (`cris/api/routes/export.py`).
- `GET /api/audit` (SC-08): nhật ký thao tác đọc từ `audit_log`, nhãn tiếng
  Việt theo hành động, lọc theo thực thể và người thao tác
  (`cris/api/routes/audit.py`).
- `GET/POST /api/periods` và `POST /api/periods/{id}/close|cancel`: mở, đóng
  nộp, huỷ kỳ báo cáo và xem tiến độ theo đơn vị qua `cris/period.py`
  (`cris/api/routes/periods.py`).
- Rà soát trùng đề tài theo khoá (lát cắt E5): `cris/ai/screen.py`
  (`screen_cohort`), lệnh `python -m cris ai screen --cohort <mã>`,
  `GET /api/ai/screen` và `GET /api/ai/screen/cohorts` — so đồ án của một
  khoá với các khoá khác, ghi gợi ý `ai_suggestion(kind='topic_overlap')`,
  không đổi dữ liệu nghiệp vụ.
- Giao diện Next.js (`frontend/`, App Router, TypeScript, Tailwind, shadcn/ui,
  xuất tĩnh): tra cứu công trình và hồ sơ giảng viên, hàng đợi liên kết tác
  giả và nghi trùng, tổng quan cho lãnh đạo, xuất CSV, nhật ký thao tác, kỳ
  báo cáo, đối chiếu và rà soát trùng đề tài theo khoá, chất lượng dữ liệu —
  gọi `/api/*`, không có server-render phía Node lúc chạy.

### Changed

- `serve` nay chạy `uvicorn` phục vụ API FastAPI; giao diện Next.js thay UI
  HTML thuần cũ; một container (ảnh Docker đa tầng) phục vụ cả API và giao
  diện, cùng cổng 8000.

### Removed

- `cris/web` (UI HTML thuần, WSGI stdlib) và `tests/test_web_*.py`; cờ
  `python -m cris serve --legacy`.

### Fixed

- Rà soát trùng đề tài theo khoá dùng ngưỡng riêng `SCREEN_THRESHOLDS =
  (0.90, 0.80)`, hiệu chỉnh trên phân bố điểm thật (cohort 21, 529 đồ án:
  p50=0,835 · p90=0,897 · p99=0,928) thay cho ngưỡng khía cạnh 0,55/0,35 kế
  thừa từ `compare.py` — ngưỡng cũ gắn cờ 529/529 (100%), ngưỡng mới gắn cờ
  47/529 (8,9%). `screen_cohort` ghi thêm `max_score`/`level` vào payload;
  CLI có `--high`/`--mid`; `GET /api/ai/screen` thêm `min_score`, trả kết
  quả sắp theo `max_score` giảm dần (`cris/ai/screen.py`,
  `cris/api/routes/screen.py`, `cris/api/schemas.py`, `cris/cli.py`).

## [0.1.0] - 2026-09-10

Bản dự thi "Phát triển phần mềm mã nguồn mở tích hợp AI 2026". Tag `v0.1.0`.

Chưa có trong bản này: đăng nhập và phân quyền thật (NFR-01, NFR-02 — giao
diện hiện chạy với một người dùng mặc định, KHÔNG triển khai lên mạng công
khai), nhập Excel khoa (S-06), kê khai và phê duyệt (phần còn lại của lát cắt
K, toàn bộ D và R), nhà cung cấp AI ngoài (giao diện `explain` đã có chỗ).

### Added

- Lát cắt **S** (đồng bộ — sync): kéo dữ liệu công bố khoa học từ kho
  `repository.ictu.edu.vn`, lưu nguyên bản gốc theo phiên bản trong bảng
  `source_record` (`cris/sync.py`).
- Lát cắt **N** (chuẩn hoá — normalize): chuẩn hoá tên, ghi xuất xứ từng
  trường qua bảng `field_provenance`, nối tác giả, gộp bản ghi trùng, báo
  cáo chất lượng dữ liệu (`cris/normalize.py`, `cris/people.py`,
  `cris/link.py`, `cris/dedup.py`, `cris/quality.py`).
- Quét bù phân trang (**S-04**): kho nguồn sắp xếp theo cột không duy nhất
  nên lật trang tuần tự bỏ sót bản ghi mà không báo lỗi (đo 09/2026: 269
  trang `/do-an/` chỉ ra 5.364 trên 5.375). Khi lật trang xong mà vẫn thiếu
  so với số kho tự công bố, `iter_archive` quét bù theo bộ lọc `?cohort=`
  (đồ án, luận văn, luận án) hoặc `?dept=` (bài báo) — các trục phân hoạch
  kho khác nhau nên chạm được phần bị bỏ sót (`cris/source/repository.py`).
- **Tích hợp AI** (`cris/ai/`, [docs/ai.md](docs/ai.md)) — AI gợi ý, người quyết;
  không có AI vẫn chạy đủ chức năng:
  - Nhà cung cấp chọn bằng `CRIS_AI_PROVIDER`: `none` (mặc định), `fake` (kiểm
    thử), `local` — mô hình `paraphrase-multilingual-MiniLM-L12-v2` ONNX 8-bit
    (118 MB, 384 chiều, có tiếng Việt) chạy CPU qua `onnxruntime`, tải một lần
    và kiểm SHA-256. Thư viện AI là extra tuỳ chọn `pip install -e ".[ai]"`;
    gói lõi vẫn chỉ phụ thuộc `psycopg`.
  - Đối chiếu đề tài `/doi-chieu`: tìm công trình gần về nghĩa trên tiêu đề +
    tóm tắt + từ khoá, bảng so sánh theo bốn khía cạnh (giống / khác / chưa đủ
    thông tin), không hiện điểm phần trăm tổng hợp, luôn ghi "không phải toàn
    văn"; `provider=none` chạy đường lui khớp từ khoá có cảnh báo.
  - Gợi ý cho hàng đợi tác giả (xếp hạng ứng viên theo chủ đề các công trình
    đã xác nhận) và hàng đợi nghi trùng (tương đồng tóm tắt); trục chủ đề từ
    gom cụm 10.951 từ khoá làm bộ lọc `/tra-cuu?topic=`.
  - Rào chắn có test: mã AI chỉ ghi vào bảng `ai_*` (migration `0007`), không
    đổi `work`, `author_link`, `duplicate_group`, `field_provenance`.
  - CLI `python -m cris ai download|embed|topics|suggest|status`.
- Lược đồ kỳ báo cáo (lát cắt K, task 1): `period`, `declaration` (duy nhất
  theo kỳ + công trình + đơn vị), `evidence`, `declaration_event`; mở/đóng/huỷ
  kỳ gắn bộ quy tắc tại thời điểm mở (`cris/period.py`, migration `0006`).
- Giao diện web cho hàng đợi xác nhận và tra cứu — **không thêm thư viện nào**,
  viết bằng WSGI thuần stdlib (`wsgiref`), chạy bằng `python -m cris serve`:
  - Hàng đợi liên kết tác giả (SC-08): nhóm theo tên thô, sắp theo số công trình
    bị ảnh hưởng, xác nhận/bác bỏ/gán lại hàng loạt trong một transaction.
  - Hàng đợi nghi trùng (SC-07): so sánh từng trường cạnh nhau cho mọi thành
    viên, người dùng chọn bản sống sót và giá trị giữ lại cho từng trường mâu
    thuẫn. Nhóm khác sinh viên hiện cảnh báo đồ án nhóm và mặc định Giữ riêng.
  - Tra cứu công trình, hồ sơ công bố giảng viên, báo cáo chất lượng dữ liệu
    (SC-11, SC-12, SC-10). Trang chi tiết công trình hiện đủ ba cột: giá trị
    đang dùng, giá trị gốc, và nguồn.
  (`cris/web/`)
- CLI thống nhất: `python -m cris migrate|seed|sync [paths]|people|normalize|link|dedup|quality [--json]|serve`.
- Bộ tài liệu phân tích nghiệp vụ (BA) bản 1.0 — 18 tệp, `docs/ba/`.
- Mô hình dữ liệu bản 0.1 cho lát cắt S + N + T-01/T-02 —
  `docs/ba/17-mo-hinh-du-lieu.md`.
- Migrations `0001`–`0007` (khởi tạo lược đồ, ràng buộc duy nhất
  `source_record`, ràng buộc DOI, view tra cứu).
- 208 test pytest chạy trên PostgreSQL 16 thật, không mock cơ sở dữ liệu;
  thêm 3 test `slow` chạy mô hình AI thật (`pytest -m slow`).
- Hồ sơ nguồn mở: `LICENSE` (Apache-2.0), `NOTICE`, `DEPENDENCIES.md`,
  `docs/LICENSE_NOTICE.md`, `CODE_OF_CONDUCT.md`, mẫu issue
  (`.github/ISSUE_TEMPLATE/`), mẫu PR, CI (`pytest -v` trên PostgreSQL 16
  qua GitHub Actions).
- `BUILDING.md` — hướng dẫn dịch và chạy từ mã nguồn (Docker và venv).

### Đã kiểm chứng trên dữ liệu thật (10/09/2026)

Toàn kho `repository.ictu.edu.vn` đồng bộ đủ 8.034 bản ghi (đồ án 5.375/5.375 nhờ quét
bù phân trang), 7.618 công trình sau chuẩn hoá. Bài báo đạt 86,6 % có liên kết tác giả
(78,8 % tự nối, 15,9 % chờ xác nhận) so với 8 % ở nguồn. Vector cho toàn bộ công trình
sinh trong 11 phút trên CPU; đối chiếu một đề tài 3,25 s. Chi tiết: BUILDING.md §9.

### Đã biết (Known issues)

- Chỉ số `mentions_placeholder` trên trang chất lượng dữ liệu **chỉ đếm sinh viên**
  (`ICTU_STUDENT`, 302 lượt): bước chuẩn hoá không tạo lượt tên cho giảng viên hướng
  dẫn ghi placeholder `ICTU_TEACHER`, nên 4.655 đồ án không có lượt tên mentor nào và
  không xuất hiện trong chỉ số này. Con số thật của placeholder ở nguồn lớn hơn ~15 lần
  (4.621 + 302). Sẽ bổ sung chỉ số "đồ án không có giảng viên hướng dẫn" ở bản kế.
- Nhập hồ sơ giảng viên tạo 400/410 người: 10 hồ sơ bị từ chối vì trùng ORCID với hồ sơ
  khác ở nguồn (8 cặp cùng người có hai hồ sơ, 2 cặp hai người chung một ORCID). Hệ
  thống ghi lỗi thay vì gộp hay tạo trùng; hai cặp khác người cần người quyết.
- Liên kết tác giả của luận văn chủ yếu vào hàng đợi (68,7 % chờ xác nhận, 5,6 % tự nối)
  vì tên GVHD kèm học vị trùng nhiều ứng viên; đây là việc của hàng đợi, không phải lỗi.

### Fixed

- Siêu dữ liệu tìm thấy (`_page`, `_backfill`) không còn được tính vào băm
  nội dung của `source_record`. Vì kho nguồn sắp xếp không ổn định, số trang
  của một bản ghi trôi giữa các lần đồng bộ; băm cả nó thì mỗi lần chạy lại
  sinh một loạt phiên bản giả cho bản ghi không hề đổi nội dung
  (`cris/sync.py`).
- `count(DISTINCT ...) OVER (...)` trong hàng đợi tác giả: PostgreSQL không
  hỗ trợ `DISTINCT` trong window function nên mọi lần mở hàng đợi đều lỗi 500.
  Thay bằng subquery gộp rồi nối lại theo tên thô (`cris/web/views_queue.py`).

[Unreleased]: https://github.com/maiychrus25/ICTU-CRIS/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.2.0
[0.1.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.1.0
