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
  await page.addInitScript(() => localStorage.setItem("theme", "light"));
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    url.host = "localhost:8000";
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  const errors: string[] = [];
  runtimeErrors.set(page, errors);
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console.error: ${message.text()} (${message.location().url})`);
  });
});

test.afterEach(async ({ page }) => {
  await page.unrouteAll({ behavior: "ignoreErrors" });
  expect(runtimeErrors.get(page), "Trang không được phát sinh pageerror hoặc console.error").toEqual([]);
});

async function assertBadgeContrast(page: Page) {
  const failures = await page.locator('[data-slot="badge"][class*="text-status-"]').evaluateAll((badges) => {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 1;
    const context = canvas.getContext("2d")!;
    const rgba = (color: string) => {
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = color;
      context.fillRect(0, 0, 1, 1);
      return [...context.getImageData(0, 0, 1, 1).data].map((channel) => channel / 255);
    };
    const blend = (front: number[], back: number[]) => {
      const alpha = front[3] + back[3] * (1 - front[3]);
      return [0, 1, 2].map((index) => (front[index] * front[3] + back[index] * back[3] * (1 - front[3])) / alpha).concat(alpha);
    };
    const background = (element: Element) => {
      let color = [0, 0, 0, 0];
      for (let current: Element | null = element; current && color[3] < 1; current = current.parentElement) {
        color = blend(color, rgba(getComputedStyle(current).backgroundColor));
      }
      return color[3] < 1 ? blend(color, [1, 1, 1, 1]) : color;
    };
    const luminance = (color: number[]) => {
      const linear = color.slice(0, 3).map((channel) => channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4);
      return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
    };
    return badges.flatMap((badge) => {
      const bg = background(badge);
      const fg = blend(rgba(getComputedStyle(badge).color), bg);
      const ratio = (Math.max(luminance(fg), luminance(bg)) + 0.05) / (Math.min(luminance(fg), luminance(bg)) + 0.05);
      return ratio < 4.5 ? [`${badge.textContent?.trim()}: ${ratio.toFixed(2)}:1 (${getComputedStyle(badge).color} trên ${getComputedStyle(badge).backgroundColor})`] : [];
    });
  });
  expect(failures, "Badge trạng thái phải đạt tương phản WCAG AA").toEqual([]);
}

async function assertResponsiveAndAccessible(page: Page, url: string) {
  await page.goto(url);
  await expect(page.locator("main h1")).toBeVisible();
  await expect(page.getByRole("status")).toHaveCount(0);

  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), `${url}: không cuộn ngang toàn trang`).toBe(true);
  await expect(page.getByRole("button", { name: "Mở điều hướng" }), `${url}: dùng nút menu dưới 1024px`).toBeVisible();
  await expect(page.locator("body > div aside")).toBeHidden();

  const uncontainedTables = await page.locator("table").evaluateAll((tables) => tables.flatMap((table) => {
    const container = table.closest('[data-slot="table-container"]');
    if (!container || table.scrollWidth <= container.clientWidth) return [];
    const overflow = getComputedStyle(container).overflowX;
    return overflow === "auto" || overflow === "scroll" ? [] : [table.textContent?.trim().slice(0, 80)];
  }));
  expect(uncontainedTables, `${url}: bảng rộng phải cuộn trong khung riêng`).toEqual([]);

  const overflowingText = await page.locator("body").evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const failures = new Set<string>();
    while (walker.nextNode()) {
      const text = walker.currentNode.textContent?.trim();
      const element = walker.currentNode.parentElement;
      if (!text || !element || element.closest('[aria-hidden="true"]') || getComputedStyle(element).visibility === "hidden") continue;
      const range = document.createRange();
      range.selectNodeContents(walker.currentNode);
      const rect = range.getBoundingClientRect();
      if (rect.width === 0 || (rect.left >= -1 && rect.right <= viewportWidth + 1)) continue;
      let scrollParent: Element | null = element;
      let contained = false;
      while (scrollParent) {
        const style = getComputedStyle(scrollParent);
        if (scrollParent.scrollWidth > scrollParent.clientWidth && ["auto", "scroll"].includes(style.overflowX)) { contained = true; break; }
        scrollParent = scrollParent.parentElement;
      }
      if (!contained) failures.add(`${element.tagName.toLowerCase()}: ${text.slice(0, 80)}`);
    }
    return [...failures];
  });
  expect(overflowingText, `${url}: chữ không được tràn khỏi viewport`).toEqual([]);

  await expect(page.locator("h1"), `${url}: đúng một h1`).toHaveCount(1);
  const headingOrder = await page.locator("h1, h2, h3, h4, h5, h6").evaluateAll((headings) => headings.map((heading) => Number(heading.tagName.slice(1))));
  expect(headingOrder.every((level, index) => index === 0 || level <= headingOrder[index - 1] + 1), `${url}: cấp heading không bị nhảy`).toBe(true);
  expect(await page.locator("img:not([alt])").count(), `${url}: mọi img phải có alt`).toBe(0);

  const unnamedIconButtons = await page.locator("button:has(svg)").evaluateAll((buttons) => buttons.flatMap((button) => {
    if (button.textContent?.trim() || button.getAttribute("aria-label") || button.getAttribute("aria-labelledby") || button.getAttribute("title")) return [];
    return [button.outerHTML.slice(0, 160)];
  }));
  expect(unnamedIconButtons, `${url}: nút chỉ có icon phải có tên truy cập`).toEqual([]);

  const unlabeledInputs = await page.locator('input:not([type="hidden"]), textarea, select').evaluateAll((inputs) => inputs.flatMap((input) => {
    const control = input as HTMLInputElement;
    if (input.getAttribute("aria-hidden") === "true") return [];
    if (control.labels?.length || input.getAttribute("aria-label") || input.getAttribute("aria-labelledby") || input.getAttribute("title")) return [];
    return [input.outerHTML.slice(0, 160)];
  }));
  expect(unlabeledInputs, `${url}: mọi ô nhập phải có nhãn`).toEqual([]);

  await page.keyboard.press("Tab");
  const focusVisible = await page.locator(":focus").evaluate((element) => {
    const style = getComputedStyle(element);
    return (style.outlineStyle !== "none" && Number.parseFloat(style.outlineWidth) > 0) || style.boxShadow !== "none";
  });
  expect(focusVisible, `${url}: focus-visible phải nhìn thấy`).toBe(true);

  await assertBadgeContrast(page);
  await page.getByRole("button", { name: "Đổi giao diện sáng/tối" }).click();
  await expect(page.locator("html")).toHaveClass(/dark/);
  await assertBadgeContrast(page);
  await page.getByRole("button", { name: "Đổi giao diện sáng/tối" }).click();
  await expect(page.locator("html")).not.toHaveClass(/dark/);
}

test("các trang H0 đáp ứng responsive và khả năng truy cập", async ({ page, request }) => {
  const works = await request.get("http://localhost:8000/api/works?page=1");
  expect(works.ok()).toBe(true);
  const workId = ((await works.json()) as { items: { id: number }[] }).items[0]?.id;
  expect(workId).toBeTruthy();

  for (const url of [
    "/tong-quan/",
    "/tra-cuu/",
    `/cong-trinh/?id=${workId}`,
    "/doi-soat/tac-gia/",
    "/doi-soat/huong-dan/",
    "/doi-soat/trung-lap/",
    "/doi-chieu/",
    "/doi-chieu/ra-soat/",
    "/ky-bao-cao/chi-tiet/?id=1",
    "/ve/",
  ]) await assertResponsiveAndAccessible(page, url);
});

test("bảng, biểu đồ, thẻ số, form và dialog vừa viewport", async ({ page }, testInfo) => {
  await page.goto("/tong-quan/");
  await expect(page.locator("main h1")).toBeVisible();
  const chart = page.getByRole("img", { name: "Biểu đồ cột chồng công trình theo năm và loại tài liệu" });
  await expect(chart).toBeVisible();
  expect(await chart.evaluate((element) => element.getBoundingClientRect().right <= document.documentElement.clientWidth + 1)).toBe(true);
  if (testInfo.project.name === "mobile") {
    const cards = page.locator('[aria-label="Chỉ số tổng quan"] > *');
    expect(await cards.nth(0).evaluate((first, second) => Math.abs(first.getBoundingClientRect().left - (second as Element).getBoundingClientRect().left), await cards.nth(1).elementHandle())).toBeLessThan(1);
    await page.screenshot({ path: path.join(imageDir, "mobile-tong-quan.png"), animations: "disabled" });
  }

  await page.goto("/doi-chieu/");
  await expect(page.locator("main h1")).toBeVisible();
  const form = page.locator("main form");
  const results = page.getByRole("region", { name: "Kết quả đối chiếu" });
  expect(await form.evaluate((element, resultTop) => element.getBoundingClientRect().bottom <= Number(resultTop) + 1, await results.evaluate((element) => element.getBoundingClientRect().top))).toBe(true);

  await page.goto("/doi-soat/tac-gia/");
  await expect(page.locator("tbody tr").first()).toBeVisible();
  const tabs = page.locator('[data-slot="tabs-list"]').filter({ has: page.getByRole("tab", { name: /^Chờ xác nhận/ }) });
  expect(await tabs.locator('[data-slot="tabs-trigger"]').first().evaluate((tab, listLeft) => tab.getBoundingClientRect().left >= Number(listLeft) - 1, await tabs.evaluate((list) => list.getBoundingClientRect().left)), "Tab đầu không được tràn khỏi mép trái").toBe(true);
  if (testInfo.project.name === "mobile") await page.screenshot({ path: path.join(imageDir, "mobile-hang-doi.png"), animations: "disabled" });
  await page.getByRole("checkbox", { name: "Chọn hàng" }).first().check();
  const batchActions = page.getByText(/liên kết đã chọn$/).locator("..");
  await expect(batchActions).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  const tableBottom = await page.locator('[data-slot="table-container"]').last().evaluate((element) => element.getBoundingClientRect().bottom);
  expect(await batchActions.evaluate((element, bottom) => element.getBoundingClientRect().top >= Number(bottom) - 1, tableBottom), "Thanh hành động không che bảng ở cuối trang").toBe(true);
  await page.getByRole("button", { name: "Chuyển cho người khác" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  expect(await dialog.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return rect.top >= 0 && rect.left >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight && element.scrollHeight <= innerHeight;
  }), "Dialog phải nằm trọn trong viewport").toBe(true);
});
