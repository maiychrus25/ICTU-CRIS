// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Danh bạ giảng viên",
  description: "Tra cứu danh bạ, hồ sơ nghiên cứu và danh sách công trình của giảng viên ICTU.",
  alternates: { canonical: "/giang-vien/" },
};

export default function LecturerLayout({ children }: { children: React.ReactNode }) {
  return children;
}
