<div align="center">

<img src="docs/images/icut-cris-mark.svg" alt="ICTU-CRIS" width="120" />

# ICTU-CRIS

**Một nguồn sự thật cho dữ liệu công bố khoa học — mỗi con số truy ngược được về bản ghi gốc.**

*Hệ thống đồng bộ, chuẩn hoá và đối soát dữ liệu công bố khoa học cho Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên.*

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/maiychrus25/CRIS/ci.yml?style=for-the-badge&label=CI)](https://github.com/maiychrus25/CRIS/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg?style=for-the-badge)](pyproject.toml)
![PostgreSQL 16](https://img.shields.io/badge/postgresql-16-blue.svg?style=for-the-badge)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg?style=for-the-badge)](BUILDING.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

![GitHub stars](https://img.shields.io/github/stars/maiychrus25/CRIS?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/maiychrus25/CRIS?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/maiychrus25/CRIS?style=flat-square)

</div>

<p align="center"><img src="docs/images/duong-ong-du-lieu.svg" alt="Sơ đồ đường ống dữ liệu ICTU-CRIS" width="900"></p>

*Đường ống sáu bước: đồng bộ → chuẩn hoá → định danh tác giả → nối tác giả → gộp trùng → báo cáo chất lượng — mỗi bước ghi qua PostgreSQL, quyết định cuối luôn thuộc về người dùng.*

Bản tương tác (pan/zoom, tra vết quan hệ, đổi sáng/tối): [docs/architecture/duong-ong-du-lieu.html](docs/architecture/duong-ong-du-lieu.html).

## 🌟 Tầm nhìn (Vision)

Dữ liệu công bố khoa học của một trường đại học hiện nằm rải rác ở ba nơi
không nói chuyện với nhau: Excel các khoa gửi qua email, kho công khai
`repository.ictu.edu.vn` (WordPress), và các chỉ mục ngoài (DOI, chỉ mục
trích dẫn). Không có cách nào truy ngược một con số trong báo cáo về bản ghi
gốc; mỗi lần điều chỉnh số liệu không để lại phiên bản nào.

ICTU-CRIS xây một nguồn sự thật duy nhất: mỗi bản ghi kéo về được giữ
nguyên bản và có phiên bản, mỗi trường dữ liệu sau chuẩn hoá nói được xuất
xứ của mình, và quyết định cuối cùng (nối tác giả, gộp bản ghi trùng) luôn
thuộc về con người, không phải máy. `CRIS` — *Current Research Information
System* — là tên gọi chuẩn quốc tế cho lớp hệ thống quản lý thông tin
nghiên cứu của một tổ chức: công trình, tác giả, đơn vị, kỳ báo cáo (chuẩn
CERIF, mạng euroCRIS). `ICTU-CRIS` là tên làm việc.

## 📊 Ba số liệu chi phối thiết kế (Three driving measurements)

Đo ngày 09–10/09/2026 trên 8.034 bản ghi và 410 hồ sơ giảng viên của kho
nguồn (xem [khao-sat-nguon/](khao-sat-nguon/README.md)):

| Số đo | Ảnh hưởng |
|---|---|
| Liên kết tác giả hiện phủ **8%** bài báo (155/1.907); chuẩn hoá tên đưa lên **86%** | Giai đoạn chuẩn hoá–đối soát là trung tâm hệ thống, không phải chức năng phụ |
| Kho **không có toàn văn** — 39/40 PDF là tóm tắt 1 trang do máy sinh | Đối chiếu đề tài chỉ ở mức tóm tắt, không dẫn chứng theo trang |
| **4.621/5.375** đồ án (86%) ghi giảng viên hướng dẫn là `ICTU_TEACHER` | Thống kê hướng dẫn đồ án chỉ đúng trên 14% kho cho tới khi nguồn được sửa |

## 🧭 Định vị theo HPDI (Human – Process – Data – Intelligence)

Khung phân tích H-P-D-I mượn từ bộ sách **DX-OS**
([opendigitransform.gitbook.io/dx-os](https://opendigitransform.gitbook.io/dx-os),
CC BY 4.0, tác giả TS. Tạ Tuấn Anh) — dự án chỉ trích dẫn khung tư duy này,
**không dùng bộ công cụ no-code của DX-OS**: lõi hệ thống là Python +
PostgreSQL, vì đối soát tác giả và truy xuất xứ từng trường dữ liệu cần một
mô hình quan hệ (relational model), không phải một chuỗi công cụ lắp ghép.

- **H (Human) — hiện trạng**: số liệu công bố khoa học hiện tổng hợp thủ
  công từ Excel các khoa gửi qua email, đối chiếu bằng mắt với kho, nhắc
  nộp bằng lời, chốt bằng bản ký sống — không có phiên bản khi điều chỉnh,
  không truy ngược được một con số về đâu ra.
- **P (Process) — ICTU-CRIS xây**: rào chắn kê khai và duyệt bằng quy tắc
  của hệ thống — lý do trả lại bắt buộc khi từ chối, phiên bản báo cáo được
  đóng băng sau khi chốt, không sửa ngầm sau khi đã ký.
- **D (Data) — ICTU-CRIS xây**: một nguồn sự thật duy nhất (`source_record`),
  xuất xứ của từng trường dữ liệu (`field_provenance`), phiên bản của mỗi
  báo cáo, và khả năng truy ngược mọi con số về bản ghi gốc.
- **I (Intelligence) — một phần, luôn có người quyết**: hệ thống gợi ý nối
  tác giả và đối chiếu đề tài, nhưng quyết định cuối luôn thuộc về người
  dùng — quy tắc BR-18 ("AI gợi ý, người quyết", xem
  [docs/ba/15-project-rules.md](docs/ba/15-project-rules.md)).

## 🏗️ Kiến trúc & Ngăn xếp công nghệ (Architecture & Tech stack)

Gói `cris` tổ chức thành đường ống bốn bước: **đồng bộ** (`sync`) → **chuẩn
hoá** (`normalize`) → **nối và gộp tác giả** (`people`, `link`, `dedup`) →
**báo cáo chất lượng** (`quality`). Lược đồ CSDL nằm ở
`cris/migrations/0001`–`0005` (PostgreSQL 16, không ORM).

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Lõi xử lý | Python 3.12, chỉ stdlib + `psycopg` 3 | Không ORM — truy vấn SQL trực tiếp |
| CSDL | PostgreSQL 16 | Migration SQL thuần `0001`–`0005` |
| Đóng gói | Docker Compose | Image chạy được ngoài thư mục mã nguồn |
| Kiểm thử | pytest 8 trên PostgreSQL thật | 139 test, không mock cơ sở dữ liệu |
| CI | GitHub Actions | `pytest -v` trên PostgreSQL 16 |
| Quy tắc | Bảng `rule_set` có phiên bản | Chuẩn hoá tên, ánh xạ loại bài, khoá gộp |

CLI thống nhất:

```
python -m cris migrate|seed|sync [paths]|people|normalize|link|dedup|quality [--json]
```

## 🚀 Cài đặt nhanh (Quick start)

```bash
cp .env.example .env
docker compose up -d db
docker compose build app
docker compose run --rm app migrate
```

Chạy đường ống:

```bash
docker compose run --rm app seed
docker compose run --rm app sync bai-bao giang-vien
docker compose run --rm app people
docker compose run --rm app normalize
docker compose run --rm app link
docker compose run --rm app dedup
docker compose run --rm app quality --json
```

Mỗi yêu cầu tới kho nguồn được giãn cách **0,35 giây**; một lần đồng bộ đầy
đủ toàn bộ kho mất khoảng **50 phút**. Xem [BUILDING.md](BUILDING.md) để
chạy không dùng Docker (venv + `pip install -e ".[dev]"`).

## 📌 Trạng thái & Lộ trình (Status & Roadmap)

- [x] Khảo sát kho nguồn và bộ BA 18 tệp
- [x] Mô hình dữ liệu 0.1
- [x] Lát cắt S + N chạy từ dòng lệnh, 139 test
- [x] Hồ sơ nguồn mở
- [ ] Nhập Excel khoa (S-06)
- [x] Giao diện hàng đợi xác nhận và tra cứu
- [x] Quét bù phân trang (S-04)
- [ ] Kỳ báo cáo, kê khai, phê duyệt (K, D, R)

## 📚 Tài liệu (Documentation)

| | Tài liệu | Nội dung |
|---|---|---|
| 📋 | [docs/ba/00-README.md](docs/ba/00-README.md) | Bộ tài liệu phân tích nghiệp vụ (BA) — 18 tệp |
| 🗄️ | [docs/ba/17-mo-hinh-du-lieu.md](docs/ba/17-mo-hinh-du-lieu.md) | Mô hình dữ liệu bản 0.1 cho lát cắt S + N + T-01/T-02 |
| 🗺️ | [docs/superpowers/plans/2026-09-10-lat-cat-s-n.md](docs/superpowers/plans/2026-09-10-lat-cat-s-n.md) | Kế hoạch triển khai lát cắt S + N |
| 📦 | [docs/superpowers/plans/2026-09-10-ho-so-nguon-mo.md](docs/superpowers/plans/2026-09-10-ho-so-nguon-mo.md) | Kế hoạch hồ sơ nguồn mở |
| 🔧 | [BUILDING.md](BUILDING.md) | Dịch và chạy từ mã nguồn (Docker, venv) |
| 📚 | [DEPENDENCIES.md](DEPENDENCIES.md) | Chính sách và danh mục thư viện |
| ⚖️ | [docs/LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md) | Lý do chọn giấy phép, ma trận tương thích, quy định header |
| 📝 | [CHANGELOG.md](CHANGELOG.md) | Lịch sử thay đổi |
| 🔍 | [khao-sat-nguon/](khao-sat-nguon/README.md) | Khảo sát kho nguồn `repository.ictu.edu.vn` + công cụ trích xuất |
| 🎓 | [docs/KH triển khai ĐATN_DHCQ_K21.docx](docs/KH%20triển%20khai%20ĐATN_DHCQ_K21.docx) | Kế hoạch đồ án tốt nghiệp của Khoa CNTT (đầu vào nghiệp vụ cho luồng đối chiếu đề tài; không phải lịch của dự án) |

## 🐛 Quản lý lỗi & Đóng góp (Bug tracker & Contributing)

Báo lỗi hoặc đề xuất tính năng qua
[GitHub Issues](https://github.com/maiychrus25/CRIS/issues), dùng mẫu
trong [.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/). Xem
[CONTRIBUTING.md](CONTRIBUTING.md) cho quy trình, chuẩn mã và
[Conventional Commits](https://www.conventionalcommits.org/) cho thông điệp
commit. Quy tắc ứng xử ở [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 🔒 Dữ liệu & Quyền riêng tư (Data & Privacy)

Kho mã nguồn chỉ chứa fixture kiểm thử đã ẩn danh thông tin cá nhân giảng
viên (tên, email, điện thoại, ngày sinh); tên tác giả trên fixture bài báo
là dữ liệu thư mục công khai (bibliographic data). Dữ liệu cá nhân thật
(số điện thoại, ngày sinh giảng viên, ...) không bao giờ được đưa vào Git —
đây là các cột bị hạn chế truy cập.

## 📜 Giấy phép (License)

Apache-2.0 — xem [LICENSE](LICENSE), [NOTICE](NOTICE) và
[docs/LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md). Bản quyền: ICTU-CRIS
contributors.
