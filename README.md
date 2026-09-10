# ICTU-CRIS

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![CI](https://github.com/maiychrus25/ICUT-CRIS/actions/workflows/ci.yml/badge.svg)](https://github.com/maiychrus25/ICUT-CRIS/actions/workflows/ci.yml)

Hệ thống hỗ trợ **tổng hợp, đối soát và phê duyệt dữ liệu công bố khoa học**
tại Trường Công nghệ Thông tin và Truyền thông (CNTT&TT), Đại học Thái
Nguyên — thay việc dò từng dòng Excel bằng một nguồn sự thật duy nhất, mỗi
con số truy ngược được về bản ghi gốc.

`CRIS` — *Current Research Information System* — là tên gọi chuẩn quốc tế
cho lớp hệ thống quản lý thông tin nghiên cứu của một tổ chức: công trình,
tác giả, đơn vị, kỳ báo cáo (chuẩn CERIF, mạng euroCRIS). `ICTU-CRIS` là tên
làm việc.

## Ba số liệu chi phối thiết kế (Three driving measurements)

Đo ngày 09–10/09/2026 trên 8.034 bản ghi và 410 hồ sơ giảng viên của kho
nguồn (xem [khao-sat-nguon/](khao-sat-nguon/README.md)):

| Số đo | Ảnh hưởng |
|---|---|
| Liên kết tác giả hiện phủ **8%** bài báo (155/1.907); chuẩn hoá tên đưa lên **86%** | Giai đoạn chuẩn hoá–đối soát là trung tâm hệ thống, không phải chức năng phụ |
| Kho **không có toàn văn** — 39/40 PDF là tóm tắt 1 trang do máy sinh | Đối chiếu đề tài chỉ ở mức tóm tắt, không dẫn chứng theo trang |
| **4.621/5.375** đồ án (86%) ghi giảng viên hướng dẫn là `ICTU_TEACHER` | Thống kê hướng dẫn đồ án chỉ đúng trên 14% kho cho tới khi nguồn được sửa |

## Định vị theo HPDI (Human – Process – Data – Intelligence)

Khung phân tích H-P-D-I mượn từ bộ sách **DX-OS**
([opendigitransform.gitbook.io/dx-os](https://opendigitransform.gitbook.io/dx-os),
CC BY 4.0, tác giả TS. Tạ Tuấn Anh) — dự án chỉ trích dẫn khung tư duy này,
**không dùng bộ công cụ no-code của DX-OS**: lõi hệ thống là Python +
PostgreSQL, vì đối soát tác giả và truy xuất xứ từng trường dữ liệu cần một
mô hình quan hệ (relational model), không phải một chuỗi công cụ lắp ghép.

- **H (Human) — hiện trạng**: theo khảo sát đợt 1 (10/09/2026), số liệu công
  bố khoa học hiện tổng hợp thủ công từ Excel các khoa gửi qua email, đối
  chiếu bằng mắt với kho, nhắc nộp bằng lời, và chốt bằng bản ký sống — không
  có phiên bản khi điều chỉnh, không truy ngược được một con số về đâu ra.
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

## Trạng thái hiện tại (Status)

Lát cắt **S** (đồng bộ) và **N** (chuẩn hoá — nối tác giả, gộp trùng, báo
cáo chất lượng) cùng phần tra cứu dữ liệu chạy được **từ dòng lệnh**, có 90
test pytest chạy trên PostgreSQL 16 thật. Chi tiết quyết định phạm vi ở
[docs/ba/15-project-rules.md](docs/ba/15-project-rules.md) Q-24 và
[docs/superpowers/plans/2026-09-10-lat-cat-s-n.md](docs/superpowers/plans/2026-09-10-lat-cat-s-n.md).

**Chưa có giao diện web.** Hàng đợi xác nhận và màn hình tra cứu, nhập Excel
khoa (S-06), và quét bù phân trang (S-04) là các kế hoạch tiếp theo, theo
thứ tự đó.

## Cài đặt nhanh (Quick start)

```bash
cp .env.example .env
docker compose up -d db
docker compose build app
docker compose run --rm app migrate
```

Xem [BUILDING.md](BUILDING.md) để chạy đủ đường ống (`seed`, `sync`,
`normalize`, `people`, `link`, `dedup`, `quality`) và cách dịch/chạy không
dùng Docker (venv + `pip install -e ".[dev]"`).

## Kiến trúc (Architecture)

Gói `cris` tổ chức thành đường ống bốn bước: **đồng bộ** (`sync`) → **chuẩn
hoá** (`normalize`) → **nối và gộp tác giả** (`people`, `link`, `dedup`) →
**báo cáo chất lượng** (`quality`). Lược đồ CSDL nằm ở
`cris/migrations/0001`–`0005` (PostgreSQL 16, không ORM).

CLI thống nhất:

```
python -m cris migrate|seed|sync [paths]|people|normalize|link|dedup|quality [--json]
```

## Tài liệu (Documentation)

| Tài liệu | Nội dung |
|---|---|
| [docs/ba/00-README.md](docs/ba/00-README.md) | Bộ tài liệu phân tích nghiệp vụ (BA) — 17 tệp |
| [docs/ba/17-mo-hinh-du-lieu.md](docs/ba/17-mo-hinh-du-lieu.md) | Mô hình dữ liệu bản 0.1 cho lát cắt S + N + T-01/T-02 |
| [docs/superpowers/plans/2026-09-10-lat-cat-s-n.md](docs/superpowers/plans/2026-09-10-lat-cat-s-n.md) | Kế hoạch triển khai lát cắt S + N |
| [BUILDING.md](BUILDING.md) | Dịch và chạy từ mã nguồn (Docker, venv) |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Chính sách và danh mục thư viện |
| [docs/LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md) | Lý do chọn giấy phép, ma trận tương thích, quy định header |
| [CHANGELOG.md](CHANGELOG.md) | Lịch sử thay đổi |
| [khao-sat-nguon/](khao-sat-nguon/README.md) | Khảo sát kho nguồn `repository.ictu.edu.vn` + công cụ trích xuất |
| [docs/KH triển khai ĐATN_DHCQ_K21.docx](docs/KH%20triển%20khai%20ĐATN_DHCQ_K21.docx) | Kế hoạch đồ án tốt nghiệp của Khoa CNTT (đầu vào nghiệp vụ cho luồng đối chiếu đề tài; không phải lịch của dự án) |

## Đóng góp (Contributing)

Xem [CONTRIBUTING.md](CONTRIBUTING.md) cho quy trình, Conventional Commits
và chuẩn mã. Báo lỗi hoặc đề xuất tính năng qua
[GitHub Issues](https://github.com/maiychrus25/ICUT-CRIS/issues), dùng mẫu
trong [.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/). Quy tắc ứng xử ở
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Giấy phép (License)

Apache-2.0 — xem [LICENSE](LICENSE), [NOTICE](NOTICE) và
[docs/LICENSE_NOTICE.md](docs/LICENSE_NOTICE.md). Bản quyền: ICTU-CRIS
contributors. Repo chỉ chứa fixture kiểm thử đã ẩn danh; dữ liệu thật (số
điện thoại, ngày sinh giảng viên, ...) không bao giờ được đưa vào Git.
