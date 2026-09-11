// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Download, Search, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { API_BASE, ApiError } from "@/lib/api";
import { docTypeLabels } from "@/lib/labels";
import { useStats, useTopics, useWorkFacets, useWorks } from "@/lib/queries";
import type { FacetOption, WorkFilters, WorkSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

const empty = "all";

function FacetSelect({ label, value, options, onChange }: { label: string; value: string; options: FacetOption[]; onChange: (value: string) => void }) {
  return <div><label className="mb-1 block text-xs font-medium">{label}</label><Select value={value} onValueChange={(next) => onChange(String(next))}><SelectTrigger aria-label={label} className="w-full"><SelectValue>{(selected) => selected === empty ? "Tất cả" : options.find((item) => item.value === selected)?.label}</SelectValue></SelectTrigger><SelectContent><SelectItem value={empty}>Tất cả</SelectItem>{options.map((item) => <SelectItem key={item.value} value={item.value}>{item.label} ({item.n})</SelectItem>)}</SelectContent></Select></div>;
}

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialMode = searchParams.get("mode") === "semantic" ? "semantic" : "keyword";
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [mode, setMode] = useState<"keyword" | "semantic">(initialMode);
  const [docType, setDocType] = useState(searchParams.get("doc_type") ?? empty);
  const [year, setYear] = useState(searchParams.get("year") ?? empty);
  const [unit, setUnit] = useState(searchParams.get("unit") ?? empty);
  const [topic, setTopic] = useState(searchParams.get("topic") ?? empty);
  const [pubType, setPubType] = useState(searchParams.get("pub_type") ?? empty);
  const [quartile, setQuartile] = useState(searchParams.get("quartile") ?? empty);
  const [cohort, setCohort] = useState(searchParams.get("cohort") ?? empty);
  const [advancedOpen, setAdvancedOpen] = useState(Boolean(searchParams.get("pub_type") || searchParams.get("quartile") || searchParams.get("cohort")));
  const [filters, setFilters] = useState<WorkFilters>({
    q: searchParams.get("q") || undefined, mode: initialMode, doc_type: searchParams.get("doc_type") || undefined,
    year: Number(searchParams.get("year")) || undefined, unit: searchParams.get("unit") || undefined,
    topic: Number(searchParams.get("topic")) || undefined, pub_type: searchParams.get("pub_type") || undefined,
    quartile: searchParams.get("quartile") || undefined, cohort: searchParams.get("cohort") || undefined,
    keyword: searchParams.get("keyword") || undefined, page: 1,
  });
  const works = useWorks(filters);
  const topics = useTopics();
  const stats = useStats();
  const facets = useWorkFacets(advancedOpen);
  const auxiliaryError = topics.error ?? stats.error ?? (advancedOpen ? facets.error : null);
  const yearOptions = facets.data?.years ?? stats.data?.by_year_type.map((row) => ({ value: String(row.year), label: String(row.year), n: Object.entries(row).reduce((total, [key, value]) => key === "year" ? total : total + value, 0) })) ?? [];
  const unitOptions = facets.data?.units ?? stats.data?.by_unit.map((item) => ({ value: String(item.unit_id), label: `${item.code} — ${item.name}`, n: item.works })) ?? [];
  const semantic = filters.mode === "semantic";
  const csvQuery = new URLSearchParams(Object.entries(filters).filter(([key, value]) => key !== "page" && value !== undefined && value !== "").map(([key, value]) => [key, String(value)]));
  const csvUrl = `${API_BASE}/api/works.csv${csvQuery.size ? `?${csvQuery}` : ""}`;
  const columns = useMemo<DataTableColumn<WorkSummary>[]>(() => [
    { accessorKey: "title", header: "Công trình", cell: ({ row }) => <div className="max-w-xl whitespace-normal"><Link href={`/cong-trinh/?id=${row.original.id}`} className="font-medium text-primary hover:underline">{row.original.title ?? "Chưa có tiêu đề"}</Link>{row.original.doi && <div className="mt-0.5 text-xs text-muted-foreground">DOI: {row.original.doi}</div>}<div className="mt-1.5 flex flex-wrap gap-1">{row.original.keywords?.slice(0, 3).map((keyword) => <Link key={keyword} href={`/tra-cuu/?keyword=${encodeURIComponent(keyword)}`}><Badge variant="outline" className="font-normal hover:border-primary hover:text-primary">{keyword}</Badge></Link>)}</div></div> },
    ...(semantic ? [{ id: "score", header: "Độ gần", cell: ({ row }: { row: { original: WorkSummary } }) => <div className="w-24"><div className="h-1.5 overflow-hidden rounded-full bg-muted" role="progressbar" aria-label={`Độ gần ${Math.round((row.original.score ?? 0) * 100)} phần trăm`} aria-valuenow={Math.round((row.original.score ?? 0) * 100)} aria-valuemin={0} aria-valuemax={100}><div className="h-full rounded-full bg-primary" style={{ width: `${Math.round((row.original.score ?? 0) * 100)}%` }} /></div><span className="mt-1 block text-xs tabular-nums text-muted-foreground">{(row.original.score ?? 0).toFixed(2)}</span></div> }] : []),
    { accessorKey: "doc_type_label", header: "Loại", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "year", header: "Năm", cell: ({ row }) => <span className="tabular-nums">{row.original.year ?? "—"}</span> },
    { accessorKey: "state", header: "Trạng thái", cell: ({ row }) => <StatusBadge value={row.original.state} /> },
  ], [semantic]);

  function apply(nextMode = mode, reset = false, syncUrl = false) {
    const next: WorkFilters = reset ? { mode: nextMode, page: 1 } : {
      q: query.trim() || undefined, mode: nextMode, doc_type: docType === empty ? undefined : docType,
      year: year === empty ? undefined : Number(year), unit: unit === empty ? undefined : unit,
      topic: topic === empty ? undefined : Number(topic), pub_type: pubType === empty ? undefined : pubType,
      quartile: quartile === empty ? undefined : quartile, cohort: cohort === empty ? undefined : cohort, page: 1,
    };
    setFilters(next);
    const params = new URLSearchParams(Object.entries(next).filter(([key, value]) => key !== "page" && value !== undefined && !(key === "mode" && value === "keyword")).map(([key, value]) => [key, String(value)]));
    if (syncUrl) router.replace(`/tra-cuu/${params.size ? `?${params}` : ""}`);
  }

  function clearFilters() {
    setQuery(""); setDocType(empty); setYear(empty); setUnit(empty); setTopic(empty); setPubType(empty); setQuartile(empty); setCohort(empty);
    apply(mode, true, true);
  }

  return <>
    <PageHeader title="Tra cứu công trình" description="Tìm từ một nguồn dữ liệu thống nhất và truy ngược từng kết quả về bản ghi gốc." action={<Button render={<a href={csvUrl} title="Mở được bằng Excel (UTF-8)" />} variant="outline"><Download />Tải CSV</Button>} />
    <form onSubmit={(event) => { event.preventDefault(); apply(); }} className="mb-5 rounded-lg border bg-card p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
        <div className="min-w-0 flex-1"><label htmlFor="search" className="mb-1.5 block text-xs font-medium">Từ khoá</label><div className="relative"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input id="search" value={query} onChange={(event) => setQuery(event.target.value)} className="pl-9" placeholder={mode === "semantic" ? "Mô tả điều bạn tìm, ví dụ: app dạy trẻ phát âm" : "Tiêu đề (không dấu cũng được) hoặc tên tác giả…"} /></div></div>
        <div><span className="mb-1.5 block text-xs font-medium">Cách tìm</span><div role="group" aria-label="Cách tìm" className="flex rounded-md border p-0.5">{(["keyword", "semantic"] as const).map((value) => <Button key={value} type="button" size="sm" variant="ghost" aria-pressed={mode === value} onClick={() => { setMode(value); apply(value, false, true); }} className={cn("flex-1", mode === value && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground")} >{value === "keyword" ? "Theo từ khoá" : <><Sparkles />Theo nghĩa (AI)</>}</Button>)}</div></div>
        <Button type="submit">Tra cứu</Button>
      </div>
      <div className="mt-3 grid gap-3 border-t pt-3 sm:grid-cols-2 lg:grid-cols-4">
        <div><label className="mb-1 block text-xs font-medium">Loại tài liệu</label><Select value={docType} onValueChange={(value) => setDocType(String(value))}><SelectTrigger aria-label="Loại tài liệu" className="w-full"><SelectValue>{(value) => value === empty ? "Tất cả" : docTypeLabels[String(value)]}</SelectValue></SelectTrigger><SelectContent><SelectItem value={empty}>Tất cả</SelectItem>{Object.entries(docTypeLabels).slice(0, 5).map(([value, label]) => <SelectItem key={value} value={value}>{label}</SelectItem>)}</SelectContent></Select></div>
        <FacetSelect label="Năm" value={year} options={yearOptions} onChange={setYear} />
        <FacetSelect label="Đơn vị" value={unit} options={unitOptions} onChange={setUnit} />
        <div><label className="mb-1 block text-xs font-medium">Chủ đề</label><Select value={topic} onValueChange={(value) => setTopic(String(value))}><SelectTrigger aria-label="Chủ đề" className="w-full"><SelectValue>{(value) => value === empty ? "Tất cả" : topics.data?.find((item) => item.id === Number(value))?.label}</SelectValue></SelectTrigger><SelectContent><SelectItem value={empty}>Tất cả</SelectItem>{topics.data?.map((item) => <SelectItem key={item.id} value={String(item.id)}>{item.label} ({item.size})</SelectItem>)}</SelectContent></Select></div>
      </div>
      <details className="mt-3 rounded-md border px-3 py-2" open={advancedOpen} onToggle={(event) => setAdvancedOpen(event.currentTarget.open)}><summary className="cursor-pointer text-sm font-medium">Bộ lọc nâng cao</summary><div className="mt-3 grid gap-3 border-t pt-3 sm:grid-cols-3"><FacetSelect label="Loại bài/chỉ mục" value={pubType} options={facets.data?.pub_types ?? []} onChange={setPubType} /><FacetSelect label="Quartile" value={quartile} options={facets.data?.quartiles ?? []} onChange={setQuartile} /><FacetSelect label="Khoá" value={cohort} options={facets.data?.cohorts ?? []} onChange={setCohort} /></div></details>
      <div className="mt-3 flex justify-end"><Button type="button" variant="ghost" size="sm" onClick={clearFilters}><X />Xoá bộ lọc</Button></div>
    </form>
    {filters.keyword && <div className="mb-4 flex items-center gap-2 text-sm"><span className="text-muted-foreground">Đang lọc từ khoá:</span><Badge>{filters.keyword}</Badge><Button type="button" size="icon-sm" variant="ghost" aria-label="Bỏ lọc từ khoá" onClick={clearFilters}><X /></Button></div>}
    {semantic && works.data?.note && <Alert className="mb-4 border-primary/25 bg-primary/5"><Sparkles /><AlertTitle>Tìm theo nghĩa</AlertTitle><AlertDescription>{works.data.note}</AlertDescription></Alert>}
    {(topics.isError || stats.isError || (advancedOpen && facets.isError)) && <Alert variant="destructive" className="mb-4"><AlertTitle>Chưa tải được một số bộ lọc</AlertTitle><AlertDescription><span>{auxiliaryError instanceof ApiError ? auxiliaryError.detail : "Hãy thử tải lại bộ lọc."}</span><Button type="button" variant="outline" size="sm" className="mt-2" onClick={() => { void topics.refetch(); void stats.refetch(); if (advancedOpen) void facets.refetch(); }}>Thử lại</Button></AlertDescription></Alert>}
    {works.isLoading ? <LoadingView /> : works.isError ? <ErrorView error={works.error} retry={() => works.refetch()} /> : !works.data?.items.length ? <EmptyView title="Không tìm thấy công trình" description="Hãy đổi nội dung tìm hoặc bỏ bớt bộ lọc rồi tra cứu lại." action={<Button type="button" variant="outline" onClick={clearFilters}>Xoá bộ lọc</Button>} /> : <DataTable columns={columns} data={works.data.items} getRowId={(row) => String(row.id)} page={{ page: works.data.page.page, perPage: works.data.page.per_page, total: works.data.page.total, onPageChange: (page) => setFilters((current) => ({ ...current, page })) }} />}
  </>;
}

export default function SearchPage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị trang tra cứu…" />}><SearchContent /></Suspense>;
}
