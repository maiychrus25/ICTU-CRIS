// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  use: { baseURL: "http://localhost:3000" },
  webServer: {
    command: "NEXT_PUBLIC_MOCK=1 npm run dev -- --webpack",
    env: { ...process.env, WATCHPACK_POLLING: "true" },
    url: "http://localhost:3000",
    reuseExistingServer: false,
  },
});
