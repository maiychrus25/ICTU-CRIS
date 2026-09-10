# Bộ tài liệu phân tích nghiệp vụ (BA) — ICTU-CRIS

Dự án: **ICTU-CRIS** — hệ thống hỗ trợ tổng hợp, đối soát và phê duyệt dữ liệu công bố khoa học tại Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên. Bản 1.0, ngày 10/09/2026.

`CRIS` (*Current Research Information System*) là tên gọi chuẩn quốc tế cho lớp hệ thống này — quản lý thông tin nghiên cứu của một tổ chức: công trình, tác giả, đơn vị, kỳ báo cáo. Dùng thuật ngữ này để đề tài có neo tài liệu (chuẩn CERIF, mạng euroCRIS) thay vì tự định nghĩa một loại phần mềm mới. `ICTU-CRIS` là tên làm việc, đổi được.

## Nguồn đầu vào

| Nguồn | Vai trò |
|---|---|
| Tổng quan dịch vụ khai thác tri thức nghiên cứu ICTU (09/09/2026) | Ba nhóm chức năng: đối chiếu đề tài, thống kê công bố, tra cứu có nguồn |
| Phân tích người dùng và quy trình quản lý công bố khoa học ICTU (09/09/2026) | Hai nhóm tác nghiệp + một vai trò phê duyệt; luồng tổng hợp → duyệt → đối soát → chốt |
| [Kiểm chứng giả định bằng dữ liệu thực](../../khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md) (10/09/2026) | Số đo trên 8.034 bản ghi + 410 hồ sơ giảng viên; định lượng lại phạm vi |
| [Khảo sát kho ICTU](../../khao-sat-nguon/README.md) | Bề mặt API, 10 lỗi dữ liệu của nguồn |
| [Kế hoạch triển khai ĐATN ĐHCQ K21](../KH%20triển%20khai%20ĐATN_DHCQ_K21.docx) (Khoa CNTT, 26/02/2026) | Quy trình đồ án thật: 12 mốc, cấp bộ môn, danh mục hướng đề tài, kiểm tra đạo văn cuối kỳ, thư viện lưu file mềm |
| Trả lời khảo sát đợt 1 (10/09/2026), ghi tại [15-project-rules.md](15-project-rules.md) §15.6 | Ba tầng phòng, khoa, giảng viên; xác nhận trình tự duyệt, thêm cấp lãnh đạo trường, tách đơn vị chủ trì, quy tắc năm công bố, nguồn chính là Excel khoa gửi |
| [Kế hoạch triển khai lát cắt S + N](../superpowers/plans/2026-09-10-lat-cat-s-n.md) (10/09/2026) | Quyết định phạm vi bản đầu (Q-24): S + N + T-01/T-02; đã triển khai thành mã nguồn `cris/` |

Tài liệu cấp trên (BRD, SRS) chưa lập. Bộ BA này viết trên cơ sở hai tài liệu định hướng ở trên; mọi giả định chưa xác nhận được đánh dấu `[CẦN XÁC NHẬN]` và gom lại ở [15-project-rules.md](15-project-rules.md).

## Sản phẩm

| # | Sản phẩm | Tệp | Phạm vi chi tiết |
|---|---|---|---|
| 1 | Sơ đồ BPMN | [01-bpmn.md](01-bpmn.md) | Kỳ báo cáo; đối chiếu đề tài |
| 2 | Swimlane workflow | [02-swimlane.md](02-swimlane.md) | Kỳ báo cáo, Hồ sơ kê khai, Công trình, Liên kết tác giả |
| 3 | Biểu đồ trạng thái | [03-state.md](03-state.md) | 5 đối tượng có vòng đời |
| 4 | Danh sách chức năng | [04-functions.md](04-functions.md) | Theo giai đoạn, có mã trace |
| 5 | Ma trận phân quyền | [05-permissions.md](05-permissions.md) | 8 actor người + 1 hệ thống nguồn |
| 6 | Tiêu chí UX + phân tích thiết kế | [06-ux.md](06-ux.md) | |
| 7 | Mô tả màn hình | [07-screens.md](07-screens.md) | 14 màn |
| 8 | Sitemap | [08-sitemap.md](08-sitemap.md) | Web ≤ cấp 2 |
| 9 | Sơ đồ use case | [09-usecase-diagram.md](09-usecase-diagram.md) | 3 nhóm |
| 10 | Sơ đồ luồng chức năng | [10-activity.md](10-activity.md) | 4 luồng |
| 11 | Đặc tả use case | [11-usecase-spec.md](11-usecase-spec.md) | UC-01..17 |
| 12 | Use scenario | [12-scenarios.md](12-scenarios.md) | 5 kịch bản |
| 13 | User story + AC | [13-user-stories.md](13-user-stories.md) | US-01..39 |
| 14 | Yêu cầu phi chức năng | [14-nfr.md](14-nfr.md) | |
| 15 | Quy tắc triển khai + việc cần xác nhận | [15-project-rules.md](15-project-rules.md) | |
| 16 | Kịch bản khảo sát người dùng | [16-kich-ban-khao-sat.md](16-kich-ban-khao-sat.md) | 3 tầng: phòng, khoa, giảng viên; trả lời §15.3 |
| 17 | Mô hình dữ liệu | [17-mo-hinh-du-lieu.md](17-mo-hinh-du-lieu.md) | Bản 0.1, lát cắt S + N + T-01/T-02; 14 bảng, 4 view, bộ kiểm thử PR-06 |

## Quy ước

Use case và chức năng đặt tên "Động từ + Đối tượng"; actor là danh từ nhóm người. Mã trace theo giai đoạn:

| Mã | Giai đoạn |
|---|---|
| `W` | Chung: đăng nhập, thiết lập, thông báo |
| `S` | Đồng bộ nguồn (sync) từ kho ICTU |
| `N` | Chuẩn hoá và đối soát (normalize): nối tác giả, gộp trùng, gán đơn vị |
| `K` | Kê khai và lập hồ sơ |
| `D` | Duyệt: khoa xác nhận, phòng kiểm tra |
| `R` | Chốt và báo cáo |
| `T` | Tra cứu và đối chiếu đề tài |
| `A` | Quản trị |

## Sơ đồ

Vẽ bằng Mermaid, đặt trực tiếp trong tài liệu (khác quy ước Excalidraw của dự án DX-Forge — đây là dự án độc lập, và hai tài liệu định hướng đầu vào đã dùng Mermaid). Nguồn phụ trợ nếu cần đặt trong [diagrams/](diagrams/).

## Ba số liệu chi phối toàn bộ thiết kế

| Số đo | Ảnh hưởng |
|---|---|
| Liên kết tác giả hiện phủ **8%** bài báo (155/1.907); chuẩn hoá tên đưa lên **86%** | Giai đoạn `N` là trung tâm hệ thống, không phải chức năng phụ |
| Kho **không có toàn văn** — 39/40 PDF là tóm tắt 1 trang do máy sinh | Đối chiếu đề tài chỉ ở mức tóm tắt; không có "dẫn chứng theo trang" |
| **4.621/5.375** đồ án (86%) ghi GVHD là `ICTU_TEACHER` | Thống kê hướng dẫn đồ án chỉ đúng trên 14% kho cho tới khi nguồn được sửa |
