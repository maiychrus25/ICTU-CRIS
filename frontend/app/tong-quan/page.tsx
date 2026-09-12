// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { CopyCheck, FileStack, History, Link2, Rss, UserRoundCheck } from "lucide-react";
import Link from "next/link";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { API_BASE } from "@/lib/api";
import { docTypeColors, docTypeLabels, getFieldValueLabel } from "@/lib/labels";
import { useRecent, useStats } from "@/lib/queries";
import type { RecentAdded, RecentChanged } from "@/lib/types";

const docTypes = ["bai_bao", "do_an", "luan_van", "luan_an", "hoc_lieu"] as const;

function formatDate(value: string | null | undefined) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Chưa có";
}

function MetricCard({ label, value, icon: Icon, href }: { label: string; value: string; icon: typeof FileStack; href?: string }) {
  const card = <Card className="h-full" size="sm"><CardHeader className="flex-row items-center justify-between"><CardTitle className="text-xs font-medium text-muted-foreground">{label}</CardTitle><Icon className="size-4 text-primary" /></CardHeader><CardContent><p className="text-2xl font-semibold tabular-nums">{value}</p>{href && <p className="mt-1 text-xs text-primary">Mở hàng đợi →</p>}</CardContent></Card>;
  return href ? <Link href={href} className="rounded-lg outline-none focus-visible:ring-3 focus-visible:ring-ring/50">{card}</Link> : card;
}

function RecentColumn({ title, items, fallbackTime, changed = false }: { title: string; items: (RecentAdded | RecentChanged)[]; fallbackTime?: string | null; changed?: boolean }) {
  return <div><h3 className="mb-2 text-sm font-semibold">{title} <span className="font-normal text-muted-foreground tabular-nums">({items.length})</span></h3>{items.length ? <ul className="divide-y rounded-lg border bg-card">{items.map((work) => <li key={work.id} className="p-3"><Link href={`/cong-trinh/?id=${work.id}`} className="line-clamp-2 font-medium leading-5 text-primary hover:underline">{work.title ?? "Chưa có tiêu đề"}</Link><p className="mt-1 text-xs text-muted-foreground"><span>{work.doc_type_label}</span>{changed && "version" in work ? ` · Phiên bản ${work.version}` : ""}<span> · {formatDate("first_seen_at" in work ? work.first_seen_at : fallbackTime)}</span></p></li>)}</ul> : <p className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">Không có công trình {changed ? "thay đổi" : "thêm mới"} trong lượt này.</p>}</div>;
}

function RecentWorks() {
  const query = useRecent();
  return <section className="mt-7" aria-labelledby="recent-title"><div className="mb-3 flex flex-wrap items-end justify-between gap-3"><div><h2 id="recent-title" className="text-base font-semibold">Mới cập nhật từ kho</h2><p className="mt-1 text-xs text-muted-foreground">Công trình thêm mới và thay đổi trong lượt đồng bộ gần nhất.</p></div><div className="flex gap-2"><Button render={<Link href="/dong-bo/" />} variant="outline" size="sm"><History />Xem lịch sử đồng bộ</Button><Button render={<a href={`${API_BASE}/api/feed.xml`} target="_blank" rel="noreferrer" />} variant="outline" size="sm" title="Theo dõi công trình mới bằng RSS"><Rss />RSS</Button></div></div>{query.isLoading ? <LoadingView label="Đang tải cập nhật mới từ kho…" /> : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} /> : query.data ? <div className="grid items-start gap-4 md:grid-cols-2"><RecentColumn title="Thêm" items={query.data.added} fallbackTime={query.data.run?.finished_at} /><RecentColumn title="Đổi" items={query.data.changed} fallbackTime={query.data.run?.finished_at} changed /></div> : <EmptyView description="Chưa có lượt đồng bộ hoàn tất để hiển thị cập nhật." />}</section>;
}

export default function OverviewPage() {
  const query = useStats();
  if (query.isLoading) return <><PageHeader title="Tổng quan" /><LoadingView /></>;
  if (query.isError) return <><PageHeader title="Tổng quan" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Tổng quan" /><EmptyView description="Chưa có số liệu tổng quan. Hãy thử lại sau lần đồng bộ tiếp theo." /></>;

  const stats = query.data;
  const yearlyData = [...stats.by_year_type].sort((a, b) => a.year - b.year);
  const totalWorks = yearlyData.reduce((sum, row) => sum + docTypes.reduce((rowSum, type) => rowSum + row[type], 0), 0);
  const unknownWorks = docTypes.reduce((sum, type) => sum + stats.unknown_year[type], 0);

  return (
    <>
      <PageHeader title="Tổng quan" description="Bức tranh 5 năm gần nhất dành cho lãnh đạo, từ số liệu có thể truy ngược về dữ liệu gốc." />
      <section aria-label="Chỉ số tổng quan" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Tổng công trình 5 năm" value={totalWorks.toLocaleString("vi-VN")} icon={FileStack} />
        <MetricCard label="Công trình có liên kết tác giả" value={`${stats.coverage.works_with_link_pct.toLocaleString("vi-VN", { maximumFractionDigits: 1 })}%`} icon={Link2} />
        <MetricCard label="Liên kết tác giả chờ xác nhận" value={stats.queues.authors_pending.toLocaleString("vi-VN")} icon={UserRoundCheck} href="/doi-soat/tac-gia/" />
        <MetricCard label="Nhóm nghi trùng đang mở" value={stats.queues.dup_groups_open.toLocaleString("vi-VN")} icon={CopyCheck} href="/doi-soat/trung-lap/" />
      </section>

      <RecentWorks />

      <section className="mt-7" aria-labelledby="year-type-chart-title">
        <div className="mb-3"><h2 id="year-type-chart-title" className="text-base font-semibold">Công trình theo năm và loại tài liệu</h2><p className="text-xs text-muted-foreground">Số lượng trong 5 năm có dữ liệu gần nhất.</p></div>
        {yearlyData.length ? <><div className="h-88 rounded-lg border bg-card p-4" role="img" aria-label="Biểu đồ cột chồng công trình theo năm và loại tài liệu"><ResponsiveContainer width="100%" height="100%"><BarChart data={yearlyData} margin={{ top: 8, right: 12, left: 10, bottom: 22 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="year" tickLine={false} axisLine={false} label={{ value: "Năm công bố", position: "insideBottom", offset: -14 }} /><YAxis allowDecimals={false} tickLine={false} axisLine={false} label={{ value: "Số công trình", angle: -90, position: "insideLeft" }} /><Tooltip cursor={{ fill: "var(--muted)" }} /><Legend verticalAlign="top" height={38} />{docTypes.map((type) => <Bar key={type} dataKey={type} name={docTypeLabels[type]} stackId="works" fill={docTypeColors[type]} />)}</BarChart></ResponsiveContainer></div><p className="mt-2 text-xs text-muted-foreground tabular-nums">{unknownWorks.toLocaleString("vi-VN")} công trình không rõ năm.</p></> : <EmptyView description="Chưa có dữ liệu theo năm để vẽ biểu đồ. Hãy chờ lần đồng bộ tiếp theo." />}
      </section>

      <div className="mt-7 grid items-start gap-7 xl:grid-cols-2">
        <section aria-labelledby="unit-table-title"><h2 id="unit-table-title" className="mb-3 text-base font-semibold">Công trình theo đơn vị</h2>{stats.by_unit.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Mã</TableHead><TableHead>Đơn vị</TableHead><TableHead className="text-right">Công trình</TableHead></TableRow></TableHeader><TableBody>{stats.by_unit.map((unit) => <TableRow key={unit.unit_id}><TableCell className="font-medium">{unit.code}</TableCell><TableCell>{unit.name}</TableCell><TableCell className="text-right font-semibold tabular-nums">{unit.works.toLocaleString("vi-VN")}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Chưa có dữ liệu đơn vị. Hãy chờ lần đồng bộ tiếp theo." />}</section>
        <section aria-labelledby="top-persons-title"><h2 id="top-persons-title" className="mb-3 text-base font-semibold">10 giảng viên có nhiều công trình nhất</h2>{stats.top_persons.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Giảng viên</TableHead><TableHead>Đơn vị</TableHead><TableHead className="text-right">Công trình</TableHead></TableRow></TableHeader><TableBody>{stats.top_persons.map((person) => <TableRow key={person.person_id}><TableCell><Link href={`/giang-vien/?id=${person.person_id}`} className="font-medium text-primary hover:underline">{person.display_name}</Link></TableCell><TableCell>{person.unit_code ?? "—"}</TableCell><TableCell className="text-right font-semibold tabular-nums">{person.works.toLocaleString("vi-VN")}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Chưa có dữ liệu xếp hạng giảng viên. Hãy chờ lần đồng bộ tiếp theo." />}</section>
      </div>
      <footer className="mt-7 border-t pt-4 text-xs text-muted-foreground">Dữ liệu đồng bộ lần cuối: <span className="tabular-nums">{formatDate(stats.last_sync?.finished_at)}</span>{stats.last_sync?.source ? ` · ${getFieldValueLabel("source", stats.last_sync.source)}` : ""}</footer>
    </>
  );
}
