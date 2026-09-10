# Dịch và chạy ICTU-CRIS từ mã nguồn (Building from source)

Tài liệu này mô tả cách dịch (build), cấu hình và chạy ICTU-CRIS hoàn toàn từ
mã nguồn, không phụ thuộc dịch vụ đóng hoặc image không rõ nguồn gốc.

## 1. Nguyên tắc (Principles)

- **Cấu hình qua biến môi trường (`.env`), không sửa mã nguồn**: mọi tham số
  vận hành (kết nối cơ sở dữ liệu, ...) được truyền qua biến môi trường
  (`DATABASE_URL`, `TEST_DATABASE_URL`); không cần sửa file trong `cris/` để
  đổi môi trường chạy.
- **Toàn bộ công cụ dịch/đóng gói đều là phần mềm nguồn mở**: trình biên dịch
  Python là CPython (PSF License), trình quản lý gói là `pip`, công cụ đóng
  gói container là Docker CE (Apache-2.0). Không có bước nào phụ thuộc công
  cụ độc quyền.
- Giấy phép mã nguồn: Apache-2.0 (xem `LICENSE`, `NOTICE`,
  `docs/LICENSE_NOTICE.md`).

## 2. Yêu cầu môi trường (Requirements)

- Python 3.12+ (nếu dịch trên máy phát triển).
- Docker Engine + Docker Compose plugin (`docker compose`) — nếu dịch/chạy
  bằng container.
- Không cần quyền root, không cần dịch vụ mạng ngoài Docker Hub và
  `repository.ictu.edu.vn` (chỉ khi chạy `sync`).

## 3. Cách 1: Dịch và chạy bằng Docker (Build and run with Docker)

Trên đường Docker, `docker-compose.yml` tự cấp `DATABASE_URL` trỏ tới
service `db` (xem service `app`) — không cần tạo `.env`; `.env` chỉ dùng cho
cách 2 (venv) ở mục 4. Muốn đổi CSDL khi chạy Docker thì ghi đè biến môi
trường trên từng lệnh, ví dụ: `docker compose run --rm -e DATABASE_URL=... app <lệnh>`.

```bash
docker compose up -d db
docker compose build app
docker compose run --rm app migrate
docker compose run --rm app seed
docker compose run --rm app sync
docker compose run --rm app people
docker compose run --rm app normalize
docker compose run --rm app link
docker compose run --rm app dedup
docker compose run --rm app quality
```

Ghi chú:

- `docker compose up -d db` khởi tạo Postgres 16 và (ở lần khởi động đầu
  tiên) tạo sẵn cơ sở dữ liệu `cris` và `cris_test` (qua
  `docker/initdb/01-test-db.sql`).
- `app` là service riêng (dùng `profiles: ["app"]`) nên không ảnh hưởng tới
  `docker compose up -d db`; image `app` chỉ chứa mã nguồn `cris/`, không
  cần checkout toàn bộ repo để chạy — chỉ cần `Dockerfile` build từ ngữ cảnh
  có `pyproject.toml`, `LICENSE`, `NOTICE`, và thư mục `cris/`.
- `docker compose run --rm app sync` mặc định đồng bộ toàn bộ các loại tài
  liệu (`giang-vien bai-bao luan-an luan-van do-an hoc-lieu-so`); có thể giới
  hạn, ví dụ: `docker compose run --rm app sync giang-vien`.
- `quality --json` in báo cáo chất lượng dạng JSON một dòng, phù hợp để đưa
  vào giám sát tự động; không có `--json` thì in JSON dạng thu gọn nhiều dòng.

## 4. Cách 2: Máy phát triển (venv, không dùng container)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # cần cho cách 2 (venv); Docker ở mục 3 không cần bước này
docker compose up -d db   # hoặc trỏ DATABASE_URL tới Postgres 16 tự quản lý
export $(grep -v '^#' .env | xargs)
python -m cris migrate
python -m cris seed
python -m cris sync
python -m cris people
python -m cris normalize
python -m cris link
python -m cris dedup
python -m cris quality
```

## 5. Kiểm thử sau khi dịch (Testing the build)

```bash
docker compose up -d db     # cần cho lần đầu để tạo cris_test
export TEST_DATABASE_URL=postgresql://cris:cris@localhost:5432/cris_test
pytest -v
```

- Cơ sở dữ liệu kiểm thử `cris_test` được tạo bởi
  `docker/initdb/01-test-db.sql` khi service `db` khởi động lần đầu (không
  tự tạo nếu volume `cris_pg` đã tồn tại từ trước — cần xoá volume để tạo
  lại nếu thiếu).
- `TEST_DATABASE_URL` có giá trị mặc định trong `tests/conftest.py`
  (`postgresql://cris:cris@localhost:5432/cris_test`) nếu không đặt biến môi
  trường; `.env.example` đã có sẵn giá trị này.

## 6. Chạy giao diện web (Running the web interface)

Sau khi đã `migrate` và có dữ liệu, mở giao diện hàng đợi xác nhận và tra cứu:

```bash
python -m cris serve                      # mặc định http://127.0.0.1:8000
python -m cris serve --host 0.0.0.0 --port 8080
```

Giao diện gồm: hàng đợi liên kết tác giả (`/doi-soat/tac-gia`), hàng đợi nghi
trùng (`/doi-soat/trung-lap`), tra cứu công trình (`/tra-cuu`), hồ sơ công bố
giảng viên, và báo cáo chất lượng dữ liệu (`/chat-luong-du-lieu`).

Mọi quyết định đều được ghi kèm người thực hiện, nên cần ít nhất một người dùng
có vai trò `rd_officer`. Chưa có thì trang trả về `503` kèm hướng dẫn:

```sql
INSERT INTO app_user(email, display_name, roles)
VALUES ('ten@ictu.edu.vn', 'Tên hiển thị', ARRAY['rd_officer']);
```

**Chưa có đăng nhập thật.** Bản này chạy với một người dùng mặc định (hoặc header
`X-CRIS-User: <id>`); xác thực và phân quyền theo đơn vị là NFR-01 và NFR-02,
chưa triển khai. Máy chủ dùng `wsgiref` — máy chủ phát triển, **không triển khai
lên mạng công khai**.

## 7. Bật AI (Enabling the AI features)

AI là **tuỳ chọn**. Mặc định `CRIS_AI_PROVIDER=none`: mọi chức năng khác chạy bình
thường, các chỗ gợi ý hiện "AI chưa bật". Để bật mô hình cục bộ (chạy CPU, không cần
GPU, không gọi ra ngoài sau khi đã tải):

```bash
pip install -e ".[ai]"            # thêm onnxruntime, tokenizers, numpy — xem DEPENDENCIES.md
python -m cris ai download        # tải mô hình 118 MB + tokenizer 17 MB vào ~/.cache/ictu-cris/models,
                                  # kiểm SHA-256 trước khi dùng; chỉ tải một lần
export CRIS_AI_PROVIDER=local     # hoặc đặt trong .env
python -m cris ai embed           # sinh vector cho toàn bộ công trình (~3 phút trên CPU 4 nhân)
python -m cris ai status          # provider đang dùng, số vector đã có
```

Đổi thư mục mô hình bằng `CRIS_AI_MODEL_DIR`. Với Docker, mount thư mục đó vào container
để không tải lại mỗi lần dựng.

Kiểm thử mô hình thật: `pytest -m slow` (tự bỏ qua nếu chưa tải mô hình). CI chạy
`pytest -m "not slow"` nên không cần mô hình.

## 8. Lưu ý khi đồng bộ (Sync notes)

- Mỗi yêu cầu tới kho nguồn được giãn cách **0,35 giây**
  (`DELAY` trong `cris/source/repository.py`) để tránh gây tải cho máy chủ
  nguồn.
- Một lần đồng bộ đầy đủ đọc khoảng **8.000 trang chi tiết**, tương đương
  khoảng **50 phút**. Có thể giới hạn phạm vi bằng cách truyền tên loại tài
  liệu cho `sync` (`giang-vien`, `bai-bao`, `luan-an`, `luan-van`, `do-an`,
  `hoc-lieu-so`) hoặc dùng `--no-details` để bỏ qua bước đọc trang chi tiết.

## 9. Đã kiểm chứng (Verified)

Các lệnh sau đã chạy thành công từ image `app` dịch bằng `docker compose
build app`, không cần thư mục mã nguồn trên máy chạy:

```
$ docker compose run --rm app migrate
[]

$ docker compose run --rm app quality --json
{"works": 0, ... "last_sync": {...}}
```

`migrate` trả về danh sách rỗng vì mọi migration đã được áp dụng từ trước;
`quality --json` in báo cáo chất lượng hiện tại của cơ sở dữ liệu.
