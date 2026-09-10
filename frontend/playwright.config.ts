// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  use: { baseURL: "http://127.0.0.1:3000" },
  webServer: {
    command: "python3 -m http.server 3000 --directory out --bind 127.0.0.1",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: false,
  },
});
