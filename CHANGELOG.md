# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/); dự
án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

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

### Fixed

- Siêu dữ liệu tìm thấy (`_page`, `_backfill`) không còn được tính vào băm
  nội dung của `source_record`. Vì kho nguồn sắp xếp không ổn định, số trang
  của một bản ghi trôi giữa các lần đồng bộ; băm cả nó thì mỗi lần chạy lại
  sinh một loạt phiên bản giả cho bản ghi không hề đổi nội dung
  (`cris/sync.py`).
- `count(DISTINCT ...) OVER (...)` trong hàng đợi tác giả: PostgreSQL không
  hỗ trợ `DISTINCT` trong window function nên mọi lần mở hàng đợi đều lỗi 500.
  Thay bằng subquery gộp rồi nối lại theo tên thô (`cris/web/views_queue.py`).

## [0.1.0] - Chưa phát hành

Sẽ gắn nhãn (tag) và điền ngày khi phát hành bản đầu.
