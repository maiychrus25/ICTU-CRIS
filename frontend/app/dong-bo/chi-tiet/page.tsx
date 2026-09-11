// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AlertTriangle, ArrowLeft, CircleAlert } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { docTypeLabels, sourceLabels, syncScopeLabels } from "@/lib/labels";
import { useSyncRun } from "@/lib/queries";
import type { SourceRecordRow } from "@/lib/types";

function formatValue(value: unknown) {
  return typeof value === "string" ? value : JSON.stringify(value);
}

function countTotal(value: Record<string, unknown> | null) {
  if (!value) return "—";
  return Object.values(value).reduce<number>((total, item) => total + (typeof item === "number" ? item : 0), 0).toLocaleString("vi-VN");
}

function SyncRunDetailContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const query = useSyncRun(id);
  const columns = useMemo<DataTableColumn<SourceRecordRow>[]>(() => [
    { accessorKey: "source_key", header: "Khoá nguồn", cell: ({ row }) => <span className="block max-w-2xl break-all font-medium">{row.original.source_key}</span> },
    { accessorKey: "doc_type", header: "Loại", cell: ({ row }) => docTypeLabels[row.original.doc_type] ?? row.original.doc_type },
    { accessorKey: "version", header: "Phiên bản", cell: ({ row }) => <span className="tabular-nums">{row.original.version}</span> },
    { accessorKey: "fetched_at", header: "Thời điểm lấy", cell: ({ row }) => <span className="whitespace-nowrap tabular-nums text-muted-foreground">{row.original.fetched_at ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(new Date(row.original.fetched_at)) : "—"}</span> },
  ], []);

  if (id === null) return <><PageHeader title="Chi tiết lượt đồng bộ" /><EmptyView title="Chưa chọn lượt đồng bộ" description="Mở một lượt từ trang lịch sử đồng bộ để xem chi tiết." action={<Link href="/dong-bo/" className="text-sm font-medium text-primary hover:underline">Đi đến lịch sử đồng bộ</Link>} /></>;
  if (query.isLoading) return <><PageHeader title={`Chi tiết lượt đồng bộ #${id}`} /><LoadingView label="Đang tải chi tiết lượt đồng bộ…" /></>;
  if (query.isError) return <><PageHeader title={`Chi tiết lượt đồng bộ #${id}`} /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title={`Chi tiết lượt đồng bộ #${id}`} /><EmptyView description="Lượt đồng bộ này không còn tồn tại. Hãy quay lại lịch sử đồng bộ." /></>;

  const run = query.data;
  return (
    <>
      <PageHeader title={`Chi tiết lượt đồng bộ #${run.id}`} description={`${sourceLabels[run.source] ?? run.source} · ${syncScopeLabels[run.scope] ?? run.scope}`} action={<div className="flex items-center gap-2"><StatusBadge value={run.status} /><Button variant="outline" render={<Link href="/dong-bo/" />}><ArrowLeft />Lịch sử</Button></div>} />
      <dl className="mb-6 grid gap-px overflow-hidden rounded-lg border bg-border sm:grid-cols-3 lg:grid-cols-6">
        {[["Dự kiến", countTotal(run.expected_count)], ["Đã lấy", countTotal(run.fetched_count)], ["Thêm", run.added], ["Đổi", run.changed], ["Mất", run.vanished], ["Thời lượng", run.duration_s === null ? "Đang chạy" : `${run.duration_s.toLocaleString("vi-VN")} giây`]].map(([label, value]) => <div key={String(label)} className="bg-card p-4"><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 font-semibold tabular-nums">{value}</dd></div>)}
      </dl>
      {run.warnings.length > 0 && <Alert className="mb-4 border-status-warning/30 bg-status-warning/10 text-status-warning"><AlertTriangle /><AlertTitle>Cảnh báo</AlertTitle><AlertDescription><ul className="list-disc space-y-1 pl-4">{run.warnings.map((warning, index) => <li key={index}>{formatValue(warning)}</li>)}</ul></AlertDescription></Alert>}
      {run.errors.length > 0 && <Alert variant="destructive" className="mb-4"><CircleAlert /><AlertTitle>Lỗi đồng bộ</AlertTitle><AlertDescription><ul className="list-disc space-y-1 pl-4">{run.errors.map((error, index) => <li key={index}>{formatValue(error)}</li>)}</ul></AlertDescription></Alert>}
      <section aria-labelledby="records-title"><h2 id="records-title" className="mb-3 text-base font-semibold">Bản ghi thay đổi gần nhất</h2>{run.records.length ? <DataTable columns={columns} data={run.records} getRowId={(record) => String(record.id)} /> : <EmptyView description="Lượt này không ghi nhận bản ghi nguồn thay đổi." />}</section>
    </>
  );
}

export default function SyncRunDetailPage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị chi tiết lượt đồng bộ…" />}><SyncRunDetailContent /></Suspense>;
}
