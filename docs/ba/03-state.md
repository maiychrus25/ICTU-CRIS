# 3. Biểu đồ trạng thái — ICTU-CRIS

## 3.1 Kỳ báo cáo (Period)

```mermaid
stateDiagram-v2
    [*] --> ChuanBi: Tạo kỳ
    ChuanBi --> DangMo: Mở kỳ
    DangMo --> DaDongNop: Hết hạn / đóng thủ công
    DaDongNop --> DangDoiSoat: Bắt đầu đối soát
    DangDoiSoat --> DaChot: Chốt dữ liệu
    DaChot --> ChoTruongDuyet: Trình ký (báo cáo chính thức)
    ChoTruongDuyet --> DaPhatHanh: Lãnh đạo trường phê duyệt
    ChoTruongDuyet --> DangDoiSoat: Lãnh đạo trường trả lại (mở lại, phiên bản mới)
    DaChot --> DaPhatHanh: Xuất báo cáo nội bộ
    DaChot --> DangDoiSoat: Mở lại (sinh phiên bản mới)
    DaPhatHanh --> DangDoiSoat: Phát hiện sai sau phát hành (mở lại, phiên bản mới)
    DangMo --> Huy: Huỷ kỳ
    ChuanBi --> Huy: Huỷ kỳ
    DaPhatHanh --> [*]
```

Quy tắc: sau `DaChot`, số liệu không đổi. Mọi điều chỉnh phải qua `Mở lại`, và sinh **phiên bản báo cáo mới**, giữ nguyên phiên bản cũ — thực hiện yêu cầu *"điều chỉnh bằng phiên bản mới"*. Mỗi phiên bản mới ghi: số cũ, số mới, lý do đổi, và danh sách báo cáo đã dùng phiên bản cũ (BR-25). Trạng thái `ChoTruongDuyet` chỉ áp dụng cho báo cáo chính thức gửi cấp trên (BR-24).

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
    [*] --> Nhap: GVHD hoặc sinh viên nhập mô tả
    Nhap --> DaDoiChieu: Chạy đối chiếu
    DaDoiChieu --> Nhap: Chỉnh mô tả, chạy lại
    DaDoiChieu --> DaNop: Đính vào đề cương gửi bộ môn
    DaNop --> CanChinh: Bộ môn yêu cầu chỉnh
    CanChinh --> Nhap
    DaNop --> DaTiepNhan: Bộ môn duyệt đề cương
    DaTiepNhan --> [*]
```

Hệ thống dừng ở `DaTiepNhan`. Việc duyệt đề cương, nộp về khoa và các mốc sau của kế hoạch ĐATN thuộc quy trình đào tạo, ngoài phạm vi.
