// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: ["/", "/tra-cuu/", "/kiem-tra-de-tai/", "/huong-dan/", "/ban-do/", "/chu-de/", "/ve/", "/cong-trinh/", "/giang-vien/"],
      disallow: ["/api/", "/doi-soat/", "/ky-bao-cao/", "/ke-khai/", "/ke-khai-cua-toi/", "/nhat-ky/", "/thong-bao/", "/bao-cao/", "/khoa/", "/dang-nhap/", "/chat-luong-du-lieu/"],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
