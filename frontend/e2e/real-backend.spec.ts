// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test, type Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const imageDir = path.resolve(process.cwd(), "../docs/images");
const runtimeErrors = new WeakMap<Page, string[]>();

test.beforeAll(async () => {
  await mkdir(imageDir, { recursive: true });
});

test.beforeEach(async ({ page }) => {
  const errors: string[] = [];
  runtimeErrors.set(page, errors);
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console.error: ${message.text()} (${message.location().url})`);
  });
});

test.afterEach(async ({ page }) => {
  expect(runtimeErrors.get(page), "Trang không được phát sinh pageerror hoặc console.error").toEqual([]);
});

async function assertHealthyPage(page: Page) {
  await expect(page.locator("main h1")).toBeVisible();
  await expect(page.getByRole("status")).toHaveCount(0);
  await expect(page.getByText("Đã xảy ra lỗi", { exact: true })).toHaveCount(0);
  await expect(page.locator("main")).not.toContainText(/undefined|NaN|\[object Object\]/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), "Trang không được tràn ngang viewport").toBe(true);

  const unnamedIconButtons = await page.locator("button:has(svg)").evaluateAll((buttons) =>
    buttons.filter((button) => !button.getAttribute("aria-label") && !button.getAttribute("title") && !button.textContent?.trim()).length,
  );
  expect(unnamedIconButtons, "Mọi nút chỉ có icon phải có aria-label hoặc title").toBe(0);
}

async function capture(page: Page, name: string) {
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(imageDir, name), fullPage: false, animations: "disabled" });
}

test("tổng quan, tra cứu, công trình và hồ sơ giảng viên dùng dữ liệu thật", async ({ page }) => {
  await page.goto("/tong-quan/");
  await assertHealthyPage(page);
  await expect(page.getByText("Tổng công trình 5 năm", { exact: true })).toBeVisible();
  await capture(page, "tong-quan.png");

  await page.goto("/tra-cuu/");
  await page.getByLabel("Từ khoá").fill("website");
  await page.getByRole("button", { name: "Tra cứu" }).click();
  await expect(page.locator('tbody a[href^="/cong-trinh/?id="]').first()).toBeVisible();
  await assertHealthyPage(page);
  await capture(page, "tra-cuu.png");

  await page.locator('tbody a[href^="/cong-trinh/?id="]').first().click();
  await expect(page).toHaveURL(/\/cong-trinh\/\?id=\d+/);
  await expect(page.getByRole("heading", { name: "Xuất xứ dữ liệu" })).toBeVisible();
  const personLink = page.locator('a[href^="/giang-vien/?id="]').first();
  await expect(personLink).toBeVisible();
  const personHref = await personLink.getAttribute("href");
  expect(personHref).toMatch(/^\/giang-vien\/\?id=\d+$/);
  await assertHealthyPage(page);
  await capture(page, "cong-trinh.png");

  await page.goto(personHref!);
  await expect(page.getByRole("heading", { name: "Danh sách công trình" })).toBeVisible();
  await assertHealthyPage(page);
  await capture(page, "giang-vien.png");
});

test("bốn tab hàng đợi tác giả chỉ được đọc", async ({ page }) => {
  await page.goto("/doi-soat/tac-gia/");
  await assertHealthyPage(page);
  await expect(page.getByText("Tên đầy đủ, nhiều ứng viên").first()).toHaveClass(/text-status-warning/);
  await expect(page.getByText("ten_day_du_nhieu_ung_vien", { exact: true })).toHaveCount(0);
  const candidate = page.locator('tbody a[href^="/giang-vien/?id="]').first();
  await expect(candidate).toBeVisible();
  await expect(candidate).toHaveCSS("text-transform", "capitalize");
  await capture(page, "hang-doi-tac-gia.png");

  for (const name of ["Chờ xác nhận", "Đã nối tự động", "Đã xác nhận", "Đã bác bỏ"]) {
    await page.getByRole("tab", { name: new RegExp(`^${name}`) }).click();
    await assertHealthyPage(page);
    if (name === "Đã nối tự động") {
      await expect(page.getByText("Tên đầy đủ, một ứng viên").first()).toHaveClass(/text-status-success/);
    }
  }
});

test("hàng đợi nghi trùng mở chi tiết nhưng không quyết định", async ({ page }) => {
  await page.goto("/doi-soat/trung-lap/");
  await expect(page.locator("tbody tr").first()).toBeVisible();
  await assertHealthyPage(page);
  await capture(page, "nghi-trung.png");

  await page.locator("tbody tr").first().click();
  await expect(page).toHaveURL(/\/doi-soat\/trung-lap\/chi-tiet\/\?id=\d+/);
  await expect(page.getByRole("heading", { name: "So sánh bản ghi" })).toBeVisible();
  await expect(page.locator("thead").getByText("Nghi trùng", { exact: true }).first()).toBeVisible();
  await assertHealthyPage(page);
});

test("chi tiết công trình gắn nhãn mã trạng thái và loại nơi công bố", async ({ page }) => {
  await page.goto("/cong-trinh/?id=458");
  await expect(page.getByText("Đã chuẩn hoá", { exact: true })).toBeVisible();
  await expect(page.getByText("Tạp chí quốc tế", { exact: true })).toBeVisible();
  await expect(page.getByText("DaChuanHoa", { exact: true })).toHaveCount(0);
  await expect(page.getByText("journal_intl", { exact: true })).toHaveCount(0);
});

test("đối chiếu đề tài thật hoàn tất trong 30 giây", async ({ page }) => {
  await page.goto("/doi-chieu/");
  await page.getByLabel("Tiêu đề đề tài").fill("Xây dựng website bán hàng");
  await page.getByRole("button", { name: "Đối chiếu đề tài" }).click();
  await expect(page.getByText("Phạm vi kết quả", { exact: true })).toBeVisible({ timeout: 30_000 });
  await expect(page.locator('a[href^="/cong-trinh/?id="]')).toHaveCount(5);
  await assertHealthyPage(page);
  await capture(page, "doi-chieu.png");
});

test("rà soát khoá 21 và các trang quản trị chỉ được đọc", async ({ page }) => {
  await page.goto("/doi-chieu/ra-soat/");
  await page.getByRole("combobox", { name: "Khoá rà soát" }).click();
  await page.getByRole("option", { name: /^Khoá 21/ }).click();
  await expect(page.getByRole("region", { name: "Kết quả rà soát" })).toBeVisible();
  await assertHealthyPage(page);
  await capture(page, "ra-soat.png");

  for (const [url, heading] of [
    ["/ky-bao-cao/", "Kỳ báo cáo"],
    ["/nhat-ky/", "Nhật ký thao tác"],
    ["/chat-luong-du-lieu/", "Chất lượng dữ liệu"],
    ["/ve/", "Về hệ thống"],
  ] as const) {
    await page.goto(url);
    await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
    await assertHealthyPage(page);
  }
});

test("focus nhìn thấy và nhãn biểu đồ đủ tương phản ở chế độ tối", async ({ page }) => {
  await page.goto("/tong-quan/");
  await assertHealthyPage(page);
  await page.getByRole("button", { name: "Đổi giao diện sáng/tối" }).click();
  await expect(page.locator("html")).toHaveClass(/dark/);
  await page.keyboard.press("Tab");
  expect(await page.locator(":focus").evaluate((element) => getComputedStyle(element).boxShadow !== "none"), "Phần tử nhận focus phải có vòng focus").toBe(true);

  const contrast = await page.locator(".recharts-cartesian-axis-tick-value").first().evaluate((tick) => {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 1;
    const context = canvas.getContext("2d")!;
    const rgb = (color: string) => {
      context.fillStyle = color;
      context.fillRect(0, 0, 1, 1);
      return [...context.getImageData(0, 0, 1, 1).data].slice(0, 3).map((channel) => {
        const value = channel / 255;
        return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
      });
    };
    const luminance = ([red, green, blue]: number[]) => 0.2126 * red + 0.7152 * green + 0.0722 * blue;
    const foreground = luminance(rgb(getComputedStyle(tick).fill));
    const background = luminance(rgb(getComputedStyle(tick.closest('[role="img"]')!).backgroundColor));
    return (Math.max(foreground, background) + 0.05) / (Math.min(foreground, background) + 0.05);
  });
  expect(contrast, "Nhãn trục biểu đồ tối phải đạt WCAG AA").toBeGreaterThanOrEqual(4.5);
});
