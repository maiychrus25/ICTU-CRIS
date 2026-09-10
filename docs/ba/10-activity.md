# 10. Sơ đồ luồng chức năng (activity) — ICTU-CRIS

## 10.1 Đồng bộ kho và dựng gợi ý theo khoa (UC-01, UC-03)

```mermaid
flowchart TD
    A["Bắt đầu đồng bộ"] --> B["Đọc danh mục từng loại tài liệu"]
    B --> C["Đọc trang chi tiết từng công trình<br/>(bắt buộc: danh mục cắt cụt tác giả)"]
    C --> D["Đối soát số bản ghi lấy được<br/>với số nguồn công bố"]
    D --> E{"Lệch số lượng?"}
    E -- "Có" --> F["Quét bù theo bộ lọc<br/>để lấy bản ghi phân trang bỏ sót"]
    F --> D
    E -- "Không" --> G["Lưu bản ghi thô, giữ nguyên giá trị gốc"]
    G --> H["Chuẩn hoá: tên người, tên đơn vị,<br/>loại công trình, năm"]
    H --> I["Nối tác giả bằng ORCID"]
    I --> J["Nối tác giả bằng tên chuẩn hoá"]
    J --> K{"Khớp duy nhất?"}
    K -- "Có" --> L["Nối tự động, ghi độ tin cậy"]
    K -- "Không" --> M["Đưa vào hàng đợi xác nhận"]
    L --> N["Suy đơn vị từ tác giả đã nối"]
    M --> N
    N --> O["Dựng danh sách gợi ý theo khoa cho kỳ"]
    O --> P["Ghi báo cáo chất lượng dữ liệu"]
```

Điểm quyết định `E` là bắt buộc, không phải tuỳ chọn: nguồn hiện có lỗi phân trang khiến duyệt tuần tự bỏ sót bản ghi mà **không báo lỗi**. Không đối soát số lượng thì mất dữ liệu âm thầm.

## 10.2 Lập hồ sơ và xử lý cảnh báo (UC-07)

```mermaid
flowchart TD
    A["Mở kỳ đang hoạt động"] --> B["Xem danh sách gợi ý theo khoa"]
    B --> C["Chọn công trình đưa vào kê khai"]
    C --> D["Hệ thống tạo hồ sơ, điền sẵn từ kho,<br/>đánh dấu nguồn từng trường"]
    D --> E["Bổ sung công trình ngoài kho nếu có"]
    E --> F["Chạy kiểm tra tự động"]
    F --> G{"Loại cảnh báo"}
    G -- "Chặn" --> H["Xử lý: bổ sung trường thiếu,<br/>đính minh chứng, xác nhận tác giả"]
    H --> I{"Cần người khác cung cấp?"}
    I -- "Có" --> J["Gửi yêu cầu bổ sung<br/>gắn vào hồ sơ, ghi rõ chờ ai"]
    J --> K["Chờ phản hồi"]
    K --> F
    I -- "Không" --> F
    G -- "Cảnh cáo" --> L["Ghi chú lý do chấp nhận"]
    G -- "Không còn" --> M["Tạo bản trình duyệt"]
    L --> M
    M --> N["Gửi lãnh đạo khoa"]
```

## 10.3 Phê duyệt và bảo toàn phiên bản (UC-10)

```mermaid
flowchart TD
    A["Lãnh đạo khoa mở bản trình"] --> B["Xem phạm vi, quy tắc thống kê,<br/>danh sách, cảnh báo còn lại"]
    B --> C{"Có lần trình trước?"}
    C -- "Có" --> D["Xem khối thay đổi:<br/>thêm / bớt / sửa"]
    C -- "Không" --> E["Xem toàn bộ danh sách"]
    D --> F{"Quyết định"}
    E --> F
    F -- "Trả lại" --> G["Nhập lý do (bắt buộc),<br/>chọn hồ sơ liên quan"]
    G --> H["Hồ sơ về trạng thái Nháp,<br/>thông báo Văn phòng khoa"]
    F -- "Phê duyệt" --> I["Đóng băng phiên bản:<br/>ghi mã, người duyệt, thời điểm"]
    I --> J["Chuyển phiên bản đã duyệt<br/>sang phòng chức năng"]
    J --> K{"Nội dung bị sửa sau khi duyệt?"}
    K -- "Có" --> L["Huỷ dấu đã duyệt,<br/>đưa về Nháp, yêu cầu trình lại"]
    K -- "Không" --> M["Giữ nguyên phiên bản"]
```

Nhánh `K → L` thực hiện nguyên tắc trong tài liệu định hướng: *"không được giữ dấu đã duyệt cho một nội dung đã khác"*.

## 10.4 Đối soát cấp trường và chốt dữ liệu (UC-11, UC-13)

```mermaid
flowchart TD
    A["Phòng chức năng mở hàng đợi kiểm tra"] --> B["Kiểm tra hồ sơ có cảnh báo trước"]
    B --> C{"Đạt yêu cầu?"}
    C -- "Không" --> D["Trả về đơn vị kèm lý do,<br/>theo dõi tới khi xử lý xong"]
    D --> A
    C -- "Đạt" --> E["Đối soát toàn trường"]
    E --> F["Ghép ứng viên trùng theo DOI,<br/>rồi theo tiêu đề chuẩn hoá"]
    F --> G{"Nhiều hồ sơ kê khai<br/>cùng một công trình?"}
    G -- "Có" --> H["Liên kết các lượt kê khai<br/>vào một công trình duy nhất"]
    G -- "Không" --> I["Giữ nguyên"]
    H --> J{"Còn hồ sơ chờ kiểm tra?"}
    I --> J
    J -- "Có" --> A
    J -- "Không" --> K["Chốt dữ liệu: khoá tập hồ sơ,<br/>sinh mã phiên bản"]
    K --> L["Xuất báo cáo kèm danh sách đối chứng"]
    L --> M{"Phát hiện sai sau khi chốt?"}
    M -- "Có" --> N["Mở lại kỳ, sinh phiên bản mới,<br/>giữ nguyên phiên bản cũ"]
    N --> A
    M -- "Không" --> O["Kết thúc kỳ"]
```
