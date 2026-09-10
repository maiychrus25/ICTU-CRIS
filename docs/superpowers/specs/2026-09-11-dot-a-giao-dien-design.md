# Thiết kế Đợt A giao diện ICTU-CRIS

Đợt A xây lớp nền tảng dùng chung, lớp dữ liệu có kiểu và bốn màn hoàn chỉnh theo `AGENTS.md`. Mọi dữ liệu chạy phía client để tương thích static export; `lib/api.ts` là cổng HTTP/mock duy nhất, còn TanStack Query quản lý cache và trạng thái tải/lỗi.

Giao diện dùng shell cố định với sáu mục điều hướng, topbar, Sheet trên mobile và theme sáng/tối. Các màn tra cứu, chi tiết công trình, đối chiếu đề tài và về hệ thống dùng component route-local; các màn Đợt B chỉ giữ điều hướng hợp lệ và thông báo rõ phạm vi.

Không thêm dependency, không dùng route động hay API phía Next.js. Thành công được xác nhận bằng kiểm thử hành vi ở chế độ mock, ESLint, TypeScript strict và static build.
