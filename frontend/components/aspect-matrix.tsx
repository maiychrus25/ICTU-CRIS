// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { aspectLabels, aspectLevelLabels, getAspectLevel, type AspectLevel } from "@/lib/labels";
import { cn } from "@/lib/utils";

const levelStyles: Record<AspectLevel, string> = {
  cao: "border-status-danger/25 bg-status-danger/10 text-status-danger",
  vua: "border-status-warning/30 bg-status-warning/10 text-status-warning",
  thap: "border-status-success/25 bg-status-success/10 text-status-success",
};

export function AspectMatrix({ aspects }: { aspects: Record<string, string> }) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {Object.entries(aspectLabels).map(([key, label]) => {
        // Backend trả "chua_du" (đối chiếu: khía cạnh chưa nhập / công trình không có tóm tắt)
        // hoặc "khong_du_du_lieu" (rà soát theo khoá): cả hai đều là "chưa đủ dữ liệu", không phải "thấp".
        const value = aspects[key] ?? "chua_du";
        const unavailable = value === "khong_du_du_lieu" || value === "chua_du";
        const level = getAspectLevel(value);
        return (
          <div key={key} className={cn("rounded-md border px-3 py-2", unavailable ? "bg-muted/60 text-muted-foreground" : levelStyles[level])}>
            <p className="text-[11px] font-medium uppercase tracking-wide opacity-80">{label}</p>
            <p className="mt-0.5 text-sm font-semibold">{unavailable ? "Chưa đủ dữ liệu" : aspectLevelLabels[level]}</p>
          </div>
        );
      })}
    </div>
  );
}
