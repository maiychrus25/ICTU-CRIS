// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("chuông hiển thị số chưa đọc và đánh dấu tất cả đã đọc", async ({ page }) => {
  await page.goto("/tong-quan/");

  const bell = page.getByRole("button", { name: /3 thông báo chưa đọc/ });
  await expect(bell).toBeVisible();
  await bell.click();
  await expect(page.getByText("Hồ sơ đã được khoa duyệt", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Đánh dấu tất cả đã đọc" }).click();

  await expect(page.getByText("Đã đánh dấu tất cả thông báo là đã đọc.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Không có thông báo chưa đọc" })).toBeVisible();
});

test("tạo bản báo cáo làm xuất hiện phiên bản mới", async ({ page }) => {
  await page.goto("/ky-bao-cao/chi-tiet/?id=401");
  await page.getByRole("tab", { name: "Báo cáo" }).click();
  await expect(page.getByText("Phiên bản v1", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "Tạo bản báo cáo" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Ghi chú").fill("Bản gửi Ban Giám hiệu");
  await dialog.getByRole("button", { name: "Tạo bản báo cáo", exact: true }).click();

  await expect(page.getByText("Đã tạo bản báo cáo v2.")).toBeVisible();
  await expect(page.getByText("Phiên bản v2", { exact: true })).toBeVisible();
});

test("trang báo cáo hiển thị mã băm và các bảng đóng băng", async ({ page }) => {
  await page.goto("/bao-cao/?id=901");

  await expect(page.getByRole("heading", { name: "Báo cáo công trình năm 2026" })).toBeVisible();
  await expect(page.getByText(/SHA-256 6f2a9d31/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Tổng hợp theo đơn vị" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Theo loại tài liệu" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Chi tiết hồ sơ" })).toBeVisible();
  await expect(page.getByRole("link", { name: "CSV" })).toHaveAttribute("href", "/api/reports/901/export?format=csv");
});

test("góc nhìn khoa hiển thị bốn thẻ số và biểu đồ năm", async ({ page }) => {
  await page.goto("/khoa/?id=1");

  await expect(page.getByRole("heading", { name: "Khoa Công nghệ thông tin" })).toBeVisible();
  await expect(page.getByText("Tổng công trình", { exact: true })).toBeVisible();
  await expect(page.getByText("Đã liên kết", { exact: true })).toBeVisible();
  await expect(page.getByText("Chờ xác nhận", { exact: true })).toBeVisible();
  await expect(page.getByText("Giảng viên chưa có công trình", { exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: "Biểu đồ công trình 5 năm theo loại tài liệu" })).toBeVisible();
});

test("chốt kỳ chuyển thẳng tới báo cáo vừa tạo", async ({ page }) => {
  await page.goto("/ky-bao-cao/chi-tiet/?id=402");
  await page.getByRole("button", { name: "Chốt kỳ" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Chốt kỳ" }).click();

  await expect(page).toHaveURL(/\/bao-cao\/\?id=\d+$/);
  await expect(page.getByText(/SHA-256/)).toBeVisible();
});
