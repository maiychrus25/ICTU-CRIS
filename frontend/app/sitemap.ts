// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

const publicRoutes = ["/", "/tra-cuu/", "/kiem-tra-de-tai/", "/huong-dan/", "/ban-do/", "/chu-de/", "/ve/", "/cong-trinh/", "/giang-vien/"];

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return publicRoutes.map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: "2026-09-13",
  }));
}
