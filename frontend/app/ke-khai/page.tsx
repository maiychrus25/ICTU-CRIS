// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Download, ExternalLink, FileCheck2, FileText, History, Image as ImageIcon, Link2, Plus, StickyNote } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { EvidenceDialog } from "@/components/evidence-dialog";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, evidenceFileUrl } from "@/lib/api";
import { getDeclarationActions, type DeclarationAction } from "@/lib/declarations";
import { stateLabels } from "@/lib/labels";
import { useDeclaration, useMe, useOfficerAccess, usePeriods, useSetDeclarationState } from "@/lib/queries";
import type { EvidenceOut } from "@/lib/types";
import { formatFileSize } from "@/lib/utils";

const evidenceLabels: Record<string, string> = { link: "Đường dẫn", file: "Tệp", note: "Ghi chú" };

function formatDate(value: string) {
  return new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function EvidenceIcon({ evidence }: { evidence: EvidenceOut }) {
  const Icon = evidence.kind === "link" ? Link2 : evidence.kind === "note" ? StickyNote : evidence.content_type?.startsWith("image/") ? ImageIcon : FileText;
  return <Icon aria-hidden className="size-4 shrink-0 text-muted-foreground" />;
}

function DeclarationDetailContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const queryClient = useQueryClient();
  const query = useDeclaration(id);
  const periods = usePeriods();
  const me = useMe();
  const setState = useSetDeclarationState();
  const canAddEvidence = useOfficerAccess();
  const [stateAction, setStateAction] = useState<DeclarationAction | null>(null);
  const [evidenceOpen, setEvidenceOpen] = useState(false);

  if (id === null) return <><PageHeader title="Chi tiết hồ sơ kê khai" /><EmptyView title="Chưa chọn hồ sơ" description="Mở một hồ sơ từ chi tiết kỳ báo cáo để xem thông tin." action={<Link href="/ky-bao-cao/" className="font-medium text-primary hover:underline">Đi đến danh sách kỳ</Link>} /></>;
  if (query.isLoading) return <><PageHeader title="Chi tiết hồ sơ kê khai" /><LoadingView label="Đang tải hồ sơ kê khai…" /></>;
  if (query.isError) return <><PageHeader title="Chi tiết hồ sơ kê khai" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Chi tiết hồ sơ kê khai" /><EmptyView description="Không tìm thấy hồ sơ kê khai này. Hãy quay lại kỳ báo cáo." /></>;

  const detail = query.data;
  const period = periods.data?.find((item) => item.id === detail.period_id);
  const actorName = (actorId: number | null) => actorId === null ? "Không có thông tin" : me.data?.user?.id === actorId ? me.data.user.display_name : `Người dùng #${actorId}`;
  const actions = getDeclarationActions(detail.state, me.data, detail.unit_code, period?.state);

  async function transition(action: DeclarationAction, reason?: string) {
    try {
      await setState.mutateAsync({ id: detail.id, input: { to_state: action.to, reason: reason?.trim() || null } });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["declaration", detail.id] }),
        queryClient.invalidateQueries({ queryKey: ["declarations", detail.period_id] }),
        queryClient.invalidateQueries({ queryKey: ["period-progress", detail.period_id] }),
      ]);
      toast.success(`Đã ${action.label.toLocaleLowerCase("vi")}.`);
      setStateAction(null);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể cập nhật trạng thái hồ sơ.");
    }
  }

  return (
    <>
      <PageHeader title={`Hồ sơ kê khai #${detail.id}`} description="Lịch sử trạng thái và minh chứng của công trình trong kỳ báo cáo." action={<StatusBadge value={detail.state} />} />
      {actions.length > 0 && <div className="mb-5 flex flex-wrap justify-end gap-2">{actions.map((action) => <Button key={action.to} type="button" variant={action.destructive ? "destructive" : "outline"} disabled={setState.isPending} onClick={() => action.reasonRequired ? setStateAction(action) : void transition(action)}>{action.label}</Button>)}</div>}
      <section aria-labelledby="declaration-info-title" className="rounded-lg border bg-card p-5">
        <div className="mb-4 flex items-center gap-2"><FileCheck2 className="size-5 text-primary" /><h2 id="declaration-info-title" className="text-base font-semibold">Thông tin hồ sơ</h2></div>
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2"><dt className="text-xs text-muted-foreground">Công trình</dt><dd className="mt-1"><Link href={`/cong-trinh/?id=${detail.work_id}`} className="font-medium text-primary hover:underline">{detail.work_title ?? `Công trình #${detail.work_id}`}</Link><p className="mt-1 text-xs text-muted-foreground">{detail.doc_type_label}</p></dd></div>
          <div><dt className="text-xs text-muted-foreground">Kỳ báo cáo</dt><dd className="mt-1"><Link href={`/ky-bao-cao/chi-tiet/?id=${detail.period_id}`} className="font-medium text-primary hover:underline">{period?.name ?? `Kỳ #${detail.period_id}`}</Link></dd></div>
          <div><dt className="text-xs text-muted-foreground">Đơn vị</dt><dd className="mt-1 font-medium">{detail.unit_code}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Trạng thái</dt><dd className="mt-1"><StatusBadge value={detail.state} /></dd></div>
          <div><dt className="text-xs text-muted-foreground">Ngày tạo</dt><dd className="mt-1 tabular-nums">{formatDate(detail.created_at)}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Cập nhật lần cuối</dt><dd className="mt-1 tabular-nums">{formatDate(detail.updated_at)}</dd></div>
          <div className="sm:col-span-2 lg:col-span-4"><dt className="text-xs text-muted-foreground">Ghi chú</dt><dd className="mt-1 whitespace-pre-wrap">{detail.note || "Không có ghi chú."}</dd></div>
        </dl>
      </section>

      <section aria-labelledby="declaration-events-title" className="mt-7">
        <div className="mb-4 flex items-center gap-2"><History className="size-5 text-primary" /><h2 id="declaration-events-title" className="text-base font-semibold">Dòng thời gian sự kiện</h2></div>
        {detail.events.length ? <ol className="ml-2 border-l border-border pl-6">{detail.events.map((event) => <li key={event.id} className="relative pb-6 last:pb-0"><span className="absolute -left-[29px] top-1.5 size-2.5 rounded-full bg-primary ring-4 ring-background" /><div className="flex flex-wrap items-center gap-2"><span className="font-medium">{event.from_state ? <>{stateLabels[event.from_state] ?? event.from_state}<ArrowRight className="mx-1 inline size-3.5" />{stateLabels[event.to_state] ?? event.to_state}</> : `Khởi tạo ở trạng thái ${stateLabels[event.to_state] ?? event.to_state}`}</span><Badge variant="outline" className="font-normal">{actorName(event.actor_id)}</Badge></div>{event.reason && <p className="mt-1.5 whitespace-pre-wrap text-sm">Lý do: {event.reason}</p>}<time className="mt-1 block text-xs text-muted-foreground tabular-nums">{formatDate(event.at)}</time></li>)}</ol> : <p className="rounded-lg border border-dashed p-5 text-sm text-muted-foreground">Chưa ghi nhận sự kiện nào cho hồ sơ này.</p>}
      </section>

      <section aria-labelledby="declaration-evidence-title" className="mt-7">
        <div className="mb-4 flex items-center justify-between gap-3"><div className="flex items-center gap-2"><FileCheck2 className="size-5 text-primary" /><h2 id="declaration-evidence-title" className="text-base font-semibold">Danh sách minh chứng</h2></div><Button type="button" size="sm" onClick={() => setEvidenceOpen(true)} disabled={!canAddEvidence}><Plus />Thêm minh chứng</Button></div>
        {detail.evidence.length ? <div className="overflow-x-auto rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Loại</TableHead><TableHead>Minh chứng</TableHead><TableHead>Kích thước</TableHead><TableHead>SHA-256</TableHead><TableHead>Ghi chú</TableHead><TableHead>Người thêm</TableHead><TableHead>Thời điểm</TableHead><TableHead><span className="sr-only">Tải tệp</span></TableHead></TableRow></TableHeader><TableBody>{detail.evidence.map((evidence) => <TableRow key={evidence.id}><TableCell><span className="inline-flex items-center gap-2"><EvidenceIcon evidence={evidence} />{evidenceLabels[evidence.kind] ?? evidence.kind}</span></TableCell><TableCell>{evidence.url ? <a href={evidence.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-medium text-primary hover:underline">{evidence.file_name || evidence.url}<ExternalLink className="size-3.5" /></a> : evidence.file_name || (evidence.kind === "note" ? "Ghi chú" : "—")}</TableCell><TableCell className="whitespace-nowrap tabular-nums">{formatFileSize(evidence.size_bytes)}</TableCell><TableCell>{evidence.sha256 ? <code title={evidence.sha256} className="rounded bg-muted px-1.5 py-1 font-mono text-xs">{evidence.sha256.slice(0, 12)}</code> : "—"}</TableCell><TableCell className="max-w-sm whitespace-normal">{evidence.note || "—"}</TableCell><TableCell>{actorName(evidence.added_by)}</TableCell><TableCell className="whitespace-nowrap text-muted-foreground tabular-nums">{formatDate(evidence.added_at)}</TableCell><TableCell>{evidence.kind === "file" && <Button render={<a href={evidenceFileUrl(evidence.id)} target="_blank" rel="noreferrer" />} variant="outline" size="xs"><Download />Tải về</Button>}</TableCell></TableRow>)}</TableBody></Table></div> : <div className="rounded-lg border border-dashed p-6 text-center"><p className="font-medium">Chưa có minh chứng</p><p className="mt-1 text-sm text-muted-foreground">Chọn “Thêm minh chứng” để gắn đường dẫn, ghi chú hoặc tải tệp lên.</p></div>}
      </section>
      <EvidenceDialog declarationId={detail.id} open={evidenceOpen} onOpenChange={setEvidenceOpen} onSaved={async () => { await Promise.all([queryClient.invalidateQueries({ queryKey: ["declaration", detail.id] }), queryClient.invalidateQueries({ queryKey: ["declarations", detail.period_id] })]); }} />
      <Dialog open={stateAction !== null} onOpenChange={(open) => { if (!open) setStateAction(null); }}><DialogContent><form onSubmit={(event) => { event.preventDefault(); if (stateAction) void transition(stateAction, String(new FormData(event.currentTarget).get("reason"))); }}><DialogHeader><DialogTitle>{stateAction?.label} hồ sơ?</DialogTitle><DialogDescription>Nêu rõ lý do để quyết định có thể được kiểm tra lại trong dòng thời gian và nhật ký.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="detail-declaration-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="detail-declaration-reason" name="reason" required /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setStateAction(null)}>Huỷ</Button><Button type="submit" variant={stateAction?.destructive ? "destructive" : "default"} disabled={setState.isPending}>{stateAction?.label}</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}

export default function DeclarationDetailPage() {
  return <Suspense fallback={<LoadingView label="Đang tải hồ sơ kê khai…" />}><DeclarationDetailContent /></Suspense>;
}
