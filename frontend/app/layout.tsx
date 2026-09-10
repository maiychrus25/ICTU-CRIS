// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";
import { Be_Vietnam_Pro } from "next/font/google";

import { AppShell } from "@/components/app-shell";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";

import "./globals.css";

const beVietnamPro = Be_Vietnam_Pro({
  variable: "--font-be-vietnam-pro",
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "ICTU-CRIS — Thông tin nghiên cứu",
  description: "Hệ thống thông tin nghiên cứu của Trường CNTT&TT – ĐH Thái Nguyên",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={beVietnamPro.variable} suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        <Providers>
          <AppShell>{children}</AppShell>
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  );
}
