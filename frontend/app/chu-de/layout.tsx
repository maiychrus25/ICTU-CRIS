// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chủ đề nghiên cứu",
  description: "Khám phá các cụm chủ đề và công trình nghiên cứu nổi bật trong kho dữ liệu ICTU-CRIS.",
  alternates: { canonical: "/chu-de/" },
};

export default function TopicsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
