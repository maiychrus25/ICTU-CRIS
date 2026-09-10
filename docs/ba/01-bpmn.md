# 1. Sơ đồ BPMN — ICTU-CRIS

## 1.1 Kỳ báo cáo công bố khoa học (quy trình lõi)

```mermaid
flowchart TD
    A["Phòng KH-CN &amp; HTQT mở kỳ báo cáo<br/>(phạm vi, tiêu chí, hạn nộp)"]
    B["Hệ thống đồng bộ kho ICTU<br/>và dựng danh sách gợi ý theo khoa"]
    C["Văn phòng khoa lập hồ sơ kê khai<br/>từ gợi ý + bổ sung công trình ngoài kho"]
    D["Hệ thống kiểm tra tự động:<br/>thiếu trường, nghi trùng, tác giả chưa nối"]
    E{"Còn cảnh báo chặn?"}
    F["Văn phòng khoa xử lý cảnh báo,<br/>yêu cầu giảng viên bổ sung minh chứng"]
    G["Trình lãnh đạo khoa"]
    H{"Lãnh đạo khoa xem xét"}
    I["Đóng băng phiên bản đã duyệt<br/>và gửi phòng chức năng"]
    J["Phòng chức năng kiểm tra hồ sơ<br/>và đối soát toàn trường"]
    K{"Đạt yêu cầu?"}
    L["Chốt dữ liệu kỳ báo cáo<br/>(khoá phiên bản)"]
    M["Xuất báo cáo kèm danh sách đối chứng"]

    A --> B --> C --> D --> E
    E -- "Có" --> F --> D
    E -- "Không" --> G --> H
    H -- "Trả lại kèm lý do" --> C
    H -- "Phê duyệt" --> I --> J --> K
    K -- "Trả về đơn vị kèm lý do" --> C
    K -- "Đạt" --> L --> M
```

Ba điểm khác so với luồng trong tài liệu định hướng:

1. Thêm bước **B (đồng bộ kho)** trước khi khoa lập hồ sơ. Đây là chỗ giải quyết vấn đề *"có nhập lại thông tin đã nằm trong kho không"* — khoa bắt đầu từ danh sách gợi ý, không từ trang trắng.
2. **D là vòng lặp có điều kiện**, không phải một bước thẳng. Hồ sơ chỉ được trình khi hết cảnh báo chặn; cảnh báo cảnh cáo thì cho qua kèm ghi chú.
3. **I là bước đóng băng phiên bản**, tách khỏi hành động phê duyệt. Điều này thực hiện yêu cầu *"sau khi duyệt, phiên bản đó phải được giữ nguyên"*.

## 1.2 Đối chiếu đề tài dự kiến (quy trình phụ, độc lập)

Theo khuyến nghị tách luồng riêng trong tài liệu phân tích quy trình. Luồng này **không** đi qua Phòng KH-CN & HTQT.

```mermaid
flowchart TD
    A["Sinh viên nhập đề tài dự kiến<br/>(tên, vấn đề, đối tượng, phương pháp)"]
    B["Hệ thống tìm công trình tương tự<br/>trong đồ án, luận văn, luận án, bài báo"]
    C["Hệ thống lập bảng đối chiếu:<br/>giống ở đâu, khác ở đâu, chỗ nào chưa đủ căn cứ"]
    D["Sinh viên xem, chỉnh mô tả, chạy lại"]
    E["Gửi giảng viên/bộ môn kèm bảng đối chiếu"]
    F{"Người có chuyên môn nhận xét"}
    G["Cấp có thẩm quyền quyết định<br/>theo quy trình đào tạo hiện hành"]

    A --> B --> C --> D
    D -- "Chạy lại" --> B
    D -- "Nộp" --> E --> F
    F -- "Yêu cầu chỉnh đề tài" --> A
    F -- "Đồng ý trình" --> G
```

Ràng buộc: đầu ra của bước C là **báo cáo hỗ trợ xem xét**, không phải quyết định "được làm / không được làm". Hệ thống không kết luận đạo văn và không khẳng định tính mới.
