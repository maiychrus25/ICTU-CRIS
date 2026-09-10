// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect } from "react";

import { LoadingView } from "@/components/state-views";

export default function HomePage() {
  useEffect(() => { window.location.replace("/tong-quan/"); }, []);
  return <LoadingView label="Đang chuyển đến trang tổng quan…" />;
}
