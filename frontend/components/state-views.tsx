// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { AlertCircle, Inbox } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";

export function LoadingView({ label = "Đang tải dữ liệu…" }: { label?: string }) {
  return <div aria-label={label} role="status" className="space-y-3"><span className="sr-only">{label}</span><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-4/5" /></div>;
}

export function EmptyView({ title = "Chưa có dữ liệu", description, action }: { title?: string; description: string; action?: React.ReactNode }) {
  return <div className="grid min-h-56 place-items-center rounded-lg border border-dashed bg-card/40 p-8 text-center"><div><Inbox className="mx-auto mb-3 size-8 text-muted-foreground" /><h2 className="font-semibold">{title}</h2><p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>{action && <div className="mt-4">{action}</div>}</div></div>;
}

export function ErrorView({ error, retry }: { error: unknown; retry?: () => void }) {
  const detail = error instanceof ApiError ? error.detail : error instanceof Error ? error.message : "Không thể tải dữ liệu.";
  return <Alert variant="destructive"><AlertCircle /><AlertTitle>Đã xảy ra lỗi</AlertTitle><AlertDescription><p>{detail}</p>{retry && <Button variant="outline" size="sm" className="mt-3" onClick={retry}>Thử lại</Button>}</AlertDescription></Alert>;
}
