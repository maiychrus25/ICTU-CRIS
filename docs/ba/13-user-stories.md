# 13. User story và AC — ICTU-CRIS

Ưu tiên: `P1` phải có ở bản đầu · `P2` nên có · `P3` để sau. AC theo khuôn *when / who / how / then*.

## Đồng bộ và chất lượng dữ liệu

| # | Tiêu đề | User story | Ưu tiên | AC | Trace |
|---|---|---|---|---|---|
| US-01 | Đồng bộ không mất bản ghi | Là chuyên viên phòng, tôi muốn biết chắc lần đồng bộ lấy đủ dữ liệu | P1 | When: chạy đồng bộ. Who: rd_officer. How: bấm Đồng bộ. Then: báo cáo nêu số lấy được và số nguồn công bố; lệch thì tự quét bù và ghi cảnh báo nếu vẫn lệch | S-01, S-03, S-04 |
| US-02 | Không mất tác giả do cắt cụt | Là chuyên viên phòng, tôi muốn danh sách tác giả đầy đủ chứ không phải bản rút gọn | P1 | When: đồng bộ. Who: hệ thống. How: đọc trang chi tiết từng công trình. Then: 0 bản ghi có danh sách tác giả kết thúc bằng dấu cắt cụt | S-02 |
| US-03 | Giữ được giá trị gốc | Là chuyên viên phòng, tôi muốn đối chiếu lại với nguồn khi có nghi vấn | P1 | When: xem một trường đã chuẩn hoá. Who: rd_officer. How: mở hồ sơ. Then: thấy cả giá trị gốc, giá trị chuẩn hoá và nguồn | S-07, N-01 |
| US-04 | Biết dữ liệu có tin được không | Là chuyên viên phòng, tôi muốn biết mức đầy đủ của dữ liệu trước khi lập báo cáo | P1 | When: mở màn chất lượng dữ liệu. Who: rd_officer. How: xem bảng độ phủ. Then: thấy độ phủ theo trường, số chưa nối tác giả, số chưa có đơn vị, số nghi trùng chờ xử lý | N-15 |
| US-05 | Không đoán khi không suy được | Là chuyên viên phòng, tôi không muốn hệ thống tự bịa giá trị | P1 | When: chuẩn hoá gặp giá trị lạ. Who: hệ thống. How: chạy chuẩn hoá. Then: giữ nguyên gốc, gắn cờ cần rà tay, không gán bừa | N-11 |

## Liên kết tác giả

| # | Tiêu đề | User story | Ưu tiên | AC | Trace |
|---|---|---|---|---|---|
| US-06 | Nối tác giả bằng ORCID | Là chuyên viên phòng, tôi muốn dùng định danh chuẩn thay vì đoán theo tên | P1 | When: có ORCID ở cả hai phía. Who: hệ thống. How: chạy nối. Then: nối tự động, độ tin cậy ghi là `orcid` | N-02 |
| US-07 | Nối tác giả khi tên viết khác nhau | Là chuyên viên phòng, tôi muốn nối được cả khi tên ghi không dấu kiểu quốc tế | P1 | When: tên dạng `The-Vinh Nguyen` và hồ sơ ghi `Nguyễn Thế Vịnh`. Who: hệ thống. How: chuẩn hoá rồi khớp. Then: nhận ra là một người; khớp duy nhất thì nối tự động | N-01, N-03 |
| US-08 | Xác nhận ca mơ hồ, không tự quyết | Là chuyên viên phòng, tôi muốn hệ thống hỏi thay vì chọn liều khi trùng tên | P1 | When: một tên khớp nhiều giảng viên. Who: hệ thống. How: chạy nối. Then: không tự nối; đưa vào hàng đợi kèm danh sách ứng viên và căn cứ | N-03, N-04 |
| US-09 | Không tự chọn học vị khi mâu thuẫn | Là chuyên viên phòng, tôi muốn được cảnh báo khi cùng một người có hai học vị khác nhau | P1 | When: cùng người ghi cả `TS.` và `ThS.`. Who: hệ thống. How: chuẩn hoá tên. Then: cảnh báo mâu thuẫn, không tự chọn một giá trị | N-06 |
| US-10 | Giảng viên tự xác nhận công trình | Là giảng viên, tôi muốn nhận đúng những bài của mình mà không phải kê khai lại | P1 | When: có công trình chờ xác nhận. Who: lecturer. How: chọn nhiều, xác nhận một lần. Then: liên kết chuyển `DaXacNhan`; bác bỏ thì ghi phủ định | N-04, N-05 |
| US-11 | Không bị hỏi lại điều đã bác bỏ | Là giảng viên, tôi không muốn hệ thống đề xuất lại cặp tôi đã nói là sai | P2 | When: đã bác bỏ một cặp. Who: hệ thống. How: chạy nối lần sau. Then: cặp đó không xuất hiện lại trong hàng đợi | N-05 |
| US-12 | Suy đơn vị từ tác giả | Là chuyên viên phòng, tôi muốn công trình có đơn vị mà không phải gán tay từng bài | P1 | When: công trình đã nối tác giả. Who: hệ thống. How: chạy suy đơn vị. Then: đơn vị suy từ tác giả; công trình nhiều khoa ghi nhận nhiều đơn vị | N-13 |

## Nghi trùng

| # | Tiêu đề | User story | Ưu tiên | AC | Trace |
|---|---|---|---|---|---|
| US-13 | Phát hiện trùng theo DOI | Là chuyên viên phòng, tôi muốn thấy ngay hai bản ghi cùng một DOI | P1 | When: hai công trình cùng DOI. Who: hệ thống. How: chạy đối soát. Then: ghép thành nhóm nghi trùng, xếp đầu hàng đợi | N-07 |
| US-14 | So sánh trước khi gộp | Là chuyên viên phòng, tôi muốn thấy hai bản khác nhau chỗ nào trước khi quyết định | P1 | When: mở một nhóm nghi trùng. Who: rd_officer. How: xem khung so sánh. Then: hiện cạnh nhau từng trường, tô đậm chỗ khác; gộp thì chọn được giá trị giữ lại cho từng trường | N-09 |
| US-15 | Không gộp nhầm đồ án nhóm | Là chuyên viên phòng, tôi không muốn mất bản ghi thật vì nhiều sinh viên cùng đề tài | P1 | When: hai đồ án trùng tiêu đề nhưng khác sinh viên. Who: hệ thống. How: chạy đối soát. Then: đề xuất Giữ riêng kèm cảnh báo đồ án nhóm; khoá gộp gồm sinh viên và khoá | N-08, N-10 |
| US-16 | Gộp không mất dấu vết | Là chuyên viên phòng, tôi muốn xem lại được hai bản gốc sau khi đã gộp | P1 | When: đã gộp. Who: rd_officer. How: mở công trình. Then: thấy lịch sử gộp và cả hai bản gốc | N-09 |

## Kê khai và duyệt

| # | Tiêu đề | User story | Ưu tiên | AC | Trace |
|---|---|---|---|---|---|
| US-17 | Không nhập lại thứ đã có | Là chuyên viên khoa, tôi muốn bắt đầu từ danh sách có sẵn chứ không từ trang trắng | P1 | When: kỳ đang mở. Who: faculty_officer. How: mở danh sách gợi ý. Then: thấy công trình hệ thống tìm được cho khoa; tạo hồ sơ đã điền sẵn, mỗi trường ghi rõ nguồn | K-01, K-02 |
| US-18 | Biết hồ sơ đang chờ ai | Là chuyên viên khoa, tôi muốn biết việc nào kẹt ở người nào | P1 | When: xem danh sách hồ sơ. Who: faculty_officer. How: mở `/ho-so`. Then: mỗi hồ sơ hiện người đang chờ và thời gian đã chờ | W-03, K-08 |
| US-19 | Yêu cầu bổ sung gắn vào hồ sơ | Là chuyên viên khoa, tôi muốn yêu cầu đi kèm hồ sơ chứ không nằm trong email riêng | P1 | When: hồ sơ thiếu minh chứng. Who: faculty_officer. How: bấm Gửi yêu cầu bổ sung. Then: yêu cầu hiện trên hồ sơ, người nhận thấy trong bảng công việc | K-06 |
| US-20 | Cảnh báo phân hai mức | Là chuyên viên khoa, tôi muốn biết cái gì buộc phải sửa và cái gì chỉ cần ghi chú | P1 | When: chạy kiểm tra. Who: hệ thống. How: mở hồ sơ. Then: cảnh báo tách hai mức; mức chặn không cho trình duyệt | K-05 |
| US-21 | Duyệt mà không phải kiểm lại từ đầu | Là lãnh đạo khoa, tôi muốn thấy ngay lần này khác lần trước chỗ nào | P1 | When: bản trình lần thứ hai trở đi. Who: faculty_head. How: mở bản trình. Then: khối thay đổi liệt kê công trình thêm, bớt, sửa | D-02 |
| US-22 | Biết mình đang xác nhận điều gì | Là lãnh đạo khoa, tôi muốn rõ phạm vi trước khi ký | P1 | When: mở bản trình. Who: faculty_head. How: xem đầu trang. Then: hiện kỳ, phạm vi, quy tắc thống kê, người lập, người kiểm tra, và câu nêu rõ phê duyệt này không phải công nhận chất lượng học thuật | D-01, UC-10 |
| US-23 | Trả lại phải có lý do | Là chuyên viên khoa, tôi muốn biết vì sao bị trả lại để sửa đúng chỗ | P1 | When: lãnh đạo trả lại. Who: faculty_head. How: bấm Trả lại. Then: lý do bắt buộc, gắn vào hồ sơ cụ thể; hồ sơ về Nháp kèm thông báo | D-04 |
| US-24 | Dấu đã duyệt không tồn tại cho nội dung khác | Là lãnh đạo khoa, tôi không muốn chữ ký của mình đứng trên danh sách đã bị sửa | P1 | When: hồ sơ đã duyệt bị sửa trường trọng yếu. Who: hệ thống. How: lưu thay đổi. Then: huỷ dấu đã duyệt, đưa về Nháp, yêu cầu trình lại | D-05 |
| US-25 | Người lập không tự duyệt | Là lãnh đạo khoa, tôi muốn hệ thống chặn việc một người vừa lập vừa duyệt | P1 | When: người tạo bản trình mở màn duyệt. Who: hệ thống. How: kiểm quyền. Then: không hiện nút Phê duyệt | D-03 |

## Đối soát cấp trường, chốt và báo cáo

| # | Tiêu đề | User story | Ưu tiên | AC | Trace |
|---|---|---|---|---|---|
| US-26 | Theo dõi tiến độ không phải nhắc tay | Là chuyên viên phòng, tôi muốn biết khoa nào chưa gửi mà không phải gọi từng nơi | P1 | When: kỳ đang mở. Who: rd_officer. How: mở chi tiết kỳ. Then: bảng theo khoa hiện đã gửi / chưa gửi / bị trả lại và ngày còn lại | D-06 |
| US-27 | Một công trình nhiều khoa kê khai chỉ đếm một lần | Là chuyên viên phòng, tôi muốn tổng toàn trường không bị cộng trùng | P1 | When: hai khoa cùng kê khai một công trình. Who: hệ thống. How: đối soát. Then: hai lượt kê khai nối về một công trình; tổng toàn trường đếm một | N-07, R-03 |
| US-28 | Số liệu không đổi sau khi chốt | Là chuyên viên phòng, tôi muốn con số đã báo cáo giữ nguyên | P1 | When: kỳ đã chốt. Who: rd_officer. How: xem báo cáo. Then: số liệu không đổi; muốn sửa phải Mở lại kỳ và sinh phiên bản mới, phiên bản cũ giữ nguyên | R-01, R-02 |
| US-29 | Truy được một con số về từng bài | Là chuyên viên phòng, tôi muốn giải trình được ngay khi bị hỏi trong họp | P1 | When: xem báo cáo. Who: rd_officer. How: bấm vào một chỉ tiêu. Then: mở danh sách công trình; bấm tiếp một dòng ra bản ghi gốc, nguồn, đơn vị kê khai, lịch sử duyệt. Tối đa hai lần bấm | R-05 |
| US-30 | Không cộng cơ học các khoa thành tổng trường | Là chuyên viên phòng, tôi muốn báo cáo tự nói rõ điều này | P1 | When: xem bảng theo khoa. Who: rd_officer. How: mở báo cáo. Then: bảng ghi chú tổng các khoa không phải tổng công trình duy nhất của trường, kèm số công trình liên khoa | R-04 |
| US-31 | Xem lại ai đã duyệt cái gì | Là chuyên viên phòng, tôi muốn xác định trách nhiệm khi có sai sót | P1 | When: mở báo cáo hoặc hồ sơ. Who: rd_officer. How: xem lịch sử. Then: hiện người lập, người kiểm tra, người duyệt và mốc thời gian | R-08, W-05 |
| US-35 | Giải thích được mọi điều chỉnh sau khi đã báo cáo | Là chuyên viên phòng, tôi muốn biết số cũ, số mới, vì sao đổi và báo cáo nào đã dùng số cũ | P1 | When: mở lại kỳ đã chốt. Who: rd_officer. How: so sánh hai phiên bản. Then: hiện số cũ, số mới, lý do, công trình thêm/bớt/sửa, và danh sách báo cáo đã phát hành từ phiên bản cũ | R-02, R-10 |
| US-36 | Ký báo cáo mà không phải kiểm lại số | Là lãnh đạo trường, tôi muốn thấy phòng đã chốt gì, đổi gì so với lần trước, rồi ký hoặc trả lại | P1 | When: kỳ ở ChoTruongDuyet. Who: school_leader. How: mở báo cáo trình ký. Then: hiện chỉ tiêu, bảng theo khoa, lịch sử chốt, phần thay đổi; hai nút Phê duyệt và Trả lại kèm lý do; không có nút sửa | R-09 |
| US-37 | Năm công bố không phụ thuộc ngày DOI | Là chuyên viên phòng, tôi muốn hệ thống tính năm theo quy tắc của loại báo cáo | P1 | When: công trình có ngày DOI, ngày online first và số phát hành khác năm. Who: hệ thống. How: áp quy tắc năm của kỳ. Then: năm tính đúng theo cấu hình; cả ba mốc vẫn lưu và hiện trên hồ sơ | N-17, A-07 |
| US-38 | Đơn vị chủ trì do người chọn | Là chuyên viên phòng, tôi không muốn hệ thống tự gán một bài vào một khoa | P1 | When: mẫu báo cáo đòi một đơn vị cho mỗi công trình. Who: rd_officer. How: chọn đơn vị chủ trì theo tiêu chí kỳ. Then: đơn vị chủ trì lưu riêng; đơn vị tham gia của từng tác giả không đổi | N-13, N-16 |
| US-39 | Kê khai một lần, dùng nhiều nơi | Là giảng viên, tôi không muốn nhập lại cùng công trình cho khoa, phòng và hồ sơ đánh giá | P2 | When: cần danh sách công bố cho một mục đích. Who: lecturer. How: xuất từ hồ sơ công bố. Then: tệp danh sách theo bộ lọc năm và loại, kèm thời điểm đồng bộ và trạng thái xác nhận từng công trình | T-02 |

## Tra cứu và đối chiếu đề tài

| # | Tiêu đề | User story | Ưu tiên | AC | Trace |
|---|---|---|---|---|---|
| US-32 | Xem hồ sơ công bố của một giảng viên | Là giảng viên, tôi muốn xem công bố của đồng nghiệp trong ba năm gần đây | P1 | When: mở hồ sơ giảng viên. Who: mọi vai trò. How: lọc theo năm. Then: danh sách và phân bố theo năm; ghi rõ thời điểm đồng bộ gần nhất và số công trình chưa xác nhận | T-02 |
| US-33 | Đối chiếu đề tài có giải thích | Là sinh viên, tôi muốn biết đề tài của mình khác các đề tài trước ở điểm nào | P2 | When: nhập mô tả đề tài. Who: student. How: bấm Đối chiếu. Then: bảng so sánh theo khía cạnh (bài toán, đối tượng, phạm vi, phương pháp) với ba trạng thái giống / khác / chưa đủ thông tin; không có điểm phần trăm tổng hợp | T-04, T-05 |
| US-34 | Biết mình đang so trên cái gì | Là giảng viên, tôi muốn biết kết quả dựa trên dữ liệu ở mức nào | P1 | When: xem kết quả đối chiếu. Who: lecturer. How: mở trang kết quả. Then: hiện rõ "so trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn" | T-06 |
