// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Đối chiếu đề tài",
  description: "Đối chiếu đề tài với công trình ICTU theo bài toán, đối tượng, phạm vi và phương pháp; AI chỉ đưa ra gợi ý.",
  alternates: { canonical: "/doi-chieu/" },
};

export default function CompareLayout({ children }: { children: React.ReactNode }) {
  return children;
}
