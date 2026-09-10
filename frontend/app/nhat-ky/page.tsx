// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Eye } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { entityLabels, labelDataCodes } from "@/lib/labels";
import { useAudit } from "@/lib/queries";
import type { AuditRow } from "@/lib/types";

function formatDate(value: string) {
  const date = new Date(value);
  return `${date.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" })} ${date.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", hour12: false })}`;
}

function JsonPanel({ title, value }: { title: string; value: Record<string, unknown> | null }) {
  return <div><h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{title}</h3><pre className="min-h-32 overflow-auto whitespace-pre-wrap break-words rounded-lg border bg-muted/50 p-3 text-xs leading-5">{value ? JSON.stringify(labelDataCodes(value), null, 2) : "Không có dữ liệu"}</pre></div>;
}

function AuditContent() {
  const searchParams = useSearchParams();
  const [entity, setEntity] = useState(searchParams.get("entity") ?? "all");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<AuditRow | null>(null);
  const entityId = searchParams.get("entity_id");
  const actor = searchParams.get("actor");
  const query = useAudit({ entity: entity === "all" ? undefined : entity, entity_id: entityId && /^\d+$/.test(entityId) ? Number(entityId) : undefined, actor: actor && /^\d+$/.test(actor) ? Number(actor) : undefined, page });
  const columns = useMemo<DataTableColumn<AuditRow>[]>(() => [
    { accessorKey: "at", header: "Thời điểm", cell: ({ row }) => <span className="whitespace-nowrap tabular-nums">{formatDate(row.original.at)}</span> },
    { accessorKey: "actor_name", header: "Người thao tác", cell: ({ row }) => row.original.actor_name ?? "Hệ thống" },
    { accessorKey: "action_label", header: "Thao tác", cell: ({ row }) => <span className="font-medium">{row.original.action_label}</span> },
    { accessorKey: "entity", header: "Thực thể", cell: ({ row }) => <span>{entityLabels[row.original.entity] ?? row.original.entity} <span className="text-muted-foreground tabular-nums">#{row.original.entity_id}</span></span> },
    { id: "changes", header: "", enableSorting: false, cell: ({ row }) => <Button type="button" variant="outline" size="sm" onClick={() => setSelected(row.original)}><Eye />Xem thay đổi</Button> },
  ], []);

  return (
    <>
      <PageHeader title="Nhật ký thao tác" description="Theo dõi ai đã thay đổi dữ liệu, vào thời điểm nào và giá trị trước — sau." />
      <div className="mb-4 max-w-sm"><label className="mb-1.5 block text-xs font-medium">Loại thực thể</label><Select value={entity} onValueChange={(value) => { setEntity(String(value)); setPage(1); }}><SelectTrigger aria-label="Loại thực thể" className="w-full"><SelectValue>{(value) => value === "all" ? "Tất cả" : entityLabels[String(value)]}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả</SelectItem>{Object.entries(entityLabels).map(([value, label]) => <SelectItem key={value} value={value}>{label}</SelectItem>)}</SelectContent></Select></div>
      {query.isLoading ? <LoadingView /> : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} /> : <DataTable columns={columns} data={query.data?.items ?? []} getRowId={(row) => String(row.id)} emptyMessage="Không có thao tác thuộc loại thực thể này. Hãy chọn Tất cả để xem toàn bộ nhật ký." page={{ page: query.data?.page.page ?? page, perPage: query.data?.page.per_page ?? 50, total: query.data?.page.total ?? 0, onPageChange: setPage }} />}

      <Dialog open={selected !== null} onOpenChange={(open) => { if (!open) setSelected(null); }}><DialogContent className="sm:max-w-3xl"><DialogHeader><DialogTitle>Thay đổi của thao tác #{selected?.id}</DialogTitle><DialogDescription>{selected?.action_label} · {selected ? formatDate(selected.at) : ""}</DialogDescription></DialogHeader><div className="grid gap-4 md:grid-cols-2"><JsonPanel title="Trước thay đổi" value={selected?.before ?? null} /><JsonPanel title="Sau thay đổi" value={selected?.after ?? null} /></div></DialogContent></Dialog>
    </>
  );
}

export default function AuditPage() {
  return <Suspense fallback={<LoadingView label="Đang tải nhật ký thao tác…" />}><AuditContent /></Suspense>;
}
