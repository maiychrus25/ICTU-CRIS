# 15. Quy tắc triển khai và việc cần xác nhận — ICTU-CRIS

## 15.1 Quy tắc nghiệp vụ cốt lõi

Những quy tắc dưới đây chi phối nhiều use case; đặt tập trung ở đây để không mâu thuẫn giữa các tài liệu.

| # | Quy tắc | Lý do |
|---|---|---|
| BR-01 | **Công trình**, **hồ sơ kê khai** và **báo cáo theo kỳ** là ba thực thể tách biệt | Một công trình có nhiều tác giả, nhiều khoa; mỗi lượt kê khai không phải một công trình mới |
| BR-02 | Một công trình có nhiều hồ sơ kê khai; đếm toàn trường đếm theo công trình | Chống cộng trùng giữa các khoa |
| BR-03 | Báo cáo theo khoa ghi nhận **sự tham gia**; tổng các khoa không phải tổng công trình duy nhất | Hai loại số liệu trả lời hai câu hỏi khác nhau |
| BR-04 | Quy tắc ghi nhận thành tích và phân bổ điểm **theo quy định của ICTU** | Đội phát triển không tự quyết. Là tham số cấu hình, không phải mã |
| BR-05 | Quy tắc thống kê gắn vào kỳ tại thời điểm mở kỳ, không đổi giữa kỳ | Để số liệu trong một kỳ so sánh được với nhau |
| BR-06 | Chuẩn hoá không bao giờ ghi đè giá trị gốc | Truy ngược và đối chứng |
| BR-07 | Chỉ nối tác giả tự động ở hai mức tin cậy cao nhất: trùng ORCID, hoặc tên chuẩn hoá khớp duy nhất | Nối sai tốn công sửa hơn không nối |
| BR-08 | Khoá gộp đồ án gồm **tiêu đề chuẩn hoá + sinh viên + khoá** | 34/43 nhóm trùng tiêu đề là đồ án nhóm; gộp theo tiêu đề sẽ xoá 52 bản ghi thật |
| BR-09 | Gộp bản ghi giữ lịch sử cả hai bản gốc | Gộp là quyết định có thể sai |
| BR-10 | Mâu thuẫn dữ liệu giữa các bản trùng (năm, tạp chí, học vị) phải do người chọn | Hệ thống không tự quyết giá trị nào đúng |
| BR-11 | Người tạo bản trình không phải người phê duyệt | Tách trách nhiệm |
| BR-12 | Phê duyệt của lãnh đạo khoa là **phê duyệt phiên bản hồ sơ để gửi phòng chức năng** | Không phải công nhận chất lượng học thuật, không xác nhận Scopus/WoS, không quyết định khen thưởng hay giờ nghiên cứu, không phê duyệt đề tài sinh viên |
| BR-13 | Nội dung thay đổi sau khi duyệt thì mất dấu đã duyệt và phải trình lại | Không giữ chữ ký trên nội dung đã khác |
| BR-14 | Lý do khi trả lại là bắt buộc và gắn vào hồ sơ cụ thể | Người sửa phải biết sửa chỗ nào |
| BR-15 | Số liệu trong một phiên bản đã chốt không đổi; điều chỉnh sinh phiên bản mới | Báo cáo đã phát hành phải tái lập được |
| BR-16 | Đầu ra của đối chiếu đề tài là tài liệu hỗ trợ xem xét | Không kết luận đạo văn, không khẳng định tính mới |
| BR-17 | Không hiển thị điểm phần trăm tương đồng tổng hợp | Một con số tạo cảm giác kết luận; bảng theo khía cạnh buộc người đọc tự đánh giá |
| BR-18 | AI gợi ý, người quyết | Tính số liệu, phân quyền và chuyển trạng thái do quy tắc xác định của hệ thống thực hiện |

## 15.2 Quy tắc triển khai

| # | Quy tắc |
|---|---|
| PR-01 | Bộ đọc nguồn tách riêng khỏi phần còn lại. Kho là WordPress không có API cho tài liệu học thuật; cấu trúc trang có thể đổi bất cứ lúc nào |
| PR-02 | Đồng bộ chạy ngoài giờ, giãn cách ≤ 3 yêu cầu/giây, không làm ảnh hưởng kho đang phục vụ người dùng |
| PR-03 | Mọi quy tắc chuẩn hoá và quy tắc thống kê là cấu hình đọc được, không nhúng trong mã |
| PR-04 | Mỗi lần đồng bộ ghi một báo cáo: số thêm, sửa, biến mất, lỗi, lệch số lượng |
| PR-05 | Không xoá bản ghi. Bản ghi biến mất ở nguồn được đánh dấu, giữ lại |
| PR-06 | Kiểm thử bắt buộc có bộ dữ liệu thật đã biết trước kết quả: 11 nhóm bài báo trùng, 43 nhóm đồ án trùng tiêu đề (34 nhóm không được gộp), 39 người có nhiều biến thể tên |
| PR-07 | Tài liệu BA cập nhật cùng lúc với thay đổi phạm vi, không cập nhật sau |

## 15.3 Việc cần xác nhận trước khi chốt thiết kế

Gom toàn bộ `[CẦN XÁC NHẬN]` rải trong bộ tài liệu. Nên đi theo **một kỳ báo cáo gần nhất** và yêu cầu người dùng kể lại từng bước.

### Về quy trình

| # | Câu hỏi | Ảnh hưởng nếu trả lời khác giả định |
|---|---|---|
| Q-01 | Ai phát yêu cầu, ai lập, ai kiểm tra, ai duyệt? | Có thể phải thêm actor `division_head` hoặc cấp Ban giám hiệu vào luồng |
| Q-02 | Lãnh đạo khoa duyệt từng công trình hay cả danh sách? | Đổi thiết kế màn SC-06 và trạng thái hồ sơ |
| Q-03 | Khi phòng chức năng trả lại, ai sửa và có cần duyệt lại không? | Đổi luồng UC-11 và quy tắc BR-13 |
| Q-04 | Ai có quyền chốt, mở lại và phát hành báo cáo chính thức? | Đổi ma trận phân quyền |
| Q-05 | Hiện dùng biểu mẫu, công cụ nào; dữ liệu lấy từ đâu? | Quyết định có cần nhập từ tệp cũ hay không |
| Q-06 | Mỗi bước mất bao lâu; lỗi nào thường khiến phải làm lại? | Chọn chỗ tối ưu trước |

### Về quy tắc thống kê

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q-07 | Quy tắc tính năm là gì — năm xuất bản, năm chấp nhận, hay năm nộp báo cáo? | Ảnh hưởng trực tiếp mọi con số theo kỳ |
| Q-08 | Quy tắc đếm đồng tác giả nội bộ? Đã đo: 56 bài có nhiều hơn một giảng viên ICTU, cao nhất 7 người/bài | BR-04; không tự quyết được |
| Q-09 | Đơn vị của công trình xác định theo tác giả nào — tác giả liên hệ, tác giả đầu, hay tất cả? | Quyết định thiết kế N-13 |
| Q-10 | Danh mục loại công trình chính thức của trường là gì? | Hiện nguồn có 48 giá trị văn bản tự do; cần danh mục đóng để ánh xạ về |

### Về dữ liệu

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q-11 | **Bản nộp gốc (toàn văn) của đồ án, luận văn đang nằm ở đâu?** Kho chỉ có tóm tắt 1 trang do máy sinh | Nếu có nguồn khác, mở lại được mức dữ liệu thứ hai và phạm vi đề tài đổi đáng kể |
| Q-12 | Tóm tắt tiếng Anh trong PDF do ai tạo — dịch từ bản tiếng Việt hay sinh mới? | Quyết định mức tin cậy khi dùng làm cơ sở đối chiếu |
| Q-13 | 4.621 đồ án mất tên GVHD — nguồn nhập gốc còn không? | Nếu còn, đây là việc khôi phục dữ liệu; nếu mất, phải thiết kế trên 14% có tên |
| Q-14 | ORCID trên hồ sơ giảng viên do ai nhập, có đối chiếu không? | ORCID là khoá nối tốt nhất đang có (phủ 91%); cần biết độ tin cậy |
| Q-15 | Trường "đơn vị" của bài báo hiện được gán theo quy tắc nào? | 37% bài chưa có đơn vị; cần biết quy tắc cũ trước khi thay |
| Q-16 | Có nguồn công bố nào ngoài kho cần đồng bộ không (Scopus, WoS, Scholar)? | Đổi phạm vi giai đoạn `S` |

### Về hệ thống

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q-17 | Trường có SSO không, và ánh xạ vai trò lấy từ đâu? | NFR-01, NFR-02 |
| Q-18 | Kho ICTU có được sửa không, hay hệ thống mới chỉ đọc? | Nếu sửa được, ba lỗi chặn nên sửa ở nguồn thay vì bù ở hệ thống mới |
| Q-19 | Ai vận hành hệ thống sau khi bàn giao? | NFR-33, PR-03 |

## 15.4 Bộ tài liệu dự án phải duy trì

| Tài liệu | Trạng thái |
|---|---|
| BRD — yêu cầu nghiệp vụ | Chưa lập. Nên lập sau buổi khảo sát xác nhận §15.3 |
| SRS — đặc tả phần mềm, kèm ma trận truy vết BR → FR → UC → US | Chưa lập |
| Bộ BA (16 tệp này) | Bản 1.0, ngày 10/09/2026 |
| Mô hình dữ liệu | Chưa lập. Phụ thuộc Q-07..Q-10 |
| Khảo sát nguồn dữ liệu | Có — [khao-sat-nguon/](../../khao-sat-nguon/README.md) |
| Kiểm chứng giả định bằng số đo | Có — [kiem-chung-gia-dinh-de-tai.md](../../khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md) |

## 15.5 Giới hạn của bản 1.0 này

Bộ tài liệu này viết trên cơ sở hai tài liệu định hướng và số đo trên dữ liệu công khai. **Chưa có buổi khảo sát nào với người dùng thật.** Toàn bộ luồng quy trình ở [01-bpmn.md](01-bpmn.md) và [02-swimlane.md](02-swimlane.md) là **mô hình đề xuất để mang đi xác nhận**, không phải quy trình nội bộ đã kiểm chứng.

Phần đã có cơ sở vững: mọi số đo về dữ liệu nguồn, các ràng buộc kỹ thuật, và các quy tắc nghiệp vụ suy ra trực tiếp từ số đo (BR-06..BR-10).

Phần cần xác nhận: toàn bộ vai trò, thẩm quyền và trình tự phê duyệt.
