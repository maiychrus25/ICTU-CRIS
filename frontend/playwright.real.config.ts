// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 30_000 },
  workers: 1,
  use: { baseURL: "http://localhost:3000" },
  webServer: {
    command: "python3 -m http.server 3000 --directory out",
    url: "http://localhost:3000",
    timeout: 120_000,
    reuseExistingServer: false,
  },
  projects: [
    { name: "desktop", testMatch: "real-backend.spec.ts", use: { viewport: { width: 1440, height: 900 } } },
    { name: "tablet", testMatch: "responsive-accessibility.real.spec.ts", use: { viewport: { width: 768, height: 1024 } } },
    { name: "mobile", testMatch: "responsive-accessibility.real.spec.ts", use: { viewport: { width: 390, height: 844 } } },
  ],
});
