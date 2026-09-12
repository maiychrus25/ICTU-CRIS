// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { AlertCircle, CircleAlert, Info, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { Pager } from "@/components/pager";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useDismissQualityAnomaly, useOfficerAccess, useQualityAnomalies } from "@/lib/queries";
import type { QualityAnomaly } from "@/lib/types";
import { cn } from "@/lib/utils";

const kinds = [
  ["scopus_no_doi", "Scopus/ISI thiếu DOI"],
  ["year_out_of_range", "Năm ngoài khoảng"],
  ["thesis_title_equals_article", "Trùng tiêu đề bài báo"],
  ["orcid_duplicate", "Trùng ORCID"],
  ["doi_invalid", "DOI sai định dạng"],
  ["missing_abstract_article", "Bài báo thiếu tóm tắt"],
] as const;
const severityLabels = { cao: "Cao", vua: "Vừa", thap: "Thấp" } as const;
const severityStyles = { cao: "border-status-danger/30 bg-status-danger/10 text-status-danger", vua: "border-status-warning/30 bg-status-warning/10 text-status-warning", thap: "border-status-success/30 bg-status-success/10 text-status-success" } as const;
const severityIcons = { cao: AlertCircle, vua: CircleAlert, thap: Info } as const;

function Detail({ item }: { item: QualityAnomaly }) {
  if (item.kind === "scopus_no_doi") return <>Chỉ mục Scopus/ISI nhưng chưa có DOI.</>;
  if (item.kind === "year_out_of_range") return <>Năm: {String(item.detail.year ?? "không hợp lệ")}</>;
  if (item.kind === "thesis_title_equals_article") return <>Trùng với <Link href={`/cong-trinh/?id=${String(item.detail.article_id)}`} className="font-medium text-primary hover:underline">bài báo #{String(item.detail.article_id)}</Link>.</>;
  if (item.kind === "orcid_duplicate") return <>Trùng với <Link href={`/giang-vien/?id=${String(item.detail.other_person_id)}`} className="font-medium text-primary hover:underline">giảng viên #{String(item.detail.other_person_id)}</Link>.</>;
  if (item.kind === "doi_invalid") return <>DOI: {String(item.detail.doi ?? "không đúng định dạng 10.xxxx/…")}</>;
  if (item.kind === "missing_abstract_article") return <>Trường tóm tắt đang để trống.</>;
  return <>{Object.entries(item.detail).map(([key, value]) => `${key}: ${String(value)}`).join(" · ") || item.kind_label}</>;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium" }).format(new Date(value));
}

export default function QualityAnomaliesPage() {
  const [kind, setKind] = useState("");
  const [severity, setSeverity] = useState("");
  const [state, setState] = useState("open");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<QualityAnomaly | null>(null);
  const query = useQualityAnomalies({ kind: kind || undefined, severity: severity || undefined, state, page });
  const dismiss = useDismissQualityAnomaly();
  const canDismiss = useOfficerAccess();
  const queryClient = useQueryClient();

  async function submitDismiss(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || !canDismiss) return;
    const reason = String(new FormData(event.currentTarget).get("reason")).trim();
    try {
      await dismiss.mutateAsync({ id: selected.id, input: { reason } });
      await Promise.all([queryClient.invalidateQueries({ queryKey: ["quality-anomalies"] }), queryClient.invalidateQueries({ queryKey: ["quality"] })]);
      toast.success("Đã bỏ qua cảnh báo và lưu lý do.");
      setSelected(null);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể bỏ qua cảnh báo.");
    }
  }

  return (
    <>
      <PageHeader title="Cảnh báo bất thường" description="Rà soát các điểm dữ liệu cần chú ý; chỉ người dùng có thẩm quyền mới quyết định bỏ qua." />
      <nav aria-label="Các mục chất lượng dữ liệu" className="mb-6 flex gap-1 border-b"><Link href="/chat-luong-du-lieu/" className="px-3 py-2 text-muted-foreground hover:text-foreground">Tổng quan</Link><Link href="/chat-luong-du-lieu/canh-bao/" aria-current="page" className="inline-flex items-center gap-1.5 border-b-2 border-primary px-3 py-2 font-medium text-primary"><ShieldAlert className="size-4" />Cảnh báo</Link></nav>

      {query.data && <section aria-label="Tóm tắt cảnh báo theo loại" className="mb-5 flex flex-wrap gap-2"><Button type="button" size="sm" variant={kind === "" ? "default" : "outline"} onClick={() => { setKind(""); setPage(1); }}>Tất cả <span className="tabular-nums">{Object.values(query.data.summary).reduce((sum, value) => sum + value.open, 0)}</span></Button>{kinds.map(([value, label]) => <Button key={value} type="button" size="sm" variant={kind === value ? "default" : "outline"} onClick={() => { setKind(value); setPage(1); }}>{label} <span className="tabular-nums">{query.data.summary[value]?.open ?? 0}</span></Button>)}</section>}

      <section aria-label="Bộ lọc cảnh báo" className="mb-4 flex flex-wrap gap-3 rounded-lg border bg-card p-3">
        <label className="grid gap-1 text-xs text-muted-foreground">Mức độ<select aria-label="Mức độ" value={severity} onChange={(event) => { setSeverity(event.target.value); setPage(1); }} className="h-9 min-w-40 rounded-md border bg-background px-3 text-sm text-foreground"><option value="">Tất cả mức độ</option><option value="cao">Cao</option><option value="vua">Vừa</option><option value="thap">Thấp</option></select></label>
        <label className="grid gap-1 text-xs text-muted-foreground">Trạng thái<select aria-label="Trạng thái" value={state} onChange={(event) => { setState(event.target.value); setPage(1); }} className="h-9 min-w-40 rounded-md border bg-background px-3 text-sm text-foreground"><option value="open">Đang mở</option><option value="dismissed">Đã bỏ qua</option><option value="resolved">Đã khắc phục</option></select></label>
      </section>

      {query.isLoading ? <LoadingView label="Đang tải cảnh báo bất thường…" /> : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} /> : query.data?.items.length ? <div className="overflow-hidden rounded-lg border bg-card"><div className="overflow-x-auto"><Table><TableHeader><TableRow><TableHead>Loại</TableHead><TableHead>Mức</TableHead><TableHead>Công trình hoặc giảng viên</TableHead><TableHead>Chi tiết</TableHead><TableHead>Ngày</TableHead><TableHead className="text-right">Thao tác</TableHead></TableRow></TableHeader><TableBody>{query.data.items.map((item) => { const Icon = severityIcons[item.severity]; return <TableRow key={item.id}><TableCell className="max-w-48 whitespace-normal font-medium">{item.kind_label}</TableCell><TableCell><Badge variant="outline" className={cn(severityStyles[item.severity])}><Icon />{severityLabels[item.severity]}</Badge></TableCell><TableCell className="max-w-72 whitespace-normal">{item.work_id ? <Link href={`/cong-trinh/?id=${item.work_id}`} className="font-medium text-primary hover:underline">{item.title ?? `Công trình #${item.work_id}`}</Link> : item.person_id ? <Link href={`/giang-vien/?id=${item.person_id}`} className="font-medium text-primary hover:underline">{item.display_name ?? `Giảng viên #${item.person_id}`}</Link> : "—"}</TableCell><TableCell className="max-w-56 whitespace-normal text-muted-foreground"><Detail item={item} /></TableCell><TableCell className="whitespace-nowrap text-xs tabular-nums">{formatDate(item.created_at)}</TableCell><TableCell className="text-right">{item.state === "open" ? <Button type="button" variant="outline" size="sm" disabled={!canDismiss} title={!canDismiss ? "Cần vai trò Chuyên viên KHCN" : undefined} onClick={() => setSelected(item)}>Bỏ qua</Button> : <Badge variant="secondary">{item.state === "dismissed" ? "Đã bỏ qua" : "Đã khắc phục"}</Badge>}</TableCell></TableRow>; })}</TableBody></Table></div><Pager page={query.data.page.page} perPage={query.data.page.per_page} total={query.data.page.total} onPageChange={setPage} /></div> : <EmptyView title="Không có cảnh báo" description="Không có cảnh báo — chạy `python -m cris quality scan` để quét lại dữ liệu." />}

      <Dialog open={selected !== null} onOpenChange={(open) => { if (!open) setSelected(null); }}><DialogContent><form onSubmit={(event) => void submitDismiss(event)}><DialogHeader><DialogTitle>Bỏ qua cảnh báo</DialogTitle><DialogDescription>Cảnh báo sẽ được chuyển sang “Đã bỏ qua”. Lý do được lưu vào nhật ký để đối chiếu.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="dismiss-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="dismiss-reason" name="reason" required minLength={3} placeholder="Nêu căn cứ đã kiểm tra…" /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setSelected(null)}>Huỷ</Button><Button type="submit" disabled={dismiss.isPending}>{dismiss.isPending ? "Đang lưu…" : "Bỏ qua"}</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}
