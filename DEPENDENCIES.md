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
| `fastapi` | `>=0.115,<1` | MIT | Router `/api/*`, OpenAPI tại `/docs`, lớp mỏng gọi vào tầng nghiệp vụ |
| `starlette` (kéo theo bởi `fastapi`) | theo `fastapi` | BSD-3-Clause | ASGI nền cho FastAPI: routing, middleware, `TestClient` |
| `uvicorn` | `>=0.30,<1` | BSD-3-Clause | Máy chủ ASGI chạy bởi `python -m cris serve` |
| `pydantic` | `>=2.7,<3` | MIT | Kiểu dữ liệu vào/ra của API (`cris/api/schemas.py`) |
| `python-multipart` | `>=0.0.9,<1` | MIT | FastAPI phân tích `multipart/form-data` cho tải tệp minh chứng lên (`UploadFile`, `POST /api/declarations/{id}/evidence/file`) |

Tầng nghiệp vụ (`cris/*.py` ngoài `cris/api/`) vẫn chỉ phụ thuộc `psycopg`; bốn
thư viện web ở trên chỉ phục vụ lớp API JSON mỏng gọi vào tầng đó.

### Thư viện phát triển (dev)

| Thư viện | Phiên bản | Giấy phép | Mục đích |
|---|---|---|---|
| `pytest` | `>=8,<10` | MIT | Chạy bộ kiểm thử tự động |
| `httpx` | `>=0.27,<1` | BSD-3-Clause | `fastapi.testclient.TestClient` gọi API trong test; không chạy trong sản phẩm |

### Thư viện tuỳ chọn cho AI (`pip install -e ".[ai]"`)

Chỉ cần khi `CRIS_AI_PROVIDER=local`. Provider `none` (mặc định) và `fake` (kiểm thử)
chạy hoàn toàn không có ba thư viện này; mã trong `cris/ai/local.py` import chúng bên
trong lớp, nên gói lõi không kéo theo. Cả ba dùng nguyên trạng từ PyPI, không sửa.

| Thư viện | Phiên bản | Giấy phép | Kích thước cài | Mục đích |
|---|---|---|---|---|
| `onnxruntime` | `>=1.17,<2` (thử: 1.29.0) | MIT | ~66 MB | Chạy mô hình embedding ONNX trên CPU |
| `tokenizers` | `>=0.15,<1` (thử: 0.23.2) | Apache-2.0 | ~12 MB | Tách token theo `tokenizer.json` của mô hình |
| `numpy` | `>=1.26,<3` (thử: 2.5.3) | BSD-3-Clause (kèm 0BSD, MIT, Zlib, CC0 cho phần con) | ~43 MB | Mean pooling, chuẩn hoá, tìm k gần nhất, k-means |

### Mô hình AI (tải một lần, không đưa vào repo)

| Mục | Giá trị |
|---|---|
| Mô hình | `paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers) |
| Bản dùng | ONNX lượng tử hoá 8-bit, repo `Xenova/paraphrase-multilingual-MiniLM-L12-v2` |
| Giấy phép | Apache-2.0 (theo mô hình gốc `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) |
| Kích thước | `model_quantized.onnx` 118 MB + `tokenizer.json` 17 MB |
| Chiều vector | 384; hỗ trợ 50+ ngôn ngữ, có tiếng Việt |
| SHA-256 | `model_quantized.onnx` `66fc00f5f29afcaff34092e1bdd20008ca3918265a82fb9695a551e510cc4ebc` · `tokenizer.json` `b60b6b43406a48bf3638526314f3d232d97058bc93472ff2de930d43686fa441` — mã kiểm băm trước khi dùng |
| Nơi lưu | `CRIS_AI_MODEL_DIR`, mặc định `~/.cache/ictu-cris/models/paraphrase-multilingual-MiniLM-L12-v2/`; tải bằng `python -m cris ai download` |
| Đo 10/09/2026 | CPU 4 nhân: 64 đoạn ~200 token trong 1,8 s → toàn kho 5.709 công trình ≈ 3 phút |

Không có thư viện nào trong nhóm này chứa mã bên thứ ba được đính kèm vào repo; mô hình
là dữ liệu tải về, không phải mã nguồn, và không bị sửa.

### Công cụ chỉ dùng trong CI / phát hành (không nằm trong sản phẩm)

| Công cụ | Giấy phép | Dùng ở |
|---|---|---|
| `ruff` | MIT | lint trong CI và pre-commit |
| `pip-audit` | Apache-2.0 | quét lỗ hổng trong CI |
| `build` | MIT | dựng sdist/wheel trong CI và Release |
| GitHub Actions: `actions/checkout`, `setup-python`, `upload-artifact`, `download-artifact`, `labeler` | MIT | workflow |
| `docker/setup-buildx-action`, `login-action`, `metadata-action`, `build-push-action` | Apache-2.0 | workflow Docker |
| `softprops/action-gh-release` | MIT | tạo GitHub Release |

## 3. Thư viện JavaScript/TypeScript (frontend, `frontend/package.json`)

Giao diện dựng tĩnh bằng `npm ci && npm run build` (không có mã Node chạy lúc
sản xuất — chỉ HTML/CSS/JS tĩnh do FastAPI phục vụ). Toàn bộ thư viện cài qua
`npm` từ npm registry, không đính kèm mã nguồn bên thứ ba vào repo, không sửa.

### Thư viện chạy (runtime — vào trong bản xuất tĩnh)

| Thư viện | Giấy phép | Mục đích |
|---|---|---|
| `next` | MIT | Framework React, xuất tĩnh (`output: "export"`) |
| `react` / `react-dom` | MIT | Thư viện UI nền |
| `@tanstack/react-query` | MIT | Gọi API, cache, trạng thái tải/lỗi |
| `@tanstack/react-table` | MIT | Bảng dữ liệu (tra cứu, hàng đợi, nhật ký) |
| `recharts` | MIT | Biểu đồ (tổng quan cho lãnh đạo) |
| `lucide-react` | ISC | Bộ icon |
| `shadcn/ui` (mã sinh vào `components/ui/`, không phải gói npm chạy) | MIT | Thành phần giao diện nền (Button, Dialog, Table, …) |
| `tailwindcss` | MIT | CSS tiện ích |
| `next-themes` | MIT | Chuyển sáng/tối |
| `sonner` | MIT | Toast thông báo |
| `@base-ui/react` | MIT | Thành phần không giao diện (primitives) cho shadcn/ui |
| `class-variance-authority` | Apache-2.0 | Biến thể className có kiểu |
| `cn` | MIT (xem `node_modules/cn/package.json`) | Gộp className có điều kiện |

### Thư viện phát triển (dev — không vào bản xuất tĩnh)

| Thư viện | Giấy phép | Mục đích |
|---|---|---|
| `typescript` | Apache-2.0 | Kiểm kiểu tĩnh (`tsc --noEmit`) |
| `eslint` (+ `eslint-config-next`) | MIT | Lint |
| `@playwright/test` | Apache-2.0 | Test đầu-cuối trên dữ liệu mẫu |
| `openapi-typescript` | MIT | Sinh kiểu TypeScript từ OpenAPI của FastAPI |

## 4. Dịch vụ ngoài (External Services)

| Dịch vụ | Phiên bản/Image | Giấy phép | Ghi chú |
|---|---|---|---|
| PostgreSQL | 16, image `postgres:16` | PostgreSQL License | Chạy như dịch vụ ngoài (container), không nhúng mã vào repo |

## 5. Mã nguồn nội bộ tương tự thư viện (First-party code)

`cris/source/repository.py` chứa các hàm parser được sao chép từ chính
`khao-sat-nguon/harvest.py` của dự án. Đây là **mã nguồn của chính dự án
(first-party)**, không phải mã nguồn của bên thứ ba, nên không thuộc phạm vi
điều chỉnh của chính sách thư viện ở trên.
