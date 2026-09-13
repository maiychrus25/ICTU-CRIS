// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from "@playwright/test";

test("tổng quan giới hạn cập nhật và xếp thẻ số hai cột trên điện thoại", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/tong-quan/");

  await expect(page.locator('[aria-label="Công trình thay đổi gần đây"] > li')).toHaveCount(5);
  await expect(page.getByRole("link", { name: "Xem tất cả (8)" })).toHaveAttribute("href", "/dong-bo/");
  const metricCards = page.locator('[aria-label="Chỉ số tổng quan"] > *');
  const first = await metricCards.nth(0).boundingBox();
  const second = await metricCards.nth(1).boundingBox();
  expect(first?.y).toBe(second?.y);
  expect(first?.x).not.toBe(second?.x);
});

test("tra cứu giấu bộ lọc phụ trên điện thoại và không cuộn bảng ở 1280px", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/tra-cuu/");

  const filters = page.getByText("Bộ lọc (0 đang áp dụng)", { exact: true });
  await expect(filters).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Loại tài liệu" })).toBeHidden();
  await filters.click();
  await page.getByRole("combobox", { name: "Loại tài liệu" }).click();
  await page.getByRole("option", { name: "Bài báo" }).click();
  await page.getByRole("button", { name: "Tra cứu", exact: true }).click();
  await expect(page.getByLabel("Bộ lọc đang áp dụng").getByText("Bài báo", { exact: true })).toBeVisible();

  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/tra-cuu/");
  const tableContainer = page.locator('main [data-slot="table-container"]').last();
  await expect(tableContainer).toBeVisible();
  expect(await tableContainer.evaluate((element) => element.scrollWidth <= element.clientWidth)).toBe(true);
});

test("bản đồ hiện nhãn tô màu thay vì mã thô", async ({ page }) => {
  await page.goto("/ban-do/");
  await expect(page.getByRole("combobox", { name: "Tô màu bản đồ theo" })).toContainText("Chủ đề");
});

test("xuất xứ rút gọn nguồn, giữ URL và ẩn trường trống", async ({ page }) => {
  await page.goto("/cong-trinh/?id=1");

  const source = page.getByRole("link", { name: /Kho ICTU · 10\/09\/2026/ }).first();
  await expect(source).toHaveAttribute("href", "https://repository.ictu.edu.vn/works/1");
  await expect(page.getByRole("button", { name: "Hiện 3 trường chưa có dữ liệu" })).toBeVisible();
  await expect(page.getByText("Tạp chí", { exact: true })).toBeHidden();
});

test("hàng đợi gom ứng viên theo lượt tên và công trình", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/doi-soat/tac-gia/");

  const group = page.getByRole("article", { name: /Nguyễn Văn A.*Xây dựng website quản lý thư viện/ });
  await expect(group).toBeVisible();
  await expect(group.getByRole("radio")).toHaveCount(3);
  await expect(group.getByRole("link", { name: /Xây dựng website quản lý thư viện/ })).toHaveCount(1);
  await expect(group.getByRole("button", { name: "Xác nhận ứng viên đã chọn" })).toBeVisible();
  await expect(page.locator('main [data-slot="table-container"]')).toHaveCount(0);
});

test("tài khoản chưa gắn giảng viên không gọi API kê khai cá nhân", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  const myWorksRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/me/works")) myWorksRequests.push(request.url());
  });
  await page.goto("/ke-khai-cua-toi/");
  await expect(page.getByText("Trang này dành cho giảng viên có tài khoản; đăng nhập bằng tài khoản giảng viên để xem công trình của mình")).toBeVisible();
  await expect(page.getByRole("button", { name: "Thử lại" })).toHaveCount(0);
  expect(myWorksRequests).toHaveLength(0);
});

test("khách chưa đăng nhập chỉ thấy sáu mục công khai", async ({ page }) => {
  await page.addInitScript(() => window.sessionStorage.setItem("cris:mock-user", "signed-out"));
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/dang-nhap/");
  const sidebar = page.locator("aside");
  for (const label of ["Tra cứu", "Chủ đề", "Bản đồ tri thức", "Kiểm tra đề tài", "Hướng dẫn", "Về hệ thống"]) {
    await expect(sidebar.getByRole("link", { name: label, exact: true })).toBeVisible();
  }
  for (const label of ["Tổng quan", "Hàng đợi tác giả", "Hàng đợi nghi trùng", "Kỳ báo cáo", "Đồng bộ", "Nhật ký"]) {
    await expect(sidebar.getByRole("link", { name: label, exact: true })).toHaveCount(0);
  }
});
