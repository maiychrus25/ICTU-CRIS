// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  testIgnore: ["real-backend.spec.ts", "responsive-accessibility.real.spec.ts"],
  timeout: 120_000,
  expect: { timeout: 30_000 },
  workers: 1,
  use: { baseURL: "http://localhost:3000" },
  webServer: {
    command: "NEXT_PUBLIC_MOCK=1 npm run dev -- --webpack",
    env: { ...process.env, WATCHPACK_POLLING: "true" },
    url: "http://localhost:3000",
    reuseExistingServer: false,
  },
});
