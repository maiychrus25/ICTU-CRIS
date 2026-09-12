// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0
import { readFile } from "node:fs/promises";
import sharp from "sharp";

const mark = await readFile("public/brand/icut-cris-mark.svg");

async function icon(path, size, inset) {
  const image = await sharp(mark).resize(size - inset * 2, size - inset * 2).png().toBuffer();
  await sharp({ create: { width: size, height: size, channels: 4, background: "#F8FAFC" } })
    .composite([{ input: image, left: inset, top: inset }])
    .png()
    .toFile(path);
}

await Promise.all([
  icon("app/apple-icon.png", 180, 18),
  icon("public/brand/icon-192.png", 192, 20),
  icon("public/brand/icon-512.png", 512, 54),
]);

const ogMark = await sharp(mark).resize(320, 320).png().toBuffer();
const ogText = Buffer.from(`<svg width="700" height="260" xmlns="http://www.w3.org/2000/svg">
  <text x="0" y="105" fill="#0F172A" font-family="Be Vietnam Pro,DejaVu Sans,sans-serif" font-size="76" font-weight="700" letter-spacing="2">ICTU-CRIS</text>
  <text x="0" y="180" fill="#475569" font-family="Be Vietnam Pro,DejaVu Sans,sans-serif" font-size="32">Thông tin nghiên cứu · ICTU</text>
</svg>`);

await sharp({ create: { width: 1200, height: 630, channels: 4, background: "#F8FAFC" } })
  .composite([
    { input: ogMark, left: 90, top: 155 },
    { input: ogText, left: 450, top: 185 },
  ])
  .png()
  .toFile("public/brand/og-image.png");
