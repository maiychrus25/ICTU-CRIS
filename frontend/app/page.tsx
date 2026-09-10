// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { LoadingView } from "@/components/state-views";

export default function HomePage() {
  const router = useRouter();
  useEffect(() => { router.replace("/tra-cuu/"); }, [router]);
  return <LoadingView label="Đang chuyển đến trang tra cứu…" />;
}
