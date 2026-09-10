# ICTU-CRIS Phase A Implementation Plan

> **For agentic workers:** Execute inline in the current user-authorized workspace. Do not commit.

**Goal:** Hoàn thiện nền tảng, dữ liệu và các màn Đợt A của frontend ICTU-CRIS.

**Architecture:** Static-exported Next.js App Router shell wraps client-fetched route pages. A single typed API client switches between backend and local fixtures, while TanStack Query hooks expose endpoint-specific data state.

**Tech Stack:** Next.js 16, React 19, TypeScript strict, Tailwind v4, shadcn/ui, TanStack Query/Table, lucide-react, sonner, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-11-dot-a-giao-dien-design.md`

## Global Constraints

- Chỉ sửa trong `frontend/`; không thêm thư viện, không commit.
- Mọi file `.ts`/`.tsx` mới có copyright và SPDX.
- Dữ liệu lấy phía client; route có query string dùng `useSearchParams` trong `Suspense`.
- Mọi trang có trạng thái tải, rỗng và lỗi phù hợp.
- Không hiển thị phần trăm tương đồng tổng hợp; luôn hiển thị `note` của kết quả đối chiếu.

### Task 1: Behavioral checks

- [x] Tạo Playwright config chạy ứng dụng với `NEXT_PUBLIC_MOCK=1`.
- [x] Viết kiểm thử cho điều hướng gốc, tra cứu, chi tiết công trình, đối chiếu và trang về hệ thống.
- [x] Chạy kiểm thử và xác nhận thất bại vì màn hình chưa tồn tại.

### Task 2: Shared foundation and data

- [x] Cấu hình static export, theme/query providers, font và token màu.
- [x] Tạo shell, page header, badge, state views, data table và pager bằng component sẵn có.
- [x] Tạo types sát schema, nhãn, fixture đủ số lượng, API client và query hooks.

### Task 3: Routes

- [x] Tạo chuyển hướng client tại `/`.
- [x] Hoàn thiện tra cứu có lọc, sắp xếp và phân trang điều khiển ngoài.
- [x] Hoàn thiện chi tiết công trình với bảng xuất xứ bốn cột và tác giả.
- [x] Hoàn thiện đối chiếu với form bốn khía cạnh, URL chia sẻ và ma trận mức.
- [x] Hoàn thiện trang về hệ thống và các trang khung Đợt B.
- [x] Xóa SVG mẫu và cập nhật README.

### Task 4: Verification

- [x] Chạy Playwright mock và sửa lỗi hành vi.
- [x] Chạy `npm run lint`, `npx tsc --noEmit`, `npm run build` ở tiền cảnh đến khi xanh.
- [x] Rà SPDX, phạm vi thay đổi và yêu cầu Đợt A.
