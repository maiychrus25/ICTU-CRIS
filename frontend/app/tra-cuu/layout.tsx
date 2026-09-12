// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tra cứu",
  description: "Tra cứu công trình, công bố khoa học, đồ án và dữ liệu giảng viên ICTU từ một nguồn thống nhất.",
  alternates: { canonical: "/tra-cuu/" },
};

export default function SearchLayout({ children }: { children: React.ReactNode }) {
  return children;
}
