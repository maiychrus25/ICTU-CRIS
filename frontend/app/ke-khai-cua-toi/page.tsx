// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { CircleAlert, Send, Undo2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { Pager } from "@/components/pager";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { getDeclarationActions, type DeclarationAction } from "@/lib/declarations";
import { useAddMyDeclaration, useMe, useMyDeclarations, useMyWorks, usePeriods, useSetDeclarationState } from "@/lib/queries";
import type { DeclarationRow } from "@/lib/types";

function showError(error: unknown, fallback: string) {
  if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : fallback);
}

export default function MyDeclarationsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [periodChoice, setPeriodChoice] = useState<number | null>(null);
  const [stateAction, setStateAction] = useState<{ row: DeclarationRow; action: DeclarationAction } | null>(null);
  const me = useMe();
  const periods = usePeriods();
  const works = useMyWorks(page);
  const declarations = useMyDeclarations();
  const addDeclaration = useAddMyDeclaration();
  const setState = useSetDeclarationState();
  const openPeriods = periods.data?.filter((period) => period.state === "DangMo") ?? [];
  const periodId = periodChoice ?? openPeriods[0]?.id ?? null;
  const selectedPeriod = openPeriods.find((period) => period.id === periodId);
  const canDeclare = Boolean(me.data?.user?.roles.some((role) => ["lecturer", "faculty_officer", "rd_officer"].includes(role)));

  async function declareWork(workId: number) {
    if (periodId === null) return;
    try {
      await addDeclaration.mutateAsync({ period_id: periodId, work_id: workId });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["my-works"] }),
        queryClient.invalidateQueries({ queryKey: ["my-declarations"] }),
        queryClient.invalidateQueries({ queryKey: ["declarations", periodId] }),
        queryClient.invalidateQueries({ queryKey: ["period-progress", periodId] }),
      ]);
      toast.success("Đã kê khai công trình vào kỳ báo cáo.");
    } catch (error) { showError(error, "Không thể kê khai công trình."); }
  }

  async function transition(row: DeclarationRow, action: DeclarationAction, reason?: string) {
    try {
      await setState.mutateAsync({ id: row.id, input: { to_state: action.to, reason: reason?.trim() || null } });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["my-declarations"] }),
        queryClient.invalidateQueries({ queryKey: ["declaration", row.id] }),
        queryClient.invalidateQueries({ queryKey: ["declarations", row.period_id] }),
        queryClient.invalidateQueries({ queryKey: ["period-progress", row.period_id] }),
      ]);
      toast.success(`Đã ${action.label.toLocaleLowerCase("vi")}.`);
      setStateAction(null);
    } catch (error) { showError(error, "Không thể cập nhật trạng thái hồ sơ."); }
  }

  if (works.isError && works.error instanceof ApiError && works.error.status === 409) {
    return <><PageHeader title="Kê khai của tôi" /><Alert variant="destructive"><CircleAlert /><AlertTitle>Chưa thể kê khai</AlertTitle><AlertDescription>Tài khoản chưa gắn với hồ sơ giảng viên — liên hệ Phòng KH-CN</AlertDescription><AlertAction><Button variant="outline" size="sm" onClick={() => works.refetch()}>Thử lại</Button></AlertAction></Alert></>;
  }
  if (me.isLoading || periods.isLoading || works.isLoading || declarations.isLoading) return <><PageHeader title="Kê khai của tôi" /><LoadingView label="Đang tải công trình và hồ sơ của bạn…" /></>;
  if (me.isError) return <><PageHeader title="Kê khai của tôi" /><ErrorView error={me.error} retry={() => me.refetch()} /></>;
  if (periods.isError) return <><PageHeader title="Kê khai của tôi" /><ErrorView error={periods.error} retry={() => periods.refetch()} /></>;
  if (works.isError) return <><PageHeader title="Kê khai của tôi" /><ErrorView error={works.error} retry={() => works.refetch()} /></>;
  if (declarations.isError) return <><PageHeader title="Kê khai của tôi" /><ErrorView error={declarations.error} retry={() => declarations.refetch()} /></>;

  return (
    <>
      <PageHeader title="Kê khai của tôi" description="Chọn công trình của bạn để kê khai vào kỳ đang mở và theo dõi hồ sơ đã tạo." />

      <section aria-labelledby="my-works-title">
        <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div><h2 id="my-works-title" className="text-base font-semibold">Công trình của tôi</h2><p className="text-xs text-muted-foreground">Công trình được lấy từ các liên kết tác giả trong hồ sơ giảng viên.</p></div>
          <div><label className="mb-1 block text-xs font-medium">Kỳ đang mở</label><Select value={periodId === null ? "" : String(periodId)} onValueChange={(value) => setPeriodChoice(Number(value))} disabled={!openPeriods.length}><SelectTrigger aria-label="Kỳ đang mở" className="w-full sm:w-80"><SelectValue>{(value) => openPeriods.find((period) => period.id === Number(value))?.name ?? "Không có kỳ đang mở"}</SelectValue></SelectTrigger><SelectContent>{openPeriods.map((period) => <SelectItem key={period.id} value={String(period.id)}>{period.name} ({period.code})</SelectItem>)}</SelectContent></Select></div>
        </div>

        {!openPeriods.length && <Alert className="mb-4"><CircleAlert /><AlertTitle>Chưa có kỳ đang mở</AlertTitle><AlertDescription>Bạn có thể xem công trình và hồ sơ cũ; việc kê khai sẽ khả dụng khi Phòng KH-CN mở kỳ mới.</AlertDescription></Alert>}
        {!works.data?.items.length ? <EmptyView title="Chưa có công trình được liên kết" description="Kiểm tra hồ sơ giảng viên hoặc liên hệ Phòng KH-CN để rà soát liên kết tác giả." /> : <div className="overflow-x-auto rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead className="min-w-80">Tiêu đề</TableHead><TableHead>Loại</TableHead><TableHead>Năm</TableHead><TableHead>Trạng thái liên kết</TableHead><TableHead className="min-w-64">Đã kê khai</TableHead><TableHead><span className="sr-only">Hành động</span></TableHead></TableRow></TableHeader><TableBody>{works.data.items.map((work) => { const declared = periodId !== null && work.declared_in.includes(periodId); const eligible = ["DaNoiTuDong", "DaXacNhan"].includes(work.link_state); return <TableRow key={work.work_id}><TableCell className="whitespace-normal"><Link href={`/cong-trinh/?id=${work.work_id}`} className="font-medium text-primary hover:underline">{work.title ?? `Công trình #${work.work_id}`}</Link>{work.doi && <p className="mt-1 text-xs text-muted-foreground">DOI: {work.doi}</p>}</TableCell><TableCell>{work.doc_type_label}</TableCell><TableCell className="tabular-nums">{work.year ?? "—"}</TableCell><TableCell><StatusBadge value={work.link_state} /></TableCell><TableCell>{declared && selectedPeriod ? <span className="font-medium">{selectedPeriod.name} <span className="text-xs text-muted-foreground">({selectedPeriod.code})</span></span> : <span className="text-muted-foreground">Chưa kê khai</span>}</TableCell><TableCell>{!declared && <span title={!eligible ? "Liên kết tác giả cần được xác nhận trước khi kê khai" : !canDeclare ? "Tài khoản chưa có vai trò được phép kê khai" : undefined}><Button type="button" size="sm" variant="outline" disabled={!canDeclare || !eligible || periodId === null || addDeclaration.isPending} onClick={() => void declareWork(work.work_id)}>Kê khai vào kỳ này</Button></span>}</TableCell></TableRow>; })}</TableBody></Table><Pager page={works.data.page.page} perPage={works.data.page.per_page} total={works.data.page.total} onPageChange={setPage} /></div>}
      </section>

      <section aria-labelledby="my-declarations-title" className="mt-8">
        <div className="mb-4"><h2 id="my-declarations-title" className="text-base font-semibold">Hồ sơ của tôi</h2><p className="text-xs text-muted-foreground">Chỉ gồm các hồ sơ do chính bạn kê khai.</p></div>
        {!declarations.data?.items.length ? <EmptyView title="Chưa có hồ sơ kê khai" description="Chọn “Kê khai vào kỳ này” ở bảng công trình phía trên để tạo hồ sơ đầu tiên." /> : <div className="overflow-x-auto rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Hồ sơ</TableHead><TableHead className="min-w-80">Công trình</TableHead><TableHead>Kỳ báo cáo</TableHead><TableHead>Trạng thái</TableHead><TableHead><span className="sr-only">Hành động</span></TableHead></TableRow></TableHeader><TableBody>{declarations.data.items.map((row) => { const period = periods.data?.find((item) => item.id === row.period_id); const actions = getDeclarationActions(row.state, me.data, row.unit_code, period?.state, true).filter((action) => action.to === "ChoKhoaDuyet" || action.to === "Rut"); return <TableRow key={row.id}><TableCell><Link href={`/ke-khai/?id=${row.id}`} className="font-semibold text-primary hover:underline">#{row.id}</Link></TableCell><TableCell className="whitespace-normal"><Link href={`/cong-trinh/?id=${row.work_id}`} className="font-medium text-primary hover:underline">{row.work_title ?? `Công trình #${row.work_id}`}</Link></TableCell><TableCell>{period ? <><span className="font-medium">{period.name}</span><p className="text-xs text-muted-foreground">{period.code}</p></> : `Kỳ #${row.period_id}`}</TableCell><TableCell><StatusBadge value={row.state} /></TableCell><TableCell><div className="flex flex-wrap justify-end gap-2">{actions.map((action) => <Button key={action.to} type="button" size="sm" variant={action.destructive ? "destructive" : "outline"} disabled={setState.isPending} onClick={() => action.reasonRequired ? setStateAction({ row, action }) : void transition(row, action)}>{action.to === "ChoKhoaDuyet" ? <Send /> : <Undo2 />}{action.label}</Button>)}</div></TableCell></TableRow>; })}</TableBody></Table></div>}
      </section>

      <Dialog open={stateAction !== null} onOpenChange={(open) => { if (!open) setStateAction(null); }}><DialogContent><form onSubmit={(event) => { event.preventDefault(); if (stateAction) void transition(stateAction.row, stateAction.action, String(new FormData(event.currentTarget).get("reason"))); }}><DialogHeader><DialogTitle>Rút hồ sơ?</DialogTitle><DialogDescription>Nêu rõ lý do để quyết định được ghi nhận trong dòng thời gian và nhật ký.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="my-declaration-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="my-declaration-reason" name="reason" required /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setStateAction(null)}>Huỷ</Button><Button type="submit" variant="destructive" disabled={setState.isPending}>Rút</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}
