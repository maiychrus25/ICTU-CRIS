// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { BookMarked, Download, Search, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState, useSyncExternalStore } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { WorkCitationDialog } from "@/components/work-citation-dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { API_BASE, ApiError } from "@/lib/api";
import { docTypeLabels, formatWorkScore } from "@/lib/labels";
import { useTopics, useUnits, useWorkFacets, useWorks } from "@/lib/queries";
import type { FacetOption, WorkFilters, WorkSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

const empty = "all";
const documentTypeTabs = [
  ["bai_bao", "Bài báo"], ["do_an", "Đồ án/Khoá luận"], ["luan_van", "Luận văn"], ["luan_an", "Luận án"], ["hoc_lieu", "Học liệu số"],
] as const;
const subscribeToHydration = () => () => undefined;

function FacetSelect({ label, value, options, onChange }: { label: string; value: string; options: FacetOption[]; onChange: (value: string) => void }) {
  return <div className="min-w-0"><label className="mb-1 block text-xs font-medium">{label}</label><Select value={value} onValueChange={(next) => onChange(String(next))}><SelectTrigger aria-label={label} className="w-full"><SelectValue>{(selected) => selected === empty ? "Tất cả" : options.find((item) => item.value === selected)?.label}</SelectValue></SelectTrigger><SelectContent><SelectItem value={empty}>Tất cả</SelectItem>{options.map((item) => <SelectItem key={item.value} value={item.value}>{item.label} ({item.n})</SelectItem>)}</SelectContent></Select></div>;
}

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const routeMode = searchParams.get("mode") === "semantic" ? "semantic" : "keyword";
  const routeDocType = searchParams.get("doc_type") ?? empty;
  const sort: NonNullable<WorkFilters["sort"]> = searchParams.get("sort") === "title" ? "title" : searchParams.get("sort") === "added" ? "added" : "recent";
  const initialArticleFilters = routeDocType === empty || routeDocType === "bai_bao";
  const initialCohortFilter = routeDocType === empty || routeDocType === "do_an";
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [pendingMode, setPendingMode] = useState<"keyword" | "semantic" | null>(null);
  const mode = pendingMode ?? routeMode;
  const [pendingDocType, setPendingDocType] = useState<string | null>(null);
  const docType = pendingDocType ?? routeDocType;
  const [year, setYear] = useState(searchParams.get("year") ?? empty);
  const [unit, setUnit] = useState(searchParams.get("unit") ?? empty);
  const [venueKind, setVenueKind] = useState(searchParams.get("venue_kind") ?? empty);
  const [score, setScore] = useState(searchParams.get("score") ?? empty);
  const [topic, setTopic] = useState(searchParams.get("topic") ?? empty);
  const [pubType, setPubType] = useState(searchParams.get("pub_type") ?? empty);
  const [quartile, setQuartile] = useState(searchParams.get("quartile") ?? empty);
  const [cohort, setCohort] = useState(searchParams.get("cohort") ?? empty);
  const hydrated = useSyncExternalStore(subscribeToHydration, () => true, () => false);
  const [advancedOpen, setAdvancedOpen] = useState(Boolean(searchParams.get("quartile") || searchParams.get("cohort") || searchParams.get("topic")));
  const [citationWorkId, setCitationWorkId] = useState<number | null>(null);
  const [filters, setFilters] = useState<WorkFilters>({
    q: searchParams.get("q") || undefined, mode: routeMode, doc_type: routeDocType === empty ? undefined : routeDocType,
    year: Number(searchParams.get("year")) || undefined, unit: searchParams.get("unit") || undefined,
    venue_kind: initialArticleFilters ? searchParams.get("venue_kind") || undefined : undefined,
    score: (initialArticleFilters ? searchParams.get("score") || undefined : undefined) as WorkFilters["score"],
    topic: Number(searchParams.get("topic")) || undefined, pub_type: initialArticleFilters ? searchParams.get("pub_type") || undefined : undefined,
    quartile: initialArticleFilters ? searchParams.get("quartile") || undefined : undefined,
    cohort: initialCohortFilter ? searchParams.get("cohort") || undefined : undefined,
    keyword: searchParams.get("keyword") || undefined,
    sort: searchParams.get("sort") === "title" ? "title" : searchParams.get("sort") === "added" ? "added" : "recent", page: 1,
  });
  const requestFilters: WorkFilters = {
    ...filters, mode, doc_type: docType === empty ? undefined : docType,
    venue_kind: docType === empty || docType === "bai_bao" ? filters.venue_kind : undefined,
    score: docType === empty || docType === "bai_bao" ? filters.score : undefined,
    pub_type: docType === empty || docType === "bai_bao" ? filters.pub_type : undefined,
    quartile: docType === empty || docType === "bai_bao" ? filters.quartile : undefined,
    cohort: docType === empty || docType === "do_an" ? filters.cohort : undefined,
  };
  const works = useWorks(requestFilters);
  const topics = useTopics();
  const units = useUnits();
  const facets = useWorkFacets();
  const yearOptions = facets.data?.years.map((item) => ({ value: String(item.value), label: String(item.value), n: item.n })) ?? [];
  const scoreOptions = facets.data?.scores ?? [];
  const supportsScore = hydrated && Array.isArray(facets.data?.scores);
  const venueOptions = facets.data?.venue_kinds ?? [];
  const showArticleFilters = docType === empty || docType === "bai_bao";
  const showCohort = docType === empty || docType === "do_an";
  const showVenueKind = hydrated && venueOptions.length > 0 && showArticleFilters;
  const documentTypeCounts = new Map(facets.data?.doc_types?.map((item) => [item.value, item.n]) ?? []);
  const documentTypes = documentTypeTabs.map(([value, label]) => ({ value, label, n: documentTypeCounts.get(value) ?? 0 }));
  const allDocuments = facets.data?.doc_types?.reduce((sum, item) => sum + item.n, 0);
  const unitOptions = units.data?.length ? units.data.filter((item) => item.active).map((item) => ({ value: item.code, label: `${item.code} — ${item.name}`, n: item.works })) : facets.data?.units.map((item) => ({ value: item.code, label: `${item.code} — ${item.name}`, n: item.n })) ?? [];
  const auxiliaryError = topics.error ?? facets.error ?? (!unitOptions.length ? units.error : null);
  const unitNames = useMemo(() => new Map(units.data?.map((item) => [item.code, item.name]) ?? []), [units.data]);
  const semantic = filters.mode === "semantic";
  const csvQuery = new URLSearchParams(Object.entries(requestFilters).filter(([key, value]) => key !== "page" && value !== undefined && value !== "").map(([key, value]) => [key, String(value)]));
  const csvUrl = `${API_BASE}/api/works.csv${csvQuery.size ? `?${csvQuery}` : ""}`;
  const activeFilters = [
    requestFilters.doc_type && docTypeLabels[requestFilters.doc_type],
    filters.year && `Năm ${filters.year}`,
    filters.unit && (unitOptions.find((item) => item.value === filters.unit)?.label ?? filters.unit),
    filters.venue_kind && (venueOptions.find((item) => item.value === filters.venue_kind)?.label ?? filters.venue_kind),
    filters.pub_type && (facets.data?.pub_types.find((item) => item.value === filters.pub_type)?.label ?? filters.pub_type),
    filters.score && (scoreOptions.find((item) => item.value === filters.score)?.label ?? filters.score),
    filters.topic && (topics.data?.find((item) => item.id === filters.topic)?.label ?? `Chủ đề #${filters.topic}`),
    filters.quartile,
    filters.cohort && `Khoá ${filters.cohort}`,
  ].filter((label): label is string => Boolean(label));

  useEffect(() => {
    function selectDocumentType(event: Event) {
      const value = (event as CustomEvent<string>).detail;
      setQuery(""); setPendingMode("keyword"); setPendingDocType(value); setYear(empty); setUnit(empty); setVenueKind(empty); setScore(empty);
      setTopic(empty); setPubType(empty); setQuartile(empty); setCohort(empty);
      setFilters({ mode: "keyword", doc_type: value, sort: "recent", page: 1 });
    }
    window.addEventListener("cris:document-type", selectDocumentType);
    return () => window.removeEventListener("cris:document-type", selectDocumentType);
  }, []);

  const columns = useMemo<DataTableColumn<WorkSummary>[]>(() => [
    { accessorKey: "title", header: "Công trình", cell: ({ row }) => <div className="w-full min-w-0 max-w-xl whitespace-normal break-words"><Link href={`/cong-trinh/?id=${row.original.id}`} className="font-medium text-primary hover:underline">{row.original.title ?? "Chưa có tiêu đề"}</Link>{row.original.doi && <div className="mt-0.5 break-all text-xs text-muted-foreground">DOI: {row.original.doi}</div>}<div className="mt-1.5 flex flex-wrap gap-1">{row.original.units?.map((item) => <Link key={item.id} href={`/tra-cuu/?unit=${encodeURIComponent(item.code)}`} title={unitNames.get(item.code)}><Badge variant="outline" className="font-normal hover:border-primary hover:text-primary">{item.code}</Badge></Link>)}{row.original.keywords?.slice(0, 3).map((keyword) => <Link key={keyword} href={`/tra-cuu/?keyword=${encodeURIComponent(keyword)}`}><Badge variant="outline" className="h-auto whitespace-normal font-normal hover:border-primary hover:text-primary">{keyword}</Badge></Link>)}</div></div> },
    ...(semantic ? [{ id: "score", header: "Độ gần", cell: ({ row }: { row: { original: WorkSummary } }) => <div className="w-24"><div className="h-1.5 overflow-hidden rounded-full bg-muted" role="progressbar" aria-label={`Độ gần ${Math.round((row.original.score ?? 0) * 100)} phần trăm`} aria-valuenow={Math.round((row.original.score ?? 0) * 100)} aria-valuemin={0} aria-valuemax={100}><div className="h-full rounded-full bg-primary" style={{ width: `${Math.round((row.original.score ?? 0) * 100)}%` }} /></div><span className="mt-1 block text-xs tabular-nums text-muted-foreground">{(row.original.score ?? 0).toFixed(2)}</span></div> }] : []),
    ...(!semantic && supportsScore ? [{ id: "work-score", header: "Điểm", cell: ({ row }: { row: { original: WorkSummary } }) => row.original.doc_type === "bai_bao" && row.original.score !== undefined ? <Badge variant="outline" className="whitespace-nowrap tabular-nums">{formatWorkScore(row.original.score)}</Badge> : null }] : []),
    { accessorKey: "doc_type_label", header: "Loại", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "year", header: "Năm", cell: ({ row }) => <span className="tabular-nums">{row.original.year ?? (row.original.doc_type === "do_an" && row.original.cohort ? `Khoá ${row.original.cohort.replace(/^K/i, "")}` : "—")}</span> },
    { accessorKey: "state", header: () => <span className="hidden 2xl:inline">Trạng thái</span>, enableSorting: false, cell: ({ row }) => <span className="hidden 2xl:inline-flex"><StatusBadge value={row.original.state} /></span> },
    { id: "citation", header: () => <span className="sr-only">Trích dẫn</span>, enableSorting: false, cell: ({ row }) => <Button type="button" variant="ghost" size="icon-sm" aria-label={`Trích dẫn ${row.original.title ?? `công trình #${row.original.id}`}`} title="Trích dẫn" onClick={() => setCitationWorkId(row.original.id)}><BookMarked /></Button> },
  ], [semantic, supportsScore, unitNames, setCitationWorkId]);

  function apply(nextMode: "keyword" | "semantic" = mode, reset = false, syncUrl = true) {
    const next: WorkFilters = reset ? { mode: nextMode, sort, page: 1 } : {
      q: query.trim() || undefined, mode: nextMode, doc_type: docType === empty ? undefined : docType,
      year: year === empty ? undefined : Number(year), unit: unit === empty ? undefined : unit,
      venue_kind: showArticleFilters && venueKind !== empty ? venueKind : undefined,
      score: showArticleFilters && score !== empty ? score as WorkFilters["score"] : undefined,
      topic: topic === empty ? undefined : Number(topic), pub_type: showArticleFilters && pubType !== empty ? pubType : undefined,
      quartile: showArticleFilters && quartile !== empty ? quartile : undefined,
      cohort: showCohort && cohort !== empty ? cohort : undefined, sort, page: 1,
    };
    setFilters(next);
    const params = new URLSearchParams(Object.entries(next).filter(([key, value]) => key !== "page" && value !== undefined && !(key === "mode" && value === "keyword") && !(key === "sort" && value === "recent")).map(([key, value]) => [key, String(value)]));
    if (syncUrl) router.replace(`/tra-cuu/${params.size ? `?${params}` : ""}`);
  }

  function clearFilters() {
    setQuery(""); setPendingDocType(empty); setYear(empty); setUnit(empty); setVenueKind(empty); setScore(empty); setTopic(empty); setPubType(empty); setQuartile(empty); setCohort(empty);
    apply(mode, true, true);
  }

  function changeDocumentType(value: string) {
    setPendingDocType(value);
    const next = {
      ...requestFilters, doc_type: value === empty ? undefined : value,
      venue_kind: value === empty || value === "bai_bao" ? requestFilters.venue_kind : undefined,
      pub_type: value === empty || value === "bai_bao" ? requestFilters.pub_type : undefined,
      score: value === empty || value === "bai_bao" ? requestFilters.score : undefined,
      quartile: value === empty || value === "bai_bao" ? requestFilters.quartile : undefined,
      cohort: value === empty || value === "do_an" ? requestFilters.cohort : undefined, page: 1,
    };
    setFilters(next);
    const params = new URLSearchParams(Object.entries(next).filter(([key, item]) => key !== "page" && item !== undefined && !(key === "mode" && item === "keyword") && !(key === "sort" && item === "recent")).map(([key, item]) => [key, String(item)]));
    router.replace(`/tra-cuu/${params.size ? `?${params}` : ""}`);
  }

  function changeSort(value: NonNullable<WorkFilters["sort"]>) {
    const next = { ...requestFilters, sort: value, page: 1 };
    setFilters(next);
    const params = new URLSearchParams(Object.entries(next).filter(([key, item]) => key !== "page" && item !== undefined && !(key === "mode" && item === "keyword") && !(key === "sort" && item === "recent")).map(([key, item]) => [key, String(item)]));
    router.replace(`/tra-cuu/${params.size ? `?${params}` : ""}`);
  }

  return <>
    <PageHeader title="Tra cứu công trình" description="Tìm từ một nguồn dữ liệu thống nhất và truy ngược từng kết quả về bản ghi gốc." action={<a href={csvUrl} title="Mở được bằng Excel (UTF-8)" className={buttonVariants({ variant: "outline" })}><Download />Tải CSV</a>} />
    <form onSubmit={(event) => { event.preventDefault(); apply(); }} className="mb-5 rounded-lg border bg-card p-4">
      <div role="tablist" aria-label="Loại công trình" className="-mx-1 mb-4 flex max-w-full gap-1 overflow-x-auto px-1 pb-1">{[{ value: empty, label: "Tất cả", n: allDocuments }, ...documentTypes].map((item) => <button key={item.value} type="button" role="tab" aria-selected={docType === item.value} onClick={() => changeDocumentType(item.value)} className={cn("min-h-9 shrink-0 rounded-lg border px-3 text-sm font-medium transition-colors", docType === item.value ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background hover:bg-muted")}><span>{item.label}</span><span suppressHydrationWarning className="ml-1.5 tabular-nums opacity-75">{item.n ? item.n.toLocaleString("vi-VN") : ""}</span></button>)}</div>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
        <div className="min-w-0 flex-1"><label htmlFor="search" className="mb-1.5 block text-xs font-medium">Từ khoá</label><div className="relative"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input id="search" value={query} onChange={(event) => setQuery(event.target.value)} className="pl-9" placeholder={mode === "semantic" ? "Mô tả điều bạn tìm, ví dụ: app dạy trẻ phát âm" : "Tiêu đề (không dấu cũng được) hoặc tên tác giả…"} /></div></div>
        <div><span className="mb-1.5 block text-xs font-medium">Cách tìm</span><div role="group" aria-label="Cách tìm" className="flex rounded-md border p-0.5">{(["keyword", "semantic"] as const).map((value) => <Button key={value} type="button" size="sm" variant="ghost" aria-pressed={mode === value} onClick={() => { setPendingMode(value); apply(value, false, true); }} className={cn("flex-1", mode === value && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground")} >{value === "keyword" ? "Theo từ khoá" : <><Sparkles />Theo nghĩa (AI)</>}</Button>)}</div></div>
        <div><label className="mb-1.5 block text-xs font-medium">Sắp xếp</label><Select value={sort} onValueChange={(value) => changeSort(String(value) as NonNullable<WorkFilters["sort"]>)}><SelectTrigger aria-label="Sắp xếp" className="w-full lg:w-44"><SelectValue>{(value) => value === "title" ? "Tiêu đề A→Z" : value === "added" ? "Mới đưa vào kho" : "Mới nhất"}</SelectValue></SelectTrigger><SelectContent><SelectItem value="recent">Mới nhất</SelectItem><SelectItem value="title">Tiêu đề A→Z</SelectItem><SelectItem value="added">Mới đưa vào kho</SelectItem></SelectContent></Select></div>
        <Button type="submit">Tra cứu</Button>
      </div>
      {activeFilters.length > 0 && <div aria-label="Bộ lọc đang áp dụng" className="mt-3 flex flex-wrap gap-1.5 lg:hidden">{activeFilters.map((label) => <Badge key={label} variant="secondary">{label}</Badge>)}</div>}
      <div className="mt-3 hidden gap-3 border-t pt-3 lg:grid lg:grid-cols-3 xl:grid-cols-6">
        <FacetSelect label="Năm" value={year} options={yearOptions} onChange={setYear} />
        <FacetSelect label="Khoa" value={unit} options={unitOptions} onChange={setUnit} />
        {showVenueKind && <FacetSelect label="Loại nơi công bố" value={venueKind} options={venueOptions} onChange={setVenueKind} />}
        {showArticleFilters && <FacetSelect label="Chỉ mục" value={pubType} options={facets.data?.pub_types ?? []} onChange={setPubType} />}
        {showArticleFilters && supportsScore && <FacetSelect label="Điểm quy đổi" value={score} options={scoreOptions} onChange={setScore} />}
      </div>
      <details className="mt-3 rounded-md border px-3 py-2 lg:hidden" open={advancedOpen} onToggle={(event) => setAdvancedOpen(event.currentTarget.open)}><summary className="min-h-9 cursor-pointer content-center text-sm font-medium">Bộ lọc ({activeFilters.length} đang áp dụng)</summary><div className="mt-3 grid min-w-0 gap-3 border-t pt-3 sm:grid-cols-2"><FacetSelect label="Năm" value={year} options={yearOptions} onChange={setYear} /><FacetSelect label="Khoa" value={unit} options={unitOptions} onChange={setUnit} />{showVenueKind && <FacetSelect label="Loại nơi công bố" value={venueKind} options={venueOptions} onChange={setVenueKind} />}{showArticleFilters && <FacetSelect label="Chỉ mục" value={pubType} options={facets.data?.pub_types ?? []} onChange={setPubType} />}{showArticleFilters && supportsScore && <FacetSelect label="Điểm quy đổi" value={score} options={scoreOptions} onChange={setScore} />}{showArticleFilters && <FacetSelect label="Quartile" value={quartile} options={facets.data?.quartiles ?? []} onChange={setQuartile} />}{showCohort && <FacetSelect label="Khoá" value={cohort} options={facets.data?.cohorts ?? []} onChange={setCohort} />}<div className="min-w-0"><label className="mb-1 block text-xs font-medium">Chủ đề</label><Select value={topic} onValueChange={(value) => setTopic(String(value))}><SelectTrigger aria-label="Chủ đề" className="w-full"><SelectValue>{(value) => value === empty ? "Tất cả" : topics.data?.find((item) => item.id === Number(value))?.label}</SelectValue></SelectTrigger><SelectContent><SelectItem value={empty}>Tất cả</SelectItem>{topics.data?.map((item) => <SelectItem key={item.id} value={String(item.id)}>{item.label} ({item.size})</SelectItem>)}</SelectContent></Select></div></div></details>
      <details className="mt-3 hidden rounded-md border px-3 py-2 lg:block" open={advancedOpen} onToggle={(event) => setAdvancedOpen(event.currentTarget.open)}><summary className="min-h-8 cursor-pointer content-center text-sm font-medium">Bộ lọc nâng cao</summary><div className="mt-3 grid gap-3 border-t pt-3 sm:grid-cols-3">{showArticleFilters && <FacetSelect label="Quartile" value={quartile} options={facets.data?.quartiles ?? []} onChange={setQuartile} />}{showCohort && <FacetSelect label="Khoá" value={cohort} options={facets.data?.cohorts ?? []} onChange={setCohort} />}<div className="min-w-0"><label className="mb-1 block text-xs font-medium">Chủ đề</label><Select value={topic} onValueChange={(value) => setTopic(String(value))}><SelectTrigger aria-label="Chủ đề" className="w-full"><SelectValue>{(value) => value === empty ? "Tất cả" : topics.data?.find((item) => item.id === Number(value))?.label}</SelectValue></SelectTrigger><SelectContent><SelectItem value={empty}>Tất cả</SelectItem>{topics.data?.map((item) => <SelectItem key={item.id} value={String(item.id)}>{item.label} ({item.size})</SelectItem>)}</SelectContent></Select></div></div></details>
      <div className="mt-3 flex justify-end"><Button type="button" variant="ghost" size="sm" onClick={clearFilters}><X />Xoá bộ lọc</Button></div>
    </form>
    {filters.keyword && <div className="mb-4 flex items-center gap-2 text-sm"><span className="text-muted-foreground">Đang lọc từ khoá:</span><Badge>{filters.keyword}</Badge><Button type="button" size="icon-sm" variant="ghost" aria-label="Bỏ lọc từ khoá" onClick={clearFilters}><X /></Button></div>}
    {semantic && works.data?.note && <Alert className="mb-4 border-primary/25 bg-primary/5"><Sparkles /><AlertTitle>Tìm theo nghĩa</AlertTitle><AlertDescription>{works.data.note}</AlertDescription></Alert>}
    {auxiliaryError && <Alert variant="destructive" className="mb-4"><AlertTitle>Chưa tải được một số bộ lọc</AlertTitle><AlertDescription><span>{auxiliaryError instanceof ApiError ? auxiliaryError.detail : "Hãy thử tải lại bộ lọc."}</span><Button type="button" variant="outline" size="sm" className="mt-2" onClick={() => { void topics.refetch(); void units.refetch(); void facets.refetch(); }}>Thử lại</Button></AlertDescription></Alert>}
    {works.isLoading ? <LoadingView /> : works.isError ? <ErrorView error={works.error} retry={() => works.refetch()} /> : !works.data?.items.length ? <EmptyView title="Không tìm thấy công trình" description="Hãy đổi nội dung tìm hoặc bỏ bớt bộ lọc rồi tra cứu lại." action={<Button type="button" variant="outline" onClick={clearFilters}>Xoá bộ lọc</Button>} /> : <div className="min-w-0 lg:[&_[data-slot=table]]:table-fixed lg:[&_th:first-child]:w-[42%]"><DataTable columns={columns} data={works.data.items} getRowId={(row) => String(row.id)} page={{ page: works.data.page.page, perPage: works.data.page.per_page, total: works.data.page.total, onPageChange: (page) => setFilters((current) => ({ ...current, page })) }} /></div>}
    {citationWorkId !== null && <WorkCitationDialog workId={citationWorkId} open onOpenChange={(open) => { if (!open) setCitationWorkId(null); }} />}
  </>;
}

export default function SearchPage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị trang tra cứu…" />}><SearchContent /></Suspense>;
}
