// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import type { RowSelectionState } from "@tanstack/react-table";
import { AlertTriangle, Bot, Check, CornerDownRight, Search, Sparkles, UserRoundX } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { AuthorQueueTabs } from "@/components/author-queue-tabs";
import { PageHeader } from "@/components/page-header";
import { PersonCombobox } from "@/components/person-combobox";
import { ErrorView, LoadingView } from "@/components/state-views";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { confidenceLabels, officerRoleRequired, stateLabels } from "@/lib/labels";
import { useAuthorQueue, useDecideAuthors, useOfficerAccess } from "@/lib/queries";
import type { AuthorQueueRow, DecideAuthorsIn } from "@/lib/types";

const states = [
  "ChoXacNhan", "DaNoiTuDong", "DaXacNhan", "DaBacBo",
] as const;

export default function AuthorQueuePage() {
  const queryClient = useQueryClient();
  const [state, setState] = useState("ChoXacNhan");
  const [search, setSearch] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [selection, setSelection] = useState<RowSelectionState>({});
  const [rejectOpen, setRejectOpen] = useState(false);
  const [reassignOpen, setReassignOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [personId, setPersonId] = useState<number | null>(null);
  const queue = useAuthorQueue(state, q, page);
  const pendingCount = useAuthorQueue("ChoXacNhan", "", 1);
  const automaticCount = useAuthorQueue("DaNoiTuDong", "", 1);
  const confirmedCount = useAuthorQueue("DaXacNhan", "", 1);
  const rejectedCount = useAuthorQueue("DaBacBo", "", 1);
  const decide = useDecideAuthors();
  const canDecide = useOfficerAccess();
  const items = queue.data?.items;
  const selectedIds = Object.entries(selection).filter(([, selected]) => selected).map(([id]) => Number(id));
  const counts = [pendingCount.data?.page.total, automaticCount.data?.page.total, confirmedCount.data?.page.total, rejectedCount.data?.page.total];
  const groupOrder = useMemo(() => {
    const names: string[] = [];
    queue.data?.items.forEach((item) => { if (!names.includes(item.raw_name)) names.push(item.raw_name); });
    return new Map(names.map((name, index) => [name, index]));
  }, [queue.data?.items]);

  const columns = useMemo<DataTableColumn<AuthorQueueRow>[]>(() => [
    { accessorKey: "raw_name", header: "Tên thô", cell: ({ row }) => <div><p className="font-medium">{row.original.raw_name}</p><p className="mt-0.5 text-[11px] text-muted-foreground">Nhóm {row.original.group_work_count} công trình</p></div> },
    { accessorKey: "work_title", header: "Công trình", cell: ({ row }) => <Link href={`/cong-trinh/?id=${row.original.work_id}`} className="block max-w-xs whitespace-normal font-medium text-primary hover:underline">{row.original.work_title ?? "Chưa có tiêu đề"}</Link> },
    { accessorKey: "candidate_name", header: "Ứng viên", cell: ({ row }) => <Link href={`/giang-vien/?id=${row.original.candidate_person_id}`} className="font-medium capitalize text-primary hover:underline">{row.original.candidate_name}</Link> },
    { accessorKey: "confidence", header: "Tin cậy", cell: ({ row }) => <Badge variant="outline" className={row.original.confidence === "ai_mentor" ? "border-primary/30 bg-primary/10 text-primary" : ["cao", "ten_day_du_duy_nhat", "orcid"].includes(row.original.confidence) ? "border-status-success/30 bg-status-success/10 text-status-success" : "border-status-warning/30 bg-status-warning/10 text-status-warning"}>{row.original.confidence === "ai_mentor" && <Sparkles />}{confidenceLabels[row.original.confidence] ?? row.original.confidence}</Badge> },
    { accessorKey: "degree_conflict", header: "Học vị", enableSorting: false, cell: ({ row }) => row.original.degree_conflict ? <span title="Học vị trong nguồn có dấu hiệu xung đột" className="inline-flex items-center gap-1 text-status-warning"><AlertTriangle className="size-4" /><span className="sr-only">Cảnh báo học vị</span></span> : <span className="text-muted-foreground">—</span> },
    { accessorKey: "group_work_count", header: "Cùng tên", cell: ({ row }) => <span className="tabular-nums">{row.original.group_work_count}</span> },
    { accessorKey: "ai_rank", header: "Gợi ý AI", enableSorting: false, cell: ({ row }) => row.original.ai_rank ? <div className="max-w-60 whitespace-normal"><Badge variant="outline" className="mb-1 text-muted-foreground"><Bot />gợi ý · hạng {row.original.ai_rank}</Badge><p className="text-xs leading-5 text-muted-foreground">{row.original.ai_reason ?? "Không có giải thích"}</p></div> : <span className="text-muted-foreground">—</span> },
  ], []);

  async function submitDecision(input: DecideAuthorsIn) {
    try {
      const result = await decide.mutateAsync(input);
      toast.success(`Đã xử lý ${result.processed.length} liên kết tác giả.`);
      setSelection({});
      setReason("");
      setPersonId(null);
      setRejectOpen(false);
      setReassignOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["author-queue"] });
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể xử lý các liên kết đã chọn.");
    }
  }

  return (
    <>
      <PageHeader title="Hàng đợi tác giả" description="AI chỉ đưa ra gợi ý; người dùng xác nhận, bác bỏ hoặc chuyển liên kết cho người khác." />
      <AuthorQueueTabs active="queue" />
      <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <Tabs value={state} onValueChange={(value) => { setState(String(value)); setPage(1); setSelection({}); }}>
          <TabsList variant="line" className="max-w-full overflow-x-auto">
            {states.map((value, index) => <TabsTrigger key={value} value={value}>{stateLabels[value]}<Badge variant="secondary" className="tabular-nums">{counts[index] ?? "…"}</Badge></TabsTrigger>)}
          </TabsList>
        </Tabs>
        <form className="flex w-full gap-2 xl:w-80" onSubmit={(event) => { event.preventDefault(); setQ(search.trim()); setPage(1); setSelection({}); }}>
          <div className="relative flex-1"><Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Tìm theo tên thô" value={search} onChange={(event) => setSearch(event.target.value)} className="pl-8" placeholder="Tìm theo tên thô…" /></div>
          <Button type="submit" variant="outline">Tìm</Button>
        </form>
      </div>

      {queue.isLoading ? <LoadingView /> : queue.isError ? <ErrorView error={queue.error} retry={() => queue.refetch()} /> : <DataTable columns={columns} data={items ?? []} emptyMessage="Không có liên kết ở trạng thái này. Hãy chọn tab khác hoặc đổi từ khoá tìm kiếm." getRowId={(row) => String(row.link_id)} rowSelection={selection} onRowSelectionChange={setSelection} getRowClassName={(row) => (groupOrder.get(row.raw_name) ?? 0) % 2 === 0 ? "bg-primary/[0.025]" : undefined} page={{ page: queue.data?.page.page ?? page, perPage: queue.data?.page.per_page ?? 50, total: queue.data?.page.total ?? 0, onPageChange: (nextPage) => { setPage(nextPage); setSelection({}); } }} />}

      {selectedIds.length > 0 && <div className="sticky bottom-[var(--data-footer-h)] z-10 mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-popover/95 p-3 shadow-lg backdrop-blur"><p className="text-sm font-medium"><span className="tabular-nums">{selectedIds.length}</span> liên kết đã chọn</p><div className="flex flex-wrap gap-2" title={canDecide ? undefined : officerRoleRequired}><Button type="button" onClick={() => submitDecision({ link_ids: selectedIds, decision: "confirm" })} disabled={!canDecide || decide.isPending}><Check />Xác nhận</Button><Button type="button" variant="destructive" onClick={() => setRejectOpen(true)} disabled={!canDecide}><UserRoundX />Bác bỏ</Button><Button type="button" variant="outline" onClick={() => setReassignOpen(true)} disabled={!canDecide}><CornerDownRight />Chuyển cho người khác</Button></div></div>}

      <Dialog open={rejectOpen} onOpenChange={setRejectOpen}>
        <DialogContent><form onSubmit={(event) => { event.preventDefault(); if (canDecide) void submitDecision({ link_ids: selectedIds, decision: "reject", reason: reason.trim() }); }}><DialogHeader><DialogTitle>Bác bỏ liên kết tác giả</DialogTitle><DialogDescription>Nhập lý do để quyết định có thể được kiểm tra lại trong nhật ký.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="reject-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="reject-reason" required value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Nêu lý do bác bỏ…" /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setRejectOpen(false)}>Huỷ</Button><Button type="submit" variant="destructive" disabled={!canDecide || decide.isPending}>Bác bỏ</Button></DialogFooter></form></DialogContent>
      </Dialog>

      <Dialog open={reassignOpen} onOpenChange={setReassignOpen}>
        <DialogContent><form onSubmit={(event) => { event.preventDefault(); if (canDecide && personId !== null) void submitDecision({ link_ids: selectedIds, decision: "reassign", person_id: personId, reason: reason.trim() || undefined }); }}><DialogHeader><DialogTitle>Chuyển cho người khác</DialogTitle><DialogDescription>Tìm và chọn người sẽ nhận các liên kết đã chọn.</DialogDescription></DialogHeader><div className="space-y-3 py-4"><div><label htmlFor="reassign-person" className="mb-1.5 block font-medium">Người nhận <span className="text-status-danger">*</span></label><PersonCombobox id="reassign-person" onValueChange={setPersonId} /></div><div><label htmlFor="reassign-reason" className="mb-1.5 block font-medium">Lý do (tuỳ chọn)</label><Textarea id="reassign-reason" value={reason} onChange={(event) => setReason(event.target.value)} /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setReassignOpen(false)}>Huỷ</Button><Button type="submit" disabled={!canDecide || decide.isPending || personId === null}>Chuyển</Button></DialogFooter></form></DialogContent>
      </Dialog>
    </>
  );
}
