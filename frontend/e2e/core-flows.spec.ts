// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("trang gốc mở tổng quan với bốn chỉ số và biểu đồ", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/tong-quan\/$/, { timeout: 15_000 });
  await expect(page.getByText("Tổng công trình 5 năm", { exact: true })).toBeVisible();
  await expect(page.getByText("Công trình có liên kết tác giả", { exact: true })).toBeVisible();
  await expect(page.getByText("Liên kết tác giả chờ xác nhận", { exact: true })).toBeVisible();
  await expect(page.getByText("Nhóm nghi trùng đang mở", { exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: "Biểu đồ cột chồng công trình theo năm và loại tài liệu" })).toBeVisible();
});

test("nhật ký lọc theo loại thực thể", async ({ page }) => {
  await page.goto("/nhat-ky/");
  await expect(page.getByText("Nhóm nghi trùng #301")).toBeVisible();
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

test("bác bỏ liên kết tác giả bắt buộc lý do", async ({ page }) => {
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
