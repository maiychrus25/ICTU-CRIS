# 11. Đặc tả use case — ICTU-CRIS

Khuôn mỗi use case: actor · tiền điều kiện · luồng chính · luồng thay thế · hậu điều kiện · quy tắc nghiệp vụ · mã chức năng.

## UC-01 Đồng bộ dữ liệu từ kho

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`, `admin`; hệ thống nguồn `repository` |
| Tiền điều kiện | Cấu hình nguồn hợp lệ |
| Luồng chính | 1. Chọn phạm vi và chạy đồng bộ. 2. Hệ thống đọc danh mục từng loại tài liệu. 3. Đọc trang chi tiết từng công trình. 4. Đối soát số bản ghi lấy được với số nguồn công bố. 5. Lưu bản ghi thô kèm giá trị gốc. 6. Ghi báo cáo kết quả đồng bộ |
| Luồng thay thế | 4a. Lệch số lượng → quét bù theo bộ lọc, lặp lại bước 4; nếu vẫn lệch, ghi cảnh báo và nêu số bản ghi chưa lấy được. 3a. Trang chi tiết lỗi → ghi nhận, tiếp tục, liệt kê ở cuối |
| Hậu điều kiện | Bản ghi thô có trong hệ thống; báo cáo đồng bộ nêu rõ số thêm, sửa, biến mất, lỗi |
| Quy tắc | Không ghi đè im lặng. Bản ghi biến mất ở nguồn được đánh dấu, không xoá |
| Chức năng | S-01..S-05, S-07 |

## UC-02 Chuẩn hoá dữ liệu công trình

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`, `admin` |
| Tiền điều kiện | Có bản ghi thô |
| Luồng chính | 1. Chuẩn hoá tên người. 2. Chuẩn hoá tên đơn vị về mã danh mục. 3. Tách trường loại công trình thành chỉ mục, loại nơi công bố, điểm. 4. Chuẩn hoá năm. 5. Đánh dấu bản ghi không suy được để rà tay |
| Luồng thay thế | 3a. Giá trị không khớp quy tắc nào → giữ nguyên gốc, gắn cờ `cần rà tay`, không đoán |
| Hậu điều kiện | Mỗi bản ghi có cả giá trị gốc và giá trị chuẩn hoá; tỷ lệ cần rà tay được ghi vào báo cáo chất lượng |
| Quy tắc | Chuẩn hoá không bao giờ ghi đè giá trị gốc |
| Chức năng | N-01, N-11, N-12, N-15 |

## UC-03 Nối tác giả với hồ sơ giảng viên

| Mục | Nội dung |
|---|---|
| Actor | Hệ thống (tự động); `rd_officer`, `faculty_officer`, `lecturer` (xác nhận) |
| Tiền điều kiện | Đã chuẩn hoá tên; có hồ sơ giảng viên |
| Luồng chính | 1. Khớp theo ORCID. 2. Với phần chưa nối, khớp theo tên chuẩn hoá. 3. Khớp duy nhất → nối tự động, ghi độ tin cậy. 4. Khớp nhiều người hoặc một phần → đưa vào hàng đợi. 5. Người có thẩm quyền xác nhận hoặc bác bỏ. 6. Suy đơn vị của công trình từ tác giả đã nối |
| Luồng thay thế | 5a. Bác bỏ → ghi nhận phủ định, không đề xuất lại cặp đó. 3a. Ứng viên có mâu thuẫn học vị giữa các bản ghi → không tự chọn, đưa vào hàng đợi kèm cảnh báo |
| Hậu điều kiện | Liên kết công trình ↔ tác giả ↔ đơn vị có trạng thái và độ tin cậy |
| Quy tắc | Chỉ hai mức tin cậy cao nhất (`orcid`, `ten_day_du_duy_nhat`) được nối tự động |
| Chức năng | N-02..N-06, N-13 |

## UC-04 Xử lý bản ghi nghi trùng

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` |
| Tiền điều kiện | Đã chuẩn hoá |
| Luồng chính | 1. Hệ thống ghép ứng viên theo DOI. 2. Ghép tiếp theo tiêu đề chuẩn hoá. 3. Hiển thị so sánh cạnh nhau, tô đậm trường khác nhau. 4. Người dùng chọn Gộp hoặc Giữ riêng. 5. Nếu gộp, chọn giá trị giữ lại cho từng trường mâu thuẫn. 6. Lưu kết quả kèm lịch sử hai bản gốc |
| Luồng thay thế | 2a. Hai bản khác sinh viên (đồ án) → hệ thống đề xuất **Giữ riêng** kèm cảnh báo "nhiều khả năng là đồ án nhóm". 4a. Bỏ qua tạm → giữ trong hàng đợi |
| Hậu điều kiện | Công trình ở trạng thái `DaGop` hoặc `GiuRieng`; số liệu tính lại |
| Quy tắc | Khoá gộp đồ án bắt buộc gồm sinh viên và khoá, không chỉ tiêu đề. Gộp không xoá bản gốc |
| Chức năng | N-07..N-10 |

## UC-05 Xem báo cáo chất lượng dữ liệu

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`, `admin`, vai trò khoa (phạm vi khoa) |
| Luồng chính | 1. Mở màn chất lượng dữ liệu. 2. Xem độ phủ theo trường, số chưa nối tác giả, số chưa có đơn vị, số nghi trùng chưa xử lý, kết quả đồng bộ gần nhất. 3. Bấm vào một chỉ số để mở hàng đợi tương ứng |
| Hậu điều kiện | Người dùng biết mức tin cậy của số liệu trước khi dùng |
| Chức năng | N-15 |

## UC-06 Mở kỳ báo cáo

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` |
| Luồng chính | 1. Tạo kỳ: tên, phạm vi, tiêu chí, hạn nộp, quy tắc thống kê áp dụng. 2. Chạy đồng bộ cho phạm vi kỳ. 3. Dựng danh sách gợi ý theo từng khoa. 4. Mở kỳ và gửi thông báo tới các khoa |
| Luồng thay thế | 2a. Đồng bộ có cảnh báo → hiện cảnh báo, cho phép mở kỳ nhưng ghi nhận vào hồ sơ kỳ |
| Hậu điều kiện | Kỳ ở trạng thái `DangMo`; các khoa nhận thông báo và thấy gợi ý |
| Quy tắc | Quy tắc thống kê gắn vào kỳ tại thời điểm mở, không đổi giữa kỳ |
| Chức năng | A-01, A-02, S-01, K-01, W-04 |

## UC-07 Lập hồ sơ kê khai

| Mục | Nội dung |
|---|---|
| Actor | `faculty_officer` |
| Tiền điều kiện | Kỳ ở `DangMo`; người dùng thuộc một khoa |
| Luồng chính | 1. Mở danh sách gợi ý. 2. Chọn công trình đưa vào kê khai. 3. Hệ thống tạo hồ sơ, điền sẵn từ kho, đánh dấu nguồn từng trường. 4. Bổ sung công trình ngoài kho. 5. Đính minh chứng. 6. Chạy kiểm tra, xử lý cảnh báo chặn |
| Luồng thay thế | 4a. Công trình đã được khoa khác kê khai → hệ thống báo và nối cả hai lượt về cùng một công trình. 6a. Cần người khác cung cấp → gửi yêu cầu bổ sung, hồ sơ chuyển `ChoBoSung` |
| Hậu điều kiện | Hồ sơ ở `Nhap`, không còn cảnh báo chặn |
| Quy tắc | Một công trình có nhiều hồ sơ kê khai; không tạo công trình mới cho mỗi lượt kê khai |
| Chức năng | K-01..K-07 |

## UC-08 Bổ sung minh chứng

| Mục | Nội dung |
|---|---|
| Actor | `lecturer`, `faculty_officer` |
| Tiền điều kiện | Có yêu cầu bổ sung gắn vào hồ sơ |
| Luồng chính | 1. Mở yêu cầu từ thông báo hoặc bảng công việc. 2. Đính tệp hoặc liên kết, ghi loại minh chứng. 3. Gửi. 4. Hồ sơ về `Nhap`, Văn phòng khoa được thông báo |
| Luồng thay thế | 2a. Không có minh chứng → trả lời kèm lý do; Văn phòng khoa quyết định giữ hay bỏ công trình |
| Chức năng | K-04, K-06, W-04 |

## UC-09 Trình duyệt hồ sơ khoa

| Mục | Nội dung |
|---|---|
| Actor | `faculty_officer` |
| Tiền điều kiện | Có ít nhất một hồ sơ ở `Nhap`, không còn cảnh báo chặn |
| Luồng chính | 1. Chọn hồ sơ đưa vào bản trình. 2. Hệ thống đóng gói: danh sách, số liệu tổng hợp, nguồn, cảnh báo còn lại, phần thay đổi so với lần trình trước. 3. Gửi lãnh đạo khoa |
| Luồng thay thế | 1a. Còn cảnh báo chặn → không cho trình, chỉ rõ hồ sơ nào |
| Hậu điều kiện | Hồ sơ chuyển `ChoKhoaDuyet` |
| Quy tắc | Người tạo bản trình không được là người phê duyệt |
| Chức năng | D-01, D-02 |

## UC-10 Phê duyệt bản trình của khoa

| Mục | Nội dung |
|---|---|
| Actor | `faculty_head` |
| Tiền điều kiện | Có bản trình ở `ChoKhoaDuyet` |
| Luồng chính | 1. Mở bản trình. 2. Xem phạm vi, quy tắc thống kê, danh sách, cảnh báo còn lại, phần thay đổi. 3. Bấm **Phê duyệt**. 4. Hệ thống đóng băng phiên bản, ghi người duyệt và thời điểm. 5. Chuyển phiên bản đã duyệt sang phòng chức năng |
| Luồng thay thế | 3a. **Trả lại** → nhập lý do (bắt buộc), chọn hồ sơ liên quan; hồ sơ về `Nhap`. 4a. Sau khi duyệt, nội dung bị sửa → huỷ dấu đã duyệt, đưa về `Nhap`, yêu cầu trình lại |
| Hậu điều kiện | Hồ sơ ở `KhoaDaDuyet` rồi `ChoPhongKiemTra`; hoặc quay về `Nhap` kèm lý do |
| Quy tắc | Lãnh đạo khoa **phê duyệt phiên bản hồ sơ do khoa lập để gửi phòng chức năng** — không phải công nhận chất lượng học thuật, không xác nhận tình trạng Scopus/WoS, không quyết định khen thưởng hay giờ nghiên cứu. Ghi rõ câu này trên màn hình duyệt |
| Chức năng | D-03..D-05 |

## UC-11 Kiểm tra hồ sơ cấp trường

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` |
| Tiền điều kiện | Có hồ sơ ở `ChoPhongKiemTra` |
| Luồng chính | 1. Mở hàng đợi, ưu tiên hồ sơ có cảnh báo hoặc thiếu minh chứng. 2. Kiểm tra thông tin xuất bản và minh chứng. 3. Đối soát toàn trường: nhận diện công trình được nhiều khoa kê khai. 4. Liên kết các lượt kê khai vào một công trình. 5. Chấp nhận |
| Luồng thay thế | 5a. Không đạt → trả về đơn vị kèm lý do; theo dõi tới khi xử lý xong |
| Hậu điều kiện | Hồ sơ ở `DatYeuCau` hoặc quay về `Nhap` |
| Chức năng | D-08, D-09, N-07..N-10 |

## UC-12 Yêu cầu điều chỉnh

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` |
| Luồng chính | 1. Chọn hồ sơ. 2. Nhập lý do và nội dung cần sửa. 3. Gửi về đơn vị. 4. Theo dõi trạng thái tới khi xử lý xong |
| Quy tắc | Lý do bắt buộc và gắn vào hồ sơ cụ thể, không gửi chung chung cho cả khoa |
| Chức năng | D-09 |

## UC-13 Chốt dữ liệu kỳ báo cáo

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` |
| Tiền điều kiện | Không còn hồ sơ ở `ChoPhongKiemTra` |
| Luồng chính | 1. Bấm Chốt dữ liệu. 2. Hệ thống hiện hộp xác nhận: số hồ sơ, số công trình duy nhất, mã phiên bản sẽ sinh. 3. Xác nhận. 4. Khoá tập hồ sơ, sinh mã phiên bản |
| Luồng thay thế | 4a. Phát hiện sai sau khi chốt → **Mở lại kỳ**: sinh phiên bản mới, giữ nguyên phiên bản cũ |
| Hậu điều kiện | Kỳ ở `DaChot`; số liệu không đổi cho tới khi mở lại |
| Quy tắc | Không sửa số liệu trong một phiên bản đã chốt. Mọi điều chỉnh tạo phiên bản mới |
| Chức năng | R-01, R-02 |

## UC-14 Xuất báo cáo và truy ngược chỉ tiêu

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`; `faculty_head` (phạm vi khoa) |
| Tiền điều kiện | Kỳ ở `DaChot` |
| Luồng chính | 1. Mở báo cáo. 2. Xem chỉ tiêu tổng hợp, bảng theo khoa, theo năm, theo loại. 3. Bấm một chỉ tiêu để mở danh sách công trình tạo nên nó. 4. Bấm một dòng để xem bản ghi gốc, nguồn, đơn vị kê khai, lịch sử duyệt. 5. Xuất tệp |
| Hậu điều kiện | Tệp xuất kèm mã phiên bản và thời điểm |
| Quy tắc | Báo cáo toàn trường tính **số công trình duy nhất**. Báo cáo theo khoa ghi nhận **sự tham gia** của khoa. Tổng các khoa không phải tổng công trình duy nhất — ghi chú này bắt buộc hiện trên bảng theo khoa |
| Chức năng | R-03..R-06, R-08 |

## UC-15 Tra cứu công trình và hồ sơ công bố

| Mục | Nội dung |
|---|---|
| Actor | Tất cả vai trò người dùng |
| Luồng chính | 1. Nhập từ khoá hoặc chọn bộ lọc. 2. Xem kết quả kèm số lượng theo loại tài liệu. 3. Mở chi tiết công trình hoặc hồ sơ giảng viên. 4. Xuất trích dẫn |
| Luồng thay thế | 3a. Giảng viên còn công trình chưa nối → hiện dòng "còn N công trình nghi thuộc người này chưa được xác nhận" |
| Quy tắc | Số liệu trên hồ sơ giảng viên ghi rõ tính trên dữ liệu đã đồng bộ, kèm thời điểm đồng bộ gần nhất |
| Chức năng | T-01, T-02, T-07, T-08 |

## UC-16 Đối chiếu đề tài dự kiến

| Mục | Nội dung |
|---|---|
| Actor | `student`, `lecturer` |
| Luồng chính | 1. Nhập tên đề tài, vấn đề, đối tượng, phương pháp, dữ liệu dự kiến. 2. Chạy đối chiếu. 3. Hệ thống trả về công trình liên quan kèm bảng so sánh theo khía cạnh. 4. Người dùng chỉnh mô tả, chạy lại. 5. Gửi giảng viên kèm bảng đối chiếu |
| Luồng thay thế | 3a. Không đủ thông tin để so một khía cạnh → ghi rõ *chưa đủ thông tin để so*, không đoán |
| Hậu điều kiện | Bảng đối chiếu lưu được, xuất được, gửi được |
| Quy tắc | Không hiển thị điểm số phần trăm tương đồng tổng hợp. Ghi rõ mức dữ liệu: so trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn. Đầu ra là tài liệu hỗ trợ xem xét, không phải quyết định |
| Chức năng | T-03..T-06, T-09 |
