// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Ban, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ApiError } from "@/lib/api";
import { officerRoleRequired } from "@/lib/labels";
import { useCancelPeriod, useClosePeriod, useOfficerAccess, usePeriodProgress, usePeriods } from "@/lib/queries";

function DueStatus({ days }: { days: number | null }) {
  if (days === null) return <span className="text-muted-foreground">Chưa có hạn nộp</span>;
  return <span className={days < 0 ? "font-medium text-status-danger" : "font-medium text-status-success"}>{days < 0 ? `Quá hạn ${Math.abs(days)} ngày` : `Còn ${days} ngày`}</span>;
}

function PeriodDetailContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const queryClient = useQueryClient();
  const progress = usePeriodProgress(id);
  const periods = usePeriods();
  const close = useClosePeriod(id ?? 0);
  const cancel = useCancelPeriod(id ?? 0);
  const canDecide = useOfficerAccess();
  const [closeOpen, setCloseOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);

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
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["period-progress", id] }),
        queryClient.invalidateQueries({ queryKey: ["periods"] }),
      ]);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể cập nhật kỳ báo cáo.");
    }
  }

  return (
    <>
      <PageHeader title={period?.name ?? `Kỳ báo cáo #${id}`} description={period ? `Mã kỳ ${period.code}` : undefined} action={<div className="flex items-center gap-3"><DueStatus days={data.days_remaining} /><StatusBadge value={state} /></div>} />
      <div className="mb-5 flex flex-wrap justify-end gap-2" title={canDecide ? undefined : officerRoleRequired}>{state === "DangMo" && <Button type="button" onClick={() => setCloseOpen(true)} disabled={!canDecide}><LockKeyhole />Đóng nộp</Button>}{(state === "ChuanBi" || state === "DangMo") && <Button type="button" variant="destructive" onClick={() => setCancelOpen(true)} disabled={!canDecide}><Ban />Huỷ kỳ</Button>}</div>
      <section aria-labelledby="period-progress-title"><div className="mb-3"><h2 id="period-progress-title" className="text-base font-semibold">Tiến độ theo đơn vị</h2><p className="text-xs text-muted-foreground">Thanh thể hiện cơ cấu trạng thái của các hồ sơ đã kê khai tại từng đơn vị.</p></div>{data.units.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Đơn vị</TableHead><TableHead className="text-right">Nháp</TableHead><TableHead className="text-right">Chờ bổ sung</TableHead><TableHead className="text-right">Đã rút</TableHead><TableHead className="min-w-52">Tiến độ</TableHead></TableRow></TableHeader><TableBody>{data.units.map((unit) => { const draft = unit.counts.Nhap ?? 0; const supplement = unit.counts.ChoBoSung ?? 0; const withdrawn = unit.counts.Rut ?? 0; return <TableRow key={unit.unit_id}><TableCell><span className="font-medium">{unit.unit_name}</span><span className="ml-2 text-xs text-muted-foreground">{unit.unit_code}</span></TableCell><TableCell className="text-right tabular-nums">{draft}</TableCell><TableCell className="text-right tabular-nums">{supplement}</TableCell><TableCell className="text-right tabular-nums">{withdrawn}</TableCell><TableCell><div role="progressbar" aria-label={`Cơ cấu hồ sơ ${unit.unit_name}`} aria-valuemin={0} aria-valuemax={Math.max(1, unit.total)} aria-valuenow={unit.total} className="flex h-2.5 overflow-hidden rounded-full bg-muted">{unit.total > 0 && <><span className="h-full bg-primary" style={{ width: `${draft / unit.total * 100}%` }} /><span className="h-full bg-status-warning" style={{ width: `${supplement / unit.total * 100}%` }} /><span className="h-full bg-status-danger" style={{ width: `${withdrawn / unit.total * 100}%` }} /></>}</div><p className="mt-1 text-[11px] text-muted-foreground tabular-nums">{unit.total} hồ sơ</p></TableCell></TableRow>; })}</TableBody></Table></div> : <EmptyView description="Chưa có đơn vị hoạt động trong kỳ này. Hãy kiểm tra lại phạm vi kỳ báo cáo." />}</section>

      <Dialog open={closeOpen} onOpenChange={setCloseOpen}><DialogContent><DialogHeader><DialogTitle>Đóng nộp kỳ báo cáo?</DialogTitle><DialogDescription>Sau khi đóng, các đơn vị không thể tiếp tục nộp hồ sơ vào kỳ này.</DialogDescription></DialogHeader><DialogFooter><Button type="button" variant="outline" onClick={() => setCloseOpen(false)}>Huỷ</Button><Button type="button" onClick={() => canDecide && void decide("close")} disabled={!canDecide || close.isPending}>Đóng nộp</Button></DialogFooter></DialogContent></Dialog>
      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}><DialogContent><DialogHeader><DialogTitle>Huỷ kỳ báo cáo?</DialogTitle><DialogDescription>Kỳ sẽ chuyển sang trạng thái Đã huỷ và không thể tiếp tục nhận hồ sơ.</DialogDescription></DialogHeader><DialogFooter><Button type="button" variant="outline" onClick={() => setCancelOpen(false)}>Quay lại</Button><Button type="button" variant="destructive" onClick={() => canDecide && void decide("cancel")} disabled={!canDecide || cancel.isPending}>Huỷ kỳ</Button></DialogFooter></DialogContent></Dialog>
    </>
  );
}

export default function PeriodDetailPage() {
  return <Suspense fallback={<LoadingView label="Đang tải tiến độ kỳ báo cáo…" />}><PeriodDetailContent /></Suspense>;
}
