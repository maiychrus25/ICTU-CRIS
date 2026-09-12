import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

for (const [file, canonical] of [
  ["out/index.html", "https://cris.ahvlabs.com/"],
  ["out/kiem-tra-de-tai/index.html", "https://cris.ahvlabs.com/kiem-tra-de-tai/"],
]) {
  const html = await readFile(file, "utf8");
  assert.match(html, /<title>[^<]+<\/title>/, `${file}: thiếu title`);
  assert.match(html, /<meta name="description" content="[^"]+"/, `${file}: thiếu description`);
  assert.match(html, /<meta property="og:image" content="https:\/\/cris\.ahvlabs\.com\/brand\/og-image\.png"/, `${file}: thiếu og:image tuyệt đối`);
  assert.ok(html.includes(`<link rel="canonical" href="${canonical}"`), `${file}: thiếu canonical`);

  const jsonLd = [...html.matchAll(/<script type="application\/ld\+json">([^<]+)<\/script>/g)];
  assert.ok(jsonLd.length, `${file}: thiếu JSON-LD`);
  jsonLd.forEach(([, value]) => JSON.parse(value));
}

console.log("SEO output hợp lệ: 2 trang, JSON-LD parse được.");
