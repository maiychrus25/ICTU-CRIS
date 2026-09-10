# Chính sách bảo mật (Security Policy)

## Phiên bản được hỗ trợ

| Phiên bản | Hỗ trợ |
|---|---|
| 0.1.x | ✅ |

## Báo lỗ hổng

Đừng mở issue công khai cho lỗ hổng bảo mật. Gửi qua **GitHub Security Advisory**
(tab *Security → Report a vulnerability* của repo) hoặc email người bảo trì ghi trong
`CODEOWNERS`. Nêu: phiên bản, cách tái hiện, ảnh hưởng. Chúng tôi xác nhận trong 7 ngày
và xử lý theo mức độ.

## Phạm vi cần lưu ý

- Hệ thống xử lý **dữ liệu cá nhân giảng viên** (email, điện thoại, ngày sinh) lấy từ
  kho công khai `repository.ictu.edu.vn`. Dữ liệu thô không nằm trong repo; giao diện
  ẩn điện thoại và ngày sinh với vai trò sinh viên.
- Bản 0.1 **chưa có đăng nhập thật** (chạy với một người dùng mặc định) — không triển
  khai lên mạng công khai. Đây là giới hạn đã công bố, không phải lỗ hổng cần báo.
- Tầng AI cục bộ không gửi dữ liệu ra ngoài; nếu bật nhà cung cấp ngoài (chưa hiện
  thực), chỉ tiêu đề/tóm tắt/từ khoá được gửi.

## Quét tự động

CI chạy `pip-audit` trên mọi push; Dependabot mở PR cập nhật hằng tuần cho thư viện
Python, action GitHub và ảnh nền Docker.
