// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { chromium } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const [baseArgument, outputArgument] = process.argv.slice(2);
if (!baseArgument || !outputArgument) {
  console.error("Cách dùng: node scripts/ui-audit.mjs <base-url> <output-dir>");
  process.exit(2);
}
const base = baseArgument.replace(/\/$/, "");
const apiBase = (process.env.AUDIT_API_BASE || base).replace(/\/$/, "");
const output = path.resolve(outputArgument);
fs.mkdirSync(output, { recursive: true });
const axeSource = fs.readFileSync("node_modules/axe-core/axe.min.js", "utf8");

async function getJson(url) {
  try {
    const response = await fetch(apiBase + url);
    return response.ok ? response.json() : null;
  } catch {
    return null;
  }
}

const periods = await getJson("/api/periods");
const period = periods?.items?.[0]?.id ?? periods?.[0]?.id ?? 1;
const duplicate = (await getJson("/api/queue/duplicates?state=NghiTrung&page=1"))?.items?.[0]?.id ?? 1;
const run = (await getJson("/api/sync/runs?page=1"))?.items?.[0]?.id ?? 1;
const topic = (await getJson("/api/topics"))?.[0]?.id ?? 1;
const routes = [
  "/", "/tong-quan/", "/tra-cuu/", "/tra-cuu/?q=m%E1%BA%A1ng&doc_type=bai_bao",
  "/cong-trinh/?id=1", "/giang-vien/?id=1", "/giang-vien/ly-lich/?id=1", "/khoa/",
  "/ban-do/", "/chu-de/", "/chu-de/chi-tiet/?id=" + topic, "/doi-chieu/",
  "/doi-chieu/chuyen-gia/", "/doi-chieu/ra-soat/", "/kiem-tra-de-tai/",
  "/doi-soat/huong-dan/", "/doi-soat/tac-gia/", "/doi-soat/trung-lap/",
  "/doi-soat/trung-lap/chi-tiet/?id=" + duplicate, "/ky-bao-cao/",
  "/ky-bao-cao/chi-tiet/?id=" + period, "/ke-khai/", "/ke-khai-cua-toi/", "/bao-cao/",
  "/chat-luong-du-lieu/", "/chat-luong-du-lieu/canh-bao/", "/don-vi/", "/dong-bo/",
  "/dong-bo/chi-tiet/?id=" + run, "/nhat-ky/", "/thong-bao/", "/huong-dan/", "/ve/",
  "/dang-nhap/",
];
const viewports = {
  desktop: { width: 1280, height: 800 },
  tablet: { width: 820, height: 1180 },
  mobile: { width: 390, height: 844 },
};

const browser = await chromium.launch();
const report = [];
for (const [viewportName, viewport] of Object.entries(viewports)) {
  for (const colorScheme of ["light", "dark"]) {
    const context = await browser.newContext({ viewport, colorScheme, locale: "vi-VN" });
    for (const route of routes) {
      const page = await context.newPage();
      if (apiBase !== base) {
        await page.route("**/api/**", async (route) => {
          const url = new URL(route.request().url());
          const target = new URL(apiBase);
          url.protocol = target.protocol;
          url.host = target.host;
          await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
        });
      }
      const consoleErrors = [];
      const failedRequests = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text().slice(0, 240));
      });
      page.on("response", (response) => {
        if (response.status() >= 400) failedRequests.push(response.status() + " " + response.url().replace(base, ""));
      });
      try {
        await page.goto(base + route, { waitUntil: "networkidle", timeout: 45_000 });
        await page.waitForTimeout(250);
      } catch (error) {
        report.push({ route, viewportName, colorScheme, error: String(error).slice(0, 240) });
        await page.close();
        continue;
      }

      const checks = await page.evaluate(({ phone }) => {
        const root = document.documentElement;
        const clientWidth = root.clientWidth;
        const fixedFooter = document.querySelector(".data-notice-footer");
        const visible = (element) => {
          const rect = element.getBoundingClientRect();
          const style = getComputedStyle(element);
          return element.getClientRects().length > 0 && rect.width > 0 && rect.height > 0
            && style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0"
            && !element.closest("[hidden],[aria-hidden='true'],[data-state='closed'],details:not([open]) *");
        };
        const insideScrollable = (element) => {
          for (let parent = element.parentElement; parent; parent = parent.parentElement) {
            const style = getComputedStyle(parent);
            if ((style.overflowX === "auto" || style.overflowX === "scroll") && parent.scrollWidth > parent.clientWidth) return true;
          }
          return false;
        };
        const describe = (element) => {
          const name = element.getAttribute("aria-label") || element.textContent || "";
          return element.tagName.toLowerCase() + " \"" + name.trim().replace(/\s+/g, " ").slice(0, 45) + "\"";
        };
        const elements = [...document.querySelectorAll("body *")].filter(visible);
        const overflowRight = elements
          .filter((element) => element.getBoundingClientRect().right > clientWidth + 2 && !insideScrollable(element))
          .slice(0, 8)
          .map((element) => describe(element) + " right=" + Math.round(element.getBoundingClientRect().right));
        const clippedText = elements
          .filter((element) => {
            if (element.closest(".sr-only") || element.children.length || element.textContent.trim().length < 4 || insideScrollable(element)) return false;
            const style = getComputedStyle(element);
            return element.scrollWidth > element.clientWidth + 3 && style.overflow !== "visible"
              && style.textOverflow !== "ellipsis" && style.webkitLineClamp === "none";
          })
          .slice(0, 8)
          .map((element) => describe(element) + " " + element.scrollWidth + ">" + element.clientWidth);
        const candidates = elements.filter((element) => {
          if (fixedFooter?.contains(element) || element.children.length || !element.textContent.trim()) return false;
          if (element.closest("[role='dialog'],[data-slot='popover-content'],[role='tooltip']")) return false;
          const style = getComputedStyle(element);
          const lineHeight = Number.parseFloat(style.lineHeight);
          const rect = element.getBoundingClientRect();
          return style.display !== "inline" && (!Number.isFinite(lineHeight) || rect.height <= lineHeight * 1.7);
        }).map((element) => ({ element, rect: element.getBoundingClientRect() })).slice(0, 700);
        const overlaps = [];
        for (let left = 0; left < candidates.length && overlaps.length < 6; left += 1) {
          for (let right = left + 1; right < candidates.length; right += 1) {
            const a = candidates[left];
            const b = candidates[right];
            if (a.element.contains(b.element) || b.element.contains(a.element)) continue;
            const horizontal = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
            const vertical = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
            if (horizontal > 4 && vertical > 4) {
              overlaps.push(describe(a.element) + " × " + describe(b.element));
              break;
            }
          }
        }
        const smallTargets = phone ? elements
          .filter((element) => element.matches("button,[role='button'],[role='tab'],a[data-slot='button']"))
          .filter((element) => {
            const rect = element.getBoundingClientRect();
            return (rect.height < 32 || rect.width < 32) && !fixedFooter?.contains(element);
          })
          .slice(0, 8)
          .map((element) => {
            const rect = element.getBoundingClientRect();
            return describe(element) + " " + Math.round(rect.width) + "×" + Math.round(rect.height);
          }) : [];
        const unlabeledFields = [...document.querySelectorAll("input:not([type='hidden']),select,textarea")]
          .filter((element) => visible(element) && element.getBoundingClientRect().width > 2)
          .filter((element) => !(element.labels?.length || element.getAttribute("aria-label") || element.getAttribute("aria-labelledby")))
          .map(describe);
        return {
          scrollWidth: root.scrollWidth,
          clientWidth,
          overflowRight,
          clippedText,
          overlaps,
          smallTargets,
          missingAlt: [...document.images].filter((image) => !image.hasAttribute("alt")).length,
          unnamedButtons: [...document.querySelectorAll("button")].filter((button) => visible(button)
            && !(button.textContent.trim() || button.getAttribute("aria-label") || button.getAttribute("title"))).length,
          unlabeledFields,
          headings: document.querySelectorAll("h1").length,
          bodyTextLength: document.body.innerText.length,
          title: document.title,
        };
      }, { phone: viewportName === "mobile" });

      await page.addScriptTag({ content: axeSource });
      const axe = (await page.evaluate(async () => {
        const result = await window.axe.run(document, {
          runOnly: ["wcag2a", "wcag2aa"],
          resultTypes: ["violations"],
        });
        return result.violations.map((violation) => ({
          id: violation.id,
          impact: violation.impact,
          nodes: violation.nodes.length,
          example: violation.nodes[0]?.html?.slice(0, 180),
        }));
      })).filter((violation) => ["serious", "critical"].includes(violation.impact));
      const name = route.replace(/[^a-z0-9]+/gi, "_").slice(0, 44) || "root";
      await page.screenshot({ path: path.join(output, viewportName + "-" + colorScheme + "-" + name + ".png"), fullPage: true });
      report.push({
        route, viewportName, colorScheme, ...checks,
        horizontalOverflow: checks.scrollWidth > checks.clientWidth,
        consoleErrors: consoleErrors.slice(0, 5),
        failedRequests: failedRequests.slice(0, 8),
        axe,
      });
      await page.close();
    }
    await context.close();
  }
}
await browser.close();

fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2));
const issues = report.filter((item) => item.error || item.horizontalOverflow || item.overflowRight?.length
  || item.clippedText?.length || item.overlaps?.length || item.smallTargets?.length || item.missingAlt
  || item.unnamedButtons || item.unlabeledFields?.length || item.consoleErrors?.length
  || item.failedRequests?.length || item.axe?.length || item.headings !== 1);
console.log("pages=" + report.length + " with_findings=" + issues.length);
for (const item of issues) {
  const summary = { ...item };
  delete summary.title;
  delete summary.scrollWidth;
  delete summary.clientWidth;
  delete summary.bodyTextLength;
  console.log(JSON.stringify(summary));
}
process.exitCode = issues.length ? 1 : 0;
