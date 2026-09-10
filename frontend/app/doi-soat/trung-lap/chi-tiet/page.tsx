// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Bot, CheckCircle2, GitMerge, Pause, Rows3 } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useDecideDuplicate, useDuplicateGroup } from "@/lib/queries";
import type { DecideDupIn, DupGroupDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}

function formatDate(value: string | null) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "—";
}

function DuplicateDetailContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const queryClient = useQueryClient();
  const query = useDuplicateGroup(id);
  const decide = useDecideDuplicate(id ?? 0);
  const [survivorId, setSurvivorId] = useState<number | null>(null);
  const [fieldChoices, setFieldChoices] = useState<Record<string, number>>({});
  const [mergeOpen, setMergeOpen] = useState(false);
  const [keepOpen, setKeepOpen] = useState(false);
  const [reason, setReason] = useState("");

  if (id === null) return <><PageHeader title="Chi tiết nhóm nghi trùng" /><EmptyView title="Chưa chọn nhóm" description="Mở một nhóm từ hàng đợi nghi trùng để so sánh." action={<Link href="/doi-soat/trung-lap/" className="font-medium text-primary hover:underline">Đi đến hàng đợi</Link>} /></>;
  if (query.isLoading) return <><PageHeader title="Chi tiết nhóm nghi trùng" /><LoadingView /></>;
  if (query.isError) return <><PageHeader title="Chi tiết nhóm nghi trùng" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Chi tiết nhóm nghi trùng" /><EmptyView description="Nhóm này không còn tồn tại. Hãy quay lại hàng đợi." /></>;
  const detail = query.data;
  const selectedSurvivor = survivorId ?? detail.members[0]?.id ?? null;

  async function submitDecision(input: DecideDupIn) {
    try {
      await decide.mutateAsync(input);
      const nextState = input.decision === "merge" ? "DaGop" : input.decision === "keep" ? "GiuRieng" : "NghiTrung";
      queryClient.setQueryData<DupGroupDetail>(["duplicate-group", id], (current) => current ? { ...current, state: nextState, survivor_work_id: input.survivor_id ?? null, reason: input.reason ?? null, decided_at: new Date().toISOString() } : current);
      await queryClient.invalidateQueries({ queryKey: ["duplicate-groups"] });
      toast.success(input.decision === "merge" ? "Đã gộp các bản ghi." : input.decision === "keep" ? "Đã giữ riêng các bản ghi." : "Đã bỏ qua nhóm này.");
      setMergeOpen(false);
      setKeepOpen(false);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.detail : "Không thể lưu quyết định.");
    }
  }

  const mergeInput: DecideDupIn = {
    decision: "merge",
    survivor_id: selectedSurvivor ?? undefined,
    field_choices: selectedSurvivor === null ? {} : Object.fromEntries(detail.diff_fields.map((field) => [field, fieldChoices[field] ?? selectedSurvivor])),
  };

  return (
    <>
      <PageHeader title={`Nhóm nghi trùng #${detail.id}`} description={`Cơ sở phát hiện: ${detail.basis_label}`} action={<StatusBadge value={detail.state} />} />
      {detail.hint && <Alert className="mb-5 border-status-warning/30 bg-status-warning/10 text-status-warning"><AlertTriangle /><AlertTitle>Cảnh báo: {detail.hint}</AlertTitle><AlertDescription>Dấu hiệu này cho thấy các bản ghi có thể thuộc cùng một đồ án nhóm. Hãy ưu tiên kiểm tra trước khi gộp.</AlertDescription></Alert>}

      <section aria-labelledby="compare-records-title">
        <div className="mb-3 flex items-center gap-2"><Rows3 className="size-4 text-primary" /><h2 id="compare-records-title" className="text-base font-semibold">So sánh bản ghi</h2></div>
        <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead className="min-w-36">Trường</TableHead>{detail.members.map((member) => <TableHead key={member.id} className="min-w-64 whitespace-normal align-top"><Link href={`/cong-trinh/?id=${member.id}`} className="font-semibold text-primary hover:underline">{member.title ?? "Chưa có tiêu đề"}</Link><div className="mt-1 flex items-center gap-2 text-xs font-normal text-muted-foreground"><span className="tabular-nums">#{member.id}</span><StatusBadge value={member.state} /></div></TableHead>)}</TableRow></TableHeader><TableBody>{detail.compare_fields.map((field) => <TableRow key={field}><TableCell className="font-medium">{detail.field_labels[field] ?? field}</TableCell>{detail.members.map((member) => <TableCell key={member.id} className={cn("max-w-sm whitespace-normal", detail.diff_fields.includes(field) && "bg-status-warning/10 text-status-warning")}>{formatValue(member.fields[field])}</TableCell>)}</TableRow>)}</TableBody></Table></div>
      </section>

      {detail.ai_similarity && Object.keys(detail.ai_similarity).length > 0 && <section className="mt-6" aria-labelledby="ai-similarity-title"><div className="mb-3 flex items-center gap-2"><Bot className="size-4 text-primary" /><h2 id="ai-similarity-title" className="text-base font-semibold">Tương đồng AI</h2><Badge variant="outline" className="text-muted-foreground">gợi ý</Badge></div><div className="flex flex-wrap gap-2 rounded-lg border bg-card p-4">{Object.entries(detail.ai_similarity).map(([field, value]) => <div key={field} className="rounded-md bg-muted px-3 py-2"><span className="text-xs text-muted-foreground">{detail.field_labels[field] ?? field}: </span><strong className="tabular-nums">{typeof value === "number" && value >= 0 && value <= 1 ? `${Math.round(value * 100)}%` : formatValue(value)}</strong></div>)}</div><p className="mt-2 text-xs text-muted-foreground">Chỉ dùng để hỗ trợ rà soát; người dùng là người đưa ra quyết định.</p></section>}

      {detail.state !== "NghiTrung" ? <section className="mt-7 rounded-lg border bg-card p-5" aria-labelledby="decision-result-title"><div className="mb-4 flex items-center gap-2"><CheckCircle2 className="size-5 text-status-success" /><h2 id="decision-result-title" className="text-base font-semibold">Kết quả quyết định</h2></div><dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><div><dt className="text-xs text-muted-foreground">Trạng thái</dt><dd className="mt-1"><StatusBadge value={detail.state} /></dd></div><div><dt className="text-xs text-muted-foreground">Người quyết định</dt><dd className="mt-1 font-medium">{detail.decided_by ? `Mã #${detail.decided_by}` : "Không có thông tin"}</dd></div><div><dt className="text-xs text-muted-foreground">Thời điểm</dt><dd className="mt-1 font-medium tabular-nums">{formatDate(detail.decided_at)}</dd></div><div><dt className="text-xs text-muted-foreground">Bản sống sót</dt><dd className="mt-1 font-medium tabular-nums">{detail.survivor_work_id ? <Link href={`/cong-trinh/?id=${detail.survivor_work_id}`} className="text-primary hover:underline">Công trình #{detail.survivor_work_id}</Link> : "Không áp dụng"}</dd></div></dl>{detail.reason && <div className="mt-4 border-t pt-4"><p className="text-xs text-muted-foreground">Lý do</p><p className="mt-1">{detail.reason}</p></div>}<p className="mt-4 text-xs text-muted-foreground">Nhóm đã được quyết định nên biểu mẫu đã khoá.</p></section> : <section className="mt-7" aria-labelledby="decision-title"><div className="mb-3"><h2 id="decision-title" className="text-base font-semibold">Quyết định của người dùng</h2><p className="text-xs text-muted-foreground">Chọn bản sống sót và nguồn giá trị cho từng trường khác nhau trước khi gộp.</p></div><div className="grid gap-5 rounded-lg border bg-card p-5 lg:grid-cols-2"><fieldset><legend className="mb-3 font-medium">Bản ghi sống sót</legend><div className="space-y-2">{detail.members.map((member) => <label key={member.id} className="flex cursor-pointer items-start gap-2 rounded-md border p-3 hover:bg-muted/50"><input type="radio" name="survivor" value={member.id} checked={selectedSurvivor === member.id} onChange={() => setSurvivorId(member.id)} className="mt-0.5 accent-primary" /><span><span className="block font-medium">Công trình #{member.id}</span><span className="mt-0.5 block text-xs text-muted-foreground">{member.title ?? "Chưa có tiêu đề"}</span></span></label>)}</div></fieldset><fieldset><legend className="mb-3 font-medium">Giá trị cho trường khác nhau</legend>{detail.diff_fields.length ? <div className="space-y-3">{detail.diff_fields.map((field) => <div key={field}><label htmlFor={`field-${field}`} className="mb-1.5 block text-xs text-muted-foreground">{detail.field_labels[field] ?? field}</label><select id={`field-${field}`} value={fieldChoices[field] ?? selectedSurvivor ?? ""} onChange={(event) => setFieldChoices((current) => ({ ...current, [field]: Number(event.target.value) }))} className="h-9 w-full rounded-lg border border-input bg-background px-2.5 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/50">{detail.members.map((member) => <option key={member.id} value={member.id}>#{member.id} — {formatValue(member.fields[field])}</option>)}</select></div>)}</div> : <p className="text-sm text-muted-foreground">Không có trường khác nhau cần chọn lại.</p>}</fieldset></div><div className="mt-4 flex flex-wrap justify-end gap-2"><Button type="button" variant="ghost" onClick={() => submitDecision({ decision: "skip" })} disabled={decide.isPending}><Pause />Bỏ qua</Button><Button type="button" variant={detail.hint ? "default" : "outline"} onClick={() => setKeepOpen(true)} disabled={decide.isPending}><Rows3 />Giữ riêng</Button><Button type="button" variant={detail.hint ? "outline" : "default"} onClick={() => setMergeOpen(true)} disabled={decide.isPending || selectedSurvivor === null}><GitMerge />Gộp</Button></div></section>}

      <Dialog open={mergeOpen} onOpenChange={setMergeOpen}><DialogContent><DialogHeader><DialogTitle>Xác nhận gộp bản ghi</DialogTitle><DialogDescription>Thao tác gộp không thể hoàn tác. Công trình #{selectedSurvivor} sẽ là bản sống sót.</DialogDescription></DialogHeader><DialogFooter><Button type="button" variant="outline" onClick={() => setMergeOpen(false)}>Huỷ</Button><Button type="button" onClick={() => submitDecision(mergeInput)} disabled={decide.isPending}><GitMerge />Xác nhận gộp</Button></DialogFooter></DialogContent></Dialog>
      <Dialog open={keepOpen} onOpenChange={setKeepOpen}><DialogContent><form onSubmit={(event) => { event.preventDefault(); void submitDecision({ decision: "keep", reason: reason.trim() }); }}><DialogHeader><DialogTitle>Giữ riêng các bản ghi</DialogTitle><DialogDescription>Nhập lý do để giải thích vì sao các công trình không được gộp.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="keep-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="keep-reason" required value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Ví dụ: Đây là đồ án nhóm của các nhóm sinh viên khác nhau…" /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setKeepOpen(false)}>Huỷ</Button><Button type="submit" disabled={decide.isPending}>Giữ riêng</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}

export default function DuplicateDetailPage() {
  return <Suspense fallback={<LoadingView label="Đang tải nhóm nghi trùng…" />}><DuplicateDetailContent /></Suspense>;
}
