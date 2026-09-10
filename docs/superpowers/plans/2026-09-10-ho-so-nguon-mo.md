# Hồ sơ nguồn mở (giấy phép, dịch từ nguồn, tài liệu, giao tiếp) — Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đưa kho ICTU-CRIS lên chuẩn dự án nguồn mở chuyên nghiệp: giấy phép ghi trong từng tệp, tài liệu dịch từ mã nguồn, chính sách thư viện, nhật ký thay đổi, hướng dẫn đóng góp, mẫu issue và PR, Dockerfile, CI, README định vị theo HPDI; không nhắc tên sự kiện bên ngoài nào trong tài liệu.

**Architecture:** Chỉ thêm tệp tài liệu, cấu hình và một test quét header; mã ứng dụng không đổi hành vi. Chủ sở hữu bản quyền: `ICTU-CRIS contributors`. Giấy phép: Apache-2.0. Ngôn ngữ: tiếng Việt, thuật ngữ tiếng Anh chuẩn để trong ngoặc.

**Tech Stack:** Python 3.12, pytest, Docker, GitHub Actions. Không thêm thư viện.

**Spec:** Chuẩn dự án nguồn mở sáu mục (kho công khai; giấy phép OSI có header từng tệp, thông báo mục đích, toàn văn; bản phát hành semver `.tar.gz`; dịch từ nguồn có BUILDING.md, cấu hình qua `.env`, chạy được ngoài thư mục nguồn; thư viện có DEPENDENCIES.md, không đính kèm, không sửa; tài liệu có bug tracker, CHANGELOG, README).

## Global Constraints

- Header SPDX đúng hai dòng, đặt ở đầu tệp (sau shebang nếu có):
  - Python, shell, YAML: `# Copyright (c) 2026 ICTU-CRIS contributors` và `# SPDX-License-Identifier: Apache-2.0`
  - SQL: `-- Copyright (c) 2026 ICTU-CRIS contributors` và `-- SPDX-License-Identifier: Apache-2.0`
- Không đổi hành vi mã trong `cris/` và `khao-sat-nguon/`; chỉ thêm header.
- Không nhắc tên sự kiện bên ngoài nào ở bất kỳ tệp nào.
- Không đưa dữ liệu thật hay thông tin cá nhân vào repo; fixture đã ẩn danh là giới hạn.
- Mọi tài liệu mới viết tiếng Việt; tiêu đề có thuật ngữ Anh trong ngoặc khi là thuật ngữ chuẩn.
- Tệp cấu hình mẫu là `.env.example`; không hướng dẫn sửa mã để cấu hình.

---

## Cấu trúc tệp

```
LICENSE                          # đã có
NOTICE                           # tên dự án, chủ sở hữu, giấy phép (Apache khuyến nghị)
BUILDING.md
DEPENDENCIES.md
CHANGELOG.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
Dockerfile
docker-compose.yml               # sửa: thêm service app dùng Dockerfile
docs/LICENSE_NOTICE.md
.github/ISSUE_TEMPLATE/bug.yml
.github/ISSUE_TEMPLATE/feature.yml
.github/pull_request_template.md
.github/workflows/ci.yml
tests/test_spdx.py
README.md                        # viết lại
docs/ba/15-project-rules.md      # sửa Q-24 và §15.5 (bỏ khung "lịch đồ án")
```

---

### Task 1: Header SPDX cho mọi tệp mã và test quét

**Files:**
- Modify: mọi tệp `.py`, `.sql`, `.sh`, `.yml`, `.yaml` do git theo dõi (35 tệp tại thời điểm lập kế hoạch, gồm `cris/`, `tests/`, `khao-sat-nguon/`, `docker/`, `docker-compose.yml`)
- Create: `tests/test_spdx.py`, `NOTICE`

**Interfaces:**
- Produces: test `test_spdx.py` chạy trong CI, thất bại khi có tệp mã thiếu header.

- [ ] **Step 1: Viết test (thất bại trước)**

`tests/test_spdx.py`:

```python
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXT = {".py", ".sql", ".sh", ".yml", ".yaml"}
COMMENT = {".sql": "--"}

def tracked_source_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split() if pathlib.Path(p).suffix in EXT]

def test_every_source_file_has_spdx_header():
    missing = []
    for path in tracked_source_files():
        c = COMMENT.get(path.suffix, "#")
        head = path.read_text(encoding="utf-8").splitlines()[:4]
        want1 = f"{c} Copyright (c) 2026 ICTU-CRIS contributors"
        want2 = f"{c} SPDX-License-Identifier: Apache-2.0"
        if want1 not in head or want2 not in head:
            missing.append(str(path.relative_to(ROOT)))
    assert missing == [], "thiếu header SPDX: " + ", ".join(missing)
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `pytest tests/test_spdx.py -v`
Expected: FAIL, thông báo liệt kê 35 tệp.

- [ ] **Step 3: Thêm header bằng script một lần**

```bash
python3 - <<'EOF'
import pathlib, subprocess
ROOT = pathlib.Path(".")
files = [p for p in subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
         if pathlib.Path(p).suffix in {".py",".sql",".sh",".yml",".yaml"}]
for f in files:
    p = pathlib.Path(f); c = "--" if p.suffix == ".sql" else "#"
    text = p.read_text(encoding="utf-8")
    if "SPDX-License-Identifier" in text.splitlines()[:4].__str__():
        continue
    hdr = f"{c} Copyright (c) 2026 ICTU-CRIS contributors\n{c} SPDX-License-Identifier: Apache-2.0\n"
    if text.startswith("#!"):
        first, rest = text.split("\n", 1)
        text = first + "\n" + hdr + rest
    else:
        text = hdr + text
    p.write_text(text, encoding="utf-8")
    print("header:", f)
EOF
```

Tệp rỗng (`cris/__init__.py`, `cris/source/__init__.py`) nhận đúng hai dòng header. Với `khao-sat-nguon/*.py` chỉ thêm header, không đổi dòng nào khác.

`NOTICE`:

```
ICTU-CRIS
Copyright (c) 2026 ICTU-CRIS contributors

Phần mềm này được cấp phép theo Apache License 2.0; xem tệp LICENSE.
Tài liệu định hướng phương pháp tham chiếu bộ sách DX-OS (opendigitransform.gitbook.io/dx-os),
giấy phép CC BY 4.0, chỉ được trích dẫn, không bao gồm mã hay nội dung của tài liệu đó.
```

- [ ] **Step 4: Chạy toàn bộ test, xác nhận đạt**

Run: `pytest -v`
Expected: `test_spdx.py` PASS và toàn bộ suite trước đó vẫn PASS (không đổi hành vi).

- [ ] **Step 5: Commit**

```bash
git add -A cris tests khao-sat-nguon docker docker-compose.yml NOTICE
git commit -m "chore: header SPDX Apache-2.0 cho mọi tệp mã, test quét header, NOTICE"
```

---

### Task 2: Thông báo giấy phép và chính sách thư viện

**Files:**
- Create: `docs/LICENSE_NOTICE.md`, `DEPENDENCIES.md`

- [ ] **Step 1: Viết `docs/LICENSE_NOTICE.md`** với đúng bốn mục:
  1. Mục đích chọn Apache-2.0: cho phép trường, đơn vị khác dùng và sửa kể cả trong dịch vụ nội bộ; có điều khoản cấp quyền bằng sáng chế; yêu cầu giữ NOTICE; tương thích rộng với thư viện.
  2. Ma trận tương thích, một bảng: `psycopg 3` (LGPL-3.0-or-later, dùng như thư viện, không sửa, tương thích); `PostgreSQL 16` (PostgreSQL License, tương thích); `pytest` (MIT, chỉ phát triển); `Docker` (Apache-2.0); `Python 3.12` (PSF); bộ sách DX-OS (CC BY 4.0, chỉ trích dẫn trong tài liệu, ghi công tác giả).
  3. Quy định header từng tệp: hai dòng như Global Constraints, ví dụ cho `.py` và `.sql`, và nêu test `tests/test_spdx.py` chặn thiếu header.
  4. Dữ liệu: dữ liệu kéo từ kho công khai của trường không thuộc giấy phép này; repo chỉ chứa fixture đã ẩn danh; dữ liệu thật nằm ngoài repo theo `.gitignore`.

- [ ] **Step 2: Viết `DEPENDENCIES.md`** với ba mục: cam kết không đính kèm mã thư viện vào repo (cài qua `pip` từ PyPI theo `pyproject.toml`), không sửa mã thư viện; bảng thư viện chạy (`psycopg[binary]>=3.2,<4`) và phát triển (`pytest>=8,<9`) kèm giấy phép và mục đích; dịch vụ ngoài (PostgreSQL 16 qua image `postgres:16`); ghi rõ `cris/source/repository.py` chứa bản sao parser từ chính `khao-sat-nguon/harvest.py` của dự án, không phải mã bên thứ ba.

- [ ] **Step 3: Commit**

```bash
git add docs/LICENSE_NOTICE.md DEPENDENCIES.md
git commit -m "docs: thông báo mục đích giấy phép, ma trận tương thích, chính sách thư viện"
```

---

### Task 3: Dockerfile, dịch từ nguồn, BUILDING.md

**Files:**
- Create: `Dockerfile`, `BUILDING.md`
- Modify: `docker-compose.yml` (thêm service `app`), `.env.example` (thêm `CRIS_IMAGE` nếu cần), `.dockerignore`

- [ ] **Step 1: Viết `Dockerfile`**

```dockerfile
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml LICENSE NOTICE ./
COPY cris ./cris
RUN pip install --no-cache-dir .
ENTRYPOINT ["python", "-m", "cris"]
CMD ["quality"]
```

`.dockerignore`: `.venv`, `.git`, `.superpowers`, `khao-sat-nguon/out`, `tests`, `docs`.

Thêm vào `docker-compose.yml`:

```yaml
  app:
    build: .
    environment:
      DATABASE_URL: postgresql://cris:cris@db:5432/cris
    depends_on: [db]
    profiles: ["app"]
```

- [ ] **Step 2: Kiểm chạy ngoài thư mục nguồn**

```bash
docker compose build app
docker compose run --rm app migrate
docker compose run --rm app quality --json
```

Expected: hai lệnh sau in danh sách migration đã áp (hoặc `[]`) và JSON chất lượng. Image chạy không cần thư mục mã nguồn.

- [ ] **Step 3: Viết `BUILDING.md`** với các mục: nguyên tắc (cấu hình qua `.env`, không sửa mã; công cụ dịch đều nguồn mở: CPython, pip, Docker CE); yêu cầu môi trường; cách 1 Docker (`cp .env.example .env`, `docker compose up -d db`, `docker compose build app`, `docker compose run --rm app migrate`, `seed`, `sync`, `people`, `normalize`, `link`, `dedup`, `quality`); cách 2 máy phát triển (venv, `pip install -e ".[dev]"`, `python -m cris migrate`...); kiểm thử sau khi dịch (`pytest -v`, cần `TEST_DATABASE_URL`); lưu ý giãn cách 0,35 giây khi đồng bộ và thời gian ước tính.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile .dockerignore docker-compose.yml BUILDING.md
git commit -m "build: Dockerfile và hướng dẫn dịch từ mã nguồn"
```

---

### Task 4: CI, mẫu issue và PR, quy tắc ứng xử

**Files:**
- Create: `.github/workflows/ci.yml`, `.github/ISSUE_TEMPLATE/bug.yml`, `.github/ISSUE_TEMPLATE/feature.yml`, `.github/pull_request_template.md`, `CODE_OF_CONDUCT.md`

- [ ] **Step 1: Viết `.github/workflows/ci.yml`**

```yaml
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      db:
        image: postgres:16
        env: { POSTGRES_USER: cris, POSTGRES_PASSWORD: cris, POSTGRES_DB: cris_test }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U cris" --health-interval 5s --health-timeout 5s --health-retries 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
      - run: pytest -v
        env:
          TEST_DATABASE_URL: postgresql://cris:cris@localhost:5432/cris_test
          DATABASE_URL: postgresql://cris:cris@localhost:5432/cris_test
```

- [ ] **Step 2: Mẫu issue** (`bug.yml`, `feature.yml`, dạng GitHub issue forms): tiêu đề, mô tả, bước tái hiện, kết quả mong đợi, phiên bản, môi trường; feature: vấn đề nghiệp vụ, mã chức năng BA liên quan (ví dụ `N-04`), đề xuất.

- [ ] **Step 3: Mẫu PR** (`pull_request_template.md`): mô tả, `Closes #`, loại thay đổi, checklist: đã đọc CONTRIBUTING, tệp mới có header SPDX, `pytest -v` đạt, cập nhật CHANGELOG, cập nhật tài liệu BA nếu đổi phạm vi (PR-07).

- [ ] **Step 4: `CODE_OF_CONDUCT.md`**: Contributor Covenant 2.1 bản tiếng Việt rút gọn, kênh liên hệ là GitHub Issues.

- [ ] **Step 5: Commit**

```bash
git add .github CODE_OF_CONDUCT.md
git commit -m "ci: workflow pytest với Postgres; mẫu issue, PR; quy tắc ứng xử"
```

---

### Task 5: CHANGELOG, CONTRIBUTING, README, sửa khung tài liệu

**Files:**
- Create: `CHANGELOG.md`, `CONTRIBUTING.md`
- Modify: `README.md` (viết lại), `docs/ba/15-project-rules.md` (Q-24, §15.5), `docs/ba/00-README.md` (nguồn đầu vào)

- [ ] **Step 1: `CHANGELOG.md`** theo Keep a Changelog: mục `[Unreleased]` liệt kê những gì nhánh này có: lát cắt S + N (đồng bộ có phiên bản, chuẩn hoá có xuất xứ, nối tác giả, gộp trùng, báo cáo chất lượng, CLI), bộ tài liệu BA 1.0, mô hình dữ liệu 0.1, hồ sơ nguồn mở. Mục `[0.1.0]` để trống với ghi chú sẽ gắn khi phát hành.

- [ ] **Step 2: `CONTRIBUTING.md`**: quy trình (issue → nhánh `feat/` hoặc `fix/` → PR → review); Conventional Commits với các tiền tố đang dùng (`feat`, `fix`, `docs`, `chore`, `build`, `ci`); chuẩn mã (Python 3.12, chỉ stdlib và psycopg, không ORM, tên bảng và trạng thái đúng chữ spec, header SPDX); kiểm thử (pytest với Postgres thật, TDD, không mock CSDL); tài liệu BA cập nhật cùng thay đổi phạm vi (PR-07); dữ liệu cá nhân không được đưa vào repo.

- [ ] **Step 3: Viết lại `README.md`** theo thứ tự: tên và một câu vấn đề; ba số đo chi phối (giữ); định vị theo HPDI: hiện trạng ở không gian H (Excel, email, bản ký sống theo khảo sát đợt 1), ICTU-CRIS xây P (rào chắn kê khai và duyệt) và D (nguồn sự thật, xuất xứ, phiên bản), một phần I có người quyết, trích DX-OS CC BY 4.0; trạng thái hiện tại (lát cắt S + N chạy được, giao diện chưa có); cài đặt nhanh (Docker, ba lệnh); kiến trúc gói `cris` và đường ống bốn bước; tài liệu (bộ BA, mô hình dữ liệu, kế hoạch, BUILDING, DEPENDENCIES, LICENSE_NOTICE, CHANGELOG); đóng góp và bug tracker; giấy phép. Bỏ mọi câu coi kế hoạch ĐATN K21 là lịch dự án; mô tả tệp đó là quy trình đồ án của khoa mà hệ thống hỗ trợ.

- [ ] **Step 4: Sửa `docs/ba/15-project-rules.md`**: Q-24 đổi thành "Lát cắt bản đầu là S + N + T-01/T-02 (đã chốt); giao diện hàng đợi và tra cứu là kế hoạch tiếp theo" và bỏ tham chiếu lịch 09/03–22/05; §15.5 bỏ câu "kế hoạch đồ án đang chạy". Sửa dòng tương ứng trong `docs/ba/00-README.md` nếu có.

- [ ] **Step 5: Kiểm tra không có tên sự kiện bên ngoài**

Run: `git ls-files -z | xargs -0 grep -niE "[o]lp|[o]lympic|cuộc th[i]|[c]ontest|[p]roteus" || true`
Expected: không có kết quả.

- [ ] **Step 6: Commit**

```bash
git add CHANGELOG.md CONTRIBUTING.md README.md docs/ba/15-project-rules.md docs/ba/00-README.md
git commit -m "docs: CHANGELOG, CONTRIBUTING, README định vị HPDI, bỏ khung lịch đồ án"
```

---

### Task 6: Đẩy nhánh, PR, phát hành

Việc hướng ra ngoài; chỉ làm khi người chủ dự án đồng ý từng bước.

- [ ] Push `feat/lat-cat-s-n` và mở PR vào `main` với mô tả theo mẫu; CI phải xanh.
- [ ] Mở ba issue đầu tiên từ danh sách việc để ngoài kế hoạch: nhập Excel khoa (S-06), giao diện hàng đợi (SC-07, SC-08), quét bù phân trang (S-04).
- [ ] Sau khi có giao diện tối thiểu: tag `v0.1.0`, GitHub Release kèm `.tar.gz`, chuyển mục `[Unreleased]` của CHANGELOG thành `[0.1.0]`.

---

## Tự rà

- Sáu tiêu chí chuẩn dự án nguồn mở: (1) Task 6; (2) Task 1, 2, LICENSE đã có; (3) Task 6; (4) Task 3; (5) Task 2; (6) Task 4, 5.
- Không đổi hành vi mã: Task 1 chỉ chèn hai dòng comment; `pytest` toàn bộ là bằng chứng.
- Không nhắc sự kiện bên ngoài: kiểm bằng grep ở Task 5 Step 5.
