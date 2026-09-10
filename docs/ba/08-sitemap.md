# 8. Sitemap — ICTU-CRIS (web, tối đa cấp 2)

```
/                          Bảng công việc của tôi
├─ /ky-bao-cao             Danh sách kỳ báo cáo
│  └─ /ky-bao-cao/[id]     Chi tiết kỳ: tiến độ, hàng đợi, chốt, xuất báo cáo
├─ /ho-so                  Hồ sơ kê khai của đơn vị
│  └─ /ho-so/[id]          Chi tiết hồ sơ: trường dữ liệu, minh chứng, cảnh báo, trao đổi
├─ /trinh-duyet            Bản trình duyệt
│  └─ /trinh-duyet/[id]    Xem xét và phê duyệt
├─ /doi-soat               Đối soát cấp trường
│  ├─ /doi-soat/trung-lap  Hàng đợi nghi trùng
│  └─ /doi-soat/tac-gia    Hàng đợi xác nhận liên kết tác giả
├─ /bao-cao                Báo cáo đã phát hành
│  └─ /bao-cao/[id]        Chi tiết báo cáo, truy ngược chỉ tiêu
├─ /tra-cuu                Tìm công trình
│  ├─ /tra-cuu/cong-trinh/[id]   Chi tiết công trình
│  └─ /tra-cuu/giang-vien/[id]   Hồ sơ công bố của giảng viên
├─ /doi-chieu              Đối chiếu đề tài dự kiến
│  └─ /doi-chieu/[id]      Kết quả đối chiếu
├─ /chat-luong-du-lieu     Báo cáo chất lượng dữ liệu
├─ /quan-tri               Quản trị
│  ├─ /quan-tri/nguoi-dung
│  ├─ /quan-tri/danh-muc
│  ├─ /quan-tri/quy-tac
│  └─ /quan-tri/dong-bo
└─ /ve                     Về hệ thống: nguồn dữ liệu, mức dữ liệu, giới hạn
```

Trang `/ve` không phải trang phụ. Nó ghi rõ hệ thống lấy dữ liệu từ đâu, cập nhật lúc nào, chỗ nào chưa đủ dữ liệu — điều kiện để người dùng tin vào số liệu và cũng là nơi trả lời nhanh câu "số này ở đâu ra".
