// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

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
