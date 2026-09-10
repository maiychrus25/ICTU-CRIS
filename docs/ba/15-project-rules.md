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
| BR-19 | Đối chiếu đề tài chạy ở giai đoạn chọn đề tài, trước hạn nộp đề cương; không thay thế kiểm tra đạo văn cuối kỳ | Kế hoạch ĐATN tách hai mốc: đề cương đầu kỳ (mốc 2), kiểm tra đạo văn trên quyển báo cáo cuối kỳ (mốc 5) bằng công cụ riêng của khoa |
| BR-20 | Hướng đề tài là danh mục đóng của khoa, gắn bộ CLO + PI cố định | GVHD chọn hướng, không sửa CLO + PI; hệ thống ánh xạ chủ đề về danh mục này thay vì tự dựng |
| BR-21 | Năm công bố là quy tắc cấu hình theo loại báo cáo, không lấy ngày DOI. Hệ thống lưu riêng ba mốc: ngày DOI, ngày online first, năm/số phát hành chính thức | Khảo sát đợt 1: phòng căn cứ năm xuất bản chính thức trên ấn phẩm và quy định của loại báo cáo; ca Online First năm trước, Issue năm sau phải theo quy tắc của kỳ |
| BR-22 | Đơn vị chủ trì của công trình là trường riêng do người xác định, tách khỏi đơn vị của từng tác giả | Khảo sát đợt 1: phòng không muốn gán một bài vào một khoa theo danh sách tác giả; khi báo cáo đòi một đơn vị thì cần tiêu chí riêng (chủ trì, tác giả đầu, khai báo khi đăng ký) |
| BR-23 | Phòng KH-CN không tự sửa các trường thuộc trách nhiệm xác nhận của khoa và giảng viên: tác giả, đơn vị, minh chứng. Sai thì trả về khoa | Khảo sát đợt 1, câu 9 |
| BR-24 | Báo cáo chính thức gửi cấp trên phải qua lãnh đạo trường phê duyệt sau khi phòng chốt số liệu | Khảo sát đợt 1, câu 10: khoa xác nhận → phòng chốt → lãnh đạo trường ký |
| BR-25 | Mỗi phiên bản báo cáo phải trả lời được: số cũ, số mới, vì sao đổi, báo cáo nào đã dùng số cũ | Khảo sát đợt 1, câu 11: pain point lớn nhất của phòng khi điều chỉnh |

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

Gom toàn bộ `[CẦN XÁC NHẬN]` rải trong bộ tài liệu. Nên đi theo **một kỳ báo cáo gần nhất** và yêu cầu người dùng kể lại từng bước. Dòng **Manh mối** ghi điều đã biết từ kế hoạch triển khai ĐATN K21, chỉ áp dụng cho quy trình đồ án, chưa chắc đúng cho kỳ báo cáo công bố.

### Về quy trình

| # | Câu hỏi | Ảnh hưởng nếu trả lời khác giả định |
|---|---|---|
| Q-01 | Ai phát yêu cầu, ai lập, ai kiểm tra, ai duyệt? **Đã xác nhận đợt 1:** phòng phát yêu cầu → khoa gom → lãnh đạo khoa xác nhận danh sách → phòng kiểm tra, chốt → lãnh đạo trường ký báo cáo chính thức | Đã thêm actor `school_leader` (BR-24); không có cấp lãnh đạo phòng riêng; cấp bộ môn chỉ có trong luồng đề tài |
| Q-02 | Lãnh đạo khoa duyệt từng công trình hay cả danh sách? | Đổi thiết kế màn SC-06 và trạng thái hồ sơ |
| Q-03 | Khi phòng chức năng trả lại, ai sửa và có cần duyệt lại không? | Đổi luồng UC-11 và quy tắc BR-13 |
| Q-04 | Ai có quyền chốt, mở lại và phát hành báo cáo chính thức? | Đổi ma trận phân quyền |
| Q-05 | Hiện dùng biểu mẫu, công cụ nào; dữ liệu lấy từ đâu? Manh mối: quy trình đồ án dùng Google Sheets danh sách tổng hợp, Google Drive nộp tệp, email, bản cứng ký sống và PDF ký số | Quyết định có cần nhập từ tệp cũ hay không; đã thêm S-08 nhập từ bảng đăng ký đồ án |
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
| Q-11 | **Bản nộp gốc (toàn văn) của đồ án, luận văn đang nằm ở đâu?** Kho chỉ có tóm tắt 1 trang do máy sinh. Manh mối: sau bảo vệ, sinh viên nộp quyển bìa cứng kèm file mềm cho Thư viện trường (mốc 12) | Nếu thư viện cho truy cập, mở lại được mức dữ liệu thứ hai và phạm vi đề tài đổi đáng kể |
| Q-12 | Tóm tắt tiếng Anh trong PDF do ai tạo — dịch từ bản tiếng Việt hay sinh mới? | Quyết định mức tin cậy khi dùng làm cơ sở đối chiếu |
| Q-13 | 4.621 đồ án mất tên GVHD — nguồn nhập gốc còn không? Manh mối: mỗi khoá có bảng đăng ký đồ án trên Google Sheets ghi cặp sinh viên–GVHD | Nếu bảng các khoá cũ còn, đây là việc khôi phục dữ liệu qua S-08; nếu mất, phải thiết kế trên 14% có tên |
| Q-14 | ORCID trên hồ sơ giảng viên do ai nhập, có đối chiếu không? | ORCID là khoá nối tốt nhất đang có (phủ 91%); cần biết độ tin cậy |
| Q-15 | Trường "đơn vị" của bài báo hiện được gán theo quy tắc nào? | 37% bài chưa có đơn vị; cần biết quy tắc cũ trước khi thay |
| Q-16 | Có nguồn công bố nào ngoài kho cần đồng bộ không (Scopus, WoS, Scholar)? | Đổi phạm vi giai đoạn `S` |

### Về hệ thống

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q-17 | Trường có SSO không, và ánh xạ vai trò lấy từ đâu? | NFR-01, NFR-02 |
| Q-18 | Kho ICTU có được sửa không, hay hệ thống mới chỉ đọc? | Nếu sửa được, ba lỗi chặn nên sửa ở nguồn thay vì bù ở hệ thống mới |
| Q-19 | Ai vận hành hệ thống sau khi bàn giao? | NFR-33, PR-03 |

### Bổ sung từ kế hoạch triển khai ĐATN K21

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q-20 | Hệ thống có được đọc Google Sheets danh sách đăng ký và Google Drive nộp tệp của khoa không, hay phải nhập tay? | Quyết định cách làm S-08 và có lấy được đề cương, quyển báo cáo hay không |
| Q-21 | Danh mục hướng đề tài có bao nhiêu mã định hướng, ai quản, có đổi theo năm không? | BR-20, N-14, A-04 |
| Q-22 | Công cụ kiểm tra đạo văn ở mốc 5 là gì, kết quả có xuất ra để đối chiếu với bảng đối chiếu đề tài không? | BR-19; quyết định có tích hợp hay chỉ tham chiếu |
| Q-23 | Thư viện trường có cho hệ thống truy cập file mềm đồ án đã nộp không, từ khoá nào? | Q-11; mở hay đóng mức dữ liệu toàn văn |
| Q-24 | Nếu ICTU-CRIS đi theo lịch này (thực hiện 09/03–22/05, nộp quyển 01/06), lát cắt nào của 60 chức năng P1 là phạm vi bản đầu? | Đề xuất: giai đoạn S, N và T-01, T-02, vì có số đo và giá trị chứng minh rõ nhất; phần kê khai và duyệt cần khảo sát người dùng mà lịch không còn chỗ. Người chủ trì quyết |

## 15.4 Bộ tài liệu dự án phải duy trì

| Tài liệu | Trạng thái |
|---|---|
| BRD — yêu cầu nghiệp vụ | Chưa lập. Nên lập sau buổi khảo sát xác nhận §15.3 |
| SRS — đặc tả phần mềm, kèm ma trận truy vết BR → FR → UC → US | Chưa lập |
| Bộ BA (16 tệp này) | Bản 1.0, ngày 10/09/2026 |
| Mô hình dữ liệu | Bản 0.1 cho lát cắt S + N + T-01/T-02 — [17-mo-hinh-du-lieu.md](17-mo-hinh-du-lieu.md). Phần kỳ, kê khai, báo cáo chờ Q-07..Q-10 và tài liệu còn nợ ở §15.6 |
| Khảo sát nguồn dữ liệu | Có — [khao-sat-nguon/](../../khao-sat-nguon/README.md) |
| Kiểm chứng giả định bằng số đo | Có — [kiem-chung-gia-dinh-de-tai.md](../../khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md) |
| Kế hoạch triển khai ĐATN ĐHCQ K21 (Khoa CNTT, 26/02/2026) | Có — [docs/KH triển khai ĐATN_DHCQ_K21.docx](../KH%20triển%20khai%20ĐATN_DHCQ_K21.docx). Quy trình thật đầu tiên trong repo, chỉ cho luồng đồ án |

## 15.5 Giới hạn của bản 1.0 này

Bộ tài liệu này viết trên cơ sở hai tài liệu định hướng, số đo trên dữ liệu công khai, kế hoạch triển khai ĐATN K21, và trả lời khảo sát đợt 1 (§15.6). Trả lời đợt 1 nhận bằng văn bản, chưa kèm file báo cáo mẫu và biểu mẫu khoa; hai tệp đó được hẹn cung cấp ở buổi gặp trực tiếp. Luồng kỳ báo cáo ở [01-bpmn.md](01-bpmn.md) §1.1 đã được xác nhận về trình tự và bổ sung cấp lãnh đạo trường, còn phải xác nhận bằng tài liệu thật về mẫu báo cáo và quy tắc thống kê. Luồng đối chiếu đề tài ở §1.2 bám theo kế hoạch ĐATN thật, phần còn phải xác nhận là quyền truy cập dữ liệu (Q-20, Q-23).

Phần đã có cơ sở vững: mọi số đo về dữ liệu nguồn, các ràng buộc kỹ thuật, các quy tắc nghiệp vụ suy ra trực tiếp từ số đo (BR-06..BR-10), hai quy tắc suy từ kế hoạch ĐATN (BR-19, BR-20), và năm quy tắc suy từ khảo sát đợt 1 (BR-21..BR-25).

## 15.6 Kết quả khảo sát đợt 1

Trả lời bằng văn bản ngày 10/09/2026 từ ba tầng: Phòng KH-CN & HTQT, văn phòng khoa CNTT, giảng viên. Theo kịch bản [16-kich-ban-khao-sat.md](16-kich-ban-khao-sat.md). Trạng thái: **XN** đã xác nhận giả định · **ĐỔI** giả định phải sửa · **MỞ** chưa trả lời được, ghi ai trả lời.

### Phòng KH-CN & HTQT

| Q | Trả lời | Trạng thái | Thay đổi trong bộ BA |
|---|---|---|---|
| Q-16 | Không có nguồn duy nhất: Excel các khoa gửi, đối chiếu kho repository, kiểm Scopus/WoS khi cần, DOI và web tạp chí. Có dùng vài hệ thống chung của ĐHTN nhưng không hệ thống nào là nguồn chuẩn | ĐỔI | Kho là nguồn tham chiếu, không phải nguồn chính. S-06 nhập Excel lên P1 hàng đầu; thêm S-09 đối chiếu nguồn chỉ mục ngoài (P2) |
| Q-05 | Báo cáo tổng hợp KH-CN theo năm, gửi Ban giám hiệu hoặc ĐHTN tuỳ loại. Mẫu khác nhau giữa các kỳ: mẫu cấp trên và mẫu nội bộ. File kỳ gần nhất sẽ cung cấp | ĐỔI | Thêm A-07 quản lý mẫu báo cáo; R-06 xuất theo mẫu đã khai. **Còn nợ:** file Excel/PDF kỳ gần nhất |
| Q-07 | Không lấy ngày DOI. Căn cứ năm xuất bản chính thức trên ấn phẩm và quy định của loại báo cáo. Online First năm trước, Issue năm sau phải theo quy tắc của báo cáo | ĐỔI | BR-21; mô hình dữ liệu lưu ba mốc ngày; năm công bố tính theo cấu hình kỳ |
| Q-08 | Một bài đếm một công trình cho trường; mỗi giảng viên tham gia đều được ghi nhận. Phải đối chiếu quy chế thi đua trước khi thành quy tắc chính thức | XN | BR-02, BR-03 đúng. **Còn nợ:** văn bản quy chế thi đua hoặc quy định thống kê KHCN |
| Q-09 | Không gán một bài vào một khoa theo tác giả. Thống kê theo khoa ghi nhận mọi khoa có người tham gia. Khi báo cáo đòi một đơn vị thì cần tiêu chí riêng. Hệ thống phải có "đơn vị chủ trì" và "đơn vị của từng tác giả" | XN + ĐỔI | Quan hệ nhiều-nhiều đúng (BR-02). Thêm BR-22, trường đơn vị chủ trì; N-13 chỉ suy đơn vị tham gia, không suy đơn vị chủ trì |
| Q-10 | Chín nhóm đang dùng: bài báo khoa học, bài quốc tế, bài trong nước, hội thảo, sách/chương sách, giáo trình, đề tài/dự án, sáng chế/giải pháp hữu ích, sản phẩm KHCN khác. Chưa phải master data | ĐỔI | A-04 khởi tạo từ danh sách này, đánh dấu nháp. Phát sinh Q-25 về phạm vi: sáu nhóm sau không có trong kho |
| Q-01 | Phòng phát yêu cầu qua email/văn bản → khoa gom từ giảng viên → gửi phòng → phòng tiếp nhận, kiểm tra, tổng hợp | XN | Luồng §1.1 đúng trình tự |
| Q-02 | Lãnh đạo khoa xác nhận danh sách trước khi gửi, không duyệt từng bài | XN | SC-06 bản trình là danh sách, đúng thiết kế |
| Q-03 | Phòng trả lại khoa, không tự sửa tác giả, đơn vị, minh chứng. Có phải trình trưởng khoa lại không thì tuỳ tính chất, cần quy định rõ | XN + ĐỔI | BR-23; siết O* của `rd_officer` trong ma trận. BR-13 giữ, cần định nghĩa "trọng yếu" (Q-26) |
| Q-04 | Phòng chốt số liệu nghiệp vụ; báo cáo chính thức còn lãnh đạo trường phê duyệt/ký trước khi gửi cấp trên | ĐỔI | BR-24; thêm actor `school_leader`; thêm trạng thái `ChoTruongDuyet`; R-09 |
| BR-15 | Sai sau khi báo cáo thì lập bảng điều chỉnh; không có versioning chuẩn; bản cũ nằm ở file đã gửi. Phải trả lời: số cũ, vì sao đổi, số mới, báo cáo nào đã dùng số cũ | XN | BR-25; R-10 so sánh phiên bản và liệt kê báo cáo đã dùng; US-35 |
| Q-06 | Không có SLA; một kỳ kéo dài nhiều ngày đến vài tuần. Bước làm lại nhiều nhất: đối chiếu và sửa dữ liệu (thiếu minh chứng, sai tên, sai năm, trùng, sai loại, nguồn không khớp) | XN | Ưu tiên giai đoạn N đúng. Sáu lỗi này là bộ kiểm thử cho K-05 |
| Q-15, Q-18 | Nhập kho do thư viện/quản trị/đầu mối được phân công, không phải phòng. Sửa được nhưng không phải ai cũng sửa mọi trường. Trường "đơn vị" không có một quy tắc | XN | Kho chỉ đọc đối với hệ thống mới. Q-18 chuyển sang: hỏi quản trị kho có sửa ba lỗi chặn không |
| Q-13 | Bảng đăng ký đồ án các khoá trước có, rải ở Drive/Sheets của khoa hoặc thư viện, không tập trung | XN | S-08 khả thi; cần quyền theo Q-20 |
| Q-17 | Có email tổ chức và xác thực dùng chung; SSO cho kho thì tuỳ triển khai. Phòng yêu cầu BA xác minh với IT | MỞ | Người trả lời: IT/quản trị hệ thống |
| Q-19 | Cần đầu mối vận hành kỹ thuật; phòng là chủ sở hữu nghiệp vụ, không lo server, CSDL, sao lưu | MỞ một phần | Phát sinh Q-27: đơn vị kỹ thuật nào nhận vận hành |
| §14.7 hợp tác quốc tế | Có nhu cầu: tác giả nước ngoài, cơ quan nước ngoài, hợp tác nghiên cứu. Phải định nghĩa trước, không suy từ DOI hay Scopus | ĐỔI | Thêm T-10 (P2) và Q-28 định nghĩa hợp tác quốc tế |

### Văn phòng khoa CNTT

| # | Trả lời | Trạng thái | Thay đổi |
|---|---|---|---|
| 1 | Nhận yêu cầu qua email/văn bản; gửi giảng viên qua email hoặc nhóm khoa; thu bằng form/Excel/Google Form/Sheet tuỳ đợt; gom thành bảng tổng hợp. Biểu mẫu do khoa cung cấp | XN | S-06 phải chịu được mẫu thay đổi theo đợt. **Còn nợ:** biểu mẫu kỳ gần nhất |
| 2 | Luôn có người phải nhắc; khoa theo dõi đã nộp/chưa nộp thủ công | XN | K-08, D-06, D-07 đúng nhu cầu |
| 3 | Khoa có tra lại kho, DOI, trang tạp chí, nguồn chỉ mục khi nghi ngờ | XN | UX-02 đúng: điền sẵn và ghi nguồn giảm việc tra tay |
| 4 | Trưởng khoa duyệt danh sách tổng hợp; có trả lại khi thiếu hoặc sai | XN | D-03, D-04 đúng |
| 5 | Phòng trả về thì đầu mối khoa liên hệ giảng viên; thay đổi ảnh hưởng danh sách đã xác nhận thì phải xác nhận lại | XN | BR-13 đúng; "trọng yếu" = ảnh hưởng danh sách đã xác nhận (đầu vào cho Q-26) |
| 6 | Bảng đăng ký đồ án có trên Sheets/Drive khoa; phải được cấp quyền xem | XN | Q-20: cần xin quyền từ khoa |
| 7 | Mã hướng đề tài do khoa quản, đầu mối được trưởng khoa phân công; số lượng và cấu trúc đổi theo giai đoạn | ĐỔI | A-04 danh mục hướng đề tài phải có hiệu lực theo thời gian |
| 8 | Có công cụ kiểm tra đạo văn, xuất báo cáo tỷ lệ tương đồng và nguồn; công cụ cụ thể có thể đổi | XN một phần | Q-22 giữ mở về tên công cụ; BR-19 đúng |
| 9 | Tốn thời gian nhất: thiếu thông tin → hỏi giảng viên → sửa → trưởng khoa xác nhận → gửi phòng → phòng trả về → sửa tiếp | XN | Chính là vòng lặp UX-01, K-06 giải quyết |

### Giảng viên

| # | Trả lời | Trạng thái | Thay đổi |
|---|---|---|---|
| 1 | Phải kê khai nhiều lần cho khoa, phòng, hồ sơ cá nhân, đánh giá; cùng công trình nhập nhiều nơi | XN | US-10 đúng; thêm US-39 xuất danh sách cá nhân dùng cho mục đích khác |
| 2 | ORCID có nhưng không đồng đều; cập nhật hồ sơ trường do đầu mối làm, không tự đồng bộ | ĐỔI | Q-14: độ tin cậy ORCID trung bình; N-02 giữ ưu tiên nhưng cần cờ "ORCID đã kiểm" |
| 3 | Tên quốc tế viết tắt, đảo, không dấu, khác nhau giữa các bài; trùng tên cần thêm đơn vị, email, ORCID | XN | N-01, N-03 đúng; ứng viên khớp tên phải kèm đơn vị và email |
| 4 | Minh chứng: bản bài, DOI/link, thông tin tạp chí, quyết định/chứng nhận, tuỳ loại và đợt | XN | K-04 liệt kê loại minh chứng theo loại công trình |
| 5 | Quyển đồ án lưu tại khoa và/hoặc thư viện; cho tra file mềm hay không tuỳ quyền truy cập và bản quyền; không mặc định công khai toàn văn | XN | Q-11, Q-23: toàn văn có nhưng hạn chế; giữ đối chiếu ở mức tóm tắt, toàn văn là tuỳ chọn có phân quyền |

### Câu hỏi phát sinh sau đợt 1

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q-25 | Phạm vi công trình của hệ thống có gồm đề tài/dự án, sách, giáo trình, sáng chế không? Kho công khai chỉ có bài báo, đồ án, luận văn, luận án | Nếu có, phần lớn dữ liệu đến từ Excel khoa (S-06), không từ đồng bộ kho |
| Q-26 | Thay đổi nào là "trọng yếu" buộc trình lại lãnh đạo khoa? Đề xuất: thêm/bớt công trình, đổi tác giả thuộc khoa, đổi loại, đổi năm | BR-13, D-05 |
| Q-27 | Đơn vị kỹ thuật nào nhận vận hành sau bàn giao: Trung tâm CNTT, thư viện, hay thuê ngoài? | NFR-32, NFR-33 |
| Q-28 | Định nghĩa "hợp tác quốc tế" của trường là gì: có tác giả thuộc cơ quan nước ngoài, có tài trợ nước ngoài, hay đồng chủ trì? | T-10; kho không có trường cơ quan của tác giả |

### Tài liệu còn nợ

- File báo cáo Excel/PDF kỳ gần nhất của phòng.
- Biểu mẫu kê khai kỳ gần nhất của khoa.
- Văn bản quy chế thi đua hoặc quy định thống kê KHCN.
- Quyền đọc bảng đăng ký đồ án các khoá.

Phần cần xác nhận: toàn bộ vai trò, thẩm quyền và trình tự phê duyệt.
