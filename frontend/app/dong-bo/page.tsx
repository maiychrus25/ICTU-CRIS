// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AlertTriangle, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { sourceLabels, syncScopeLabels } from "@/lib/labels";
import { useSyncRuns } from "@/lib/queries";
import type { SyncRunSummary } from "@/lib/types";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function formatDuration(value: number | null) {
  if (value === null) return "Đang chạy";
  const minutes = Math.floor(value / 60);
  const seconds = Math.round(value % 60);
  return minutes ? `${minutes} phút ${seconds} giây` : `${seconds} giây`;
}

export default function SyncRunsPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const query = useSyncRuns(page);
  const columns = useMemo<DataTableColumn<SyncRunSummary>[]>(() => [
    { accessorKey: "started_at", header: "Thời điểm", cell: ({ row }) => <span className="whitespace-nowrap tabular-nums">{formatDate(row.original.started_at)}</span> },
    { accessorKey: "source", header: "Nguồn / phạm vi", cell: ({ row }) => <div><p className="font-medium">{sourceLabels[row.original.source] ?? row.original.source}</p><p className="text-xs text-muted-foreground">{syncScopeLabels[row.original.scope] ?? row.original.scope}</p></div> },
    { accessorKey: "status", header: "Trạng thái", cell: ({ row }) => <StatusBadge value={row.original.status} /> },
    { id: "changes", header: "Thêm / đổi / mất", cell: ({ row }) => <span className="whitespace-nowrap tabular-nums"><span className="text-status-success">+{row.original.added}</span> / <span>{row.original.changed}</span> / <span className="text-status-danger">{row.original.vanished}</span></span> },
    { id: "issues", header: "Lỗi / cảnh báo", cell: ({ row }) => <span className="inline-flex items-center gap-1.5 tabular-nums">{row.original.warnings.length > 0 && <AlertTriangle className="size-3.5 text-status-warning" />}{row.original.errors.length} / {row.original.warnings.length}</span> },
    { accessorKey: "duration_s", header: "Thời lượng", cell: ({ row }) => <span className="whitespace-nowrap tabular-nums text-muted-foreground">{formatDuration(row.original.duration_s)}</span> },
    { id: "open", header: "Dự kiến / đã lấy", enableSorting: false, cell: () => <span className="inline-flex items-center gap-1 whitespace-nowrap text-xs font-medium text-primary">Xem chi tiết <ArrowRight className="size-3.5" /></span> },
  ], []);

  return (
    <>
      <PageHeader title="Lịch sử đồng bộ" description="Theo dõi từng lượt lấy dữ liệu, thay đổi phát hiện được và cảnh báo từ nguồn." />
      {query.isLoading ? <LoadingView label="Đang tải lịch sử đồng bộ…" />
        : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} />
        : !query.data?.items.length ? <EmptyView title="Chưa có lượt đồng bộ" description={"Chưa có lượt đồng bộ — chạy `python -m cris sync`."} />
        : <DataTable columns={columns} data={query.data.items} getRowId={(run) => String(run.id)} onRowClick={(run) => router.push(`/dong-bo/chi-tiet/?id=${run.id}`)} page={{ page: query.data.page.page, perPage: query.data.page.per_page, total: query.data.page.total, onPageChange: setPage }} />}
    </>
  );
}
