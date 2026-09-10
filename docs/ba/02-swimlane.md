# 2. Swimlane workflow — ICTU-CRIS (theo đối tượng)

## 2.1 Kỳ báo cáo (Period)

| Giai đoạn | Phòng KH-CN & HTQT | Hệ thống | Văn phòng khoa | Lãnh đạo khoa | Lãnh đạo trường |
|---|---|---|---|---|---|
| Mở kỳ | Đặt phạm vi, tiêu chí, hạn nộp, mẫu báo cáo, quy tắc năm công bố | Sinh bản ghi kỳ, gửi thông báo tới các khoa | Nhận thông báo | Nhận thông báo | — |
| Thu thập | Theo dõi bảng tiến độ theo khoa | Đồng bộ kho, dựng gợi ý theo khoa, nhập tệp Excel khoa gửi | Lập hồ sơ | — | — |
| Đóng nộp | Đóng cổng nộp | Khoá thao tác lập mới, giữ quyền sửa theo yêu cầu trả về | — | — | — |
| Đối soát | Kiểm tra, gộp trùng toàn trường; trả về khoa, không tự sửa trường khoa xác nhận | Đề xuất gộp, tính lại số liệu | Xử lý yêu cầu điều chỉnh | Duyệt lại nếu danh sách đổi | — |
| Chốt | Xác nhận tập hồ sơ | Khoá phiên bản, sinh mã phiên bản | — | — | — |
| Trình ký | Trình báo cáo chính thức | Đóng gói tệp theo mẫu kỳ | — | — | Phê duyệt hoặc trả lại |
| Phát hành | Xuất báo cáo | Sinh tệp kèm danh sách đối chứng, ghi phiên bản | — | — | — |

Báo cáo nội bộ bỏ qua giai đoạn Trình ký (BR-24).

## 2.2 Hồ sơ kê khai (Declaration)

| Giai đoạn | Giảng viên | Văn phòng khoa | Hệ thống | Lãnh đạo khoa | Phòng KH-CN |
|---|---|---|---|---|---|
| Tạo | Kê khai công trình chưa có trong kho | Chọn từ gợi ý, tạo hồ sơ | Điền sẵn trường lấy từ kho, đánh dấu nguồn | — | — |
| Kiểm tra | — | Xem cảnh báo | Sinh cảnh báo: thiếu trường, nghi trùng, tác giả chưa nối, minh chứng thiếu | — | — |
| Bổ sung | Nộp minh chứng theo yêu cầu | Gửi yêu cầu bổ sung gắn vào hồ sơ | Theo dõi hồ sơ đang chờ ai | — | — |
| Trình duyệt | — | Tạo bản trình kèm nguồn và phần thay đổi | Đóng gói phiên bản trình | Xem, so với lần trình trước | — |
| Phê duyệt | — | — | Đóng băng phiên bản | Duyệt hoặc trả lại kèm lý do | — |
| Kiểm tra cấp trường | — | Sửa theo yêu cầu trả về | Ghi lý do trả lại, trạng thái duyệt lại | Duyệt lại nếu trọng yếu | Kiểm tra, trả về hoặc chấp nhận |

## 2.3 Công trình (Work) — thực thể duy nhất sau đối soát

| Giai đoạn | Nguồn | Hệ thống | Phòng KH-CN |
|---|---|---|---|
| Nhập | Kho ICTU / kê khai của khoa | Tạo bản ghi thô, giữ nguyên giá trị gốc | — |
| Chuẩn hoá | — | Chuẩn hoá tên tác giả, tên đơn vị, loại công trình, năm | — |
| Nghi trùng | — | Ghép ứng viên theo DOI, rồi theo tiêu đề chuẩn hoá | Xem hàng đợi nghi trùng |
| Gộp | — | Gộp theo quyết định của người dùng, giữ lịch sử hai bản gốc | Quyết định gộp hay giữ riêng |
| Liên kết | — | Nối công trình ↔ tác giả ↔ đơn vị | Xác nhận liên kết mơ hồ |

Một công trình có **nhiều** hồ sơ kê khai (nhiều khoa cùng kê khai). Đây là lý do phải tách hai thực thể; xem [15-project-rules.md](15-project-rules.md) §Quy tắc nghiệp vụ.

## 2.4 Liên kết tác giả (AuthorLink)

| Giai đoạn | Hệ thống | Văn phòng khoa | Giảng viên | Phòng KH-CN |
|---|---|---|---|---|
| Sinh ứng viên | Khớp ORCID trước, khớp tên chuẩn hoá sau; gán độ tin cậy | — | — | — |
| Tự nối | Nối thẳng khi khớp ORCID hoặc khớp tên duy nhất | — | — | — |
| Chờ xác nhận | Đưa vào hàng đợi khi tên khớp nhiều người hoặc chỉ khớp một phần | Xác nhận trong phạm vi khoa | Xác nhận công trình của mình | Xác nhận ca liên khoa |
| Bác bỏ | Ghi nhận phủ định để không đề xuất lại | Bác bỏ kèm lý do | Bác bỏ kèm lý do | — |
