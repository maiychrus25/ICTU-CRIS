// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import Image from "next/image";
import { useState } from "react";

import { cn } from "@/lib/utils";

function getInitial(name: string) {
  const plainName = name.replace(/^(?:(?:GS|PGS)\.)?(?:(?:TS|ThS)\.)?\s*/i, "").trim();
  return Array.from(plainName)[0]?.toLocaleUpperCase("vi-VN") ?? "?";
}

export function PersonAvatar({ name, src, small = false }: { name: string; src?: string | null; small?: boolean }) {
  const [failed, setFailed] = useState(false);
  const className = cn("shrink-0 rounded-full border bg-muted object-cover", small ? "size-9" : "size-24 sm:size-28");

  return src && !failed ? (
    <Image src={src} alt={`Ảnh đại diện của ${name}`} width={small ? 36 : 112} height={small ? 36 : 112} referrerPolicy="no-referrer" className={className} onError={() => setFailed(true)} />
  ) : (
    <span role="img" aria-label={`Ảnh đại diện thay thế của ${name}`} className={cn(className, "grid place-items-center font-semibold text-primary", small ? "text-sm" : "text-3xl")}>
      {getInitial(name)}
    </span>
  );
}
