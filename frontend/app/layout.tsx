// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata, Viewport } from "next";
import { Be_Vietnam_Pro } from "next/font/google";

import { AppShell } from "@/components/app-shell";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";
import { SITE_URL } from "@/lib/site";

import "./globals.css";

const beVietnamPro = Be_Vietnam_Pro({
  variable: "--font-be-vietnam-pro",
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    template: "%s · ICTU-CRIS",
    default: "ICTU-CRIS — Hệ thống thông tin nghiên cứu ICTU",
  },
  description: "Tra cứu công bố khoa học, giảng viên và đồ án của Trường CNTT&TT, Đại học Thái Nguyên trên hệ thống ICTU-CRIS.",
  keywords: ["ICTU-CRIS", "công bố khoa học", "giảng viên", "đồ án", "Trường CNTT&TT", "Đại học Thái Nguyên"],
  applicationName: "ICTU-CRIS",
  authors: [{ name: "Trường Công nghệ Thông tin và Truyền thông – Đại học Thái Nguyên", url: "https://ictu.edu.vn" }],
  alternates: { canonical: `${SITE_URL}/` },
  icons: {
    icon: [{ url: "/icon.svg", type: "image/svg+xml" }],
    apple: [{ url: "/apple-icon.png", sizes: "180x180", type: "image/png" }],
  },
  manifest: "/manifest.webmanifest",
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    locale: "vi_VN",
    siteName: "ICTU-CRIS",
    title: "ICTU-CRIS — Hệ thống thông tin nghiên cứu ICTU",
    description: "Tra cứu công bố khoa học, giảng viên và đồ án của Trường CNTT&TT, Đại học Thái Nguyên.",
    url: SITE_URL,
    images: [{ url: `${SITE_URL}/brand/og-image.png`, width: 1200, height: 630, alt: "ICTU-CRIS — Thông tin nghiên cứu ICTU" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ICTU-CRIS — Hệ thống thông tin nghiên cứu ICTU",
    description: "Tra cứu công bố khoa học, giảng viên và đồ án của ICTU.",
    images: [`${SITE_URL}/brand/og-image.png`],
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#F8FAFC" },
    { media: "(prefers-color-scheme: dark)", color: "#0F172A" },
  ],
};

const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      name: "ICTU-CRIS",
      url: `${SITE_URL}/`,
      potentialAction: {
        "@type": "SearchAction",
        target: { "@type": "EntryPoint", urlTemplate: `${SITE_URL}/tra-cuu/?q={search_term_string}` },
        "query-input": "required name=search_term_string",
      },
    },
    {
      "@type": "Organization",
      name: "Trường Công nghệ Thông tin và Truyền thông – Đại học Thái Nguyên",
      url: "https://ictu.edu.vn",
      logo: `${SITE_URL}/brand/icut-cris-logo.svg`,
    },
    {
      "@type": "SoftwareApplication",
      name: "ICTU-CRIS",
      applicationCategory: "EducationalApplication",
      operatingSystem: "Web",
      url: `${SITE_URL}/`,
      license: "https://www.apache.org/licenses/LICENSE-2.0",
      codeRepository: "https://github.com/maiychrus25/ICTU-CRIS",
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={beVietnamPro.variable} suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
        <Providers>
          <AppShell>{children}</AppShell>
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  );
}
