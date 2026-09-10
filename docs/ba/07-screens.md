# 7. Mô tả màn hình — ICTU-CRIS

Mã màn `SC-xx`. Mỗi màn ghi: đường dẫn, actor, mục đích, thành phần chính, hành động, trạng thái rỗng.

## SC-01 Bảng công việc của tôi (`/`)

| Mục | Nội dung |
|---|---|
| Actor | Tất cả vai trò người dùng |
| Mục đích | Trả lời "hôm nay tôi phải làm gì" trong một màn |
| Thành phần | Kỳ đang hoạt động và ngày còn lại · Nhóm thẻ theo trạng thái (nháp, chờ tôi xử lý, đang chờ người khác, bị trả lại) · Danh sách việc chờ tôi, sắp theo hạn · Thông báo gần đây |
| Hành động | Mở hồ sơ · Mở kỳ · Đánh dấu đã đọc thông báo |
| Rỗng | "Không có việc nào đang chờ bạn trong kỳ này" kèm liên kết sang danh sách hồ sơ của đơn vị |

Nội dung thẻ khác nhau theo vai trò: `faculty_officer` thấy hồ sơ của khoa; `faculty_head` thấy bản trình chờ duyệt; `rd_officer` thấy tiến độ nộp toàn trường và hàng đợi kiểm tra.

## SC-02 Danh sách kỳ báo cáo (`/ky-bao-cao`)

| Mục | Nội dung |
|---|---|
| Actor | Tất cả (nội dung theo phạm vi đơn vị) |
| Thành phần | Bảng kỳ: tên, phạm vi, hạn nộp, trạng thái, số hồ sơ của đơn vị mình |
| Hành động | Mở kỳ · `rd_officer`: Tạo kỳ mới |

## SC-03 Chi tiết kỳ báo cáo (`/ky-bao-cao/[id]`)

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` (đầy đủ), vai trò khoa (thu gọn theo phạm vi) |
| Thành phần | Thẻ thông tin kỳ: phạm vi, tiêu chí, quy tắc thống kê đang áp dụng, hạn nộp · Bảng tiến độ theo khoa: đã gửi / chưa gửi / bị trả lại, thanh tiến độ, ngày còn lại · Hàng đợi kiểm tra · Khối chốt dữ liệu |
| Hành động | Mở / đóng nộp kỳ · Nhắc hạn · Mở hàng đợi · Chốt dữ liệu · Mở lại kỳ · Xuất báo cáo |
| Ràng buộc | Nút **Chốt dữ liệu** chỉ bật khi không còn hồ sơ ở trạng thái `ChoPhongKiemTra`. Bấm chốt hiện hộp xác nhận nêu rõ số hồ sơ, số công trình duy nhất và mã phiên bản sẽ sinh |

## SC-04 Danh sách hồ sơ kê khai (`/ho-so`)

| Mục | Nội dung |
|---|---|
| Actor | `faculty_officer`, `rd_officer` |
| Thành phần | Thanh lọc: kỳ, trạng thái, đang chờ ai, có cảnh báo · Bảng hồ sơ: tiêu đề công trình, tác giả thuộc khoa, loại, trạng thái, người đang chờ, số cảnh báo · Khối gợi ý "Công trình hệ thống tìm thấy cho khoa bạn — chưa được kê khai" |
| Hành động | Tạo hồ sơ từ gợi ý (chọn nhiều) · Tạo thủ công · Mở hồ sơ · Xuất danh sách |
| Rỗng | Nếu chưa đồng bộ: "Chưa có dữ liệu đồng bộ cho kỳ này". Nếu đã đồng bộ mà không có gợi ý: nêu rõ có thể do liên kết tác giả chưa đủ, kèm liên kết sang `/chat-luong-du-lieu` |

## SC-05 Chi tiết hồ sơ kê khai (`/ho-so/[id]`)

| Mục | Nội dung |
|---|---|
| Actor | `faculty_officer` (sửa), các vai trò khác (xem) |
| Thành phần | Khối trường dữ liệu — mỗi trường hiện **giá trị đang dùng**, **giá trị gốc** và **nguồn** (kho ICTU / kê khai / sửa tay) · Khối tác giả: danh sách, trạng thái liên kết từng người · Khối minh chứng · Khối cảnh báo tách hai mức · Khối trao đổi và yêu cầu bổ sung · Dòng thời gian trạng thái |
| Hành động | Sửa trường · Thêm minh chứng · Gửi yêu cầu bổ sung · Xác nhận liên kết tác giả · Rút hồ sơ · Đưa vào bản trình |
| Ràng buộc | Sửa trường trọng yếu khi hồ sơ đã ở `KhoaDaDuyet` sẽ hiện cảnh báo: thao tác này huỷ dấu đã duyệt và đưa hồ sơ về `Nhap` |

## SC-06 Bản trình duyệt (`/trinh-duyet/[id]`)

| Mục | Nội dung |
|---|---|
| Actor | `faculty_head` (duyệt), `faculty_officer` (tạo, xem) |
| Mục đích | Đủ để lãnh đạo khoa xác nhận trong vài phút mà không phải kiểm lại từ đầu |
| Thành phần | Đầu trang: kỳ, phạm vi, quy tắc thống kê đang áp dụng, người lập, người kiểm tra · Số liệu tổng hợp · Danh sách công trình kèm tác giả thuộc khoa và nguồn · Khối cảnh báo còn lại · **Khối thay đổi so với lần trình trước**: thêm / bớt / sửa |
| Hành động | **Phê duyệt** · **Trả lại kèm lý do** (lý do bắt buộc, chọn hồ sơ liên quan) · Xem chi tiết từng hồ sơ |
| Ràng buộc | Không có nút sửa nội dung. Không phê duyệt được nếu còn cảnh báo mức chặn |

## SC-07 Hàng đợi nghi trùng (`/doi-soat/trung-lap`)

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer` |
| Thành phần | Danh sách cặp/nhóm nghi trùng, sắp theo độ tin cậy (DOI trùng lên đầu) · Khung so sánh cạnh nhau: từng trường, tô đậm chỗ khác nhau · Căn cứ ghép |
| Hành động | **Gộp** (chọn giá trị giữ lại cho từng trường mâu thuẫn) · **Giữ riêng** kèm lý do · Bỏ qua tạm |
| Ràng buộc | Với đồ án, nếu hai bản khác sinh viên thì hệ thống hiện cảnh báo "nhiều khả năng là đồ án nhóm" và mặc định đề xuất **Giữ riêng** |

## SC-08 Hàng đợi liên kết tác giả (`/doi-soat/tac-gia`)

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`, `faculty_officer` (phạm vi khoa), `lecturer` (bản thân) |
| Thành phần | Danh sách chuỗi tên chưa nối, kèm số công trình bị ảnh hưởng · Ứng viên đề xuất kèm độ tin cậy và căn cứ (ORCID / tên chuẩn hoá) · Cảnh báo mâu thuẫn học vị |
| Hành động | Xác nhận · Bác bỏ · Chọn người khác · **Xử lý hàng loạt** cho cùng một chuỗi tên |
| Ghi chú | Đây là màn có tác động lớn nhất tới chất lượng số liệu; ưu tiên thao tác nhanh và bàn phím |

## SC-09 Báo cáo kỳ (`/bao-cao/[id]`)

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`, `faculty_head` (phạm vi khoa) |
| Thành phần | Đầu trang: mã phiên bản, thời điểm chốt, quy tắc thống kê · Chỉ tiêu tổng hợp · Bảng theo khoa · Bảng theo năm và theo loại · Lịch sử phê duyệt |
| Hành động | Bấm bất kỳ chỉ tiêu nào để mở danh sách công trình tạo nên nó · Xuất tệp · So sánh với kỳ trước |
| Ràng buộc | Mỗi bảng ghi rõ **quy tắc đếm** đang dùng. Bảng theo khoa ghi chú: tổng các khoa không phải tổng công trình duy nhất của trường |

## SC-10 Chất lượng dữ liệu (`/chat-luong-du-lieu`)

| Mục | Nội dung |
|---|---|
| Actor | `rd_officer`, `admin`, vai trò khoa (phạm vi khoa) |
| Thành phần | Độ phủ theo trường (có / thiếu / chưa chuẩn hoá) · Số công trình chưa nối tác giả · Số chưa có đơn vị · Số nghi trùng chưa xử lý · Kết quả lần đồng bộ gần nhất, gồm cả cảnh báo lệch số lượng |
| Hành động | Mở hàng đợi tương ứng · Chạy đồng bộ lại |
| Mục đích | Trả lời trước câu hỏi "số liệu này có tin được không" thay vì để người dùng phát hiện sau |

## SC-11 Tìm công trình (`/tra-cuu`)

| Mục | Nội dung |
|---|---|
| Actor | Tất cả |
| Thành phần | Ô tìm · Bộ lọc: loại, năm, đơn vị, tác giả, chỉ mục · Kết quả kèm nhãn loại và năm · Số lượng theo từng loại tài liệu |
| Hành động | Mở chi tiết · Lưu vào danh mục · Xuất trích dẫn |
| Ràng buộc | Bộ lọc phải giữ được ngữ cảnh khi tìm trong một loại tài liệu cụ thể |

## SC-12 Hồ sơ công bố giảng viên (`/tra-cuu/giang-vien/[id]`)

| Mục | Nội dung |
|---|---|
| Actor | Tất cả |
| Thành phần | Thông tin cơ bản và định danh ngoài (ORCID, Google Scholar) · Số đếm theo loại công trình · Phân bố theo năm · Danh sách công trình theo nhóm |
| Ràng buộc | Ghi rõ số liệu tính trên dữ liệu đã đồng bộ, kèm thời điểm đồng bộ gần nhất. Nếu giảng viên có công trình chưa nối, hiện dòng "còn N công trình nghi thuộc người này chưa được xác nhận" |

## SC-13 Đối chiếu đề tài (`/doi-chieu`)

| Mục | Nội dung |
|---|---|
| Actor | `student`, `lecturer` |
| Thành phần | Biểu mẫu nhập: tên đề tài, vấn đề giải quyết, đối tượng, phương pháp, dữ liệu dự kiến · Nút chạy đối chiếu |
| Ràng buộc | Ghi rõ ngay trên biểu mẫu: kết quả là tài liệu tham khảo cho giảng viên xem xét, không phải kết luận về tính mới hay đạo văn |

## SC-14 Kết quả đối chiếu (`/doi-chieu/[id]`)

| Mục | Nội dung |
|---|---|
| Actor | `student`, `lecturer` |
| Thành phần | Danh sách công trình liên quan · Với mỗi công trình: **bảng so sánh theo khía cạnh** (bài toán, đối tượng, phạm vi, phương pháp) với ba trạng thái: giống / khác / chưa đủ thông tin để so · Nhãn mức dữ liệu: "so trên tiêu đề, tóm tắt và từ khoá" |
| Hành động | Chỉnh mô tả và chạy lại · Gửi giảng viên · Xuất bảng đối chiếu |
| Ràng buộc | **Không hiển thị một điểm số phần trăm tương đồng tổng hợp.** Một con số duy nhất tạo cảm giác kết luận; bảng theo khía cạnh buộc người đọc tự đánh giá |
