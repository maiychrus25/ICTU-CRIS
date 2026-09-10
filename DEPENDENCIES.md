# Chính sách thư viện (Dependencies Policy)

## 1. Cam kết (Bundling policy)

- Dự án **không đính kèm mã nguồn của thư viện bên thứ ba vào repo**. Toàn bộ
  thư viện được cài đặt qua `pip` từ PyPI, theo khai báo tại `pyproject.toml`.
- Dự án **không sửa đổi mã nguồn của bất kỳ thư viện nào**; mọi thư viện được
  dùng nguyên trạng như được phát hành trên PyPI.
- Việc đóng gói và phân phối image Docker của dự án tuân thủ LGPL §4 đối với
  `psycopg`: thư viện được cài đặt nguyên trạng từ PyPI (không đóng gói
  tĩnh, không sửa) và có thể thay thế bằng bản build khác của người dùng
  cuối theo đúng điều khoản LGPL.

## 2. Thư viện Python (Python dependencies)

### Thư viện chạy (runtime)

| Thư viện | Phiên bản | Giấy phép | Mục đích |
|---|---|---|---|
| `psycopg[binary]` | `>=3.2,<4` | LGPL-3.0-or-later | Driver kết nối PostgreSQL cho mã đồng bộ/chuẩn hoá dữ liệu |
| `psycopg-binary` (kéo theo bởi `psycopg[binary]`) | theo `psycopg` | LGPL-3.0-or-later | Bản build sẵn của driver, đóng gói `libpq` |
| ↳ `libpq` (đóng gói trong `psycopg-binary`) | theo bản build | PostgreSQL License | Thư viện client PostgreSQL, dùng nguyên trạng, không sửa |
| ↳ OpenSSL (đóng gói trong `psycopg-binary`) | theo bản build | Apache-2.0 | TLS cho `libpq`, dùng nguyên trạng, không sửa |

### Thư viện phát triển (dev)

| Thư viện | Phiên bản | Giấy phép | Mục đích |
|---|---|---|---|
| `pytest` | `>=8,<9` | MIT | Chạy bộ kiểm thử tự động |

## 3. Dịch vụ ngoài (External Services)

| Dịch vụ | Phiên bản/Image | Giấy phép | Ghi chú |
|---|---|---|---|
| PostgreSQL | 16, image `postgres:16` | PostgreSQL License | Chạy như dịch vụ ngoài (container), không nhúng mã vào repo |

## 4. Mã nguồn nội bộ tương tự thư viện (First-party code)

`cris/source/repository.py` chứa các hàm parser được sao chép từ chính
`khao-sat-nguon/harvest.py` của dự án. Đây là **mã nguồn của chính dự án
(first-party)**, không phải mã nguồn của bên thứ ba, nên không thuộc phạm vi
điều chỉnh của chính sách thư viện ở trên.
