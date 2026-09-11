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
- Đăng nhập cục bộ (NFR-01, `cris/auth.py`): mật khẩu băm PBKDF2-HMAC-SHA256
  (260.000 vòng, salt riêng mỗi người), không lưu mật khẩu thô, chỉ thư viện
  chuẩn (`hashlib`, `secrets`, `hmac`). Phiên đăng nhập là cookie `cris_session`
  (`HttpOnly`, `SameSite=Lax`, hết hạn 12 giờ, gia hạn khi dùng) — đặt
  `CRIS_COOKIE_SECURE=1` khi chạy sau HTTPS thật để bật thêm cờ `Secure`; chạy
  HTTP nội bộ thì để tắt, ngược lại trình duyệt sẽ không gửi cookie. Đăng nhập
  sai bị giới hạn 5 lần/5 phút theo email (bộ nhớ tiến trình, không chia sẻ
  giữa nhiều worker `uvicorn`) để hạn chế dò mật khẩu.
- **Chế độ mở**: chừng nào chưa ai được đặt mật khẩu (`python -m cris user
  set-password`), hệ thống chạy với một người dùng mặc định (hoặc header
  `X-CRIS-User`), không bắt buộc đăng nhập — giới hạn đã công bố cho demo/nội
  bộ, không phải lỗ hổng cần báo, nhưng **không triển khai lên mạng công khai**
  ở chế độ này. Phân quyền theo đơn vị (NFR-02) và SSO trường thật vẫn ngoài
  phạm vi bản hiện tại.
- Tầng AI cục bộ không gửi dữ liệu ra ngoài; nếu bật nhà cung cấp ngoài (chưa hiện
  thực), chỉ tiêu đề/tóm tắt/từ khoá được gửi.

## Quét tự động

CI chạy `pip-audit` trên mọi push; Dependabot mở PR cập nhật hằng tuần cho thư viện
Python, action GitHub và ảnh nền Docker.
