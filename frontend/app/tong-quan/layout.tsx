// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tổng quan",
  description: "Theo dõi số liệu công trình nghiên cứu ICTU theo năm, loại tài liệu và đơn vị với khả năng truy ngược dữ liệu gốc.",
  alternates: { canonical: "/tong-quan/" },
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return children;
}
