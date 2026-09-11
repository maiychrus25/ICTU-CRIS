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

## 6. Chạy giao diện (Running the interface)

Giao diện là ứng dụng Next.js xuất tĩnh (`frontend/`, App Router, TypeScript,
Tailwind, shadcn/ui) gọi vào API FastAPI qua `/api/*`; không có server-render
phía Node lúc chạy — chỉ HTML/CSS/JS tĩnh do FastAPI phục vụ.

### 6.1 Dựng giao diện (build tĩnh)

Yêu cầu Node.js 24.

```bash
cd frontend
npm ci
npm run build            # next build (output: "export") → frontend/out/
```

`frontend/out/` là thư mục FastAPI mount ở `/` khi có (xem `cris/api/app.py`).
Sau khi đã `migrate` và có dữ liệu, chạy API phục vụ cả hai:

```bash
python -m cris serve                      # FastAPI/uvicorn, mặc định http://127.0.0.1:8000
python -m cris serve --host 0.0.0.0 --port 8080
```

`serve` chạy lớp API JSON FastAPI: router `/api/*` (tra cứu, hàng đợi liên kết
tác giả, hàng đợi nghi trùng, đối chiếu đề tài, tổng quan, xuất CSV, nhật ký,
kỳ báo cáo, rà soát trùng đề tài, chất lượng dữ liệu), tài liệu OpenAPI tương
tác tại `/docs`. Bản xuất tĩnh của giao diện Next.js (`frontend/out`), nếu có,
được phục vụ ở `/` — **cùng gốc**, không cần CORS trong sản xuất.

### 6.2 Chạy phát triển hai cổng (dev, hot reload)

```bash
# cổng 1: API
python -m cris serve --port 8000

# cổng 2: Next.js dev server, gọi API ở cổng 8000
cd frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev   # http://localhost:3000
```

`lib/api.ts` đọc `NEXT_PUBLIC_API_BASE` lúc build (rỗng = cùng gốc, dùng khi
chạy sau FastAPI); `CRIS_CORS_ORIGINS` ở phía API mặc định đã mở cho
`http://localhost:3000`. Chạy giao diện độc lập không cần backend bằng dữ liệu
mẫu: `NEXT_PUBLIC_MOCK=1 npm run dev` (đọc `frontend/lib/fixtures.ts`).

### 6.3 Kiểm thử giao diện (Playwright)

```bash
cd frontend
npm run lint && npx tsc --noEmit && npm run build
npx playwright install --with-deps chromium
npx playwright test        # chạy trên dữ liệu mẫu (NEXT_PUBLIC_MOCK), không cần backend
```

### 6.4 Ảnh Docker đa tầng (multi-stage)

`Dockerfile` có hai tầng: `node:24-alpine` dựng `frontend/out/` (`npm ci &&
npm run build`), rồi tầng `python:3.12-slim` sao chép `frontend/out/` vào
`/app/frontend/out` và cài `cris`. Một ảnh duy nhất chạy được mọi lệnh CLI lẫn
`serve` (API + giao diện cùng container, cùng cổng 8000):

```bash
docker build -t ictu-cris:full --build-arg EXTRAS="[ai]" .   # EXTRAS rỗng: không cài AI
docker run --rm -p 8000:8000 -e DATABASE_URL=postgresql://cris:cris@host:5432/cris \
  ictu-cris:full serve --host 0.0.0.0 --port 8000
```

Gói sdist/wheel dựng bằng `python -m build` (xem `release.yml`) **không** đóng
gói `frontend/` — `pyproject.toml` chỉ khai `packages.find include = ["cris*"]`,
nên bản phát hành PyPI-style là mã Python thuần. **Ảnh Docker mới mới là bản
chạy đủ** (API + giao diện): người triển khai dùng ảnh
`ghcr.io/maiychrus25/ictu-cris`, không phải sdist/wheel, để có giao diện.

Mọi quyết định đều được ghi kèm người thực hiện, nên cần ít nhất một người dùng
có vai trò `rd_officer`. Chưa có thì `/api/*` (dùng `link.decide_link` /
`dedup.decide_group`) trả về `503` kèm hướng dẫn:

```sql
INSERT INTO app_user(email, display_name, roles)
VALUES ('ten@ictu.edu.vn', 'Tên hiển thị', ARRAY['rd_officer']);
```

**Phân quyền theo đơn vị (NFR-02) chưa triển khai.** API FastAPI chạy qua
`uvicorn` — cân nhắc kỹ trước khi mở ra mạng công khai; xem mục 6.5 để bật
đăng nhập (NFR-01) và mục 9 "Ràng buộc thiết kế" trong `docs/SRS.md`.

### 6.5 Đăng nhập (login, NFR-01)

Mặc định hệ thống chạy **"chế độ mở"**: chưa `app_user` nào có mật khẩu → API
không bắt buộc đăng nhập, nhận diện người thao tác qua header `X-CRIS-User:
<id>` hoặc người dùng `rd_officer` đầu tiên (hành vi cũ, hợp cho demo và bộ
test). Ngay khi một người dùng được đặt mật khẩu, **toàn hệ thống** chuyển
sang bắt buộc đăng nhập.

```bash
# venv (cách 2) hoặc Docker (cách 1, thay bằng `docker compose run --rm app ...`)
python -m cris user set-password ten@ictu.edu.vn   # hỏi mật khẩu (getpass), hoặc:
CRIS_PASSWORD='...' python -m cris user set-password ten@ictu.edu.vn
python -m cris user list                            # id, email, vai trò, has_password
```

- Mật khẩu băm bằng `hashlib.pbkdf2_hmac` (PBKDF2-HMAC-SHA256, 260.000 vòng,
  salt 16 byte riêng mỗi người) — chỉ thư viện chuẩn, không thêm dependency
  (`cris/auth.py`).
- Cookie phiên `cris_session`: `HttpOnly`, `SameSite=Lax`, hết hạn 12 giờ (gia
  hạn khi dùng, tối đa một lần mỗi 5 phút). Đặt `CRIS_COOKIE_SECURE=1` khi
  chạy sau HTTPS thật để bật thêm cờ `Secure`.
- Đăng nhập sai bị giới hạn 5 lần/5 phút theo email (bộ nhớ tiến trình) → 429.
- `deploy/setup.sh`: đặt `CRIS_ADMIN_PASSWORD` trong `deploy/.env` **trước**
  khi chạy script để bật đăng nhập bắt buộc ngay lúc cài; để trống thì cài đặt
  xong vẫn ở chế độ mở.
- `GET /api/about` trả thêm `auth_required: bool` để giao diện biết đăng nhập
  có bắt buộc không.
- `python -m cris user create --email <email> --name "<tên>" --roles
  faculty_officer,rd_officer [--unit <mã đơn vị>] [--password]` tạo tài
  khoản mới (lát cắt H1); `--roles` phân tách bằng dấu phẩy. Vai trò cấp
  khoa (`faculty_officer`, `faculty_head`) chỉ thấy/thao tác được hồ sơ của
  `--unit` (NFR-02) — nên gán đơn vị ngay lúc tạo, hoặc gán sau bằng
  `python -m cris user set-unit --email <email> --unit <mã đơn vị>`.
- `python -m cris user create-lecturers [--unit <mã đơn vị>] [--dry-run]`
  tạo tài khoản vai `lecturer` (chưa mật khẩu) cho mỗi `person` giảng viên
  có email, khớp theo email nên chạy lại không tạo trùng (lát cắt H3);
  `--dry-run` chỉ đếm, không ghi.
- Ba vai trò dùng trong kịch bản demo (`docs/demo-kich-ban.md`): `rd_officer`
  (phòng KH-CN, toàn trường — kiểm tra và chốt hồ sơ), `faculty_officer`
  (chuyên viên khoa — kê khai và trình khoa duyệt), `faculty_head` (lãnh đạo
  khoa — duyệt hoặc trả hồ sơ về khoa mình). `lecturer` (giảng viên tự kê
  khai công trình của chính mình) dùng chung cơ chế đăng nhập cục bộ này.

### 6.6 Minh chứng dạng tệp (evidence uploads)

Tệp minh chứng kê khai (PDF/ảnh/docx, tối đa 10 MB) lưu dưới `CRIS_DATA_DIR` (mặc định
`/data` trong ảnh Docker, `ENV CRIS_DATA_DIR=/data` ở `Dockerfile`), đường dẫn
`evidence/<id hồ sơ>/<sha256 rút gọn><đuôi>`; loại tệp kiểm bằng chữ ký byte đầu, không
tin phần mở rộng tên tệp gửi lên. Chạy Docker Compose (mục 3): volume `cris_data:/data`
đã khai trong `deploy/docker-compose.yml`, giữ nguyên qua các lần nâng cấp. Chạy venv
(mục 4): đặt `CRIS_DATA_DIR` trỏ tới một thư mục ghi được trước khi `serve`, ví dụ
`export CRIS_DATA_DIR=$(pwd)/.data`.

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
python -m cris ai mentors         # gợi ý người hướng dẫn cho đồ án đang ghi ICTU_TEACHER (cần embed trước)
python -m cris ai status          # provider đang dùng, số vector đã có
```

Đổi thư mục mô hình bằng `CRIS_AI_MODEL_DIR`. Với Docker, mount thư mục đó vào container
để không tải lại mỗi lần dựng — `ai download` ghi vào đúng thư mục này (kể cả khi chạy qua
`docker compose run --rm app ai download`, tránh mất tệp khi container bị xoá sau khi chạy).

`ai mentors` chỉ tìm được ứng viên cho đồ án đã có lượt tên vai `mentor` giữ chỗ; các bản
ghi `do_an` đồng bộ trước khi có nhánh đọc `meta.GVHD` (`cris/normalize.py`) cần chuẩn hoá
lại một lần bằng `python -m cris normalize --redo --doc-type do_an` (không tự chạy lại mặc
định — `normalize_pending` chỉ xử lý phần đang chờ) trước khi chạy `ai mentors`. Chi tiết
thuật toán, ngưỡng và số đo trên dữ liệu thật ở [docs/ai.md](docs/ai.md) mục 6.

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

Ngày 10/09/2026, trên máy phát triển (CPU 4 nhân, không GPU), qua image `python:3.12-slim`
mount thư mục mã nguồn và PostgreSQL 16 từ `docker compose`:

| Việc | Kết quả |
|---|---|
| `pip install -e ".[dev]"` rồi `pytest -q -m "not slow"` | 208 passed, 3 skipped (test `slow` tự bỏ qua khi chưa có mô hình) |
| `pip install -e ".[dev,ai]"` + mô hình đã tải, `pytest -q -m slow` | 3 passed in 9,3 s — 384 chiều, cùng chủ đề gần hơn khác chủ đề, xuyên ngôn ngữ Việt–Anh, 64 đoạn < 30 s |
| `python -m cris ai download` (kiểm SHA-256) rồi `ensure_model(download=False)` | nhận tệp đã có, không tải lại, không ghi |
| `CRIS_AI_PROVIDER=none python -c "import cris.web.wsgi, cris.cli"` | `onnxruntime`, `numpy`, `tokenizers` không nằm trong `sys.modules` |
| `python -m cris serve` rồi gọi 13 route bằng `curl` | trang có dữ liệu 200; id không tồn tại 404; DB chưa có `rd_officer` 503 kèm câu SQL hướng dẫn |
| `python -m cris migrate` trên DB trống | áp `0001`–`0007` liền một lượt |
| Đồng bộ toàn kho `python -m cris sync` (6 loại, đọc cả trang chi tiết) | giảng viên 410, luận án 11, học liệu 2, luận văn 323, bài báo 1.907, **đồ án 5.375/5.375** — tất cả `status=ok`, không cảnh báo lệch số lượng; quét bù S-04 lấy đủ 11 bản ghi phân trang bỏ sót. Toàn bộ ≈ 2 giờ ở 3 yêu cầu/giây |
| `people` → `normalize` → `link` → `dedup` trên dữ liệu thật | 400/410 người (10 hồ sơ trùng ORCID ở nguồn bị từ chối, xem CHANGELOG "Đã biết"); 7.618 công trình; nối tự động 3.135 lượt, hàng đợi 903; 39 nhóm nghi trùng, 15 có cảnh báo đồ án nhóm. Bài báo: 78,8 % nối tự động + 15,9 % chờ xác nhận = 86,6 % có liên kết (mốc nguồn 8 %) |
| `CRIS_AI_PROVIDER=local python -m cris ai embed` trên 7.618 công trình | 679 s ≈ 11 phút, CPU 4 nhân (NFR-40 ≤ 15 phút). Lưu ý: chỉ 210/1.907 bài báo có tóm tắt ở nguồn, phần còn lại embed bằng tiêu đề + từ khoá |
| `ai topics` / `ai suggest` | 40 cụm trên 11.716 từ khoá trong 52 s; 978 gợi ý hàng đợi tác giả + 26 gợi ý nghi trùng trong 8 s |
| `POST /doi-chieu` qua server sống, DB thật, provider `local` | lần đầu 5,07 s (nạp mô hình một lần cho tiến trình), các lần sau 3,28–3,29 s (NFR-41 ≤ 5 s); các trang khác 0,05–0,13 s; 0 traceback |
| `compare_topic` một đề tài thật trên 7.618 vector | 3,25 s kể cả nạp provider (NFR-41 ≤ 5 s). Đề tài "học tiếng Anh cho trẻ khiếm thính, luyện phát âm": top-5 tách đúng hai trục — đồ án luyện phát âm tiếng Anh (*phương pháp: giống*) và đồ án cho người khiếm thính (*đối tượng: giống*) |

`migrate` trả về danh sách rỗng khi mọi migration đã được áp dụng; `quality --json` in
báo cáo chất lượng hiện tại của cơ sở dữ liệu.

Ngày 11/09/2026 (E6 — đóng gói một container, gỡ UI cũ), cùng máy phát triển:

| Việc | Kết quả |
|---|---|
| `docker build -t ictu-cris:full --build-arg EXTRAS="[ai]" .` (Dockerfile đa tầng) | dựng thành công, ảnh 507 MB; `frontend/out/index.html` có trong ảnh |
| `grep -rl 'localhost:8001' /app/frontend/out` trong ảnh | không có kết quả — bản xuất tĩnh gọi API cùng gốc |
| `docker run ... ictu-cris:full serve --host 0.0.0.0 --port 8000` rồi `curl` 11 trang tĩnh (`/`, `/tra-cuu/`, `/tong-quan/`, `/doi-soat/tac-gia/`, `/doi-soat/trung-lap/`, `/doi-chieu/`, `/doi-chieu/ra-soat/`, `/ky-bao-cao/`, `/nhat-ky/`, `/chat-luong-du-lieu/`, `/ve/`) + 3 route API (`/api/health`, `/api/stats`, `/docs`) | tất cả `200`, 0 dòng traceback trong `docker logs` |
| `CRIS_AI_PROVIDER=none python -c "import cris.api.app, cris.cli"` | `onnxruntime`, `numpy`, `tokenizers` không nằm trong `sys.modules` |
| Gỡ `cris/web/` (UI HTML cũ) và `tests/test_web_*.py`, bỏ cờ `--legacy` | `ruff check --select E9,F63,F7,F82` sạch; `pytest -q` **193 passed, 3 skipped** (từ 245 passed, 3 skipped trước khi xoá — đúng bằng 52 test web đã gỡ) |

Ngày 11/09/2026 chiều (lát cắt G — đăng nhập, tìm người, chủ đề, lịch sử đồng bộ, kê
khai), cùng máy phát triển:

| Việc | Kết quả |
|---|---|
| `pytest -q -m "not slow"` sau G1–G3 | **243 passed**, 3 skipped (`slow` tự bỏ qua khi chưa có mô hình) |
| `npx playwright test` (`frontend/e2e/`) | mock (`core-flows.spec.ts`, `NEXT_PUBLIC_MOCK`) **11** kịch bản; thật (`real-backend.spec.ts`, gọi API sống) **9** kịch bản |
| `docker build -t ictu-cris:full --build-arg EXTRAS="[ai]" .` (Dockerfile đa tầng) sau khi thêm `frontend/` cho lát cắt G | dựng thành công, ảnh đa tầng không đổi cấu trúc |
| `python -m cris migrate` trên DB đã có `0001`–`0008` | áp thêm `0009_auth.sql` (`app_user.password_hash`, bảng `session`) |

Ngày 11/09/2026 tối (lát cắt H — duyệt hai cấp theo BA, chỉnh tay có xuất xứ, tìm kiếm
không dấu, giảng viên tự kê khai), cùng máy phát triển:

| Việc | Kết quả |
|---|---|
| `pytest -q -m "not slow"` sau H1–H3 | **292 passed**, 3 skipped (`slow` tự bỏ qua khi chưa có mô hình) |
| `npx playwright test` (`frontend/e2e/`, cấu hình mặc định, dữ liệu mẫu) | mock (`core-flows.spec.ts`) **14** kịch bản |
| `npx playwright test --config=playwright.real.config.ts` (ba project `desktop`/`tablet`/`mobile`) | thật: `real-backend.spec.ts` trên `desktop` **9** + `responsive-accessibility.real.spec.ts` trên `tablet`/`mobile` **2+2** — tổng **13** |
| `python -m cris migrate` trên DB đã có `0001`–`0009` | áp thêm `0010_declaration_states.sql` (mở CHECK `declaration.state` đủ 8 trạng thái) |

Ngày 11/09/2026 đêm (lát cắt I — CI/CD triển khai máy chủ thật, minh chứng dạng tệp, AI
gợi ý người hướng dẫn, hướng dẫn sử dụng trong ứng dụng), cùng máy phát triển:

| Việc | Kết quả |
|---|---|
| `pytest -q -m "not slow"` sau I1–I4 | **322 passed**, 3 skipped (`slow` cần mô hình) |
| `npx playwright test` (cấu hình mặc định, dữ liệu mẫu) | mock: `core-flows.spec.ts` **17** + `user-guide.spec.ts` **1** — tổng **18** kịch bản |
| `npx playwright test --config=playwright.real.config.ts` (ba project `desktop`/`tablet`/`mobile`) | thật: `real-backend.spec.ts` trên `desktop` **9** + `responsive-accessibility.real.spec.ts` trên `tablet`/`mobile` **2+2** — tổng **13** |
| `python -m cris migrate` trên DB đã có `0001`–`0010` | áp thêm `0011_evidence_file.sql` (cột `storage_path`/`size_bytes`/`sha256`/`content_type`/`original_name` của `evidence`) rồi `0012_ai_mentor.sql` (mở CHECK `ai_suggestion.kind` thêm `mentor`, `author_link.confidence` thêm `ai_mentor`) |
| `python -m cris normalize --redo --doc-type do_an` trên 5.375 đồ án thật | ~41,5 s, `{'created': 0, 'updated': 5375, 'skipped': 0}`, tạo đúng **4.621** lượt tên vai `mentor` giữ chỗ (khớp README "Ba số liệu") |
| `python -m cris ai mentors` (mặc định `k=5, min_votes=2, min_score=0.70`) sau khi embed | ~12 s, `scanned=4621 suggested=1381` (**29,9%**) — chi tiết ngưỡng và ví dụ ở [docs/ai.md](docs/ai.md) mục 6 |

## 10. Triển khai máy chủ thật (Production deploy)

`deploy/setup.sh` ở trên là cài **một máy** bằng tay. Máy chủ thật
(`https://cris.ahvlabs.com`) nâng cấp tự động mỗi khi có GitHub Release, qua
`deploy/upgrade.sh` (sao lưu CSDL, kéo/dựng ảnh `-ai`, migrate, kiểm tra
`/api/health`, tự khôi phục nếu lỗi) và `.github/workflows/deploy.yml`. Kiến
trúc, secrets cần tạo, quy trình phát hành và quay lui — xem
[docs/deploy-prod.md](docs/deploy-prod.md).
