// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hồ sơ giảng viên",
  description: "Xem hồ sơ nghiên cứu, thống kê theo năm và danh sách công trình của giảng viên ICTU.",
  alternates: { canonical: "/giang-vien/" },
};

export default function LecturerLayout({ children }: { children: React.ReactNode }) {
  return children;
}
