// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("hướng dẫn hiển thị đủ vai trò, ảnh mô tả và mở được trang tra cứu", async ({ page }) => {
  await page.goto("/huong-dan/");

  for (const role of ["Phòng KH-CN", "Khoa", "Giảng viên", "Lãnh đạo"]) {
    await expect(page.getByRole("heading", { name: role, exact: true })).toBeVisible();
  }

  const images = page.locator("main img");
  await expect(images).toHaveCount(10);
  expect(await images.evaluateAll((items) => items.every((item) => Boolean(item.getAttribute("alt")?.trim())))).toBe(true);

  await page.locator('main a[href="/tra-cuu/"]').first().click();
  await expect(page).toHaveURL(/\/tra-cuu\/$/);
  await expect(page.getByRole("heading", { name: "Tra cứu công trình" })).toBeVisible();
});
