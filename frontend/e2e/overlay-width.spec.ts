// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { expect, test, type Page } from "@playwright/test";

/** Popup overlay phải đủ rộng cho mục dài nhất và không tràn khỏi màn hình. */
async function expectPopupFitsContent(page: Page, popupSelector: string, itemSelector: string) {
  const metrics = await page.evaluate(
    ([popupSel, itemSel]) => {
      const popups = [...document.querySelectorAll(popupSel)].filter(
        (node) => node.getBoundingClientRect().width > 0,
      );
      const popup = popups[popups.length - 1];
      if (!popup) return null;
      const box = popup.getBoundingClientRect();
      const items = [...popup.querySelectorAll(itemSel)];
      const clipped = items
        .filter((item) => {
          const text = item.querySelector("span") ?? item;
          return text.scrollWidth > text.clientWidth + 1;
        })
        .map((item) => item.textContent?.trim() ?? "");
      return {
        clipped,
        selfClipped: popup.scrollWidth > popup.clientWidth + 1,
        left: box.left,
        right: box.right,
        viewportWidth: window.innerWidth,
        pageOverflow: document.documentElement.scrollWidth - window.innerWidth,
      };
    },
    [popupSelector, itemSelector] as const,
  );

  expect(metrics, "popup phải mở ra").not.toBeNull();
  expect(metrics!.clipped, "không mục nào được bị cắt chữ").toEqual([]);
  expect(metrics!.selfClipped, "popup không được giấu nội dung theo chiều ngang").toBe(false);
  expect(metrics!.left).toBeGreaterThanOrEqual(-1);
  expect(metrics!.right).toBeLessThanOrEqual(metrics!.viewportWidth + 1);
  expect(metrics!.pageOverflow, "trang không được tràn ngang").toBeLessThanOrEqual(0);
}

for (const viewport of [
  { name: "desktop", width: 1440, height: 900 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
]) {
  test(`bộ lọc Khoa hiện đủ tên khoa ở ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto("/tra-cuu/");
    // Dưới 1024px các ô lọc nằm trong khối gập, mặc định đóng — mở ra như người dùng thật.
    const collapsedFilters = page.getByText(/^Bộ lọc \(\d+ đang áp dụng\)$/);
    if (await collapsedFilters.isVisible()) await collapsedFilters.click();
    // Trang dựng hai ô "Khoa" (hàng lọc rộng và khối gập hẹp); chỉ một cái hiện mỗi lúc.
    await page.locator('[aria-label="Khoa"]:visible').first().click();
    await expect(page.getByRole("option", { name: /Khoa Công nghệ điện tử và truyền thông/ })).toBeVisible();
    await expectPopupFitsContent(page, '[data-slot="select-content"]', '[data-slot="select-item"]');
  });
}

test("menu Hành động hiện đủ chữ từng mục", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/ky-bao-cao/");
  await page.getByRole("link", { name: "Báo cáo công trình năm 2026", exact: true }).click();
  await page.getByRole("tab", { name: "Hồ sơ kê khai" }).click();
  await page.getByRole("button", { name: /Hành động hồ sơ/ }).first().click();
  await expect(page.getByRole("menuitem").first()).toBeVisible();
  await expectPopupFitsContent(page, '[data-slot="dropdown-menu-content"]', '[data-slot="dropdown-menu-item"]');
});
