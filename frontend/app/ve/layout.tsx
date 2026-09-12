// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Về hệ thống",
  description: "Tìm hiểu nguồn dữ liệu, khả năng AI, giấy phép và các giới hạn được công bố minh bạch của ICTU-CRIS.",
  alternates: { canonical: "/ve/" },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return children;
}
