// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

const notice = "Dữ liệu được lấy từ DSpace của Trường CNTT&TT – ĐH Thái Nguyên";

test("footer nguồn dữ liệu hiện ở app-shell và cổng công khai", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/tra-cuu/");
  await expect(page.locator("footer").filter({ hasText: notice })).toBeVisible({ timeout: 30_000 });
  await page.goto("/kiem-tra-de-tai/");
  await expect(page.locator("footer").filter({ hasText: notice })).toBeVisible();
});

test("tổng quan hiển thị công trình mới, công trình đổi và RSS", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/tong-quan/");
  await expect(page.getByRole("heading", { name: "Mới cập nhật từ kho" })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("heading", { name: /^Thêm/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: /^Đổi/ })).toBeVisible();
  await expect(page.getByRole("link", { name: "RSS" })).toHaveAttribute("href", "/api/feed.xml");
  await expect(page.getByRole("link", { name: "Xem lịch sử đồng bộ" })).toHaveAttribute("href", "/dong-bo/");
});

test("hồ sơ có học hàm, Scholar, lý lịch và trích dẫn từng bài", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/giang-vien/?id=1");
  await expect(page.getByText("Phó giáo sư · Tiến sĩ", { exact: true })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("link", { name: /Google Scholar/ })).toHaveAttribute("target", "_blank");
  await page.getByRole("button", { name: "Trích dẫn" }).first().click();
  await expect(page.getByRole("dialog")).toContainText("(2025)");
  await page.keyboard.press("Escape");
  await page.getByRole("link", { name: "Lý lịch khoa học" }).click();
  await expect(page).toHaveURL(/\/giang-vien\/ly-lich\/\?id=1$/);
  await expect(page.locator("aside")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "In / Lưu PDF" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Sao chép trích dẫn tất cả" })).toBeVisible();
  await expect(page.locator("footer").filter({ hasText: notice })).toBeVisible();
});

test("cảnh báo lọc được và bỏ qua bắt buộc lý do", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/chat-luong-du-lieu/canh-bao/");
  await expect(page.getByRole("heading", { name: "Cảnh báo bất thường" })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("button", { name: /DOI sai định dạng.*1/ })).toBeVisible();
  await page.getByRole("button", { name: "Bỏ qua" }).first().click();
  const dialog = page.getByRole("dialog");
  const reason = dialog.getByLabel("Lý do *");
  await dialog.getByRole("button", { name: "Bỏ qua" }).click();
  expect(await reason.evaluate((element: HTMLTextAreaElement) => element.validity.valid)).toBe(false);
  await reason.fill("Đã kiểm tra với bản ghi nguồn.");
  await dialog.getByRole("button", { name: "Bỏ qua" }).click();
  await expect(page.getByText("Đã bỏ qua cảnh báo và lưu lý do.")).toBeVisible();
  await expect(page.getByText("DOI: 10.1x/sai")).toHaveCount(0);
});

test("metric cảnh báo mở đúng tab", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/chat-luong-du-lieu/");
  await page.getByRole("link", { name: "Mở cảnh báo" }).click({ timeout: 30_000 });
  await expect(page).toHaveURL(/\/chat-luong-du-lieu\/canh-bao\/$/);
});
