// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kiểm tra đề tài",
  description: "Kiểm tra đề tài dự kiến với đồ án các khoá trước và tìm giảng viên gần chuyên môn tại ICTU, không cần đăng nhập.",
  alternates: { canonical: "/kiem-tra-de-tai/" },
};

export default function PublicTopicLayout({ children }: { children: React.ReactNode }) {
  return children;
}
