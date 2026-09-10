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

## 3. Dịch vụ ngoài (External Services)

| Dịch vụ | Phiên bản/Image | Giấy phép | Ghi chú |
|---|---|---|---|
| PostgreSQL | 16, image `postgres:16` | PostgreSQL License | Chạy như dịch vụ ngoài (container), không nhúng mã vào repo |

## 4. Mã nguồn nội bộ tương tự thư viện (First-party code)

`cris/source/repository.py` chứa các hàm parser được sao chép từ chính
`khao-sat-nguon/harvest.py` của dự án. Đây là **mã nguồn của chính dự án
(first-party)**, không phải mã nguồn của bên thứ ba, nên không thuộc phạm vi
điều chỉnh của chính sách thư viện ở trên.
