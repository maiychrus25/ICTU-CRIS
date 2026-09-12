// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Bản đồ tri thức",
  description: "Khám phá công trình, xu hướng chủ đề và quan hệ đồng tác giả trong bản đồ tri thức nghiên cứu ICTU.",
  alternates: { canonical: "/ban-do/" },
};

export default function KnowledgeMapLayout({ children }: { children: React.ReactNode }) {
  return children;
}
