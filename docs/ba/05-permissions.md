# 5. Ma trận phân quyền — ICTU-CRIS

## Bảng 1 — Actor

| STT | Actor | Mô tả |
|---|---|---|
| 1 | Chuyên viên Văn phòng khoa (`faculty_officer`) | Lập và quản lý hồ sơ kê khai của khoa mình. Người dùng chính, thao tác nhiều nhất |
| 2 | Lãnh đạo khoa (`faculty_head`) | Xem xét và phê duyệt bản trình của khoa mình. Không sửa nội dung hồ sơ |
| 3 | Chuyên viên Phòng KH-CN & HTQT (`rd_officer`) | Mở kỳ, kiểm tra, đối soát toàn trường, chốt dữ liệu, xuất báo cáo |
| 4 | Giảng viên (`lecturer`) | Kê khai và xác nhận công trình của mình; xác nhận liên kết tác giả; nhận yêu cầu bổ sung |
| 5 | Sinh viên, học viên (`student`) | Tra cứu và đối chiếu đề tài dự kiến. Không thấy dữ liệu kỳ báo cáo |
| 6 | Quản trị hệ thống (`admin`) | Người dùng, vai trò, danh mục, quy tắc thống kê, lịch đồng bộ |
| 7 | Kho ICTU (`repository`) | Hệ thống nguồn, chỉ đọc. Không phải người |

`[CẦN XÁC NHẬN]` Tài liệu định hướng ghi rõ chưa đủ căn cứ khẳng định có bước phê duyệt của lãnh đạo phòng hoặc Ban giám hiệu. Nếu có, bổ sung actor `division_head` với quyền tương tự `faculty_head` ở cấp trường.

## Bảng 2 — Ma trận

`O` được phép · `X` không · `O*` có điều kiện, ghi chú bên dưới.

| Chức năng | faculty_officer | faculty_head | rd_officer | lecturer | student | admin |
|---|---|---|---|---|---|---|
| Đăng nhập, bảng công việc (W-01..03) | O | O | O | O | O | O |
| Xem nhật ký thao tác (W-05) | O* | O* | O | X | X | O |
| Chạy đồng bộ kho (S-01..05) | X | X | O | X | X | O |
| Nhập công trình ngoài kho (S-06) | O | X | O | O* | X | X |
| Chuẩn hoá tên, nối tác giả tự động (N-01..03) | X | X | O | X | X | O |
| Xác nhận liên kết tác giả (N-04) | O* | X | O | O* | X | X |
| Quyết định gộp bản ghi trùng (N-07..10) | X | X | O | X | X | X |
| Chuẩn hoá loại, đơn vị, từ khoá (N-11..14) | X | X | O | X | X | O |
| Xem báo cáo chất lượng dữ liệu (N-15) | O* | O* | O | X | X | O |
| Tạo, sửa hồ sơ kê khai (K-01..04, K-07) | O | X | O* | X | X | X |
| Kê khai công trình của tôi (K-09) | O | O | O | O | X | X |
| Gửi yêu cầu bổ sung (K-06) | O | X | O | X | X | X |
| Xem tiến độ kê khai của khoa (K-08) | O | O | O | X | X | X |
| Tạo bản trình duyệt (D-01, D-02) | O | X | X | X | X | X |
| Phê duyệt / trả lại bản trình khoa (D-03, D-04) | X | O | X | X | X | X |
| Theo dõi tiến độ nộp toàn trường (D-06, D-07) | X | X | O | X | X | X |
| Hàng đợi kiểm tra, yêu cầu điều chỉnh (D-08, D-09) | X | X | O | X | X | X |
| Chốt kỳ, mở lại kỳ (R-01, R-02) | X | X | O | X | X | X |
| Xuất báo cáo toàn trường (R-03, R-06) | X | X | O | X | X | X |
| Xem báo cáo theo khoa (R-04) | O* | O* | O | X | X | X |
| Truy ngược chỉ tiêu, lịch sử duyệt (R-05, R-08) | O* | O* | O | X | X | X |
| Tìm công trình, xem hồ sơ giảng viên (T-01, T-02) | O | O | O | O | O | O |
| Đối chiếu đề tài dự kiến (T-03..T-06) | O | O | O | O | O | X |
| Xuất trích dẫn (T-08) | O | O | O | O | O | O |
| Quản lý kỳ, quy tắc, danh mục (A-01, A-02, A-04) | X | X | O | X | X | O |
| Quản lý người dùng, vai trò (A-03) | X | X | X | X | X | O |
| Cấu hình đồng bộ, nhật ký hệ thống (A-05, A-06) | X | X | O* | X | X | O |

## Chú thích `O*`

| Vị trí | Điều kiện |
|---|---|
| `faculty_officer`, `faculty_head` — nhật ký, chất lượng dữ liệu, báo cáo, truy ngược | Chỉ trong phạm vi khoa mình |
| `rd_officer` — tạo, sửa hồ sơ kê khai | Chỉ khi khoa đã bàn giao và có ghi nhận lý do can thiệp |
| `lecturer` — nhập công trình ngoài kho | Chỉ công trình có tên mình trong danh sách tác giả |
| `faculty_officer`, `lecturer` — xác nhận liên kết tác giả | Chỉ ca thuộc khoa mình / thuộc bản thân mình; ca liên khoa do `rd_officer` quyết |
| `rd_officer` — cấu hình đồng bộ | Đặt được lịch và phạm vi, không sửa được thông tin kết nối nguồn |

## Nguyên tắc phân quyền

1. **Người lập không phải người duyệt.** `faculty_officer` không phê duyệt được bản trình do chính mình tạo.
2. **Người duyệt không sửa nội dung.** `faculty_head` chỉ có hai hành động: phê duyệt, hoặc trả lại kèm lý do.
3. **Chốt dữ liệu là thẩm quyền cấp trường.** Chỉ `rd_officer` chốt và mở lại kỳ.
4. **Phạm vi đơn vị là ràng buộc mặc định.** Mọi quyền của vai trò cấp khoa giới hạn trong khoa được gán.
5. **Quyết định gộp bản ghi trùng tập trung ở cấp trường**, vì công trình có thể liên quan nhiều khoa.
