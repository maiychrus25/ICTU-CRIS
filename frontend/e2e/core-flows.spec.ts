// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("trang gốc mở tổng quan với bốn chỉ số và biểu đồ", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/tong-quan\/$/, { timeout: 30_000 });
  await expect(page.getByText("Tổng công trình 5 năm", { exact: true })).toBeVisible();
  await expect(page.getByText("Công trình có liên kết tác giả", { exact: true })).toBeVisible();
  await expect(page.getByText("Liên kết tác giả chờ xác nhận", { exact: true })).toBeVisible();
  await expect(page.getByText("Nhóm nghi trùng đang mở", { exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: "Biểu đồ cột chồng công trình theo năm và loại tài liệu" })).toBeVisible();
});

test("đăng nhập sai hiển thị nguyên văn lỗi từ API", async ({ page }) => {
  await page.goto("/dang-nhap/");
  await page.getByLabel("Email").fill("sai@ictu.edu.vn");
  await page.getByLabel("Mật khẩu").fill("khong-dung");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page.getByText("Email hoặc mật khẩu không đúng.")).toBeVisible();
});

test("đăng nhập đúng hiển thị người dùng, vai trò và quyền quyết định", async ({ page }) => {
  await page.goto("/dang-nhap/?next=/doi-soat/tac-gia/");
  await page.getByLabel("Email").fill("nguyen.minh.anh@ictu.edu.vn");
  await page.getByLabel("Mật khẩu").fill("demo1234");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();

  await expect(page).toHaveURL(/\/doi-soat\/tac-gia\/$/);
  await expect(page.getByText("Nguyễn Minh Anh", { exact: true })).toBeVisible();
  await expect(page.getByText("Chuyên viên KHCN", { exact: true })).toBeVisible();
  await page.getByRole("checkbox", { name: "Chọn hàng" }).first().check();
  await expect(page.getByRole("button", { name: "Xác nhận" })).toBeEnabled();
});

test("nhật ký lọc theo loại thực thể", async ({ page }) => {
  await page.goto("/nhat-ky/");
  await expect(page.getByText("Nhóm nghi trùng #301")).toBeVisible();
  await page.getByRole("row", { name: /Xác nhận liên kết/ }).getByRole("button", { name: "Xem thay đổi" }).click();
  await expect(page.getByRole("dialog")).toContainText('"state": "Chờ xác nhận"');
  await expect(page.getByRole("dialog")).not.toContainText("ChoXacNhan");
  await page.keyboard.press("Escape");
  await page.getByRole("combobox", { name: "Loại thực thể" }).click();
  await page.getByRole("option", { name: "Kỳ báo cáo" }).click();
  await expect(page.getByText("Kỳ báo cáo #401")).toBeVisible();
  await expect(page.getByText("Nhóm nghi trùng #301")).toBeHidden();
});

test("mở kỳ báo cáo bị chặn khi thiếu mã", async ({ page }) => {
  await page.goto("/ky-bao-cao/");
  await page.getByRole("button", { name: "Mở kỳ mới" }).click();
  const dialog = page.getByRole("dialog");
  const code = dialog.getByLabel("Mã kỳ *");
  await dialog.getByRole("button", { name: "Mở kỳ", exact: true }).click();
  await expect(dialog).toBeVisible();
  expect(await code.evaluate((element: HTMLInputElement) => element.validity.valid)).toBe(false);
});

test("kê khai công trình và chặn yêu cầu bổ sung thiếu lý do", async ({ page }) => {
  await page.goto("/ky-bao-cao/");
  await page.getByRole("link", { name: "Báo cáo công trình năm 2026", exact: true }).click();
  await page.getByRole("tab", { name: "Hồ sơ kê khai" }).click();

  await page.getByRole("button", { name: "Kê khai công trình" }).click();
  const createDialog = page.getByRole("dialog");
  await createDialog.getByRole("combobox", { name: "Tìm công trình" }).fill("Thiết kế hệ thống tưới cây");
  await createDialog.getByRole("option", { name: /Thiết kế hệ thống tưới cây tự động/ }).click();
  await createDialog.getByRole("combobox", { name: "Đơn vị kê khai" }).click();
  await page.getByRole("option", { name: "KHMT — Khoa Khoa học máy tính" }).click();
  await createDialog.getByLabel("Ghi chú").fill("Kê khai từ kiểm thử giao diện.");
  await createDialog.getByRole("button", { name: "Kê khai", exact: true }).click();

  await expect(page.getByText("Đã kê khai công trình vào kỳ báo cáo.")).toBeVisible();
  const row = page.getByRole("row", { name: /Thiết kế hệ thống tưới cây tự động/ });
  await expect(row).toContainText("Nháp");
  await row.getByRole("button", { name: /Hành động hồ sơ/ }).click();
  await page.getByRole("menuitem", { name: "Yêu cầu bổ sung" }).click();

  const reasonDialog = page.getByRole("dialog");
  const reason = reasonDialog.getByLabel("Lý do *");
  await reasonDialog.getByRole("button", { name: "Yêu cầu bổ sung" }).click();
  await expect(reasonDialog).toBeVisible();
  expect(await reason.evaluate((element: HTMLTextAreaElement) => element.validity.valid)).toBe(false);
});

test("tra cứu và mở bảng xuất xứ công trình", async ({ page }) => {
  await page.goto("/tra-cuu/");
  await page.getByLabel("Từ khoá").fill("Xây dựng website quản lý thư viện");
  await page.getByRole("button", { name: "Tra cứu" }).click();
  await page.getByRole("link", { name: /Xây dựng website quản lý thư viện/ }).click();

  await expect(page.getByRole("heading", { name: "Xuất xứ dữ liệu" })).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "Giá trị đang dùng" })).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "Giá trị gốc" })).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "Nguồn", exact: true })).toBeVisible();
});

test("chỉnh tay tiêu đề bắt buộc lý do và ghi nhận xuất xứ", async ({ page }) => {
  await page.goto("/cong-trinh/?id=1");
  await page.getByRole("button", { name: "Chỉnh sửa Tiêu đề" }).click();

  const dialog = page.getByRole("dialog");
  const reason = dialog.getByLabel("Lý do *");
  await dialog.getByLabel("Giá trị mới *").fill("Xây dựng website quản lý thư viện trường THPT");
  await dialog.getByRole("button", { name: "Lưu chỉnh sửa" }).click();
  await expect(dialog).toBeVisible();
  expect(await reason.evaluate((element: HTMLTextAreaElement) => element.validity.valid)).toBe(false);

  await reason.fill("Đối chiếu lại bản ghi gốc của khoa.");
  await dialog.getByRole("button", { name: "Lưu chỉnh sửa" }).click();
  await expect(page.getByText("Đã chỉnh tay", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Xây dựng website quản lý thư viện trường THPT", exact: true })).toBeVisible();
});

test("hồ sơ nháp được trình khoa duyệt bởi chuyên viên", async ({ page }) => {
  await page.goto("/ke-khai/?id=601");
  await expect(page.locator('[data-slot="badge"]').filter({ hasText: /^Nháp$/ }).first()).toBeVisible();
  await page.getByRole("button", { name: "Trình khoa duyệt" }).click();

  await expect(page.getByText("Đã trình khoa duyệt.")).toBeVisible();
  await expect(page.locator('[data-slot="badge"]').filter({ hasText: /^Chờ khoa duyệt$/ }).first()).toBeVisible();
});

test("tải tệp minh chứng và hiển thị kích thước cùng mã băm", async ({ page }) => {
  await page.goto("/ke-khai/?id=601");
  await page.getByRole("button", { name: "Thêm minh chứng" }).click();

  const dialog = page.getByRole("dialog");
  await dialog.getByRole("tab", { name: "Tải tệp lên" }).click();
  await dialog.getByLabel("Chọn tệp minh chứng").setInputFiles({
    name: "qua-lon.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.alloc(10 * 1024 * 1024 + 1),
  });
  await expect(dialog.getByText("Tệp vượt quá giới hạn 10 MB.")).toBeVisible();
  await expect(dialog.getByRole("button", { name: "Thêm minh chứng" })).toBeDisabled();

  await dialog.getByLabel("Chọn tệp minh chứng").setInputFiles({
    name: "minh-chung.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-1.4\nminh chung ICTU\n%%EOF"),
  });
  await expect(dialog.getByText("minh-chung.pdf", { exact: true })).toBeVisible();
  await dialog.getByRole("button", { name: "Thêm minh chứng" }).click();

  await expect(page.getByText("Đã tải tệp minh chứng lên.")).toBeVisible();
  const evidenceRow = page.getByRole("row", { name: /minh-chung\.pdf/ });
  await expect(evidenceRow).toContainText("KB");
  await expect(evidenceRow).toContainText("8f14e45fceea");
  await expect(evidenceRow.getByRole("link", { name: "Tải về" })).toHaveAttribute("href", /\/api\/evidence\/\d+\/file$/);
});

test("đưa gợi ý người hướng dẫn AI vào hàng đợi xác nhận", async ({ page }) => {
  await page.goto("/doi-soat/huong-dan/");

  await expect(page.getByText(/4\.621\/5\.375 đồ án/)).toBeVisible();
  const suggestionRow = page.getByRole("row", { name: /Xây dựng website quản lý thư viện/ }).filter({ hasText: "TS. Nguyễn Văn A" }).first();
  await expect(suggestionRow).toContainText("TS. Nguyễn Văn A");
  await suggestionRow.getByRole("button", { name: "Đưa vào hàng đợi" }).click();

  await expect(page.getByText("Đã đưa gợi ý vào hàng đợi tác giả.")).toBeVisible();
  await expect(suggestionRow.getByRole("link", { name: "Đang chờ xác nhận" })).toHaveAttribute("href", "/doi-soat/tac-gia/");
});

test("giảng viên tự kê khai công trình rồi trình khoa duyệt", async ({ page }) => {
  await page.goto("/dang-nhap/?next=/ke-khai-cua-toi/");
  await page.getByLabel("Email").fill("giang.vien@ictu.edu.vn");
  await page.getByLabel("Mật khẩu").fill("demo1234");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();

  await expect(page).toHaveURL(/\/ke-khai-cua-toi\/$/);
  await expect(page.getByRole("heading", { name: "Kê khai của tôi" })).toBeVisible({ timeout: 15_000 });
  const navigationLinks = page.getByRole("navigation", { name: "Điều hướng chính" }).getByRole("link");
  await expect(navigationLinks.nth(1)).toHaveText("Kê khai của tôi");

  const pendingWorkRow = page.getByRole("row", { name: /Phát triển hệ thống điểm danh sinh viên/ });
  await expect(pendingWorkRow.getByRole("button", { name: "Kê khai vào kỳ này" })).toBeDisabled();

  const workRow = page.getByRole("row", { name: /Mô hình dự báo chất lượng không khí/ });
  await workRow.getByRole("button", { name: "Kê khai vào kỳ này" }).click();
  await expect(page.getByText("Đã kê khai công trình vào kỳ báo cáo.")).toBeVisible();

  const declarationRow = page.getByRole("row", { name: /Mô hình dự báo chất lượng không khí/ }).last();
  await expect(declarationRow.locator('[data-slot="badge"]')).toHaveText(/Nháp/);
  await declarationRow.getByRole("button", { name: "Trình khoa duyệt" }).click();
  await expect(page.getByText("Đã trình khoa duyệt.")).toBeVisible();
  await expect(declarationRow.locator('[data-slot="badge"]')).toHaveText(/Chờ khoa duyệt/);

  await page.getByRole("navigation", { name: "Điều hướng chính" }).getByRole("link", { name: "Kỳ báo cáo" }).click();
  await page.getByRole("link", { name: "Báo cáo công trình năm 2025", exact: true }).click();
  await page.getByRole("tab", { name: "Hồ sơ kê khai" }).click();
  await page.getByRole("link", { name: "#610", exact: true }).click();
  await expect(page.locator('[data-slot="badge"]').filter({ hasText: /^Nháp$/ }).first()).toBeVisible();
  await expect(page.getByRole("button", { name: "Trình khoa duyệt" })).toHaveCount(0);
});

test("quyết định liên kết tác giả dùng lý do và bộ chọn người", async ({ page }) => {
  await page.goto("/doi-soat/tac-gia/");
  await page.getByRole("checkbox", { name: "Chọn hàng" }).first().check();
  await page.getByRole("button", { name: "Bác bỏ" }).click();

  const dialog = page.getByRole("dialog");
  const reason = dialog.getByLabel("Lý do *");
  await dialog.getByRole("button", { name: "Bác bỏ" }).click();
  await expect(dialog).toBeVisible();
  expect(await reason.evaluate((element: HTMLTextAreaElement) => element.validity.valid)).toBe(false);

  await reason.fill("Không đúng giảng viên trong nguồn gốc.");
  await dialog.getByRole("button", { name: "Bác bỏ" }).click();
  await expect(page.getByText("Đã xử lý 1 liên kết tác giả.")).toBeVisible();

  await page.getByRole("checkbox", { name: "Chọn hàng" }).first().check();
  await page.getByRole("button", { name: "Chuyển cho người khác" }).click();
  const reassignDialog = page.getByRole("dialog");
  await reassignDialog.getByRole("combobox", { name: "Tìm người" }).fill("Nguyễn Văn");
  await reassignDialog.getByRole("option", { name: /TS\. Nguyễn Văn A.*CNTT.*42 công trình/ }).click();
  await reassignDialog.getByRole("button", { name: "Chuyển", exact: true }).click();
  await expect(page.getByText("Đã xử lý 1 liên kết tác giả.").last()).toBeVisible();
});

test("chủ đề mở chi tiết rồi điền bộ lọc tra cứu", async ({ page }) => {
  await page.goto("/chu-de/");
  await expect(page.getByText(/Cụm chủ đề do AI gom từ từ khoá/)).toBeVisible();
  await page.getByRole("link", { name: /Trí tuệ nhân tạo.*38 công trình/ }).click();

  await expect(page).toHaveURL(/\/chu-de\/chi-tiet\/\?id=1$/);
  await expect(page.getByRole("heading", { name: "Trí tuệ nhân tạo" })).toBeVisible();
  await expect(page.getByRole("progressbar", { name: /học sâu/i })).toBeVisible();
  await page.getByRole("link", { name: "Tra cứu theo chủ đề này" }).click();

  await expect(page).toHaveURL(/\/tra-cuu\/\?topic=1$/);
  await expect(page.getByRole("combobox", { name: "Chủ đề" })).toContainText("Trí tuệ nhân tạo");
  await page.getByRole("combobox", { name: "Đơn vị" }).click();
  await expect(page.getByRole("option", { name: "CNTT — Khoa Công nghệ thông tin" })).toBeVisible();
});

test("đồng bộ mở chi tiết lượt và hiển thị cảnh báo", async ({ page }) => {
  await page.goto("/dong-bo/");
  await expect(page.getByRole("heading", { name: "Lịch sử đồng bộ" })).toBeVisible();
  await page.getByRole("row", { name: /Kho dữ liệu ICTU.*Toàn bộ dữ liệu/ }).click();

  await expect(page).toHaveURL(/\/dong-bo\/chi-tiet\/\?id=18$/);
  await expect(page.getByRole("heading", { name: "Chi tiết lượt đồng bộ #18" })).toBeVisible();
  await expect(page.getByText("2 bản ghi thiếu mã đơn vị.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Bản ghi thay đổi gần nhất" })).toBeVisible();
});

test("đối chiếu đề tài hiển thị note và ma trận khía cạnh", async ({ page }) => {
  await page.goto("/doi-chieu/");
  await page.locator("#compare-title").fill("Hệ thống quản lý thư viện thông minh");
  await page.locator("#compare-description").fill("Ứng dụng web quản lý mượn trả tài liệu trong trường học.");
  await page.getByRole("button", { name: "Đối chiếu đề tài" }).click();

  await expect(page.getByText("Kết quả đối chiếu dựa trên tiêu đề, tóm tắt và siêu dữ liệu; không phải toàn văn.")).toBeVisible();
  await expect(page.getByText("Bài toán", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Đối tượng", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Phạm vi", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Phương pháp", { exact: true }).first()).toBeVisible();
});

test("rà soát theo khoá mở đối chiếu với tiêu đề điền sẵn", async ({ page }) => {
  await page.goto("/doi-chieu/ra-soat/");
  await expect(page.getByRole("heading", { name: "Rà soát trùng đề tài theo khoá" })).toBeVisible();

  await page.getByRole("combobox", { name: "Khoá rà soát" }).click();
  await page.getByRole("option", { name: /Khoá 21 — 529 đồ án, 47 gắn cờ/ }).click();

  await expect(page.locator('[data-slot="badge"]').filter({ hasText: /^Cao$/ }).first()).toBeVisible();
  await page.getByRole("link", { name: "Đối chiếu chi tiết" }).first().click();
  await expect(page).toHaveURL(/\/doi-chieu\/\?title=/);
  await expect(page.getByLabel("Tiêu đề đề tài")).toHaveValue("Phát triển hệ thống điểm danh sinh viên bằng nhận diện khuôn mặt");
});
