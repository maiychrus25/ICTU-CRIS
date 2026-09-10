// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { ArrowRight, DatabaseZap, Link2 } from "lucide-react";
import Link from "next/link";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { docTypeColors, docTypeLabels, getFieldValueLabel } from "@/lib/labels";
import { useQuality } from "@/lib/queries";

function formatValue(value: unknown) {
  if (typeof value === "number") return value.toLocaleString("vi-VN");
  if (value === null || value === undefined || value === "") return "—";
  return String(value);
}

function formatDate(value: unknown) {
  return typeof value === "string" ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Chưa có";
}

export default function QualityPage() {
  const query = useQuality();
  if (query.isLoading) return <><PageHeader title="Chất lượng dữ liệu" /><LoadingView /></>;
  if (query.isError) return <><PageHeader title="Chất lượng dữ liệu" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Chất lượng dữ liệu" /><EmptyView description="Chưa có chỉ số chất lượng. Hãy thử lại sau lần đồng bộ tiếp theo." /></>;
  const quality = query.data;
  const chartData = Object.entries(quality.works_by_type).map(([key, count]) => ({ key, type: docTypeLabels[key] ?? key, count }));
  const syncSource = typeof quality.last_sync?.source === "string" ? quality.last_sync.source : null;

  return (
    <>
      <PageHeader title="Chất lượng dữ liệu" description="Theo dõi các điểm cần xử lý và mở đúng hàng đợi từ một nơi." />
      <div className="grid items-start gap-7 lg:grid-cols-[minmax(0,1fr)_minmax(360px,0.9fr)]">
        <section aria-labelledby="quality-metrics-title"><div className="mb-3 flex items-center gap-2"><DatabaseZap className="size-4 text-primary" /><h2 id="quality-metrics-title" className="text-base font-semibold">Chỉ số cần theo dõi</h2></div>{quality.metrics.length ? <div className="divide-y overflow-hidden rounded-lg border bg-card">{quality.metrics.map((metric) => <div key={metric.key} className="flex min-h-16 flex-wrap items-center justify-between gap-3 px-4 py-3"><div><p className="text-sm text-muted-foreground">{metric.label}</p><p className="mt-0.5 text-xl font-semibold tabular-nums">{formatValue(metric.value)}</p></div>{metric.queue_url && <Button render={<Link href={metric.queue_url} />} variant="outline" size="sm">Mở hàng đợi<ArrowRight /></Button>}</div>)}</div> : <EmptyView description="Không có chỉ số cần theo dõi ở lần đồng bộ này." />}</section>

        <section aria-labelledby="coverage-title"><div className="mb-3 flex items-center gap-2"><Link2 className="size-4 text-primary" /><h2 id="coverage-title" className="text-base font-semibold">Mức phủ liên kết tác giả</h2></div><div className="rounded-lg border bg-card p-5"><div className="mb-2 flex items-end justify-between gap-4"><span className="text-sm text-muted-foreground">Công trình đã có liên kết</span><strong className="text-2xl text-primary tabular-nums">{quality.works_with_link_pct.toLocaleString("vi-VN", { maximumFractionDigits: 1 })}%</strong></div><div role="progressbar" aria-label="Tỷ lệ công trình có liên kết tác giả" aria-valuemin={0} aria-valuemax={100} aria-valuenow={quality.works_with_link_pct} className="h-2.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${Math.max(0, Math.min(100, quality.works_with_link_pct))}%` }} /></div><p className="mt-3 text-xs leading-5 text-muted-foreground">Tỷ lệ được tính trên toàn bộ công trình sau lần đồng bộ gần nhất.</p></div></section>
      </div>

      <section className="mt-7" aria-labelledby="works-type-chart-title"><div className="mb-3"><h2 id="works-type-chart-title" className="text-base font-semibold">Công trình theo loại tài liệu</h2><p className="text-xs text-muted-foreground">Phân bố dữ liệu hiện có trong hệ thống.</p></div>{chartData.length ? <div className="h-80 rounded-lg border bg-card p-4" role="img" aria-label="Biểu đồ số công trình theo loại tài liệu"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 16, left: 18, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} /><XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} /><YAxis dataKey="type" type="category" width={86} tickLine={false} axisLine={false} /><Tooltip cursor={{ fill: "var(--muted)" }} /><Bar dataKey="count" name="Công trình" radius={[0, 4, 4, 0]}>{chartData.map((item) => <Cell key={item.key} fill={docTypeColors[item.key] ?? "var(--primary)"} />)}</Bar></BarChart></ResponsiveContainer></div> : <EmptyView description="Chưa có dữ liệu theo loại tài liệu để vẽ biểu đồ." />}</section>
      <footer className="mt-7 border-t pt-4 text-xs text-muted-foreground">Dữ liệu đồng bộ lần cuối: <span className="tabular-nums">{formatDate(quality.last_sync?.finished_at)}</span>{syncSource ? ` · ${getFieldValueLabel("source", syncSource)}` : ""}</footer>
    </>
  );
}
