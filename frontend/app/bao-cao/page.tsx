// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Download, Printer } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { reportExportUrl } from "@/lib/api";
import { docTypeLabels, stateLabels } from "@/lib/labels";
import { usePeriods, useReport } from "@/lib/queries";

const stateOrder = ["Nhap", "ChoBoSung", "ChoKhoaDuyet", "KhoaDaDuyet", "ChoPhongKiemTra", "DatYeuCau", "DaChot", "Rut"];

function formatDate(value: string) {
  return new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function ReportContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const report = useReport(id);
  const periods = usePeriods();
  const [query, setQuery] = useState("");
  const [unit, setUnit] = useState("all");
  const data = report.data;
  const items = useMemo(() => data?.items.filter((item) => {
    const text = ((item.work.title ?? "") + " " + item.authors.join(" ")).toLocaleLowerCase("vi");
    return (!query.trim() || text.includes(query.trim().toLocaleLowerCase("vi"))) && (unit === "all" || item.unit.code === unit);
  }) ?? [], [data, query, unit]);

  if (id === null) return <><PageHeader title="Báo cáo đóng băng" /><EmptyView title="Chưa chọn báo cáo" description="Mở một phiên bản từ chi tiết kỳ báo cáo để xem số liệu." /></>;
  if (report.isLoading || periods.isLoading) return <><PageHeader title="Báo cáo đóng băng" /><LoadingView label="Đang tải bản báo cáo…" /></>;
  if (report.isError) return <><PageHeader title="Báo cáo đóng băng" /><ErrorView error={report.error} retry={() => report.refetch()} /></>;
  if (periods.isError) return <><PageHeader title="Báo cáo đóng băng" /><ErrorView error={periods.error} retry={() => periods.refetch()} /></>;
  if (!data) return <><PageHeader title="Báo cáo đóng băng" /><EmptyView description="Không tìm thấy bản báo cáo này. Hãy mở lại từ chi tiết kỳ báo cáo." /></>;

  const period = periods.data?.find((item) => item.id === data.period_id);
  const stateKeys = stateOrder.filter((state) => data.summary.units.some((item) => (item.by_state[state] ?? 0) > 0));
  const description = "Phiên bản v" + data.version + " · đóng băng lúc " + formatDate(data.generated_at);
  return <>
    <PageHeader title={period?.name ?? "Báo cáo kỳ #" + data.period_id} description={description} action={<div className="flex flex-wrap gap-2 print:hidden"><Button render={<a href={reportExportUrl(data.id, "csv")} />} variant="outline"><Download />CSV</Button><Button render={<a href={reportExportUrl(data.id, "xlsx")} />} variant="outline"><Download />XLSX</Button><Button type="button" variant="outline" onClick={() => window.print()}><Printer />In</Button></div>} />
    <TooltipProvider><Tooltip><TooltipTrigger render={<Badge variant="outline" className="mb-6 font-mono" />}>Đóng băng · SHA-256 {data.sha256.slice(0, 8)}…</TooltipTrigger><TooltipContent>Nội dung không thể thay đổi; băm để đối chiếu</TooltipContent></Tooltip></TooltipProvider>
    {data.note && <p className="mb-6 border-l-2 border-primary pl-3 text-sm text-muted-foreground">{data.note}</p>}

    <section className="mb-7" aria-labelledby="unit-summary-title"><h2 id="unit-summary-title" className="mb-3 text-base font-semibold">Tổng hợp theo đơn vị</h2>{data.summary.units.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Đơn vị</TableHead><TableHead className="text-right">Tổng hồ sơ</TableHead>{stateKeys.map((state) => <TableHead key={state} className={"text-right " + (["DatYeuCau", "DaChot"].includes(state) ? "font-bold" : "")}>{stateLabels[state] ?? state}</TableHead>)}</TableRow></TableHeader><TableBody>{data.summary.units.map((item) => <TableRow key={item.unit_id}><TableCell><span className="font-medium">{item.name}</span><span className="ml-2 text-xs text-muted-foreground">{item.code}</span></TableCell><TableCell className="text-right tabular-nums">{item.declared}</TableCell>{stateKeys.map((state) => <TableCell key={state} className={"text-right tabular-nums " + (["DatYeuCau", "DaChot"].includes(state) ? "font-bold" : "")}>{item.by_state[state] ?? 0}</TableCell>)}</TableRow>)}</TableBody></Table></div> : <EmptyView description="Bản báo cáo không có dữ liệu đơn vị." />}</section>

    <section className="mb-7" aria-labelledby="doc-type-summary-title"><h2 id="doc-type-summary-title" className="mb-3 text-base font-semibold">Theo loại tài liệu</h2>{Object.keys(data.summary.by_doc_type).length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Loại tài liệu</TableHead><TableHead className="text-right">Số hồ sơ</TableHead></TableRow></TableHeader><TableBody>{Object.entries(data.summary.by_doc_type).map(([type, count]) => <TableRow key={type}><TableCell>{docTypeLabels[type] ?? type}</TableCell><TableCell className="text-right font-semibold tabular-nums">{count.toLocaleString("vi-VN")}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Bản báo cáo không có thống kê loại tài liệu." />}</section>

    <section aria-labelledby="report-items-title"><div className="mb-3 flex flex-col justify-between gap-3 sm:flex-row sm:items-end"><div><h2 id="report-items-title" className="text-base font-semibold">Chi tiết hồ sơ</h2><p className="text-xs text-muted-foreground tabular-nums">{items.length.toLocaleString("vi-VN")} / {data.items.length.toLocaleString("vi-VN")} hồ sơ</p></div><div className="flex flex-col gap-2 sm:flex-row"><Input value={query} onChange={(event) => setQuery(event.target.value)} aria-label="Tìm nhanh hồ sơ" placeholder="Tìm tiêu đề hoặc tác giả…" className="sm:w-72" /><Select value={unit} onValueChange={(value) => setUnit(String(value))}><SelectTrigger aria-label="Lọc đơn vị" className="sm:w-52"><SelectValue>{(value) => value === "all" ? "Tất cả đơn vị" : value}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả đơn vị</SelectItem>{data.summary.units.map((item) => <SelectItem key={item.unit_id} value={item.code}>{item.code} — {item.name}</SelectItem>)}</SelectContent></Select></div></div>{items.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Hồ sơ</TableHead><TableHead className="min-w-80">Công trình</TableHead><TableHead>Tác giả</TableHead><TableHead>Đơn vị</TableHead><TableHead>Trạng thái</TableHead><TableHead className="text-right">Minh chứng</TableHead></TableRow></TableHeader><TableBody>{items.map((item) => <TableRow key={item.declaration_id}><TableCell className="font-medium tabular-nums">#{item.declaration_id}</TableCell><TableCell className="whitespace-normal"><span className="font-medium">{item.work.title ?? "Công trình #" + item.work.id}</span><span className="mt-0.5 block text-xs text-muted-foreground">{docTypeLabels[item.work.doc_type] ?? item.work.doc_type} · {item.work.year ?? "Chưa rõ năm"}{item.work.quartile ? " · " + item.work.quartile : ""}{item.work.indexes.length ? " · " + item.work.indexes.join(", ") : ""}</span></TableCell><TableCell className="max-w-xs whitespace-normal">{item.authors.join(", ") || "—"}</TableCell><TableCell>{item.unit.code}</TableCell><TableCell>{stateLabels[item.state] ?? item.state}</TableCell><TableCell className="text-right tabular-nums">{item.evidence_count}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView title="Không có hồ sơ phù hợp" description="Đổi từ khoá hoặc bộ lọc đơn vị để xem hồ sơ khác." />}</section>
  </>;
}

export default function ReportPage() {
  return <Suspense fallback={<LoadingView label="Đang tải bản báo cáo…" />}><ReportContent /></Suspense>;
}
