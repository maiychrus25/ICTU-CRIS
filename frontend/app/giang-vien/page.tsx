// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { ExternalLink, Mail, TimerReset } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { docTypeLabels } from "@/lib/labels";
import { usePerson } from "@/lib/queries";
import type { PersonPublication } from "@/lib/types";

function formatDate(value: string | null | undefined) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Chưa có";
}

function PersonContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const query = usePerson(id);
  const columns = useMemo<DataTableColumn<PersonPublication>[]>(() => [
    { accessorKey: "title", header: "Công trình", cell: ({ row }) => <div className="max-w-xl whitespace-normal"><Link href={`/cong-trinh/?id=${row.original.work_id}`} className="font-medium text-primary hover:underline">{row.original.title ?? "Chưa có tiêu đề"}</Link>{row.original.doi && <p className="mt-0.5 text-xs text-muted-foreground">DOI: {row.original.doi}</p>}</div> },
    { accessorKey: "doc_type", header: "Loại", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "year", header: "Năm", cell: ({ row }) => <span className="tabular-nums">{row.original.year ?? "—"}</span> },
    { accessorKey: "link_state", header: "Liên kết", cell: ({ row }) => <StatusBadge value={row.original.link_state} /> },
  ], []);

  if (id === null) return <><PageHeader title="Hồ sơ giảng viên" /><EmptyView title="Chưa chọn giảng viên" description="Mở tên một giảng viên từ công trình hoặc hàng đợi tác giả để xem hồ sơ." action={<Link href="/tra-cuu/" className="font-medium text-primary hover:underline">Đi đến tra cứu</Link>} /></>;
  if (query.isLoading) return <><PageHeader title="Hồ sơ giảng viên" /><LoadingView /></>;
  if (query.isError) return <><PageHeader title="Hồ sơ giảng viên" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Hồ sơ giảng viên" /><EmptyView description="Hồ sơ này không còn tồn tại. Hãy quay lại trang tra cứu." /></>;
  const person = query.data;
  const yearlyData = Object.entries(person.by_year).sort(([a], [b]) => Number(a) - Number(b)).map(([year, count]) => ({ year, count }));

  return (
    <>
      <PageHeader title={person.display_name} description={person.degree ?? "Giảng viên"} />
      <div className="mb-6 flex flex-wrap gap-x-5 gap-y-2 text-sm">{person.orcid && <a href={person.orcid.startsWith("http") ? person.orcid : `https://orcid.org/${person.orcid}`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-primary hover:underline">ORCID {person.orcid}<ExternalLink className="size-3.5" /></a>}{person.email && <a href={`mailto:${person.email}`} className="inline-flex items-center gap-1.5 text-primary hover:underline"><Mail className="size-3.5" />{person.email}</a>}</div>
      {person.pending_count > 0 && <Alert className="mb-6 border-status-warning/30 bg-status-warning/10"><TimerReset /><AlertTitle>Có {person.pending_count} công trình đang chờ xác nhận liên kết</AlertTitle><AlertDescription><Link href="/doi-soat/tac-gia/">Mở hàng đợi tác giả để rà soát</Link></AlertDescription></Alert>}

      <section className="mb-7" aria-labelledby="type-stats-title"><h2 id="type-stats-title" className="mb-3 text-base font-semibold">Công trình theo loại</h2>{Object.keys(person.by_type).length ? <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{Object.entries(person.by_type).map(([type, count]) => <Card key={type} size="sm"><CardHeader><CardTitle className="text-xs font-medium text-muted-foreground">{docTypeLabels[type] ?? type}</CardTitle></CardHeader><CardContent><p className="text-2xl font-semibold text-primary tabular-nums">{count.toLocaleString("vi-VN")}</p></CardContent></Card>)}</div> : <EmptyView description="Chưa có số liệu công trình theo loại. Hãy chờ lần đồng bộ tiếp theo." />}</section>

      <section className="mb-7" aria-labelledby="year-chart-title"><div className="mb-3"><h2 id="year-chart-title" className="text-base font-semibold">Công trình theo năm</h2><p className="text-xs text-muted-foreground">Số công trình có liên kết với giảng viên theo năm công bố.</p></div>{yearlyData.length ? <div className="h-72 rounded-lg border bg-card p-4" role="img" aria-label="Biểu đồ cột số công trình theo năm"><ResponsiveContainer width="100%" height="100%"><BarChart data={yearlyData} margin={{ top: 8, right: 8, left: -18, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="year" tickLine={false} axisLine={false} /><YAxis allowDecimals={false} tickLine={false} axisLine={false} /><Tooltip cursor={{ fill: "var(--muted)" }} /><Bar dataKey="count" name="Công trình" fill="var(--primary)" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div> : <EmptyView description="Chưa có số liệu theo năm để vẽ biểu đồ." />}</section>

      <section aria-labelledby="publications-title"><div className="mb-3"><h2 id="publications-title" className="text-base font-semibold">Danh sách công trình</h2><p className="text-xs text-muted-foreground">Mở từng công trình để xem dữ liệu và xuất xứ.</p></div><DataTable columns={columns} data={person.publications} getRowId={(row) => String(row.work_id)} emptyMessage="Giảng viên chưa có công trình được liên kết. Hãy kiểm tra hàng đợi tác giả." /></section>
      <footer className="mt-7 border-t pt-4 text-xs text-muted-foreground">Dữ liệu đồng bộ lần cuối: <span className="tabular-nums">{formatDate(person.last_sync?.finished_at)}</span>{person.last_sync?.source ? ` · ${person.last_sync.source}` : ""}</footer>
    </>
  );
}

export default function PersonPage() {
  return <Suspense fallback={<LoadingView label="Đang tải hồ sơ giảng viên…" />}><PersonContent /></Suspense>;
}
