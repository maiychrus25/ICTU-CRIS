# Đóng góp cho ICTU-CRIS (Contributing)

## Quy trình (Process)

1. Mở issue mô tả vấn đề hoặc đề xuất trước khi viết mã đáng kể — dùng mẫu
   trong [.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/) (`bug.yml` hoặc
   `feature.yml`).
2. Tạo nhánh từ `main`: `feat/<mô-tả-ngắn>` cho tính năng mới, `fix/<mô-tả-ngắn>`
   cho sửa lỗi.
3. Viết test trước khi viết mã (xem mục Kiểm thử bên dưới).
4. Mở Pull Request theo [mẫu PR](.github/pull_request_template.md), điền đủ
   checklist.
5. Review trước khi merge. CI ([.github/workflows/ci.yml](.github/workflows/ci.yml))
   phải xanh — chạy `pytest -v` trên PostgreSQL 16 thật.

## Commit message — Conventional Commits

Định dạng: `<type>: <mô tả ngắn gọn bằng tiếng Việt>`.

Các tiền tố (type) đang dùng trong dự án:

| Type | Dùng khi |
|---|---|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa lỗi |
| `docs` | Chỉ thay đổi tài liệu |
| `chore` | Việc lặt vặt không ảnh hưởng hành vi (đổi cấu hình, dọn dẹp) |
| `build` | Thay đổi cách dịch/đóng gói (Dockerfile, pyproject.toml) |
| `ci` | Thay đổi cấu hình CI |

Ví dụ: `feat: thêm bước gộp trùng cho tác giả trùng tên`.

## Chuẩn mã (Coding standards)

- Python 3.12+.
- Chỉ dùng thư viện chuẩn (stdlib) và `psycopg` để kết nối PostgreSQL —
  **không dùng ORM** (SQLAlchemy, Django ORM, ...). Nối tác giả, gộp trùng và
  truy vết xuất xứ dữ liệu cần truy vấn SQL trực tiếp trên mô hình quan hệ;
  một lớp ORM ở giữa sẽ che mất đúng phần cần kiểm soát nhất.
- Tên bảng, cột và giá trị trạng thái phải viết đúng chính tả theo đặc tả
  trong [docs/ba/17-mo-hinh-du-lieu.md](docs/ba/17-mo-hinh-du-lieu.md) —
  không tự đặt tên khác đi.
- Mỗi tệp mới có phần mở rộng `.py`, `.sql`, `.sh`, `.yml`, `.yaml` phải có
  header SPDX ở hai dòng đầu — dùng `--` cho `.sql`, `#` cho các loại còn lại
  (xem [docs/LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md) §3):

  ```python
  # Copyright (c) 2026 ICTU-CRIS contributors
  # SPDX-License-Identifier: Apache-2.0
  ```

  Thiếu header bị chặn tự động bởi `tests/test_spdx.py`.

## Kiểm thử (Testing)

- `pytest` chạy trên **PostgreSQL 16 thật** qua `TEST_DATABASE_URL` — không
  mock cơ sở dữ liệu.
- Theo TDD: viết test thất bại trước, viết mã tối thiểu để test qua, sau đó
  refactor.
- Chạy `pytest -v` trước khi mở PR; xem [BUILDING.md](BUILDING.md) §5 để
  dựng CSDL kiểm thử.

## Tài liệu BA đi cùng thay đổi phạm vi (PR-07)

Nếu PR đổi phạm vi nghiệp vụ — thêm/bớt chức năng, đổi luồng duyệt, đổi mô
hình dữ liệu — phải cập nhật tài liệu tương ứng trong
[docs/ba/](docs/ba/00-README.md) trong cùng PR đó. Đây là quy tắc PR-07, có
trong checklist của [mẫu PR](.github/pull_request_template.md).

## Dữ liệu cá nhân (Personal data)

- Không đưa dữ liệu cá nhân thật (số điện thoại, ngày sinh giảng viên, ...)
  vào repo dưới bất kỳ hình thức nào: mã nguồn, fixture, ảnh chụp màn hình,
  log đính kèm issue hoặc PR.
- Fixture kiểm thử trong `tests/fixtures/` phải ẩn danh thông tin cá nhân
  giảng viên (tên, email, điện thoại, ngày sinh); tên tác giả trên fixture
  bài báo là dữ liệu thư mục công khai nên được giữ nguyên.
- Dữ liệu thật thu thập từ `khao-sat-nguon/` nằm ngoài repo (xem
  `.gitignore`) và không bao giờ được commit.

## Giấy phép (License)

Đóng góp vào dự án đồng nghĩa với việc đồng ý phát hành mã theo Apache-2.0
(xem [LICENSE](LICENSE), [NOTICE](NOTICE),
[docs/LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md)).

## Quy trình PR

- Tiêu đề theo Conventional Commits: `type(scope): mô tả` — `feat`, `fix`, `docs`,
  `chore`, `ci`, `build`, `refactor`, `test`, `style`, `perf`, `revert`. Workflow
  **PR Check** chặn tiêu đề sai, thân rỗng, và PR không liên kết issue (`closes #N`);
  gắn nhãn `skip-issue-link` cho sửa nhỏ không cần issue.
- Nhãn được gắn tự động theo đường dẫn (`.github/labeler.yml`).
- Issue chỉ đóng qua PR merge; đóng tay sẽ được mở lại (trừ `wontfix`/`invalid`/`duplicate`).
- Không có dòng ghi công AI (`Co-Authored-By`…) trong thông điệp commit.
- Tuỳ chọn: `pip install pre-commit && pre-commit install` để kiểm header SPDX, YAML,
  lỗi cú pháp trước khi commit.

## Quy trình phát hành

1. Cập nhật `version` trong `pyproject.toml` và `CITATION.cff`; chuyển mục
   `[Unreleased]` của `CHANGELOG.md` thành `[X.Y.Z] - YYYY-MM-DD`; viết
   `docs/release-notes/vX.Y.Z.md`.
2. Commit, rồi tag có chú thích: `git tag -a vX.Y.Z -m "..."` và `git push origin main vX.Y.Z`.
3. Workflow **Release** kiểm phiên bản khớp tag, dựng sdist (`.tar.gz`) + wheel, tạo
   GitHub Release với ghi chú từ tệp release-notes cộng danh sách thay đổi tự sinh, đính
   kèm gói và `SHA256SUMS`. Workflow **Docker** đẩy `ghcr.io/maiychrus25/cris:X.Y.Z`,
   `:X.Y`, `:latest`.
4. Tag có dấu gạch (`v0.2.0-rc1`) được đánh dấu *pre-release*.
