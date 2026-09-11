// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { Ban, CheckCircle2, CircleDashed, Clock3, CopyCheck, FileText, LockKeyhole, ShieldCheck, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { docTypeLabels, stateLabels } from "@/lib/labels";
import { cn } from "@/lib/utils";

const states = {
  DaNoiTuDong: { icon: ShieldCheck, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  DaXacNhan: { icon: CheckCircle2, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  DaChuanHoa: { icon: ShieldCheck, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  DaGop: { icon: CopyCheck, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  active: { icon: CheckCircle2, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  GiuRieng: { icon: CheckCircle2, className: "border-primary/25 bg-primary/10 text-primary" },
  ChoXacNhan: { icon: Clock3, className: "border-status-warning/30 bg-status-warning/10 text-status-warning" },
  NghiTrung: { icon: CircleDashed, className: "border-status-warning/30 bg-status-warning/10 text-status-warning" },
  DaBacBo: { icon: XCircle, className: "border-status-danger/25 bg-status-danger/10 text-status-danger" },
  vanished: { icon: XCircle, className: "border-status-danger/25 bg-status-danger/10 text-status-danger" },
  ChuanBi: { icon: Clock3, className: "border-status-warning/30 bg-status-warning/10 text-status-warning" },
  DangMo: { icon: CheckCircle2, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  DaDongNop: { icon: LockKeyhole, className: "border-primary/25 bg-primary/10 text-primary" },
  Huy: { icon: Ban, className: "border-status-danger/25 bg-status-danger/10 text-status-danger" },
  running: { icon: Clock3, className: "border-status-warning/30 bg-status-warning/10 text-status-warning" },
  ok: { icon: CheckCircle2, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  success: { icon: CheckCircle2, className: "border-status-success/25 bg-status-success/10 text-status-success" },
  warning: { icon: CircleDashed, className: "border-status-warning/30 bg-status-warning/10 text-status-warning" },
  failed: { icon: XCircle, className: "border-status-danger/25 bg-status-danger/10 text-status-danger" },
} as const;

export function StatusBadge({ value, kind = "state" }: { value: string; kind?: "state" | "docType" }) {
  if (kind === "docType") return <Badge variant="outline" className="font-normal"><FileText />{docTypeLabels[value] ?? value}</Badge>;
  const config = states[value as keyof typeof states];
  const Icon = config?.icon ?? CircleDashed;
  return <Badge variant="outline" className={cn("font-normal", config?.className)}><Icon />{stateLabels[value] ?? value}</Badge>;
}
