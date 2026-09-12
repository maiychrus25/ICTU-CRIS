// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

const notice = "Dữ liệu được lấy từ DSpace của Trường CNTT&TT – ĐH Thái Nguyên";

test("footer nguồn dữ liệu cố định và không che bảng tra cứu", async ({ page }) => {
  test.setTimeout(60_000);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/tra-cuu/");
  const footer = page.locator("footer").filter({ hasText: notice });
  const lastRow = page.locator("tbody tr").last();
  await expect(lastRow).toBeVisible({ timeout: 30_000 });
  await expect(footer).toHaveCSS("position", "fixed");
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await lastRow.scrollIntoViewIfNeeded();

  const footerBox = await footer.boundingBox();
  const rowBox = await lastRow.boundingBox();
  expect(footerBox).not.toBeNull();
  expect(rowBox).not.toBeNull();
  expect(footerBox!.x).toBe(240);
  expect(footerBox!.y + footerBox!.height).toBeLessThanOrEqual(page.viewportSize()!.height + 1);
  expect(rowBox!.y + rowBox!.height).toBeLessThanOrEqual(footerBox!.y + 1);

  await page.goto("/kiem-tra-de-tai/");
  const publicFooter = page.locator("footer").filter({ hasText: notice });
  await expect(publicFooter).toHaveCSS("position", "fixed");
  await page.getByLabel("Tên đề tài dự định").fill("Xây dựng website bán hàng");
  await page.getByRole("button", { name: "Kiểm tra", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Đề tài tương tự các khoá trước" })).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  const publicFooterBox = await publicFooter.boundingBox();
  expect(publicFooterBox).not.toBeNull();
  expect(publicFooterBox!.x).toBe(0);
  expect(publicFooterBox!.y + publicFooterBox!.height).toBeLessThanOrEqual(page.viewportSize()!.height + 1);

  for (const width of [390, 768]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/tra-cuu/");
    const responsiveBox = await page.locator("footer").filter({ hasText: notice }).boundingBox();
    expect(responsiveBox).not.toBeNull();
    expect(responsiveBox!.x).toBe(0);
    expect(responsiveBox!.width).toBe(width);
  }
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
  const footer = page.locator("footer").filter({ hasText: notice });
  await expect(footer).toHaveCSS("position", "fixed");
  await page.emulateMedia({ media: "print" });
  await expect(footer).toHaveCSS("position", "static");
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
