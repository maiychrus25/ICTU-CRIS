// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hướng dẫn sử dụng",
  description: "Hướng dẫn sử dụng ICTU-CRIS theo vai trò, từ tra cứu, kê khai đến đối soát dữ liệu và đọc gợi ý AI.",
  alternates: { canonical: "/huong-dan/" },
};

export default function GuideLayout({ children }: { children: React.ReactNode }) {
  return children;
}
