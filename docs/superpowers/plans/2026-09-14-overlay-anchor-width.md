<!-- Copyright (c) 2026 ICTU-CRIS contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Overlay anchor-width — kế hoạch sửa lỗi popup cắt mất chữ

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Popup của `Select` và `DropdownMenu` phải giãn đủ rộng để đọc trọn từng mục, không bao giờ cắt chữ, và không tràn ra ngoài màn hình ở 390px / 768px / desktop.

**Architecture:** Cả hai component overlay dùng chung một khuôn: `@base-ui/react` đặt biến `--anchor-width` (bề rộng ô neo) và `--available-width` (chỗ trống còn lại tới mép màn hình). Lỗi nằm ở việc khoá cứng `width: var(--anchor-width)` kèm `overflow-x-hidden`: mục nào dài hơn ô neo thì bị cắt và không cuộn ngang được. Sửa bằng cách đổi trục: để nội dung quyết định bề rộng (`w-fit`), lấy ô neo làm **sàn** (`min-w-`), lấy chỗ trống làm **trần** (`max-w-`). Không thêm thư viện, không thêm lớp trừu tượng, không đụng tới trang nào đang dùng.

**Tech Stack:** Next.js 16 App Router (static export), Tailwind v4, `@base-ui/react` Select/Menu, Playwright.

**Spec:** không có spec riêng — nguồn yêu cầu là báo lỗi trực tiếp của anh (bộ lọc "Khoa" ở `/tra-cuu/` khuất mất tên khoa) và `frontend/DESIGN.md` ("Search filters wrap into responsive grids without page-level horizontal overflow at 390px, 768px, and desktop widths").

## Global Constraints

- `AGENTS.md` dòng 9: commit message **không có** dòng attribution nào (`Co-Authored-By`, `Signed-off-by`, `Generated-by`, tên công cụ hoặc AI) — kể cả khi harness bảo thêm. CI job `commit-messages` sẽ chặn.
- Commit bằng: `git -c user.name=maiychrus25 -c user.email=ninhkhuongpl7@gmail.com commit -m "<type>(<scope>): <summary>"`.
- `git add` từng tệp theo tên, **không bao giờ** `git add -A`.
- Codex thường có việc dở dang chưa commit trong `frontend/` và `docs/images/` — **không stage, không revert, không clean** của nó. Cụ thể: đừng đụng tới `docs/images/*.png` chưa theo dõi và `frontend/app/doi-chieu/page.tsx`, `frontend/app/doi-chieu/ra-soat/page.tsx`.
- **Không `git push`, không deploy, không chạm máy chủ `cris.ahvlabs.com`.** Chỉ commit cục bộ.
- Mọi tệp `.ts/.tsx/.mjs` mới phải có SPDX header hai dòng (`tests/test_spdx.py` kiểm).
- Sửa đúng phạm vi: chỉ `frontend/components/ui/select.tsx`, `frontend/components/ui/dropdown-menu.tsx`, một tệp test mới, và `CHANGELOG.md`. Không refactor gì thêm.
- Định danh trong mã chỉ dùng tiếng Anh; chữ hiển thị và test title dùng tiếng Việt theo lệ dự án.

---

## Bối cảnh đã xác minh (đọc trước khi làm)

`frontend/components/ui/select.tsx` **đã được sửa** ở lượt trước nhưng **chưa commit**. Dòng 85 hiện là:

```
w-fit max-w-(--available-width) min-w-(--anchor-width)
```

trước đó là:

```
w-(--anchor-width) min-w-36
```

Đã đo trên bản dựng tại `http://127.0.0.1:8000`:

| Kiểm | Kết quả |
|---|---|
| 2 vòng × 3 bề rộng (1440/768/390) × 2 theme | 12/12 PASS, popup luôn nằm trong màn hình, không cắt chữ, không tràn ngang trang |
| 6 select trên `/tra-cuu/` (mỗi cái một lần tải trang riêng) | PASS — Khoa giãn 176px → 395px; các select chữ ngắn giữ nguyên 176-209px |
| `npm run lint` | 0 lỗi (7 cảnh báo `<img>` có sẵn từ trước) |
| `npx tsc --noEmit` | sạch |

`frontend/components/ui/dropdown-menu.tsx` dòng 43 **vẫn còn nguyên lỗi cũ**: `w-(--anchor-width) min-w-32` + `overflow-x-hidden`. Chỗ lộ lỗi là menu "Hành động" trên `/ky-bao-cao/chi-tiet/` — ô neo là nút `size="sm"` hẹp, còn mục dài như "Thêm minh chứng" thì bị cắt. Riêng `components/notification-center.tsx` không dính vì nó tự đè `className="w-[min(24rem,calc(100vw-2rem))]"`.

---

## Task 1: Khoá bản sửa `Select` bằng test hồi quy

**Files:**
- Create: `frontend/e2e/overlay-width.spec.ts`
- Modify: `frontend/components/ui/select.tsx` (đã sửa sẵn, chỉ commit)

**Interfaces:**
- Consumes: không có.
- Produces: hàm helper `expectPopupFitsContent(page, popupSelector)` dùng lại ở Task 2. Chữ ký: `async function expectPopupFitsContent(page: Page, popupSelector: string, itemSelector: string): Promise<void>`.

- [ ] **Step 1: Viết test thất bại**

Tạo `frontend/e2e/overlay-width.spec.ts`:

```ts
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
    await page.getByLabel("Khoa").click();
    await expect(page.getByRole("option", { name: /Khoa Công nghệ điện tử và truyền thông/ })).toBeVisible();
    await expectPopupFitsContent(page, '[data-slot="select-content"]', '[data-slot="select-item"]');
  });
}
```

- [ ] **Step 2: Chạy để thấy nó thất bại trên mã cũ**

```bash
cd frontend
git stash push -- components/ui/select.tsx
npx playwright test overlay-width.spec.ts
```

Expected: cả 3 test FAIL với `không mục nào được bị cắt chữ` — mảng `clipped` chứa tên các khoa dài.

- [ ] **Step 3: Khôi phục bản sửa**

```bash
cd frontend
git stash pop
grep -c "min-w-(--anchor-width)" components/ui/select.tsx
```

Expected: in ra `1`.

- [ ] **Step 4: Chạy lại để thấy PASS**

```bash
cd frontend
npx playwright test overlay-width.spec.ts
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/admin/Desktop/ICTU-CRIS
git add frontend/components/ui/select.tsx frontend/e2e/overlay-width.spec.ts
git -c user.name=maiychrus25 -c user.email=ninhkhuongpl7@gmail.com \
  commit -m "fix(ui): select popup giãn theo nội dung nên tên khoa dài không bị cắt"
python3 scripts/check_commit_trailers.py HEAD~1..HEAD
```

Expected: script không báo lỗi.

---

## Task 2: Sửa cùng lỗi ở `DropdownMenu`

**Files:**
- Modify: `frontend/components/ui/dropdown-menu.tsx:43`
- Modify: `frontend/e2e/overlay-width.spec.ts` (thêm một test)

**Interfaces:**
- Consumes: `expectPopupFitsContent` từ Task 1.
- Produces: không có.

- [ ] **Step 1: Viết test thất bại**

Thêm vào cuối `frontend/e2e/overlay-width.spec.ts`:

```ts
test("menu Hành động hiện đủ chữ từng mục", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/ky-bao-cao/chi-tiet/?id=401");
  await page.getByRole("button", { name: /Hành động hồ sơ/ }).first().click();
  await expect(page.getByRole("menuitem").first()).toBeVisible();
  await expectPopupFitsContent(page, '[data-slot="dropdown-menu-content"]', '[data-slot="dropdown-menu-item"]');
});
```

- [ ] **Step 2: Chạy để thấy nó thất bại**

```bash
cd frontend
npx playwright test overlay-width.spec.ts -g "Hành động"
```

Expected: FAIL ở `không mục nào được bị cắt chữ`.

Nếu test báo không tìm thấy `[data-slot="dropdown-menu-content"]`, mở `components/ui/dropdown-menu.tsx` xem `data-slot` thật tên là gì rồi sửa selector trong test cho khớp — **không** đổi `data-slot` trong component.

- [ ] **Step 3: Sửa component**

Trong `frontend/components/ui/dropdown-menu.tsx` dòng 43, đổi đúng một đoạn trong chuỗi className:

```
-  w-(--anchor-width) min-w-32
+  w-fit max-w-(--available-width) min-w-32
```

Giữ nguyên toàn bộ phần còn lại của chuỗi. Lưu ý khác với `select.tsx`: ở đây **giữ** `min-w-32` thay vì `min-w-(--anchor-width)`, vì menu ngữ cảnh neo vào nút nhỏ thì không có lý do phải rộng bằng nút; sàn 8rem là đủ và giống hành vi menu quen thuộc.

- [ ] **Step 4: Chạy lại để thấy PASS**

```bash
cd frontend
npx playwright test overlay-width.spec.ts
```

Expected: 4 passed.

- [ ] **Step 5: Kiểm không hồi quy chỗ khác dùng dropdown**

```bash
cd frontend
npx playwright test core-flows.spec.ts phase-l.spec.ts
```

Expected: pass như trước khi sửa. `components/notification-center.tsx` tự đè bề rộng nên phải giữ nguyên 24rem — nếu test chuông thông báo đổi kết quả thì dừng lại, báo cáo, đừng sửa tiếp.

- [ ] **Step 6: Commit**

```bash
cd /Users/admin/Desktop/ICTU-CRIS
git add frontend/components/ui/dropdown-menu.tsx frontend/e2e/overlay-width.spec.ts
git -c user.name=maiychrus25 -c user.email=ninhkhuongpl7@gmail.com \
  commit -m "fix(ui): dropdown menu giãn theo nội dung thay vì khoá cứng bề rộng nút neo"
python3 scripts/check_commit_trailers.py HEAD~1..HEAD
```

---

## Task 3: Ghi tài liệu

**Files:**
- Modify: `CHANGELOG.md` (mục `## [Unreleased]`, dòng 6)

**Interfaces:**
- Consumes: không có.
- Produces: không có.

- [ ] **Step 1: Thêm mục Fixed vào `[Unreleased]`**

Ngay dưới dòng `## [Unreleased]` chèn:

```markdown

### Fixed

- Popup của bộ lọc và menu ngữ cảnh giãn theo nội dung thay vì bị khoá cứng bằng
  bề rộng ô neo: tên khoa dài như "ĐTVT — Khoa Công nghệ điện tử và truyền thông"
  hiện đủ chữ ở `/tra-cuu/`, không còn bị cắt và không cuộn ngang được. Trần bề
  rộng lấy theo chỗ trống còn lại nên ở 390px popup vẫn nằm trọn trong màn hình
  (`components/ui/select.tsx`, `components/ui/dropdown-menu.tsx`; test hồi quy
  `e2e/overlay-width.spec.ts` chạy ở 390/768/1440px).
```

- [ ] **Step 2: Kiểm tra định dạng**

```bash
cd /Users/admin/Desktop/ICTU-CRIS
sed -n '1,20p' CHANGELOG.md
```

Expected: `### Fixed` nằm dưới `## [Unreleased]` và trên `## [0.7.0] - 2026-09-13`.

- [ ] **Step 3: Commit**

```bash
cd /Users/admin/Desktop/ICTU-CRIS
git add CHANGELOG.md
git -c user.name=maiychrus25 -c user.email=ninhkhuongpl7@gmail.com \
  commit -m "docs(changelog): popup bộ lọc và menu giãn theo nội dung"
python3 scripts/check_commit_trailers.py HEAD~1..HEAD
```

---

## Ngoài phạm vi (cần anh duyệt riêng)

- **Đưa lên máy chủ.** Bản chạy thật `cris.ahvlabs.com` dựng từ mã trên GitHub nên còn nguyên lỗi cho tới khi có release mới. Quy trình theo `AGENTS.md` dòng 224: tag → GitHub Release → `docker.yml` → `deploy.yml`. Agent không được push và không được chạm máy chủ.
- **Hai tệp Codex xoá dở** (`frontend/app/doi-chieu/page.tsx`, `ra-soat/page.tsx`) đã bị khôi phục nhầm ở lượt trước. Chờ anh quyết giữ hay xoá lại.

---

## Kết quả thực thi (14/09/2026)

Kế hoạch ban đầu **thiếu một bước**: chỉ đổi công thức bề rộng là chưa đủ.

- Test Task 1 fail ở 390px: popup đúng bề rộng nhưng nằm lệch ra ngoài mép phải 28px,
  **9/10 lần đo**, và không tự chỉnh lại sau đó. Nguyên nhân: khi bề rộng thôi bị khoá
  cứng, chế độ `alignItemWithTrigger` của `@base-ui/react` tính va chạm mép màn hình
  bằng bề rộng cũ. Khắc phục: đặt mặc định `alignItemWithTrigger = false` trong
  `SelectContent` → 10/10 đúng.
- Ở 360px và 320px, tên khoa dài nhất vẫn bị cắt vì hết chỗ vật lý. Khắc phục: bỏ
  `whitespace-nowrap` khỏi `SelectPrimitive.ItemText` để chữ xuống dòng thay vì bị giấu.
- Task 2 (`dropdown-menu.tsx`) đã sửa nhưng **test không chứng minh được gì**: gỡ bản
  sửa ra thì test vẫn xanh, vì nhãn menu hiện có đều ngắn hơn nút neo. Giữ lại như rào
  chắn cho nhãn dài về sau, không phải bằng chứng có lỗi hôm nay.

Kiểm chứng cuối: 12/12 PASS từ 320px tới 1440px ở cả hai theme; toàn bộ 43 test e2e mock
pass; `tsc --noEmit` sạch; `npm run lint` 0 lỗi.
