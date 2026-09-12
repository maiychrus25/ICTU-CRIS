// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = { robots: { index: false, follow: false } };

export default function ReportLayout({ children }: { children: React.ReactNode }) {
  return children;
}
