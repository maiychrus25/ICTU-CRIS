// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AlertTriangle, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDuplicateGroups } from "@/lib/queries";
import type { DupGroupSummary } from "@/lib/types";

const states = [
  ["NghiTrung", "Nghi trùng"],
  ["DaGop", "Đã gộp"],
  ["GiuRieng", "Giữ riêng"],
  ["all", "Tất cả"],
] as const;

function formatDate(value: string | null) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium" }).format(new Date(value)) : "—";
}

export default function DuplicateQueuePage() {
  const router = useRouter();
  const [state, setState] = useState("NghiTrung");
  const [page, setPage] = useState(1);
  const query = useDuplicateGroups(state, page);
  const columns = useMemo<DataTableColumn<DupGroupSummary>[]>(() => [
    { accessorKey: "id", header: "Mã nhóm", cell: ({ row }) => <span className="font-medium text-primary tabular-nums">#{row.original.id}</span> },
    { accessorKey: "doc_type", header: "Loại tài liệu", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "basis_label", header: "Cơ sở", cell: ({ row }) => <span className="font-medium">{row.original.basis_label}</span> },
    { accessorKey: "member_count", header: "Thành viên", cell: ({ row }) => <span className="tabular-nums">{row.original.member_count}</span> },
    { accessorKey: "hint", header: "Lưu ý", enableSorting: false, cell: ({ row }) => row.original.hint ? <Badge variant="outline" className="border-status-warning/30 bg-status-warning/10 text-status-warning"><AlertTriangle />{row.original.hint}</Badge> : <span className="text-muted-foreground">—</span> },
    { accessorKey: "created_at", header: "Ngày tạo", cell: ({ row }) => <span className="tabular-nums text-muted-foreground">{formatDate(row.original.created_at)}</span> },
    { id: "open", header: "", enableSorting: false, cell: () => <ArrowRight className="size-4 text-muted-foreground" /> },
  ], []);

  return (
    <>
      <PageHeader title="Hàng đợi nghi trùng" description="Mở từng nhóm để so sánh dữ liệu cạnh nhau trước khi quyết định gộp hoặc giữ riêng." />
      <Tabs value={state} onValueChange={(value) => { setState(String(value)); setPage(1); }} className="mb-4">
        <TabsList variant="line" className="max-w-full overflow-x-auto">{states.map(([value, label]) => <TabsTrigger key={value} value={value}>{label}</TabsTrigger>)}</TabsList>
      </Tabs>
      {query.isLoading ? <LoadingView /> : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} /> : <DataTable columns={columns} data={query.data?.items ?? []} emptyMessage="Không có nhóm nghi trùng ở trạng thái này. Hãy chọn tab khác để xem các nhóm đã xử lý." getRowId={(row) => String(row.id)} onRowClick={(row) => router.push(`/doi-soat/trung-lap/chi-tiet/?id=${row.id}`)} page={{ page: query.data?.page.page ?? page, perPage: query.data?.page.per_page ?? 50, total: query.data?.page.total ?? 0, onPageChange: setPage }} />}
    </>
  );
}
