// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";

import { DataTable, type DataTableColumn } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { useTopic } from "@/lib/queries";
import type { WorkSummary } from "@/lib/types";

function TopicDetailContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const query = useTopic(id);
  const columns = useMemo<DataTableColumn<WorkSummary>[]>(() => [
    { accessorKey: "title", header: "Công trình", cell: ({ row }) => <Link href={`/cong-trinh/?id=${row.original.id}`} className="block max-w-2xl whitespace-normal font-medium text-primary hover:underline">{row.original.title ?? "Chưa có tiêu đề"}</Link> },
    { accessorKey: "doc_type", header: "Loại", cell: ({ row }) => <StatusBadge value={row.original.doc_type} kind="docType" /> },
    { accessorKey: "year", header: "Năm", cell: ({ row }) => <span className="tabular-nums">{row.original.year ?? "—"}</span> },
    { accessorKey: "state", header: "Trạng thái", cell: ({ row }) => <StatusBadge value={row.original.state} /> },
  ], []);

  if (id === null) return <><PageHeader title="Chi tiết chủ đề" /><EmptyView title="Chưa chọn chủ đề" description="Mở một cụm từ trang Chủ đề để xem từ khoá và công trình." action={<Link href="/chu-de/" className="text-sm font-medium text-primary hover:underline">Đi đến danh sách chủ đề</Link>} /></>;
  if (query.isLoading) return <><PageHeader title="Chi tiết chủ đề" /><LoadingView label="Đang tải chi tiết chủ đề…" /></>;
  if (query.isError) return <><PageHeader title="Chi tiết chủ đề" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Chi tiết chủ đề" /><EmptyView description="Cụm chủ đề này không còn tồn tại. Hãy quay lại danh sách chủ đề." /></>;

  const topic = query.data;
  const maxWeight = Math.max(topic.keywords[0]?.weight ?? 1, 0.0001);
  return (
    <>
      <PageHeader title={topic.label} description={`${topic.size} công trình trong cụm chủ đề`} action={<Button render={<Link href={`/tra-cuu/?topic=${topic.id}`} />}>Tra cứu theo chủ đề này</Button>} />
      <section className="mb-8" aria-labelledby="keywords-title">
        <div className="mb-3"><h2 id="keywords-title" className="text-base font-semibold">Từ khoá và trọng số</h2><p className="text-xs text-muted-foreground">Thanh dài hơn thể hiện từ khoá có trọng số lớn hơn trong cụm.</p></div>
        {topic.keywords.length ? <div className="grid gap-x-8 gap-y-3 rounded-lg border bg-card p-4 md:grid-cols-2">{topic.keywords.map(({ keyword, weight }) => (
          <div key={keyword}><div className="mb-1 flex items-center justify-between gap-3 text-xs"><span className="font-medium">{keyword}</span><span className="tabular-nums text-muted-foreground">{weight.toLocaleString("vi-VN", { maximumFractionDigits: 3 })}</span></div><div role="progressbar" aria-label={`Trọng số từ khoá ${keyword}`} aria-valuemin={0} aria-valuemax={maxWeight} aria-valuenow={weight} className="h-1.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${Math.max(0, Math.min(100, weight / maxWeight * 100))}%` }} /></div></div>
        ))}</div> : <EmptyView description="Cụm này chưa có từ khoá. Hãy chạy lại quy trình phân tích chủ đề." />}
      </section>
      <section aria-labelledby="topic-works-title"><h2 id="topic-works-title" className="mb-3 text-base font-semibold">Công trình thuộc chủ đề</h2>{topic.works.length ? <DataTable columns={columns} data={topic.works} getRowId={(work) => String(work.id)} /> : <EmptyView description="Chưa có công trình khớp cụm chủ đề này. Hãy kiểm tra lại dữ liệu từ khoá." />}</section>
    </>
  );
}

export default function TopicDetailPage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị chi tiết chủ đề…" />}><TopicDetailContent /></Suspense>;
}
