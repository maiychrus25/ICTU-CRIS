// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Ban, FilePlus2, LockKeyhole, MoreHorizontal, Plus, Search } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { getDeclarationActions, type DeclarationAction } from "@/lib/declarations";
import { officerRoleRequired, stateLabels } from "@/lib/labels";
import {
  useAddDeclaration, useAddDeclarationEvidence, useCancelPeriod, useClosePeriod, useDeclarations,
  useFinalizePeriod, useMe, useOfficerAccess, usePeriodProgress, usePeriods, useSetDeclarationState, useStats, useWorks,
} from "@/lib/queries";
import type { DeclarationRow, EvidenceKind, PeriodFinalizeOut } from "@/lib/types";

const progressGroups = [
  { label: "Đang soạn", states: ["Nhap", "ChoBoSung"], className: "bg-slate-400 dark:bg-slate-500" },
  { label: "Chờ khoa", states: ["ChoKhoaDuyet"], className: "bg-blue-400 dark:bg-blue-500" },
  { label: "Khoa đã duyệt", states: ["KhoaDaDuyet"], className: "bg-blue-700 dark:bg-blue-600" },
  { label: "Chờ phòng", states: ["ChoPhongKiemTra"], className: "bg-violet-500" },
  { label: "Đạt", states: ["DatYeuCau"], className: "bg-emerald-500" },
  { label: "Đã chốt", states: ["DaChot"], className: "bg-emerald-800 dark:bg-emerald-700" },
  { label: "Rút", states: ["Rut"], className: "bg-red-400 dark:bg-red-500" },
] as const;

function formatDate(value: string | null) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "—";
}

function DueStatus({ days }: { days: number | null }) {
  if (days === null) return <span className="text-muted-foreground">Chưa có hạn nộp</span>;
  return <span className={days < 0 ? "font-medium text-status-danger" : "font-medium text-status-success"}>{days < 0 ? `Quá hạn ${Math.abs(days)} ngày` : `Còn ${days} ngày`}</span>;
}

function WorkPicker({ onValueChange }: { onValueChange: (id: number | null) => void }) {
  const [text, setText] = useState("");
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const works = useWorks({ q: query }, query.length > 0);

  useEffect(() => {
    const timeout = window.setTimeout(() => setQuery(text.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [text]);

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-2.5 top-2.5 z-10 size-4 text-muted-foreground" />
      <Input
        role="combobox" aria-label="Tìm công trình" aria-autocomplete="list" aria-expanded={open}
        value={text} autoComplete="off" className="pl-8" placeholder="Nhập tiêu đề công trình…"
        onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}
        onChange={(event) => { setText(event.target.value); onValueChange(null); setOpen(true); }}
      />
      {open && query && (
        <div role="listbox" className="absolute z-50 mt-1 max-h-64 w-full overflow-y-auto rounded-lg border bg-popover p-1 text-popover-foreground shadow-md">
          {works.isFetching ? <p className="px-3 py-2 text-sm text-muted-foreground">Đang tìm công trình…</p>
            : works.isError ? <div className="flex items-center justify-between gap-2 px-3 py-2 text-sm text-destructive"><span>Không thể tìm công trình.</span><Button type="button" variant="ghost" size="sm" onMouseDown={(event) => event.preventDefault()} onClick={() => works.refetch()}>Thử lại</Button></div>
            : works.data?.items.length ? works.data.items.map((work) => (
              <button key={work.id} type="button" role="option" aria-selected="false" className="block w-full rounded-md px-3 py-2 text-left hover:bg-accent focus:bg-accent focus:outline-none" onMouseDown={(event) => event.preventDefault()} onClick={() => { setText(work.title ?? `Công trình #${work.id}`); onValueChange(work.id); setOpen(false); }}>
                <span className="block font-medium">{work.title ?? `Công trình #${work.id}`}</span>
                <span className="block text-xs text-muted-foreground">{work.doc_type_label} · {work.year ?? "Chưa rõ năm"}</span>
              </button>
            )) : <p className="px-3 py-2 text-sm text-muted-foreground">Không tìm thấy công trình phù hợp.</p>}
        </div>
      )}
    </div>
  );
}

function DeclarationsTab({ periodId, periodState }: { periodId: number; periodState: string }) {
  const queryClient = useQueryClient();
  const canDecide = useOfficerAccess();
  const me = useMe();
  const [unit, setUnit] = useState("all");
  const declarations = useDeclarations(periodId, unit === "all" ? undefined : Number(unit));
  const stats = useStats();
  const add = useAddDeclaration(periodId);
  const setState = useSetDeclarationState();
  const addEvidence = useAddDeclarationEvidence();
  const [declareOpen, setDeclareOpen] = useState(false);
  const [workId, setWorkId] = useState<number | null>(null);
  const [unitId, setUnitId] = useState("");
  const [stateAction, setStateAction] = useState<{ row: DeclarationRow; action: DeclarationAction } | null>(null);
  const [evidenceRow, setEvidenceRow] = useState<DeclarationRow | null>(null);
  const [evidenceKind, setEvidenceKind] = useState<EvidenceKind>("link");
  const canAct = periodState === "DangMo" && canDecide;

  async function invalidate(includeProgress = true) {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["declarations", periodId] }),
      ...(includeProgress ? [queryClient.invalidateQueries({ queryKey: ["period-progress", periodId] })] : []),
    ]);
  }

  function showError(error: unknown, fallback: string) {
    if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : fallback);
  }

  async function createDeclaration(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canAct || workId === null || !unitId) return;
    const form = new FormData(event.currentTarget);
    try {
      await add.mutateAsync({ work_id: workId, unit_id: Number(unitId), note: String(form.get("note")).trim() || null });
      await invalidate();
      toast.success("Đã kê khai công trình vào kỳ báo cáo.");
      setDeclareOpen(false);
      setWorkId(null);
      setUnitId("");
    } catch (error) { showError(error, "Không thể kê khai công trình."); }
  }

  async function transition(row: DeclarationRow, action: DeclarationAction, reason?: string) {
    try {
      await setState.mutateAsync({ id: row.id, input: { to_state: action.to, reason: reason?.trim() || null } });
      await invalidate();
      await queryClient.invalidateQueries({ queryKey: ["declaration", row.id] });
      toast.success(`Đã ${action.label.toLocaleLowerCase("vi")}.`);
      setStateAction(null);
    } catch (error) { showError(error, "Không thể cập nhật trạng thái hồ sơ."); }
  }

  async function submitEvidence(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canAct || !evidenceRow) return;
    const form = new FormData(event.currentTarget);
    try {
      await addEvidence.mutateAsync({ id: evidenceRow.id, input: {
        kind: evidenceKind, url: String(form.get("url")).trim() || null,
        file_name: String(form.get("file_name")).trim() || null, note: String(form.get("note")).trim() || null,
      } });
      await invalidate(false);
      await queryClient.invalidateQueries({ queryKey: ["declaration", evidenceRow.id] });
      toast.success("Đã thêm minh chứng.");
      setEvidenceRow(null);
      setEvidenceKind("link");
    } catch (error) { showError(error, "Không thể thêm minh chứng."); }
  }

  if (declarations.isLoading || stats.isLoading) return <LoadingView label="Đang tải hồ sơ kê khai…" />;
  if (declarations.isError) return <ErrorView error={declarations.error} retry={() => declarations.refetch()} />;
  if (stats.isError) return <ErrorView error={stats.error} retry={() => stats.refetch()} />;

  return (
    <section aria-labelledby="declarations-title">
      <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div><h2 id="declarations-title" className="text-base font-semibold">Hồ sơ kê khai</h2><p className="text-xs text-muted-foreground">Công trình do các đơn vị kê khai trong kỳ báo cáo này.</p></div>
        <div className="flex flex-wrap items-end gap-2">
          <div><label className="mb-1 block text-xs font-medium">Đơn vị</label><Select value={unit} onValueChange={(value) => setUnit(String(value))}><SelectTrigger aria-label="Lọc theo đơn vị" className="w-56"><SelectValue>{(value) => value === "all" ? "Tất cả đơn vị" : stats.data?.by_unit.find((item) => item.unit_id === Number(value))?.code}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả đơn vị</SelectItem>{stats.data?.by_unit.map((item) => <SelectItem key={item.unit_id} value={String(item.unit_id)}>{item.code} — {item.name}</SelectItem>)}</SelectContent></Select></div>
          <span title={canAct ? undefined : periodState !== "DangMo" ? "Chỉ kê khai khi kỳ đang mở" : officerRoleRequired}><Button type="button" onClick={() => { setUnitId(stats.data?.by_unit[0] ? String(stats.data.by_unit[0].unit_id) : ""); setDeclareOpen(true); }} disabled={!canAct}><Plus />Kê khai công trình</Button></span>
        </div>
      </div>

      {!declarations.data?.items.length ? <EmptyView title="Chưa có hồ sơ kê khai" description={unit === "all" ? "Kê khai công trình đầu tiên cho kỳ báo cáo này." : "Đơn vị đã chọn chưa có hồ sơ; hãy đổi bộ lọc hoặc kê khai công trình."} /> : (
        <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Hồ sơ</TableHead><TableHead className="min-w-72">Công trình</TableHead><TableHead>Loại</TableHead><TableHead>Đơn vị</TableHead><TableHead>Trạng thái</TableHead><TableHead className="text-right">Minh chứng</TableHead><TableHead>Cập nhật lần cuối</TableHead><TableHead><span className="sr-only">Hành động</span></TableHead></TableRow></TableHeader><TableBody>
          {declarations.data.items.map((row) => { const rowActions = getDeclarationActions(row.state, me.data, row.unit_code, periodState); return <TableRow key={row.id}>
            <TableCell><Link href={`/ke-khai/?id=${row.id}`} className="font-semibold text-primary hover:underline">#{row.id}</Link></TableCell>
            <TableCell className="whitespace-normal"><Link href={`/cong-trinh/?id=${row.work_id}`} className="font-medium text-primary hover:underline">{row.work_title ?? `Công trình #${row.work_id}`}</Link></TableCell>
            <TableCell>{row.doc_type_label}</TableCell><TableCell>{row.unit_code}</TableCell><TableCell><StatusBadge value={row.state} /></TableCell>
            <TableCell className="text-right tabular-nums">{row.evidence_count}</TableCell><TableCell className="whitespace-nowrap text-muted-foreground tabular-nums">{formatDate(row.last_event_at ?? row.updated_at)}</TableCell>
            <TableCell>{(rowActions.length > 0 || canDecide) && <DropdownMenu><DropdownMenuTrigger render={<Button type="button" variant="outline" size="sm" aria-label={`Hành động hồ sơ #${row.id}`} />}><MoreHorizontal />Hành động</DropdownMenuTrigger><DropdownMenuContent align="end">
              {rowActions.map((action) => <DropdownMenuItem key={action.to} variant={action.destructive ? "destructive" : "default"} onClick={() => action.reasonRequired ? setStateAction({ row, action }) : void transition(row, action)}>{action.label}</DropdownMenuItem>)}
              {canDecide && <DropdownMenuItem onClick={() => setEvidenceRow(row)}><FilePlus2 />Thêm minh chứng</DropdownMenuItem>}
            </DropdownMenuContent></DropdownMenu>}</TableCell>
          </TableRow>; })}
        </TableBody></Table></div>
      )}

      <Dialog open={declareOpen} onOpenChange={(open) => { setDeclareOpen(open); if (!open) setWorkId(null); }}><DialogContent className="sm:max-w-xl"><form onSubmit={(event) => void createDeclaration(event)}><DialogHeader><DialogTitle>Kê khai công trình</DialogTitle><DialogDescription>Chọn công trình và đơn vị chịu trách nhiệm kê khai trong kỳ này.</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div><label className="mb-1.5 block font-medium">Công trình <span className="text-status-danger">*</span></label><WorkPicker key={String(declareOpen)} onValueChange={setWorkId} /></div><div><label className="mb-1.5 block font-medium">Đơn vị <span className="text-status-danger">*</span></label><Select value={unitId} onValueChange={(value) => setUnitId(String(value))}><SelectTrigger aria-label="Đơn vị kê khai" className="w-full"><SelectValue>{(value) => stats.data?.by_unit.find((item) => item.unit_id === Number(value))?.code ?? "Chọn đơn vị"}</SelectValue></SelectTrigger><SelectContent>{stats.data?.by_unit.map((item) => <SelectItem key={item.unit_id} value={String(item.unit_id)}>{item.code} — {item.name}</SelectItem>)}</SelectContent></Select></div><div><label htmlFor="declaration-note" className="mb-1.5 block font-medium">Ghi chú</label><Textarea id="declaration-note" name="note" /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setDeclareOpen(false)}>Huỷ</Button><Button type="submit" disabled={!canAct || workId === null || !unitId || add.isPending}>Kê khai</Button></DialogFooter></form></DialogContent></Dialog>

      <Dialog open={stateAction !== null} onOpenChange={(open) => { if (!open) setStateAction(null); }}><DialogContent><form onSubmit={(event) => { event.preventDefault(); if (stateAction) void transition(stateAction.row, stateAction.action, String(new FormData(event.currentTarget).get("reason"))); }}><DialogHeader><DialogTitle>{stateAction?.action.label} hồ sơ?</DialogTitle><DialogDescription>Nêu rõ lý do để quyết định có thể được kiểm tra lại trong dòng thời gian và nhật ký.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="declaration-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="declaration-reason" name="reason" required /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setStateAction(null)}>Huỷ</Button><Button type="submit" variant={stateAction?.action.destructive ? "destructive" : "default"} disabled={setState.isPending}>{stateAction?.action.label}</Button></DialogFooter></form></DialogContent></Dialog>

      <Dialog open={evidenceRow !== null} onOpenChange={(open) => { if (!open) setEvidenceRow(null); }}><DialogContent className="sm:max-w-xl"><form onSubmit={(event) => void submitEvidence(event)}><DialogHeader><DialogTitle>Thêm minh chứng</DialogTitle><DialogDescription>Gắn đường dẫn, tệp hoặc ghi chú làm minh chứng cho hồ sơ #{evidenceRow?.id}.</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div><label className="mb-1.5 block font-medium">Loại minh chứng</label><Select value={evidenceKind} onValueChange={(value) => setEvidenceKind(value as EvidenceKind)}><SelectTrigger aria-label="Loại minh chứng" className="w-full"><SelectValue>{(value) => value === "link" ? "Đường dẫn" : value === "file" ? "Tệp" : "Ghi chú"}</SelectValue></SelectTrigger><SelectContent><SelectItem value="link">Đường dẫn</SelectItem><SelectItem value="file">Tệp</SelectItem><SelectItem value="note">Ghi chú</SelectItem></SelectContent></Select></div><div><label htmlFor="evidence-url" className="mb-1.5 block font-medium">URL</label><Input id="evidence-url" name="url" type="url" placeholder="https://…" /></div><div><label htmlFor="evidence-file" className="mb-1.5 block font-medium">Tên tệp</label><Input id="evidence-file" name="file_name" /></div><div><label htmlFor="evidence-note" className="mb-1.5 block font-medium">Ghi chú</label><Textarea id="evidence-note" name="note" /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setEvidenceRow(null)}>Huỷ</Button><Button type="submit" disabled={!canAct || addEvidence.isPending}>Thêm minh chứng</Button></DialogFooter></form></DialogContent></Dialog>
    </section>
  );
}

function PeriodDetailContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const queryClient = useQueryClient();
  const progress = usePeriodProgress(id);
  const periods = usePeriods();
  const close = useClosePeriod(id ?? 0);
  const cancel = useCancelPeriod(id ?? 0);
  const finalize = useFinalizePeriod(id ?? 0);
  const canDecide = useOfficerAccess();
  const [tab, setTab] = useState("progress");
  const [closeOpen, setCloseOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [finalizeOpen, setFinalizeOpen] = useState(false);
  const [finalizeResult, setFinalizeResult] = useState<PeriodFinalizeOut | null>(null);

  if (id === null) return <><PageHeader title="Chi tiết kỳ báo cáo" /><EmptyView title="Chưa chọn kỳ báo cáo" description="Mở một kỳ từ danh sách để xem tiến độ." action={<Link href="/ky-bao-cao/" className="font-medium text-primary hover:underline">Đi đến danh sách kỳ</Link>} /></>;
  if (progress.isLoading || periods.isLoading) return <><PageHeader title="Chi tiết kỳ báo cáo" /><LoadingView /></>;
  if (progress.isError) return <><PageHeader title="Chi tiết kỳ báo cáo" /><ErrorView error={progress.error} retry={() => progress.refetch()} /></>;
  if (periods.isError) return <><PageHeader title="Chi tiết kỳ báo cáo" /><ErrorView error={periods.error} retry={() => periods.refetch()} /></>;
  if (!progress.data) return <><PageHeader title="Chi tiết kỳ báo cáo" /><EmptyView description="Không tìm thấy tiến độ của kỳ báo cáo này. Hãy quay lại danh sách kỳ." /></>;

  const data = progress.data;
  const period = periods.data?.find((item) => item.id === id);
  const state = data.state;

  async function decide(action: "close" | "cancel") {
    try {
      await (action === "close" ? close.mutateAsync() : cancel.mutateAsync());
      toast.success(action === "close" ? "Đã đóng nộp kỳ báo cáo." : "Đã huỷ kỳ báo cáo.");
      setCloseOpen(false);
      setCancelOpen(false);
      await Promise.all([queryClient.invalidateQueries({ queryKey: ["period-progress", id] }), queryClient.invalidateQueries({ queryKey: ["periods"] })]);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể cập nhật kỳ báo cáo.");
    }
  }

  async function finalizeDeclarations() {
    try {
      const result = await finalize.mutateAsync();
      setFinalizeResult(result);
      toast.success(`Đã chốt ${result.finalized} hồ sơ.`);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["period-progress", id] }),
        queryClient.invalidateQueries({ queryKey: ["declarations", id] }),
      ]);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể chốt kỳ báo cáo.");
    }
  }

  return (
    <>
      <PageHeader title={period?.name ?? `Kỳ báo cáo #${id}`} description={period ? `Mã kỳ ${period.code}` : undefined} action={<div className="flex items-center gap-3"><DueStatus days={data.days_remaining} /><StatusBadge value={state} /></div>} />
      <div className="mb-5 flex flex-wrap justify-end gap-2" title={canDecide ? undefined : officerRoleRequired}>{state === "DangMo" && <Button type="button" onClick={() => setCloseOpen(true)} disabled={!canDecide}><LockKeyhole />Đóng nộp</Button>}{state === "DaDongNop" && <Button type="button" onClick={() => { setFinalizeResult(null); setFinalizeOpen(true); }} disabled={!canDecide}><LockKeyhole />Chốt kỳ</Button>}{(state === "ChuanBi" || state === "DangMo") && <Button type="button" variant="destructive" onClick={() => setCancelOpen(true)} disabled={!canDecide}><Ban />Huỷ kỳ</Button>}</div>
      <Tabs value={tab} onValueChange={(value) => setTab(String(value))} className="mb-5"><TabsList variant="line"><TabsTrigger value="progress">Tiến độ theo đơn vị</TabsTrigger><TabsTrigger value="declarations">Hồ sơ kê khai</TabsTrigger></TabsList></Tabs>

      {tab === "progress" ? <section aria-labelledby="period-progress-title"><div className="mb-3"><h2 id="period-progress-title" className="text-base font-semibold">Tiến độ theo đơn vị</h2><p className="text-xs text-muted-foreground">Thanh thể hiện cơ cấu trạng thái của các hồ sơ đã kê khai tại từng đơn vị.</p></div>{data.units.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Đơn vị</TableHead>{progressGroups.map((group) => <TableHead key={group.label} className="text-right">{group.label}</TableHead>)}<TableHead className="min-w-52">Tiến độ</TableHead></TableRow></TableHeader><TableBody>{data.units.map((unit) => { const counts = progressGroups.map((group) => group.states.reduce((total, item) => total + (unit.counts[item] ?? 0), 0)); return <TableRow key={unit.unit_id}><TableCell><span className="font-medium">{unit.unit_name}</span><span className="ml-2 text-xs text-muted-foreground">{unit.unit_code}</span></TableCell>{counts.map((count, index) => <TableCell key={progressGroups[index].label} className="text-right tabular-nums">{count}</TableCell>)}<TableCell><div role="progressbar" aria-label={`Cơ cấu hồ sơ ${unit.unit_name}`} aria-valuemin={0} aria-valuemax={Math.max(1, unit.total)} aria-valuenow={unit.total} className="flex h-2.5 overflow-hidden rounded-full bg-muted">{unit.total > 0 && counts.map((count, index) => count > 0 && <span key={progressGroups[index].label} className={`h-full ${progressGroups[index].className}`} style={{ width: `${count / unit.total * 100}%` }} title={`${progressGroups[index].label}: ${count}`} />)}</div><p className="mt-1 text-[11px] text-muted-foreground tabular-nums">{unit.total} hồ sơ</p></TableCell></TableRow>; })}</TableBody></Table></div> : <EmptyView description="Chưa có đơn vị hoạt động trong kỳ này. Hãy kiểm tra lại phạm vi kỳ báo cáo." />}</section> : <DeclarationsTab periodId={id} periodState={state} />}

      <Dialog open={closeOpen} onOpenChange={setCloseOpen}><DialogContent><DialogHeader><DialogTitle>Đóng nộp kỳ báo cáo?</DialogTitle><DialogDescription>Sau khi đóng, các đơn vị không thể tiếp tục nộp hồ sơ vào kỳ này.</DialogDescription></DialogHeader><DialogFooter><Button type="button" variant="outline" onClick={() => setCloseOpen(false)}>Huỷ</Button><Button type="button" onClick={() => canDecide && void decide("close")} disabled={!canDecide || close.isPending}>Đóng nộp</Button></DialogFooter></DialogContent></Dialog>
      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}><DialogContent><DialogHeader><DialogTitle>Huỷ kỳ báo cáo?</DialogTitle><DialogDescription>Kỳ sẽ chuyển sang trạng thái Đã huỷ và không thể tiếp tục nhận hồ sơ.</DialogDescription></DialogHeader><DialogFooter><Button type="button" variant="outline" onClick={() => setCancelOpen(false)}>Quay lại</Button><Button type="button" variant="destructive" onClick={() => canDecide && void decide("cancel")} disabled={!canDecide || cancel.isPending}>Huỷ kỳ</Button></DialogFooter></DialogContent></Dialog>
      <Dialog open={finalizeOpen} onOpenChange={setFinalizeOpen}><DialogContent><DialogHeader><DialogTitle>Chốt kỳ báo cáo?</DialogTitle><DialogDescription>Hồ sơ Đạt yêu cầu sẽ chuyển sang Đã chốt; các hồ sơ còn lại được giữ nguyên và liệt kê là bỏ qua.</DialogDescription></DialogHeader>{finalizeResult ? <dl className="grid grid-cols-2 gap-4 py-4"><div className="rounded-lg border p-4"><dt className="text-xs text-muted-foreground">Đã chốt</dt><dd className="mt-1 text-2xl font-semibold tabular-nums">{finalizeResult.finalized}</dd></div><div className="rounded-lg border p-4"><dt className="text-xs text-muted-foreground">Bỏ qua</dt><dd className="mt-1 text-2xl font-semibold tabular-nums">{finalizeResult.skipped.length}</dd></div>{finalizeResult.skipped.length > 0 && <div className="col-span-2 text-xs text-muted-foreground">Hồ sơ bỏ qua: {finalizeResult.skipped.map((item) => `#${item.id} (${stateLabels[item.state] ?? item.state})`).join(", ")}</div>}</dl> : <p className="py-4 text-sm">Hành động ghi nhận người thực hiện và không tự thay đổi hồ sơ chưa đạt yêu cầu.</p>}<DialogFooter>{finalizeResult ? <Button type="button" onClick={() => setFinalizeOpen(false)}>Đóng</Button> : <><Button type="button" variant="outline" onClick={() => setFinalizeOpen(false)}>Huỷ</Button><Button type="button" onClick={() => canDecide && void finalizeDeclarations()} disabled={!canDecide || finalize.isPending}>Chốt kỳ</Button></>}</DialogFooter></DialogContent></Dialog>
    </>
  );
}

export default function PeriodDetailPage() {
  return <Suspense fallback={<LoadingView label="Đang tải tiến độ kỳ báo cáo…" />}><PeriodDetailContent /></Suspense>;
}
