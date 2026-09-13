// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test, type Page } from "@playwright/test";
import { readFile } from "node:fs/promises";

async function expectNoPageOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
}

test("hồ sơ giảng viên hiện đầy đủ danh tính và fallback khi ảnh lỗi", async ({ page }) => {
  await page.route("https://repository.ictu.edu.vn/**", (route) => route.fulfill({ contentType: "image/svg+xml", body: '<svg xmlns="http://www.w3.org/2000/svg" width="112" height="112" />' }));
  await page.goto("/giang-vien/?id=1");

  await expect(page.getByRole("heading", { name: "PGS.TS. Nguyễn Văn A" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Ảnh đại diện của PGS.TS. Nguyễn Văn A" })).toHaveAttribute("referrerpolicy", "no-referrer");
  await page.unroute("https://repository.ictu.edu.vn/**");
  await page.route("https://repository.ictu.edu.vn/**", (route) => route.abort());
  await page.reload();
  await expect(page.getByLabel("Ảnh đại diện thay thế của PGS.TS. Nguyễn Văn A")).toContainText("N");
  await expect(page.getByText("Hiệu trưởng", { exact: true })).toBeVisible();
  await expect(page.getByText("Trí tuệ nhân tạo và khai phá dữ liệu", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: /ORCID/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /Google Scholar/ })).toBeVisible();
  await expect(page.getByText(/giới tính|ngày sinh|điện thoại/i)).toHaveCount(0);

  await page.goto("/doi-chieu/chuyen-gia/");
  await page.getByText("Bộ lọc nâng cao", { exact: true }).click();
  await page.getByRole("combobox", { name: "Tìm người" }).fill("Nguyễn");
  const searchAvatar = page.getByLabel("Ảnh đại diện thay thế của TS. Nguyễn Văn A", { exact: true });
  await expect(searchAvatar).toBeVisible();
  expect((await searchAvatar.boundingBox())?.width).toBe(36);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/giang-vien/?id=1");
  await expect(page.getByRole("button", { name: "Tải BibTeX (tất cả)" })).toBeVisible();
  await expectNoPageOverflow(page);
});

test("lọc loại nơi công bố giữ URL và mỗi kết quả mở được trích dẫn", async ({ page }) => {
  await page.goto("/tra-cuu/");

  await expect(page.getByRole("combobox", { name: "Chỉ mục" })).toBeVisible();
  await page.getByRole("combobox", { name: "Loại nơi công bố" }).click();
  await page.getByRole("option", { name: "Tạp chí quốc tế (1)" }).click();
  await page.getByRole("button", { name: "Tra cứu", exact: true }).click();

  await expect(page).toHaveURL(/venue_kind=journal_intl/);
  await expect(page.locator("tbody tr")).toHaveCount(1);
  const row = page.getByRole("row", { name: /Ứng dụng học sâu trong nhận dạng bệnh trên lá chè/ });
  await row.getByRole("button", { name: /Trích dẫn/ }).click();
  await expect(page.getByRole("dialog", { name: "Trích dẫn công trình" })).toBeVisible();
  await page.keyboard.press("Escape");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/tra-cuu/?venue_kind=journal_intl");
  await page.getByText("Bộ lọc (1 đang áp dụng)", { exact: true }).click();
  await expect(page.getByRole("combobox", { name: "Loại nơi công bố" })).toBeVisible();
  await expectNoPageOverflow(page);
});

test("tải BibTeX và sao chép APA cho toàn bộ công trình của giảng viên", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/giang-vien/?id=1");

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Tải BibTeX (tất cả)" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("giang-vien-1.bib");
  expect(await readFile(await download.path()!, "utf8")).toContain("@thesis{");

  await page.getByRole("button", { name: "Sao chép APA (tất cả)" }).click();
  await expect.poll(() => page.evaluate(() => navigator.clipboard.readText())).toContain("Nguyễn, V. A.");
});
