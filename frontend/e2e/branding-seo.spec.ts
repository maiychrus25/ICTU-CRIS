// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("mỗi trang có tiêu đề riêng và nhận diện ICTU-CRIS", async ({ page }) => {
  await page.goto("/tra-cuu/");
  await expect(page).toHaveTitle("Tra cứu · ICTU-CRIS");
  await expect(page.locator('aside img[src="/brand/icut-cris-mark.svg"]:visible')).toBeVisible();

  await page.goto("/dang-nhap/");
  await expect(page.locator('main img[src="/brand/icut-cris-logo.svg"]')).toBeVisible();
});
