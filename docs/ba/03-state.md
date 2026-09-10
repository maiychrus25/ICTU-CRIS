# 3. Biểu đồ trạng thái — ICTU-CRIS

## 3.1 Kỳ báo cáo (Period)

```mermaid
stateDiagram-v2
    [*] --> ChuanBi: Tạo kỳ
    ChuanBi --> DangMo: Mở kỳ
    DangMo --> DaDongNop: Hết hạn / đóng thủ công
    DaDongNop --> DangDoiSoat: Bắt đầu đối soát
    DangDoiSoat --> DaChot: Chốt dữ liệu
    DaChot --> DaPhatHanh: Xuất báo cáo
    DaChot --> DangDoiSoat: Mở lại (sinh phiên bản mới)
    DangMo --> Huy: Huỷ kỳ
    ChuanBi --> Huy: Huỷ kỳ
    DaPhatHanh --> [*]
```

Quy tắc: sau `DaChot`, số liệu không đổi. Mọi điều chỉnh phải qua `Mở lại`, và sinh **phiên bản báo cáo mới**, giữ nguyên phiên bản cũ — thực hiện yêu cầu *"điều chỉnh bằng phiên bản mới"*.

## 3.2 Hồ sơ kê khai (Declaration)

```mermaid
stateDiagram-v2
    [*] --> Nhap: Tạo từ gợi ý hoặc nhập tay
    Nhap --> ChoBoSung: Gửi yêu cầu bổ sung
    ChoBoSung --> Nhap: Người cung cấp đã nộp
    Nhap --> ChoKhoaDuyet: Trình lãnh đạo khoa
    ChoKhoaDuyet --> Nhap: Khoa trả lại kèm lý do
    ChoKhoaDuyet --> KhoaDaDuyet: Khoa phê duyệt (đóng băng phiên bản)
    KhoaDaDuyet --> ChoPhongKiemTra: Gửi phòng chức năng
    ChoPhongKiemTra --> Nhap: Phòng trả về kèm lý do
    ChoPhongKiemTra --> DatYeuCau: Phòng chấp nhận
    DatYeuCau --> DaChot: Kỳ báo cáo chốt
    Nhap --> Rut: Khoa rút hồ sơ
    DaChot --> [*]
```

Quy tắc trọng yếu: từ `KhoaDaDuyet` trở đi, mọi thay đổi danh sách công trình hoặc số liệu trọng yếu đưa hồ sơ về `Nhap` và **huỷ dấu đã duyệt**. Không giữ dấu "đã duyệt" cho nội dung đã khác.

## 3.3 Công trình (Work)

```mermaid
stateDiagram-v2
    [*] --> Tho: Nhập từ kho hoặc kê khai
    Tho --> DaChuanHoa: Chuẩn hoá xong
    DaChuanHoa --> NghiTrung: Có ứng viên trùng
    NghiTrung --> DaGop: Người dùng quyết định gộp
    NghiTrung --> GiuRieng: Người dùng xác nhận là hai công trình khác nhau
    DaChuanHoa --> DaXacNhan: Không có nghi vấn
    GiuRieng --> DaXacNhan
    DaGop --> DaXacNhan
    DaXacNhan --> [*]
```

## 3.4 Liên kết tác giả (AuthorLink)

```mermaid
stateDiagram-v2
    [*] --> ChuaNoi
    ChuaNoi --> DaNoiTuDong: Khớp ORCID / khớp tên duy nhất
    ChuaNoi --> ChoXacNhan: Khớp nhiều người hoặc khớp một phần
    ChoXacNhan --> DaXacNhan: Người dùng chọn đúng người
    ChoXacNhan --> DaBacBo: Người dùng bác bỏ
    DaNoiTuDong --> DaBacBo: Người dùng phát hiện sai
    DaBacBo --> ChuaNoi: Nguồn cập nhật lại
    DaXacNhan --> [*]
```

Độ tin cậy gắn vào liên kết: `orcid` > `ten_day_du_duy_nhat` > `ten_day_du_nhieu_ung_vien` > `ten_mot_phan`. Chỉ hai mức đầu được tự nối.

## 3.5 Đề tài dự kiến (Proposal — luồng đối chiếu)

```mermaid
stateDiagram-v2
    [*] --> Nhap: Sinh viên nhập mô tả
    Nhap --> DaDoiChieu: Chạy đối chiếu
    DaDoiChieu --> Nhap: Chỉnh mô tả, chạy lại
    DaDoiChieu --> DaNop: Gửi giảng viên/bộ môn
    DaNop --> CanChinh: Có nhận xét yêu cầu chỉnh
    CanChinh --> Nhap
    DaNop --> DaTiepNhan: Được đồng ý trình
    DaTiepNhan --> [*]
```

Hệ thống dừng ở `DaTiepNhan`. Quyết định phê duyệt đề tài thuộc quy trình đào tạo, ngoài phạm vi.
