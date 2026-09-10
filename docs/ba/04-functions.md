# 4. Danh sách chức năng — ICTU-CRIS

Mã trace theo giai đoạn: `W` chung · `S` đồng bộ · `N` chuẩn hoá/đối soát · `K` kê khai · `D` duyệt · `R` báo cáo · `T` tra cứu · `A` quản trị.

## Chung, xác thực, thông báo

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| W-01 | Đăng nhập hệ thống | Xác thực theo tài khoản trường; ánh xạ về vai trò và đơn vị | P1 |
| W-02 | Chọn ngữ cảnh làm việc | Chọn kỳ báo cáo và đơn vị đang thao tác | P1 |
| W-03 | Xem bảng công việc của tôi | Việc đang chờ chính người đăng nhập xử lý | P1 |
| W-04 | Nhận thông báo | Mở kỳ, sắp hết hạn, hồ sơ bị trả lại, yêu cầu bổ sung | P2 |
| W-05 | Xem nhật ký thao tác | Ai làm gì, lúc nào, trên hồ sơ nào | P1 |

## Đồng bộ nguồn (S)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| S-01 | Đồng bộ kho ICTU | Kéo bài báo, đồ án, luận văn, luận án, hồ sơ giảng viên | P1 |
| S-02 | Đọc trang chi tiết công trình | Bắt buộc — trang danh mục cắt cụt danh sách tác giả ở 17% bài báo | P1 |
| S-03 | Đối soát số lượng sau đồng bộ | So số bản ghi lấy được với số nguồn công bố; cảnh báo khi lệch | P1 |
| S-04 | Bù bản ghi phân trang bỏ sót | Quét thêm theo bộ lọc để lấy bản ghi lật trang không tới được | P1 |
| S-05 | Ghi nhận thay đổi giữa hai lần đồng bộ | Thêm, sửa, biến mất; không ghi đè im lặng | P2 |
| S-06 | Nhập công trình từ tệp khoa gửi | Excel/CSV/Google Sheet theo mẫu thay đổi từng đợt, có bước ánh xạ cột; khảo sát đợt 1 cho biết đây là nguồn chính hiện nay, kho chỉ để đối chiếu | P1 |
| S-07 | Lưu giá trị gốc | Giữ nguyên bản gốc mọi trường trước khi chuẩn hoá, để truy ngược | P1 |
| S-08 | Nhập danh sách đăng ký đồ án theo khoá | Từ bảng tổng hợp của khoa (Google Sheets): mã sinh viên, lớp, GVHD, hướng đề tài. Nguồn đáng tin cho cặp sinh viên–GVHD mà kho đang ghi placeholder `ICTU_TEACHER` | P1 |
| S-09 | Đối chiếu nguồn chỉ mục ngoài | Kiểm DOI, Scopus, WoS cho bài quốc tế khi cần xác minh; ghi kết quả và thời điểm kiểm vào công trình | P2 |

## Chuẩn hoá và đối soát (N)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| N-01 | Chuẩn hoá tên người | Bỏ dấu, hạ chữ thường, cắt tiền tố học hàm/học vị, xử lý dạng đảo họ-tên có gạch nối | P1 |
| N-02 | Nối tác giả bằng ORCID | Khoá nối ưu tiên; hiện phủ 91% hồ sơ giảng viên | P1 |
| N-03 | Nối tác giả bằng tên chuẩn hoá | Áp dụng khi không có ORCID; gán độ tin cậy | P1 |
| N-04 | Quản lý hàng đợi xác nhận liên kết | Ca khớp nhiều người hoặc khớp một phần | P1 |
| N-05 | Ghi nhận bác bỏ liên kết | Không đề xuất lại cặp đã bị bác bỏ | P2 |
| N-06 | Cảnh báo mâu thuẫn học vị | Cùng một người ghi cả `TS.` và `ThS.` ở các bản ghi khác nhau — không tự chọn | P1 |
| N-07 | Phát hiện nghi trùng theo DOI | Khớp chính xác, độ tin cậy cao nhất | P1 |
| N-08 | Phát hiện nghi trùng theo tiêu đề chuẩn hoá | Kèm so sánh năm, tạp chí, tác giả | P1 |
| N-09 | Gộp bản ghi trùng | Chọn giá trị giữ lại cho từng trường mâu thuẫn; giữ lịch sử cả hai bản gốc | P1 |
| N-10 | Áp quy tắc không gộp đồ án nhóm | Khoá gộp phải gồm sinh viên và khoá, không chỉ tiêu đề | P1 |
| N-11 | Chuẩn hoá loại công trình | Tách trường văn bản tự do thành: chỉ mục, loại nơi công bố, điểm | P1 |
| N-12 | Chuẩn hoá tên đơn vị | Gom biến thể của cùng một đơn vị về một mã | P1 |
| N-13 | Suy đơn vị tham gia từ tác giả | Ghi nhận mọi đơn vị có tác giả tham gia (nhiều-nhiều); giải quyết 37% bài báo chưa có đơn vị. Không suy đơn vị chủ trì | P1 |
| N-16 | Xác định đơn vị chủ trì | Trường riêng do người chọn theo tiêu chí của kỳ (chủ trì, tác giả đầu, khai báo khi đăng ký); dùng khi mẫu báo cáo đòi một đơn vị (BR-22) | P1 |
| N-17 | Xác định năm công bố theo quy tắc kỳ | Lưu ba mốc: ngày DOI, ngày online first, năm/số phát hành chính thức; năm tính theo cấu hình của loại báo cáo, không lấy ngày DOI (BR-21) | P1 |
| N-14 | Gom cụm từ khoá | Ánh xạ từ khoá về danh mục hướng đề tài của khoa (mã định hướng) thay vì tự dựng trục chủ đề; 76% từ khoá hiện chỉ xuất hiện một lần | P2 |
| N-15 | Báo cáo chất lượng dữ liệu | Bảng độ phủ theo trường, theo đơn vị, theo kỳ | P2 |

## Kê khai và lập hồ sơ (K)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| K-01 | Xem danh sách gợi ý theo khoa | Công trình hệ thống cho là thuộc khoa trong kỳ, kèm căn cứ | P1 |
| K-02 | Tạo hồ sơ kê khai từ gợi ý | Điền sẵn trường lấy từ kho, đánh dấu rõ nguồn từng trường | P1 |
| K-03 | Tạo hồ sơ kê khai thủ công | Cho công trình chưa có trong nguồn nào | P1 |
| K-04 | Đính kèm minh chứng | Tệp hoặc liên kết; ghi loại minh chứng | P1 |
| K-05 | Xem cảnh báo trên hồ sơ | Phân hai mức: chặn và cảnh cáo | P1 |
| K-06 | Gửi yêu cầu bổ sung | Gắn trực tiếp vào hồ sơ, chỉ rõ đang chờ ai | P1 |
| K-07 | Rút hồ sơ | Trước khi trình duyệt | P2 |
| K-08 | Xem tiến độ kê khai của khoa | Bao nhiêu hồ sơ ở trạng thái nào, đang chờ ai | P1 |
| K-09 | Kê khai công trình của tôi | Giảng viên tự kê khai và xác nhận | P2 |

## Duyệt (D)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| D-01 | Tạo bản trình duyệt | Đóng gói danh sách, số liệu tổng hợp, nguồn, cảnh báo còn lại | P1 |
| D-02 | Xem phần thay đổi so với lần trình trước | Chỉ rõ công trình thêm, bớt, sửa | P1 |
| D-03 | Phê duyệt bản trình của khoa | Đóng băng phiên bản; ghi người duyệt và thời điểm | P1 |
| D-04 | Trả lại kèm lý do | Lý do bắt buộc, gắn vào hồ sơ cụ thể | P1 |
| D-05 | Huỷ dấu đã duyệt khi nội dung đổi | Tự động khi danh sách hoặc số liệu trọng yếu thay đổi | P1 |
| D-06 | Theo dõi tiến độ nộp theo khoa | Khoa nào đã gửi, chưa gửi, còn bao nhiêu ngày | P1 |
| D-07 | Nhắc hạn tự động | Thay việc nhắc thủ công từng đơn vị | P2 |
| D-08 | Quản lý hàng đợi kiểm tra | Ưu tiên hồ sơ có cảnh báo hoặc thiếu minh chứng | P1 |
| D-09 | Yêu cầu điều chỉnh từ cấp trường | Trả về đơn vị, theo dõi tới khi xử lý xong | P1 |

## Chốt và báo cáo (R)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| R-01 | Chốt dữ liệu kỳ | Khoá tập hồ sơ dùng lập báo cáo; sinh mã phiên bản | P1 |
| R-02 | Mở lại kỳ đã chốt | Sinh phiên bản mới, giữ nguyên phiên bản cũ | P1 |
| R-03 | Xuất báo cáo toàn trường | Số công trình duy nhất sau chuẩn hoá | P1 |
| R-04 | Xuất báo cáo theo khoa | Ghi nhận sự tham gia của khoa, không cộng cơ học thành tổng trường | P1 |
| R-05 | Truy ngược một con số | Bấm vào chỉ tiêu ra danh sách công trình và nguồn từng bản ghi | P1 |
| R-06 | Xuất tệp | Định dạng theo yêu cầu quản lý; kèm mã phiên bản và thời điểm | P1 |
| R-07 | So sánh giữa các kỳ | Diễn biến theo năm hoặc theo kỳ | P2 |
| R-08 | Xem lịch sử phê duyệt của báo cáo | Ai lập, ai kiểm tra, ai duyệt, mốc thời gian | P1 |
| R-09 | Trình lãnh đạo trường ký báo cáo chính thức | Sau khi phòng chốt; lãnh đạo trường phê duyệt hoặc trả lại kèm lý do; báo cáo nội bộ bỏ qua (BR-24) | P1 |
| R-10 | So sánh hai phiên bản báo cáo | Số cũ, số mới, lý do đổi, danh sách công trình thêm/bớt/sửa, và báo cáo nào đã dùng phiên bản cũ (BR-25) | P1 |

## Tra cứu và đối chiếu đề tài (T)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| T-01 | Tìm công trình | Theo từ khoá, tác giả, năm, loại, đơn vị | P1 |
| T-02 | Xem hồ sơ công bố của giảng viên | Danh sách và phân bố theo năm, chủ đề; xuất được danh sách cá nhân để dùng cho khoa, phòng, hồ sơ đánh giá, không phải nhập lại | P1 |
| T-03 | Nhập đề tài dự kiến | Hướng đề tài (chọn từ danh mục khoa), tên, vấn đề, đối tượng, phương pháp, dữ liệu dự kiến. GVHD nhập khi chuẩn bị đề cương; sinh viên nhập khi tìm hướng trước lúc liên hệ GVHD | P2 |
| T-04 | Đối chiếu đề tài với kho | Trả về công trình liên quan kèm mức tương đồng | P2 |
| T-05 | Lập bảng so sánh có giải thích | Giống ở bài toán nào, khác về đối tượng/phạm vi/phương pháp | P2 |
| T-06 | Hiển thị mức dữ liệu đang có | Nói rõ đang so trên tóm tắt, không phải toàn văn | P1 |
| T-07 | Lưu tài liệu đã chọn | Danh mục cá nhân | P3 |
| T-08 | Xuất trích dẫn | APA, IEEE, BibTeX | P2 |
| T-09 | Xuất bảng đối chiếu để đính vào đề cương | Tệp kèm nhận xét, nộp cùng đề cương cho lãnh đạo bộ môn | P3 |
| T-10 | Thống kê hợp tác quốc tế | Theo định nghĩa của trường (Q-28), không suy từ DOI hay Scopus; cần trường cơ quan của tác giả mà kho chưa có | P2 |

## Quản trị (A)

| Mã | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| A-01 | Quản lý kỳ báo cáo | Tạo, mở, đóng nộp, huỷ | P1 |
| A-02 | Quản lý quy tắc thống kê | Quy tắc tính năm, loại công trình, đồng tác giả, đơn vị | P1 |
| A-03 | Quản lý người dùng và vai trò | Gán vai trò theo đơn vị | P1 |
| A-04 | Quản lý danh mục | Đơn vị, loại công trình (khởi tạo từ 9 nhóm phòng đang dùng, đánh dấu nháp tới khi có văn bản), chỉ mục, mức điểm, hướng đề tài (mã định hướng, bộ CLO + PI, có hiệu lực theo thời gian) | P1 |
| A-07 | Quản lý mẫu báo cáo | Mỗi kỳ gắn một mẫu: cấp trên hoặc nội bộ; mẫu khai cột, quy tắc năm công bố, tiêu chí đơn vị chủ trì; R-06 xuất theo mẫu này | P1 |
| A-05 | Cấu hình lịch đồng bộ | Tần suất, phạm vi | P2 |
| A-06 | Xem nhật ký hệ thống | Đồng bộ, lỗi, thay đổi cấu hình | P2 |
