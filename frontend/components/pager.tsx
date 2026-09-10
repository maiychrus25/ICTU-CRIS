// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export function Pager({ page, perPage, total, onPageChange }: { page: number; perPage: number; total: number; onPageChange: (page: number) => void }) {
  const pages = Math.max(1, Math.ceil(total / perPage));
  return (
    <div className="flex items-center justify-between gap-4 border-t px-3 py-3 text-xs text-muted-foreground">
      <span className="tabular-nums">{total ? `${(page - 1) * perPage + 1}–${Math.min(page * perPage, total)} trong ${total}` : "0 kết quả"}</span>
      <div className="flex items-center gap-2"><span className="tabular-nums">Trang {page}/{pages}</span><Button variant="outline" size="icon-sm" aria-label="Trang trước" disabled={page <= 1} onClick={() => onPageChange(page - 1)}><ChevronLeft /></Button><Button variant="outline" size="icon-sm" aria-label="Trang sau" disabled={page >= pages} onClick={() => onPageChange(page + 1)}><ChevronRight /></Button></div>
    </div>
  );
}
