// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("trang gốc chuyển sang tra cứu", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/tra-cuu\/$/);
  await expect(page.getByRole("heading", { name: "Tra cứu công trình" })).toBeVisible();
  await expect(page.locator("html")).toHaveCSS("font-family", /Be Vietnam Pro/);
  await expect(page.getByText("Tất cả", { exact: true })).toBeVisible();
});

test("chi tiết công trình hiển thị xuất xứ và tác giả", async ({ page }) => {
  await page.goto("/cong-trinh/?id=1");
  await expect(page.getByRole("heading", { name: "Chi tiết công trình" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Xuất xứ dữ liệu" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Tác giả" })).toBeVisible();
});

test("đối chiếu hiển thị ghi chú và ma trận khía cạnh", async ({ page }) => {
  await page.goto("/doi-chieu/?id=101");
  await expect(page.getByRole("heading", { name: "Đối chiếu đề tài" })).toBeVisible();
  await expect(page.getByText(/không phải toàn văn/i)).toBeVisible();
  await expect(page.getByText("Bài toán", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Phương pháp", { exact: true }).first()).toBeVisible();
});

test("trang về hệ thống nêu AI và giới hạn", async ({ page }) => {
  await page.goto("/ve/");
  await expect(page.getByRole("heading", { name: "Về hệ thống" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "AI trong hệ thống" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Giới hạn cần lưu ý" })).toBeVisible();
});
