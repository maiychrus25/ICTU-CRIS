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
    M["Lập báo cáo theo mẫu của kỳ<br/>kèm danh sách đối chứng"]
    N{"Báo cáo chính thức gửi cấp trên?"}
    O["Lãnh đạo trường phê duyệt, ký"]
    P["Phát hành"]

    A --> B --> C --> D --> E
    E -- "Có" --> F --> D
    E -- "Không" --> G --> H
    H -- "Trả lại kèm lý do" --> C
    H -- "Phê duyệt" --> I --> J --> K
    K -- "Trả về đơn vị kèm lý do" --> C
    K -- "Đạt" --> L --> M --> N
    N -- "Có" --> O --> P
    N -- "Nội bộ" --> P
```

Bốn điểm khác so với luồng trong tài liệu định hướng:

1. Thêm bước **B (đồng bộ kho)** trước khi khoa lập hồ sơ. Đây là chỗ giải quyết vấn đề *"có nhập lại thông tin đã nằm trong kho không"* — khoa bắt đầu từ danh sách gợi ý, không từ trang trắng. Khảo sát đợt 1 cho biết kho chỉ là nguồn tham chiếu; nguồn chính hiện là Excel các khoa gửi, nên bước C phải nhận cả nhập tệp.
2. **D là vòng lặp có điều kiện**, không phải một bước thẳng. Hồ sơ chỉ được trình khi hết cảnh báo chặn; cảnh báo cảnh cáo thì cho qua kèm ghi chú.
3. **I là bước đóng băng phiên bản**, tách khỏi hành động phê duyệt. Điều này thực hiện yêu cầu *"sau khi duyệt, phiên bản đó phải được giữ nguyên"*.
4. **N–O là cấp lãnh đạo trường**, bổ sung theo khảo sát đợt 1: phòng chốt số liệu nghiệp vụ, báo cáo chính thức gửi ĐHTN hoặc cấp trên còn phải lãnh đạo trường ký (BR-24). Báo cáo nội bộ không qua bước này.

## 1.2 Đối chiếu đề tài dự kiến (quy trình phụ, độc lập)

Theo khuyến nghị tách luồng riêng trong tài liệu phân tích quy trình. Luồng này **không** đi qua Phòng KH-CN & HTQT. Trình tự bám theo kế hoạch triển khai ĐATN của Khoa CNTT (mốc 1–3): sinh viên liên hệ GVHD, GVHD chọn hướng đề tài và soạn đề cương, lãnh đạo bộ môn duyệt.

```mermaid
flowchart TD
    A["Sinh viên liên hệ GVHD,<br/>nêu nguyện vọng đề tài"]
    B["GVHD chọn hướng đề tài trong danh mục khoa,<br/>nhập đề tài dự kiến (tên, vấn đề, đối tượng, phương pháp)"]
    C["Hệ thống tìm công trình tương tự<br/>trong đồ án, luận văn, luận án, bài báo"]
    D["Hệ thống lập bảng đối chiếu:<br/>giống ở đâu, khác ở đâu, chỗ nào chưa đủ căn cứ"]
    E["GVHD và sinh viên xem, chỉnh mô tả, chạy lại"]
    F["GVHD soạn đề cương theo mẫu của hướng đề tài,<br/>đính bảng đối chiếu (ngoài hệ thống)"]
    G{"Lãnh đạo bộ môn xem xét đề cương"}
    H["Nộp đề cương về khoa<br/>theo quy trình đào tạo hiện hành"]

    A --> B --> C --> D --> E
    E -- "Chạy lại" --> C
    E -- "Chốt mô tả" --> F --> G
    G -- "Yêu cầu chỉnh đề tài" --> B
    G -- "Duyệt" --> H
```

Ràng buộc: đầu ra của bước D là **báo cáo hỗ trợ xem xét**, không phải quyết định "được làm / không được làm". Hệ thống không kết luận đạo văn và không khẳng định tính mới.

Hai mốc thời gian tách biệt trong kế hoạch ĐATN: đối chiếu đề tài phải xong **trước hạn nộp đề cương** (mốc 2, đầu kỳ); kiểm tra đạo văn diễn ra **cuối kỳ** trên quyển báo cáo (mốc 5) bằng công cụ riêng của khoa. Hệ thống chỉ phục vụ mốc đầu, không thay thế mốc sau.
