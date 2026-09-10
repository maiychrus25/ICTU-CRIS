# ICTU-CRIS

Hệ thống hỗ trợ **tổng hợp, đối soát và phê duyệt dữ liệu công bố khoa học** tại Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên.

`CRIS` — *Current Research Information System* — là tên gọi chuẩn quốc tế cho lớp hệ thống quản lý thông tin nghiên cứu của một tổ chức: công trình, tác giả, đơn vị, kỳ báo cáo (chuẩn CERIF, mạng euroCRIS). `ICTU-CRIS` là tên làm việc.

Trạng thái: **giai đoạn phân tích nghiệp vụ**. Chưa có mã nguồn.

## Nội dung

| Thư mục | Nội dung |
|---|---|
| [docs/ba/](docs/ba/00-README.md) | Bộ tài liệu phân tích nghiệp vụ — 16 tệp |
| [khao-sat-nguon/](khao-sat-nguon/README.md) | Khảo sát kho nguồn `repository.ictu.edu.vn` + công cụ trích xuất |

## Bắt đầu từ đâu

1. [docs/ba/00-README.md](docs/ba/00-README.md) — mục lục bộ BA, quy ước mã trace
2. [khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md](khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md) — số đo thực tế trên dữ liệu nguồn
3. [docs/ba/15-project-rules.md](docs/ba/15-project-rules.md) §15.3 — 28 câu hỏi cần xác nhận, §15.6 — kết quả khảo sát đợt 1
4. [docs/KH triển khai ĐATN_DHCQ_K21.docx](docs/KH%20triển%20khai%20ĐATN_DHCQ_K21.docx) — kế hoạch đồ án đang chạy của Khoa CNTT, quy trình thật đầu tiên trong repo

## Ba số liệu chi phối thiết kế

Đo ngày 09–10/09/2026 trên 8.034 bản ghi và 410 hồ sơ giảng viên của kho nguồn:

| Số đo | Ảnh hưởng |
|---|---|
| Liên kết tác giả hiện phủ **8%** bài báo (155/1.907); chuẩn hoá tên đưa lên **86%** | Giai đoạn chuẩn hoá–đối soát là trung tâm hệ thống |
| Kho **không có toàn văn** — 39/40 PDF là tóm tắt 1 trang do máy sinh | Đối chiếu đề tài chỉ ở mức tóm tắt, không dẫn chứng theo trang |
| **4.621/5.375** đồ án (86%) ghi giảng viên hướng dẫn là `ICTU_TEACHER` | Thống kê hướng dẫn đồ án chỉ đúng trên 14% kho |

## Giới hạn của bản này

Đã có trả lời khảo sát đợt 1 bằng văn bản từ phòng, khoa và giảng viên (10/09/2026, xem [docs/ba/15-project-rules.md](docs/ba/15-project-rules.md) §15.6). Trình tự duyệt đã được xác nhận và bổ sung cấp lãnh đạo trường. Chưa nhận được file báo cáo mẫu, biểu mẫu khoa và văn bản quy tắc thống kê, nên mô hình dữ liệu và mẫu báo cáo vẫn chờ. Phần có cơ sở vững là các số đo trên dữ liệu nguồn và những quy tắc nghiệp vụ suy ra trực tiếp từ đó.

## Dữ liệu

Dữ liệu thô trích xuất từ kho nguồn **không nằm trong repo** — xem [.gitignore](.gitignore). Tái tạo bằng:

```bash
cd khao-sat-nguon
python3 harvest.py archives   # 8.034 bản ghi
python3 gv_detail.py          # 410 hồ sơ giảng viên
python3 normalize.py
```

Chỉ dùng thư viện chuẩn Python. Công cụ giãn cách 0,35 giây mỗi yêu cầu; `robots.txt` của trang nguồn cho phép crawl toàn bộ.
