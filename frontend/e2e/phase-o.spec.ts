// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("mở danh bạ giảng viên từ điều hướng công khai", async ({ page }) => {
  await page.goto("/tra-cuu/");
  const navigation = page.getByRole("navigation", { name: "Điều hướng chính" });
  await navigation.getByRole("link", { name: "Giảng viên", exact: true }).click();

  await expect(page).toHaveURL(/\/giang-vien\/$/);
  await expect(page.getByRole("heading", { name: /Giảng viên · 32/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /PGS\.TS\. Nguyễn Văn A/ }).first()).toBeVisible();
});

test("tìm và lọc danh bạ theo khoa, học vị và công trình", async ({ page }) => {
  await page.goto("/giang-vien/");
  await page.getByLabel("Tìm theo tên giảng viên").fill("nguyen van a");
  await page.getByRole("combobox", { name: "Khoa" }).click();
  await page.getByRole("option", { name: /CNTT — Khoa Công nghệ thông tin/ }).click();
  await page.getByRole("combobox", { name: "Học hàm, học vị" }).click();
  await page.getByRole("option", { name: "Phó giáo sư" }).click();
  await page.getByRole("checkbox", { name: "Chỉ người có công trình" }).check();

  await expect(page).toHaveURL(/q=nguyen(?:\+|%20)van(?:\+|%20)a/);
  await expect(page).toHaveURL(/unit=CNTT/);
  await expect(page).toHaveURL(/degree=pgs/);
  await expect(page).toHaveURL(/has_works=true/);
  await expect(page.getByRole("link", { name: /PGS\.TS\. Nguyễn Văn A/ })).toHaveCount(1);
  await expect(page.getByRole("region", { name: "Danh sách giảng viên" }).getByText(/@|\.edu\.vn|điện thoại|ngày sinh/i)).toHaveCount(0);
});

test("mở hồ sơ rồi quay lại vẫn giữ bộ lọc danh bạ", async ({ page }) => {
  await page.goto("/giang-vien/?q=nguyen+van+a&unit=CNTT&degree=pgs&sort=name&page=1");
  await page.getByRole("link", { name: /PGS\.TS\. Nguyễn Văn A/ }).click();

  await expect(page).toHaveURL(/\/giang-vien\/\?id=1$/);
  await expect(page.getByRole("link", { name: "Danh bạ giảng viên" })).toBeVisible();
  await page.goBack();
  await expect(page).toHaveURL(/q=nguyen(?:\+|%20)van(?:\+|%20)a&unit=CNTT&degree=pgs&sort=name&page=1/);
  await expect(page.getByRole("combobox", { name: "Khoa" })).toContainText("CNTT");
});

test("tab loại công trình và sắp xếp đồng bộ URL", async ({ page }) => {
  await page.goto("/tra-cuu/");
  await page.getByRole("navigation", { name: "Điều hướng chính" }).getByRole("link", { name: /Đồ án\/Khoá luận/ }).click();
  await expect(page.getByRole("tab", { name: /Đồ án\/Khoá luận/ })).toHaveAttribute("aria-selected", "true");
  await page.getByRole("combobox", { name: "Sắp xếp" }).click();
  await page.getByRole("option", { name: "Tiêu đề A→Z" }).click();

  await expect(page).toHaveURL(/doc_type=do_an/);
  await expect(page).toHaveURL(/sort=title/);
  await expect(page.getByRole("cell", { name: "Khoá 21" }).first()).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Loại nơi công bố" })).toHaveCount(0);
});

test("thẻ toàn bộ kho mở đúng danh sách loại và danh bạ", async ({ page }) => {
  await page.goto("/tong-quan/");
  const repository = page.getByRole("region", { name: "Toàn bộ kho" });
  await expect(repository.getByText("7.618", { exact: true })).toBeVisible();
  await repository.getByRole("link", { name: /Đồ án\/Khoá luận/ }).click();
  await expect(page).toHaveURL(/\/tra-cuu\/\?doc_type=do_an$/);

  await page.goto("/tong-quan/");
  await page.getByRole("region", { name: "Toàn bộ kho" }).getByRole("link", { name: /Giảng viên/ }).click();
  await expect(page).toHaveURL(/\/giang-vien\/$/);
});
