# 8. Sitemap — ICTU-CRIS (web, tối đa cấp 2)

## Cập nhật 11/09/2026

Giao diện làm lại bằng Next.js xuất tĩnh (xem
[2026-09-11-giao-dien-nextjs.md](../superpowers/plans/2026-09-11-giao-dien-nextjs.md) và
[2026-09-11-mo-rong-sau-ui.md](../superpowers/plans/2026-09-11-mo-rong-sau-ui.md)) dùng
đường dẫn phẳng, trang chi tiết nhận id qua **query string** (không phải route động
`[id]` — lý do: xuất tĩnh `next export` phải liệt kê trước mọi id lúc build, không hợp
với dữ liệu đổi theo mỗi lần đồng bộ). Cập nhật 12/09/2026 (lát cắt J + K, xem
[2026-09-12-lat-cat-j-k.md](../superpowers/plans/2026-09-12-lat-cat-j-k.md)): thêm năm
đường dẫn — bản đồ tri thức, tìm chuyên gia, cổng kiểm tra đề tài công khai, lý lịch khoa
học, cảnh báo bất thường dữ liệu. Đường dẫn UI thật đang chạy:

```
/tong-quan/                                Tổng quan cho lãnh đạo
/tra-cuu/                                  Tìm công trình
/cong-trinh/?id=                           Chi tiết công trình (xuất xứ từng trường)
/giang-vien/?id=                           Hồ sơ công bố của giảng viên
/giang-vien/ly-lich/?id=                   Lý lịch khoa học in được (A4)
/doi-chieu/                                Đối chiếu đề tài dự kiến (bốn khía cạnh)
/doi-chieu/ra-soat/                        Rà soát trùng đề tài theo khoá
/doi-chieu/chuyen-gia/                     Tìm chuyên gia / gợi ý phản biện (tab thứ ba)
/kiem-tra-de-tai/                          Cổng kiểm tra đề tài — công khai, không đăng nhập
/ban-do/                                   Bản đồ tri thức (PCA) + xu hướng chủ đề + đồng tác giả
/doi-soat/tac-gia/                         Hàng đợi xác nhận liên kết tác giả
/doi-soat/trung-lap/                       Hàng đợi nghi trùng
/doi-soat/trung-lap/chi-tiet/?id=          Chi tiết nhóm nghi trùng (so cạnh nhau)
/doi-soat/huong-dan/                       Gợi ý người hướng dẫn AI cho đồ án ICTU_TEACHER
/huong-dan/                                Hướng dẫn sử dụng trong ứng dụng, theo vai trò
/ky-bao-cao/                               Danh sách kỳ báo cáo
/ky-bao-cao/chi-tiet/?id=                  Chi tiết kỳ: tiến độ theo đơn vị, hồ sơ kê khai
/ke-khai/?id=                              Chi tiết hồ sơ kê khai: trạng thái, minh chứng
/ke-khai-cua-toi/                          Giảng viên tự kê khai công trình của mình
/nhat-ky/                                  Nhật ký thao tác
/chat-luong-du-lieu/                       Báo cáo chất lượng dữ liệu
/chat-luong-du-lieu/canh-bao/              Cảnh báo bất thường dữ liệu (tab trong trang trên)
/dang-nhap/                                Đăng nhập cục bộ
/chu-de/                                   Lưới 40 cụm chủ đề AI
/chu-de/chi-tiet/?id=                      Chi tiết cụm: từ khoá, công trình khớp
/dong-bo/                                  Lịch sử các lượt đồng bộ
/dong-bo/chi-tiet/?id=                     Chi tiết một lượt đồng bộ
/ve/                                       Về hệ thống
```

Sitemap gốc bên dưới (`ho-so`, `trinh-duyet`, `bao-cao`, `quan-tri`, v.v.) mô tả tầm nhìn
đầy đủ của lát cắt K/D/R, không phải đường dẫn đã triển khai — xem đường dẫn thật ở trên.

```
/                          Bảng công việc của tôi
├─ /ky-bao-cao             Danh sách kỳ báo cáo
│  └─ /ky-bao-cao/[id]     Chi tiết kỳ: tiến độ, hàng đợi, chốt, xuất báo cáo
├─ /ho-so                  Hồ sơ kê khai của đơn vị
│  └─ /ho-so/[id]          Chi tiết hồ sơ: trường dữ liệu, minh chứng, cảnh báo, trao đổi
├─ /trinh-duyet            Bản trình duyệt
│  └─ /trinh-duyet/[id]    Xem xét và phê duyệt
├─ /doi-soat               Đối soát cấp trường
│  ├─ /doi-soat/trung-lap  Hàng đợi nghi trùng   ✅
│  └─ /doi-soat/tac-gia    Hàng đợi xác nhận liên kết tác giả   ✅
├─ /bao-cao                Báo cáo đã phát hành
│  └─ /bao-cao/[id]        Chi tiết báo cáo, truy ngược chỉ tiêu
├─ /tra-cuu                Tìm công trình   ✅
│  ├─ /tra-cuu/cong-trinh/[id]   Chi tiết công trình   ✅
│  └─ /tra-cuu/giang-vien/[id]   Hồ sơ công bố của giảng viên   ✅
├─ /doi-chieu              Đối chiếu đề tài dự kiến   ✅
│  └─ /doi-chieu/[id]      Kết quả đối chiếu   ✅
├─ /chat-luong-du-lieu     Báo cáo chất lượng dữ liệu   ✅
├─ /quan-tri               Quản trị
│  ├─ /quan-tri/nguoi-dung
│  ├─ /quan-tri/danh-muc
│  ├─ /quan-tri/quy-tac
│  └─ /quan-tri/dong-bo
└─ /ve                     Về hệ thống: nguồn dữ liệu, mức dữ liệu, giới hạn   ✅
```

✅ = đã triển khai trong bản 0.1.0 (lát cắt giao diện, `cris/web/`). Các đường
dẫn còn lại thuộc lát cắt K, D, R (kỳ báo cáo, kê khai, phê duyệt) và luồng đối
chiếu đề tài — chưa làm. `/doi-soat/trung-lap/[id]` (trang so sánh chi tiết) đã
có, tuy sitemap gốc không liệt kê riêng.

Trang `/ve` không phải trang phụ. Nó ghi rõ hệ thống lấy dữ liệu từ đâu, cập nhật lúc nào, chỗ nào chưa đủ dữ liệu — điều kiện để người dùng tin vào số liệu và cũng là nơi trả lời nhanh câu "số này ở đâu ra".