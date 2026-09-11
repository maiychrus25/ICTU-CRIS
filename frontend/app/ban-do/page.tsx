// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useMemo, useState } from "react";
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { CoauthorGraph } from "@/components/coauthor-graph";
import { KnowledgeMap } from "@/components/knowledge-map";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCoauthors, useKnowledgeMap, useTrends } from "@/lib/queries";
import type { CoauthorsOut, MapColor } from "@/lib/types";
import { cn } from "@/lib/utils";

const colors = ["#2563eb", "#7c3aed", "#0891b2", "#c2410c", "#4f46e5", "#0f766e"];

function MapView() {
  const [color, setColor] = useState<MapColor>("topic");
  const [query, setQuery] = useState("");
  const map = useKnowledgeMap(color);
  return <section aria-label="Bản đồ công trình"><div className="mb-4 flex flex-col gap-3 rounded-lg border bg-card p-3 sm:flex-row"><div className="min-w-0 flex-1"><label htmlFor="map-search" className="mb-1 block text-xs font-medium">Tìm nhanh trên bản đồ</label><Input id="map-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Nhập một phần tiêu đề công trình…" /></div><div className="sm:w-52"><label className="mb-1 block text-xs font-medium">Tô màu theo</label><Select value={color} onValueChange={(value) => setColor(value as MapColor)}><SelectTrigger aria-label="Tô màu bản đồ theo" className="w-full"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="topic">Chủ đề</SelectItem><SelectItem value="unit">Đơn vị</SelectItem><SelectItem value="year">Năm</SelectItem><SelectItem value="doc_type">Loại tài liệu</SelectItem></SelectContent></Select></div></div>{map.isLoading ? <LoadingView label="Đang tải bản đồ tri thức…" /> : map.isError ? <ErrorView error={map.error} retry={() => map.refetch()} /> : !map.data?.points.length ? <EmptyView title="Chưa có bản đồ" description="Bản đồ sẽ xuất hiện sau khi dữ liệu AI được xây dựng." /> : <><KnowledgeMap data={map.data} color={color} query={query} /><p className="mt-2 text-xs text-muted-foreground">Cuộn hoặc chụm để thu phóng, kéo để di chuyển, bấm một điểm để mở công trình. Vị trí thể hiện độ gần chuyên môn, không phải xếp hạng chất lượng.</p></>}</section>;
}

function TrendsView() {
  const [by, setBy] = useState<"cohort" | "year">("cohort");
  const [percent, setPercent] = useState(false);
  const trends = useTrends(by);
  const [selection, setSelection] = useState<number[]>([]);
  const selected = selection.length ? selection : (trends.data?.series.slice(0, 4).map((series) => series.topic_id ?? -1) ?? []);
  const visible = trends.data?.series.filter((series) => selected.includes(series.topic_id ?? -1)).slice(0, 6) ?? [];
  const chartData = trends.data?.keys.map((key) => Object.fromEntries([["key", key], ...visible.map((series) => [series.label, percent ? (series.values.find((value) => value.key === key)?.share ?? 0) * 100 : series.values.find((value) => value.key === key)?.count ?? 0])])) ?? [];

  function toggle(topicId: number) {
    setSelection((current) => { const base = current.length ? current : selected; return base.includes(topicId) ? base.filter((id) => id !== topicId) : base.length < 6 ? [...base, topicId] : base; });
  }

  return <section aria-label="Xu hướng chủ đề"><div className="mb-4 flex flex-wrap items-end justify-between gap-3"><div><span className="mb-1 block text-xs font-medium">Trục thời gian</span><div role="group" aria-label="Trục thời gian" className="flex rounded-md border p-0.5"><Button type="button" size="sm" variant="ghost" aria-pressed={by === "cohort"} className={cn(by === "cohort" && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground")} onClick={() => { setBy("cohort"); setSelection([]); }}>Theo khoá</Button><Button type="button" size="sm" variant="ghost" aria-pressed={by === "year"} className={cn(by === "year" && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground")} onClick={() => { setBy("year"); setSelection([]); }}>Theo năm</Button></div></div><div><span className="mb-1 block text-xs font-medium">Cách tính</span><div role="group" aria-label="Cách tính xu hướng" className="flex rounded-md border p-0.5"><Button type="button" size="sm" variant="ghost" aria-pressed={!percent} className={cn(!percent && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground")} onClick={() => setPercent(false)}>Số lượng</Button><Button type="button" size="sm" variant="ghost" aria-pressed={percent} className={cn(percent && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground")} onClick={() => setPercent(true)}>Tỉ lệ %</Button></div></div></div>
    {trends.isLoading ? <LoadingView label="Đang tải xu hướng…" /> : trends.isError ? <ErrorView error={trends.error} retry={() => trends.refetch()} /> : !trends.data?.series.length ? <EmptyView title="Chưa có dữ liệu xu hướng" description="Hãy chờ lần phân cụm chủ đề tiếp theo." /> : <><fieldset className="mb-4 rounded-lg border bg-card p-3"><legend className="px-1 text-xs font-medium">Chọn tối đa 6 cụm để so</legend><div className="flex flex-wrap gap-x-4 gap-y-2">{trends.data.series.map((series) => { const id = series.topic_id ?? -1; return <label key={id} className="inline-flex items-center gap-2 text-sm"><input type="checkbox" checked={selected.includes(id)} disabled={!selected.includes(id) && selected.length >= 6} onChange={() => toggle(id)} />{series.label}</label>; })}</div></fieldset><div role="img" aria-label={`Biểu đồ vùng xếp chồng theo ${by === "cohort" ? "khoá" : "năm"}`} className="h-96 rounded-lg border bg-card p-4"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="key" /><YAxis unit={percent ? "%" : undefined} /><Tooltip /><Legend />{visible.map((series, index) => <Area key={series.label} type="monotone" dataKey={series.label} stackId="topics" stroke={colors[index]} fill={colors[index]} fillOpacity={0.65} />)}</AreaChart></ResponsiveContainer></div><div className="mt-4 overflow-hidden rounded-lg border bg-card"><Table data-testid="trend-table"><TableHeader><TableRow><TableHead>{by === "cohort" ? "Khoá" : "Năm"}</TableHead>{visible.map((series) => <TableHead key={series.label} className="text-right">{series.label}</TableHead>)}</TableRow></TableHeader><TableBody>{chartData.map((row) => <TableRow key={String(row.key)}><TableCell className="font-medium">{String(row.key)}</TableCell>{visible.map((series) => <TableCell key={series.label} className="text-right tabular-nums">{Number(row[series.label]).toLocaleString("vi-VN", { maximumFractionDigits: percent ? 1 : 0 })}{percent ? "%" : ""}</TableCell>)}</TableRow>)}</TableBody></Table></div></>}
  </section>;
}

function CoauthorsView() {
  const coauthors = useCoauthors();
  const [unit, setUnit] = useState("all");
  const filtered = useMemo<CoauthorsOut | null>(() => {
    if (!coauthors.data) return null;
    const nodes = unit === "all" ? coauthors.data.nodes : coauthors.data.nodes.filter((node) => node.unit_code === unit);
    const ids = new Set(nodes.map((node) => node.person_id));
    return { nodes, edges: coauthors.data.edges.filter((edge) => ids.has(edge.a) && ids.has(edge.b)) };
  }, [coauthors.data, unit]);
  const units = [...new Set(coauthors.data?.nodes.map((node) => node.unit_code).filter(Boolean) ?? [])] as string[];
  return <section aria-label="Mạng lưới đồng tác giả"><div className="mb-4 ml-auto max-w-64"><label className="mb-1 block text-xs font-medium">Lọc theo đơn vị</label><Select value={unit} onValueChange={(value) => setUnit(String(value))}><SelectTrigger aria-label="Lọc đồng tác giả theo đơn vị" className="w-full"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">Tất cả đơn vị</SelectItem>{units.map((value) => <SelectItem key={value} value={value}>{value}</SelectItem>)}</SelectContent></Select></div>{coauthors.isLoading ? <LoadingView label="Đang tải mạng lưới đồng tác giả…" /> : coauthors.isError ? <ErrorView error={coauthors.error} retry={() => coauthors.refetch()} /> : !filtered?.nodes.length ? <EmptyView title="Chưa có đồng tác giả phù hợp" description="Hãy chọn đơn vị khác hoặc chờ dữ liệu liên kết được xác nhận." /> : <><CoauthorGraph data={filtered} /><p className="mt-2 text-xs text-muted-foreground">Nút lớn hơn là giảng viên có nhiều công trình hơn; cạnh đậm hơn là có nhiều công trình chung hơn. Bấm một nút để mở hồ sơ.</p></>}</section>;
}

export default function KnowledgePage() {
  const [tab, setTab] = useState("map");
  return <><PageHeader title="Bản đồ tri thức" description="Khám phá công trình, xu hướng chủ đề và quan hệ đồng tác giả trong một không gian trực quan." /><Tabs value={tab} onValueChange={(value) => setTab(String(value))} className="mb-5"><TabsList><TabsTrigger value="map">Bản đồ</TabsTrigger><TabsTrigger value="trends">Xu hướng</TabsTrigger><TabsTrigger value="coauthors">Đồng tác giả</TabsTrigger></TabsList></Tabs>{tab === "map" ? <MapView /> : tab === "trends" ? <TrendsView /> : <CoauthorsView />}</>;
}
