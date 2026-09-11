# 14. Yêu cầu phi chức năng (NFR) — ICTU-CRIS

## 14.1 An toàn và bảo mật

| # | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-01 | Xác thực theo tài khoản trường; không lưu mật khẩu riêng | Trường chưa có SSO sẵn dùng: đã làm đăng nhập cục bộ (lát cắt G2, `cris/auth.py`) — mật khẩu băm PBKDF2-HMAC-SHA256 (260.000 vòng, salt 16 byte riêng mỗi người, chỉ thư viện chuẩn), phiên 12 giờ qua cookie `cris_session` (HttpOnly, SameSite=Lax), giới hạn 5 lần đăng nhập sai/5 phút theo email. **Chế độ mở** (không bắt buộc đăng nhập) cho tới khi có người đặt mật khẩu. SSO của trường vẫn là mục tiêu, để tích hợp ở lát cắt sau |
| NFR-02 | Phân quyền theo vai trò **và** phạm vi đơn vị | Mọi truy vấn của vai trò cấp khoa bị lọc theo đơn vị ở tầng dữ liệu, không chỉ ẩn trên giao diện |
| NFR-03 | Tách vai trò lập và vai trò duyệt | Hệ thống chặn ở tầng nghiệp vụ, không dựa vào quy ước |
| NFR-04 | Nhật ký thao tác không sửa được | Ghi ai, làm gì, lúc nào, trên đối tượng nào; chỉ thêm, không sửa, không xoá |
| NFR-05 | Không để lộ tên đăng nhập qua API công khai | Rút kinh nghiệm từ lỗi của kho nguồn hiện tại |
| NFR-06 | Minh chứng chỉ người có quyền trên hồ sơ mới tải được | Không dùng đường dẫn đoán được; kiểm quyền mỗi lần tải |
| NFR-07 | Dữ liệu cá nhân giảng viên hiển thị theo mức | Điện thoại và ngày sinh không hiển thị cho `student` |

## 14.2 Hiệu suất

Các mốc dưới đây lấy từ số đo thực tế trên nguồn: 8.034 bản ghi, thời gian phản hồi trung bình của kho là 0,25 giây/trang, toàn bộ 400 trang danh mục kéo hết trong khoảng 4 phút.

| # | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-08 | Đồng bộ toàn bộ kho | ≤ 60 phút với ~8.000 công trình khi phải đọc cả trang chi tiết; chạy ngoài giờ |
| NFR-09 | Đồng bộ gia tăng | ≤ 10 phút; chỉ đọc chi tiết bản ghi mới hoặc đã đổi |
| NFR-10 | Tốc độ gọi nguồn | ≤ 3 yêu cầu/giây, có giãn cách; không làm ảnh hưởng kho đang phục vụ người dùng |
| NFR-11 | Nối tác giả toàn bộ | ≤ 5 phút cho ~5.800 lượt tác giả và 410 hồ sơ giảng viên |
| NFR-12 | Mở màn danh sách hồ sơ | ≤ 1,5 giây với 500 hồ sơ trong một kỳ |
| NFR-13 | Truy ngược một chỉ tiêu | ≤ 2 giây từ lúc bấm tới lúc hiện danh sách công trình |
| NFR-14 | Đối chiếu đề tài | ≤ 5 giây trên toàn bộ ~5.700 đồ án và luận văn |
| NFR-15 | Xuất báo cáo kỳ | ≤ 30 giây cho tệp đầy đủ kèm danh sách đối chứng |

## 14.3 Tính đúng đắn của số liệu

Nhóm NFR riêng, vì đây là thứ quyết định hệ thống có dùng được hay không.

| # | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-16 | Đồng bộ không mất bản ghi âm thầm | Sau mỗi lần đồng bộ, số bản ghi lấy được phải khớp số nguồn công bố; lệch thì cảnh báo, không im lặng |
| NFR-17 | Chuẩn hoá không phá dữ liệu gốc | 100% bản ghi giữ được giá trị gốc của mọi trường đã chuẩn hoá |
| NFR-18 | Độ phủ liên kết tác giả | ≥ 85% công trình có ít nhất một tác giả được nối, sau khi chạy chuẩn hoá và xử lý hàng đợi. Mốc so sánh: nguồn hiện tại đạt 8% |
| NFR-19 | Không nối sai | Tỷ lệ liên kết tự động bị người dùng bác bỏ ≤ 2%, đo trên mẫu kiểm tra thủ công ≥ 200 liên kết |
| NFR-20 | Không gộp sai | 0 trường hợp gộp nhầm đồ án nhóm trong bộ kiểm thử; khoá gộp bắt buộc gồm sinh viên và khoá |
| NFR-21 | Số liệu báo cáo tái lập được | Chạy lại việc tính số liệu trên cùng một phiên bản đã chốt cho ra kết quả giống hệt |
| NFR-22 | Mọi chỉ tiêu truy ngược được | 100% con số trong báo cáo mở ra được danh sách công trình tạo nên nó |
| NFR-23 | Đối chiếu thủ công khớp | Trên mẫu ≥ 3 khoa của một kỳ, số liệu hệ thống khớp danh sách kiểm tra tay; sai lệch phải giải thích được |

## 14.4 Tính minh bạch

| # | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-24 | Mỗi trường dữ liệu nói được nguồn của mình | Kho ICTU / kê khai của khoa / sửa tay, kèm thời điểm |
| NFR-25 | Nói rõ mức dữ liệu ở nơi có thể gây hiểu nhầm | Màn đối chiếu đề tài ghi rõ so trên tóm tắt; hồ sơ giảng viên ghi rõ thời điểm đồng bộ |
| NFR-26 | Không tạo cảm giác kết luận | Đối chiếu đề tài không hiển thị điểm phần trăm tổng hợp; không dùng từ "đạo văn", "trùng lặp %" |
| NFR-27 | AI không sinh số liệu | Mọi con số lấy từ dữ liệu và có đường dẫn đối chứng. AI chỉ dùng để gợi ý ghép bản ghi, phân loại chủ đề, diễn giải biến động |
| NFR-28 | Gợi ý của AI luôn có người quyết | Không có luồng nào để AI tự động gộp bản ghi, tự xác nhận liên kết hay tự chuyển trạng thái |

## 14.5 Khả năng vận hành

| # | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-29 | Chịu được thay đổi cấu trúc nguồn | Kho là WordPress không có API cho tài liệu học thuật; bộ đọc tách riêng, đổi được mà không sửa phần còn lại |
| NFR-30 | Đồng bộ chạy lại được | Chạy lại lần hai trên cùng dữ liệu nguồn không tạo bản ghi trùng |
| NFR-31 | Ngắt giữa chừng không hỏng dữ liệu | Đồng bộ ghi theo lô, có điểm tiếp tục |
| NFR-32 | Sao lưu và phục hồi | Sao lưu hằng ngày; phục hồi được về một phiên bản báo cáo đã chốt |
| NFR-33 | Không phụ thuộc một người | Quy tắc chuẩn hoá và quy tắc thống kê là cấu hình, không nằm trong mã |

## 14.6 Khả năng dùng

| # | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-34 | Dùng được sau vài tháng không đụng tới | Người dùng quay lại sau một kỳ hoàn thành được tác vụ chính mà không cần đọc tài liệu |
| NFR-35 | Màn duyệt dùng được trên điện thoại | Bản trình duyệt và xác nhận liên kết tác giả đọc và thao tác được trên màn hình hẹp |
| NFR-36 | Tiếng Việt có dấu đúng ở mọi nơi | Kể cả khi xuất tệp; tệp xuất mở được bằng Excel không lỗi phông |
| NFR-37 | Thao tác hàng loạt cho việc lặp lại | Xác nhận liên kết tác giả và xử lý nghi trùng chọn nhiều được |

## 14.7 Ràng buộc đã biết từ nguồn dữ liệu

Không phải yêu cầu, mà là giới hạn phải ghi vào tài liệu để không hứa quá:

| Ràng buộc | Ảnh hưởng |
|---|---|
| Kho công khai không có toàn văn — PDF là tóm tắt 1 trang do máy sinh. Khảo sát đợt 1: quyển hoàn chỉnh lưu ở khoa và/hoặc thư viện, cho tra file mềm hay không tuỳ quyền truy cập và bản quyền, không mặc định công khai | Đối chiếu ở mức tóm tắt là mặc định; toàn văn là tuỳ chọn có phân quyền nếu thư viện cấp; không hứa dẫn chứng theo trang |
| 4.621/5.375 đồ án ghi GVHD là `ICTU_TEACHER` | Thống kê hướng dẫn đồ án chỉ đúng trên 14% kho cho tới khi nguồn được sửa. Bảng đăng ký đồ án theo khoá của khoa (Google Sheets, Drive, thư viện) là nguồn khôi phục, xem S-08; cần được cấp quyền đọc |
| Kho không có trường đơn vị công tác hay quốc gia của tác giả | Phòng có nhu cầu thống kê hợp tác quốc tế (khảo sát đợt 1) nhưng phải định nghĩa trước (Q-28); T-10 chỉ làm được khi có dữ liệu cơ quan tác giả từ nhập tay hoặc nguồn chỉ mục ngoài |
| Nguồn có lỗi phân trang bỏ sót bản ghi | Bắt buộc có bước đối soát số lượng (NFR-16) |
| Kho chỉ có bài báo, đồ án, luận văn, luận án; phòng quản lý 9 nhóm công trình gồm đề tài, sách, giáo trình, sáng chế | Nếu phạm vi gồm các nhóm ngoài kho (Q-25), dữ liệu đến từ Excel khoa gửi qua S-06, không qua đồng bộ |
| Mẫu báo cáo khác nhau giữa các kỳ và giữa cấp trên với nội bộ | Mẫu là cấu hình của kỳ (A-07); không có một mẫu cố định trong mã |
