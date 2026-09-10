# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/); dự
án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

Chưa có trong bản này: giao diện web (hàng đợi xác nhận, tra cứu dữ liệu —
hiện chỉ chạy được từ dòng lệnh), nhập Excel khoa (S-06), quét bù phân
trang (S-04).

### Added

- Lát cắt **S** (đồng bộ — sync): kéo dữ liệu công bố khoa học từ kho
  `repository.ictu.edu.vn`, lưu nguyên bản gốc theo phiên bản trong bảng
  `source_record` (`cris/sync.py`).
- Lát cắt **N** (chuẩn hoá — normalize): chuẩn hoá tên, ghi xuất xứ từng
  trường qua bảng `field_provenance`, nối tác giả, gộp bản ghi trùng, báo
  cáo chất lượng dữ liệu (`cris/normalize.py`, `cris/people.py`,
  `cris/link.py`, `cris/dedup.py`, `cris/quality.py`).
- CLI thống nhất: `python -m cris migrate|seed|sync [paths]|people|normalize|link|dedup|quality [--json]`.
- Bộ tài liệu phân tích nghiệp vụ (BA) bản 1.0 — 18 tệp, `docs/ba/`.
- Mô hình dữ liệu bản 0.1 cho lát cắt S + N + T-01/T-02 —
  `docs/ba/17-mo-hinh-du-lieu.md`.
- Migrations `0001`–`0005` (khởi tạo lược đồ, ràng buộc duy nhất
  `source_record`, ràng buộc DOI, view tra cứu).
- 90 test pytest chạy trên PostgreSQL 16 thật, không mock cơ sở dữ liệu.
- Hồ sơ nguồn mở: `LICENSE` (Apache-2.0), `NOTICE`, `DEPENDENCIES.md`,
  `docs/LICENSE_NOTICE.md`, `CODE_OF_CONDUCT.md`, mẫu issue
  (`.github/ISSUE_TEMPLATE/`), mẫu PR, CI (`pytest -v` trên PostgreSQL 16
  qua GitHub Actions).
- `BUILDING.md` — hướng dẫn dịch và chạy từ mã nguồn (Docker và venv).

## [0.1.0] - Chưa phát hành

Sẽ gắn nhãn (tag) và điền ngày khi phát hành bản đầu.
