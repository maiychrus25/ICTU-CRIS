// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("lọc điểm quy đổi cập nhật URL và chỉ giữ công trình phù hợp", async ({ page }) => {
  await page.goto("/tra-cuu/");

  await page.getByRole("combobox", { name: "Điểm quy đổi" }).click();
  await page.getByRole("option", { name: "0,75 điểm (1)" }).click();
  await page.getByRole("button", { name: "Tra cứu", exact: true }).click();

  await expect(page).toHaveURL(/\/tra-cuu\/\?score=0\.75$/);
  await expect(page.getByRole("row", { name: /Ứng dụng học sâu trong nhận dạng bệnh trên lá chè/ })).toContainText("0,75 điểm");
  await expect(page.locator("tbody tr")).toHaveCount(1);
});

test("chip đơn vị ở chi tiết công trình mở tra cứu theo mã", async ({ page }) => {
  await page.goto("/cong-trinh/?id=2");

  const unit = page.getByRole("link", { name: "CNTT" });
  await expect(unit).toHaveAttribute("title", "Khoa Công nghệ thông tin");
  await unit.click();

  await expect(page).toHaveURL(/\/tra-cuu\/\?unit=CNTT$/);
});

test("hồ sơ giảng viên tách chức vụ khỏi đơn vị", async ({ page }) => {
  await page.goto("/giang-vien/?id=1");

  await expect(page.getByText("Hiệu trưởng", { exact: true })).toBeVisible();
  await expect(page.getByText("CNTT — Khoa Công nghệ thông tin", { exact: true })).toHaveAttribute("title", "Suy từ đa số công trình đã liên kết");
  await expect(page.getByText("Ban Giám hiệu", { exact: true })).toHaveCount(0);
});
