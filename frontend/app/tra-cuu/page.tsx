// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { docTypeLabels } from "@/lib/labels";
import { useTopics, useWorks } from "@/lib/queries";
import type { WorkFilters, WorkSummary } from "@/lib/types";

function SearchContent() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [docType, setDocType] = useState("all");
  const [year, setYear] = useState("");
  const [topic, setTopic] = useState("all");
  const [filters, setFilters] = useState<WorkFilters>({ q: searchParams.get("q") ?? "", page: 1 });
  const works = useWorks(filters);
  const topics = useTopics();
  const columns = useMemo<DataTableColumn<WorkSummary>[]>(() => [
    { accessorKey: "title", header: "Công trình", cell: ({ row }) => <div className="max-w-xl whitespace-normal"><Link href={`/cong-trinh/?id=${row.original.id}`} className="font-medium text-primary hover:underline">{row.original.title ?? "Chưa có tiêu đề"}</Link>{row.original.doi && <div className="mt-0.5 text-xs text-muted-foreground">DOI: {row.original.doi}</div>}</div> },
    { accessorKey: "doc_type_label", header: "Loại", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "year", header: "Năm", cell: ({ row }) => <span className="tabular-nums">{row.original.year ?? "—"}</span> },
    { accessorKey: "state", header: "Trạng thái", cell: ({ row }) => <StatusBadge value={row.original.state} /> },
  ], []);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    setFilters({ q: query.trim() || undefined, doc_type: docType === "all" ? undefined : docType, year: year ? Number(year) : undefined, topic: topic === "all" ? undefined : Number(topic), page: 1 });
  }

  return (
    <>
      <PageHeader title="Tra cứu công trình" description="Tìm từ một nguồn dữ liệu thống nhất và truy ngược từng kết quả về bản ghi gốc." />
      <form onSubmit={submit} className="mb-5 grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-2 xl:grid-cols-[minmax(240px,1fr)_180px_130px_200px_auto]">
        <div><label htmlFor="search" className="mb-1.5 block text-xs font-medium">Từ khoá</label><Input id="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Tiêu đề, DOI hoặc tác giả…" /></div>
        <div><label className="mb-1.5 block text-xs font-medium">Loại tài liệu</label><Select value={docType} onValueChange={(value) => setDocType(String(value))}><SelectTrigger className="w-full"><SelectValue>{(value) => value === "all" ? "Tất cả" : docTypeLabels[String(value)]}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả</SelectItem>{Object.entries(docTypeLabels).slice(0, 5).map(([value, label]) => <SelectItem key={value} value={value}>{label}</SelectItem>)}</SelectContent></Select></div>
        <div><label htmlFor="year" className="mb-1.5 block text-xs font-medium">Năm</label><Input id="year" type="number" min="1900" max="2100" value={year} onChange={(event) => setYear(event.target.value)} placeholder="2025" /></div>
        <div><label className="mb-1.5 block text-xs font-medium">Chủ đề</label><Select value={topic} onValueChange={(value) => setTopic(String(value))} disabled={topics.isLoading}><SelectTrigger className="w-full"><SelectValue>{(value) => value === "all" ? "Tất cả chủ đề" : topics.data?.find((item) => item.id === Number(value))?.label}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả chủ đề</SelectItem>{topics.data?.map((item) => <SelectItem key={item.id} value={String(item.id)}>{item.label} ({item.size})</SelectItem>)}</SelectContent></Select></div>
        <div className="flex items-end"><Button type="submit" className="w-full">Tra cứu</Button></div>
      </form>
      {topics.isError && <div className="mb-4"><ErrorView error={topics.error} retry={() => topics.refetch()} /></div>}
      {works.isLoading ? <LoadingView /> : works.isError ? <ErrorView error={works.error} retry={() => works.refetch()} /> : !works.data?.items.length ? <EmptyView title="Không tìm thấy công trình" description="Hãy đổi từ khoá hoặc bỏ bớt bộ lọc rồi tra cứu lại." action={<Button type="button" variant="outline" onClick={() => { setQuery(""); setDocType("all"); setYear(""); setTopic("all"); setFilters({ page: 1 }); }}>Xoá bộ lọc</Button>} /> : <DataTable columns={columns} data={works.data.items} getRowId={(row) => String(row.id)} page={{ page: works.data.page.page, perPage: works.data.page.per_page, total: works.data.page.total, onPageChange: (page) => setFilters((current) => ({ ...current, page })) }} />}
    </>
  );
}

export default function SearchPage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị trang tra cứu…" />}><SearchContent /></Suspense>;
}
