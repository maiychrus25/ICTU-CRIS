// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import Link from "next/link";

import { cn } from "@/lib/utils";

const modes = [
  ["/doi-chieu/", "Đối chiếu một đề tài"],
  ["/doi-chieu/ra-soat/", "Rà soát theo khoá"],
] as const;

export function CompareModeTabs({ active }: { active: "compare" | "screen" }) {
  return (
    <nav role="tablist" aria-label="Chế độ đối chiếu đề tài" className="mb-5 flex w-fit rounded-lg bg-muted p-1">
      {modes.map(([href, label], index) => {
        const selected = index === (active === "compare" ? 0 : 1);
        return <Link key={href} href={href} role="tab" aria-selected={selected} className={cn("rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground", selected && "bg-background text-foreground shadow-sm")}>{label}</Link>;
      })}
    </nav>
  );
}
