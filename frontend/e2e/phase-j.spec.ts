// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("tìm theo nghĩa lưu chế độ trong URL và hiện ghi chú cùng độ gần", async ({ page }) => {
  await page.goto("/tra-cuu/");
  await page.getByRole("button", { name: "Theo nghĩa (AI)" }).click();
  await page.getByLabel("Từ khoá").fill("app dạy trẻ phát âm");
  await page.getByRole("button", { name: "Tra cứu", exact: true }).click();

  await expect(page).toHaveURL(/mode=semantic/);
  await expect(page.getByText("Tìm theo nghĩa (AI): kết quả có thể không chứa từ đã gõ.")).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "Độ gần" })).toBeVisible();
  await expect(page.getByRole("progressbar", { name: /Độ gần/ }).first()).toBeVisible();
});

test("tìm chuyên gia trả ba dẫn chứng và URL chia sẻ", async ({ page }) => {
  await page.goto("/doi-chieu/chuyen-gia/");
  await page.getByLabel("Tiêu đề đề tài").fill("Ứng dụng AI hỗ trợ học phát âm");
  await page.getByLabel("Mô tả").fill("Nhận dạng giọng nói tiếng Việt cho trẻ em.");
  await page.getByRole("button", { name: "Tìm chuyên gia", exact: true }).click();

  await expect(page).toHaveURL(/\/doi-chieu\/chuyen-gia\/\?id=\d+/);
  const first = page.getByRole("region", { name: "Kết quả tìm chuyên gia" }).locator("article").first();
  await expect(first.getByRole("listitem")).toHaveCount(3);
  await expect(first).toContainText("bài liên quan");
  await expect(page.getByText(/Gợi ý được tính trên tiêu đề và tóm tắt/)).toBeVisible();
});

test("cổng kiểm tra đề tài công khai không có sidebar và trả hai nhóm kết quả", async ({ page }) => {
  await page.goto("/kiem-tra-de-tai/");
  await expect(page.locator("aside")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Mở điều hướng" })).toHaveCount(0);
  await page.getByLabel("Tên đề tài dự định").fill("Xây dựng website quản lý thư viện thông minh");
  await page.getByRole("button", { name: "Kiểm tra", exact: true }).click();

  await expect(page.getByRole("heading", { name: "Đề tài tương tự các khoá trước" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Giảng viên gần chuyên môn" })).toBeVisible();
  await expect(page.locator('a[href^="mailto:"]')).toHaveCount(0);
});

test("bản đồ canvas mở chi tiết khi bấm một điểm", async ({ page }) => {
  await page.goto("/ban-do/");
  const canvas = page.getByTestId("knowledge-map-canvas");
  await expect(canvas).toBeVisible({ timeout: 15_000 });
  const box = await canvas.boundingBox();
  expect(box).not.toBeNull();
  const position = { x: box!.width * 0.28, y: box!.height * 0.325 };
  await canvas.hover({ position });
  await expect(page.getByRole("tooltip")).toBeVisible();
  await canvas.click({ position });
  await expect(page).toHaveURL(/\/cong-trinh\/\?id=\d+/, { timeout: 30_000 });
});

test("xu hướng đổi được giữa khoá và năm", async ({ page }) => {
  await page.goto("/ban-do/");
  await page.getByRole("tab", { name: "Xu hướng" }).click();
  const table = page.getByTestId("trend-table");
  await expect(table.getByText("K18", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Theo năm" }).click();
  await expect(table.getByText("2021", { exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: "Biểu đồ vùng xếp chồng theo năm" })).toBeVisible();
});
