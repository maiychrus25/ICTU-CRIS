// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { BookMarked, BookOpen, Building2, Copy, Download, ExternalLink, FileText, Mail, TimerReset } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { PersonAvatar } from "@/components/person-avatar";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { WorkCitationDialog } from "@/components/work-citation-dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { docTypeLabels, getFieldValueLabel } from "@/lib/labels";
import { api, API_BASE, ApiError } from "@/lib/api";
import { usePerson } from "@/lib/queries";
import type { PersonPublication } from "@/lib/types";

function formatDate(value: string | null | undefined) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Chưa có";
}

function formatPersonName(name: string, rank?: string | null, degree?: string | null) {
  const rankValue = rank?.toLocaleLowerCase("vi-VN").replaceAll(".", "");
  const degreeValue = degree?.toLocaleLowerCase("vi-VN").replaceAll(".", "");
  const rankTitle = rankValue === "pgs" || rankValue?.includes("phó giáo sư") ? "PGS" : rankValue === "gs" || rankValue?.includes("giáo sư") ? "GS" : null;
  const degreeTitle = degreeValue === "ts" || degreeValue?.includes("tiến sĩ") ? "TS" : degreeValue === "ths" || degreeValue?.includes("thạc sĩ") ? "ThS" : null;
  const titles = [rankTitle, degreeTitle].filter(Boolean);
  return titles.length ? `${titles.join(".")}. ${name.replace(/^(?:(?:GS|PGS)\.)?(?:(?:TS|ThS)\.)?\s*/i, "")}` : name;
}

function formatCredential(value: string) {
  return { gs: "Giáo sư", pgs: "Phó giáo sư", ts: "Tiến sĩ", ths: "Thạc sĩ" }[value.toLocaleLowerCase("vi-VN").replaceAll(".", "")] ?? value;
}

function PersonContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const query = usePerson(id);
  const [citationWorkId, setCitationWorkId] = useState<number | null>(null);
  const [citationAction, setCitationAction] = useState<"bibtex" | "apa" | null>(null);
  const columns = useMemo<DataTableColumn<PersonPublication>[]>(() => [
    { accessorKey: "title", header: "Công trình", cell: ({ row }) => <div className="max-w-xl whitespace-normal"><Link href={`/cong-trinh/?id=${row.original.work_id}`} className="font-medium text-primary hover:underline">{row.original.title ?? "Chưa có tiêu đề"}</Link>{row.original.doi && <p className="mt-0.5 text-xs text-muted-foreground">DOI: {row.original.doi}</p>}</div> },
    { accessorKey: "doc_type", header: "Loại", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "year", header: "Năm", cell: ({ row }) => <span className="tabular-nums">{row.original.year ?? "—"}</span> },
    { accessorKey: "link_state", header: "Liên kết", cell: ({ row }) => <StatusBadge value={row.original.link_state} /> },
    { id: "citation", header: "Trích dẫn", enableSorting: false, cell: ({ row }) => <Button type="button" variant="ghost" size="sm" onClick={() => setCitationWorkId(row.original.work_id)}><BookMarked />Trích dẫn</Button> },
  ], []);

  if (id === null) return <><PageHeader title="Hồ sơ giảng viên" /><EmptyView title="Chưa chọn giảng viên" description="Mở tên một giảng viên từ công trình hoặc hàng đợi tác giả để xem hồ sơ." action={<Link href="/tra-cuu/" className="font-medium text-primary hover:underline">Đi đến tra cứu</Link>} /></>;
  if (query.isLoading) return <><PageHeader title="Hồ sơ giảng viên" /><LoadingView /></>;
  if (query.isError) return <><PageHeader title="Hồ sơ giảng viên" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Hồ sơ giảng viên" /><EmptyView description="Hồ sơ này không còn tồn tại. Hãy quay lại trang tra cứu." /></>;
  const person = query.data;
  const yearlyData = Object.entries(person.by_year).sort(([a], [b]) => Number(a) - Number(b)).map(([year, count]) => ({ year, count }));
  const credentials = [person.rank, person.degree].filter(Boolean).map((value) => formatCredential(value!)).join(" · ");
  const displayName = formatPersonName(person.display_name, person.rank, person.degree);
  const unitSource = person.unit_source === "auto" ? "Suy từ đa số công trình" : person.unit_source === "manual" ? "Do quản trị gán" : undefined;

  async function downloadBibtex() {
    setCitationAction("bibtex");
    try {
      const text = await api.getPersonCitation(person.id, "bibtex");
      const url = URL.createObjectURL(new Blob([text], { type: "application/x-bibtex;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url; link.download = `giang-vien-${person.id}.bib`; link.click(); URL.revokeObjectURL(url);
    } catch (error) { toast.error(error instanceof ApiError ? error.detail : "Không thể tải tệp BibTeX."); }
    finally { setCitationAction(null); }
  }

  async function copyApa() {
    setCitationAction("apa");
    try {
      await navigator.clipboard.writeText(await api.getPersonCitation(person.id, "apa"));
      toast.success("Đã sao chép APA cho tất cả công trình.");
    } catch (error) { toast.error(error instanceof ApiError ? error.detail : "Không thể sao chép APA."); }
    finally { setCitationAction(null); }
  }

  return (
    <>
      <PageHeader title="Hồ sơ giảng viên" description="Thông tin chuyên môn và các công trình đã liên kết trong ICTU-CRIS." />
      <section aria-labelledby="person-name" className="mb-6 rounded-lg border bg-card p-5">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start">
          <PersonAvatar name={displayName} src={person.avatar_url} />
          <div className="min-w-0 flex-1">
            <h2 id="person-name" className="text-xl font-semibold tracking-tight sm:text-2xl">{displayName}</h2>
            {person.position && <p className="mt-1 font-medium">{person.position}</p>}
            {credentials && <p className="mt-0.5 text-sm text-muted-foreground">{credentials}</p>}
            <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm">
              {person.unit && <span title={unitSource} className="inline-flex items-center gap-1.5"><Building2 className="size-3.5 text-muted-foreground" />Khoa: {person.unit.code} — {person.unit.name}</span>}
              {person.field && <span className="inline-flex items-center gap-1.5"><BookOpen className="size-3.5 text-muted-foreground" /><span className="text-muted-foreground">Lĩnh vực:</span> <span>{person.field}</span></span>}
              {person.orcid && <a href={person.orcid.startsWith("http") ? person.orcid : `https://orcid.org/${person.orcid}`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-primary hover:underline">ORCID {person.orcid}<ExternalLink className="size-3.5" /></a>}
              {person.scholar_url && <a href={person.scholar_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-primary hover:underline">Google Scholar<ExternalLink className="size-3.5" /></a>}
              {person.email && <a href={`mailto:${person.email}`} className="inline-flex items-center gap-1.5 text-primary hover:underline"><Mail className="size-3.5" />{person.email}</a>}
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <Link href={`/giang-vien/ly-lich/?id=${person.id}`} className={buttonVariants()}><FileText />Lý lịch khoa học</Link>
              <Button type="button" variant="outline" disabled={citationAction !== null} onClick={() => void downloadBibtex()}><Download />{citationAction === "bibtex" ? "Đang tải…" : "Tải BibTeX (tất cả)"}</Button>
              <Button type="button" variant="outline" disabled={citationAction !== null} onClick={() => void copyApa()}><Copy />{citationAction === "apa" ? "Đang sao chép…" : "Sao chép APA (tất cả)"}</Button>
              <a href={`${API_BASE}/api/persons/${person.id}/publications.csv`} title="Mở được bằng Excel (UTF-8)" className={buttonVariants({ variant: "outline" })}><Download />Tải CSV</a>
            </div>
          </div>
        </div>
      </section>
      {person.pending_count > 0 && <Alert className="mb-6 border-status-warning/30 bg-status-warning/10"><TimerReset /><AlertTitle>Có {person.pending_count} công trình đang chờ xác nhận liên kết</AlertTitle><AlertDescription><Link href="/doi-soat/tac-gia/">Mở hàng đợi tác giả để rà soát</Link></AlertDescription></Alert>}

      <section className="mb-7" aria-labelledby="type-stats-title"><h2 id="type-stats-title" className="mb-3 text-base font-semibold">Công trình theo loại</h2>{Object.keys(person.by_type).length ? <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{Object.entries(person.by_type).map(([type, count]) => <Card key={type} size="sm"><CardHeader><CardTitle className="text-xs font-medium text-muted-foreground">{docTypeLabels[type] ?? type}</CardTitle></CardHeader><CardContent><p className="text-2xl font-semibold text-primary tabular-nums">{count.toLocaleString("vi-VN")}</p></CardContent></Card>)}</div> : <EmptyView description="Chưa có số liệu công trình theo loại. Hãy chờ lần đồng bộ tiếp theo." />}</section>

      <section className="mb-7" aria-labelledby="year-chart-title"><div className="mb-3"><h2 id="year-chart-title" className="text-base font-semibold">Công trình theo năm</h2><p className="text-xs text-muted-foreground">Số công trình có liên kết với giảng viên theo năm công bố.</p></div>{yearlyData.length ? <div className="h-72 rounded-lg border bg-card p-4" role="img" aria-label="Biểu đồ cột số công trình theo năm"><ResponsiveContainer width="100%" height="100%"><BarChart data={yearlyData} margin={{ top: 8, right: 8, left: -18, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="year" tickLine={false} axisLine={false} /><YAxis allowDecimals={false} tickLine={false} axisLine={false} /><Tooltip cursor={{ fill: "var(--muted)" }} /><Bar dataKey="count" name="Công trình" fill="var(--primary)" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div> : <EmptyView description="Chưa có số liệu theo năm để vẽ biểu đồ." />}</section>

      <section aria-labelledby="publications-title"><div className="mb-3"><h2 id="publications-title" className="text-base font-semibold">Danh sách công trình</h2><p className="text-xs text-muted-foreground">Mở từng công trình để xem dữ liệu và xuất xứ.</p></div><DataTable columns={columns} data={person.publications} getRowId={(row) => String(row.work_id)} emptyMessage="Giảng viên chưa có công trình được liên kết. Hãy kiểm tra hàng đợi tác giả." /></section>
      {citationWorkId !== null && <WorkCitationDialog workId={citationWorkId} open onOpenChange={(open) => { if (!open) setCitationWorkId(null); }} />}
      <footer className="mt-7 border-t pt-4 text-xs text-muted-foreground">Dữ liệu đồng bộ lần cuối: <span className="tabular-nums">{formatDate(person.last_sync?.finished_at)}</span>{person.last_sync?.source ? ` · ${getFieldValueLabel("source", person.last_sync.source)}` : ""}</footer>
    </>
  );
}

export default function PersonPage() {
  return <Suspense fallback={<LoadingView label="Đang tải hồ sơ giảng viên…" />}><PersonContent /></Suspense>;
}
