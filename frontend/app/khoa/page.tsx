// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { BookOpenCheck, Link2, UserRoundCheck, UsersRound } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { YearTypeChart } from "@/components/year-type-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { stateLabels } from "@/lib/labels";
import { useMe, usePeriods, useStats, useUnitOverview } from "@/lib/queries";

function MetricCard({ label, value, icon: Icon }: { label: string; value: number | string; icon: typeof BookOpenCheck }) {
  return <Card size="sm"><CardHeader className="flex-row items-center justify-between"><CardTitle className="text-xs font-medium text-muted-foreground">{label}</CardTitle><Icon className="size-4 text-primary" /></CardHeader><CardContent><p className="text-2xl font-semibold tabular-nums">{typeof value === "number" ? value.toLocaleString("vi-VN") : value}</p></CardContent></Card>;
}

function FacultyContent() {
  const rawId = useSearchParams().get("id");
  const requestedId = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const me = useMe();
  const stats = useStats();
  const periods = usePeriods();
  const router = useRouter();
  const user = me.data?.user;
  const canChoose = Boolean(user?.roles.some((role) => ["rd_officer", "school_leader"].includes(role)));
  const ownUnit = user?.roles.some((role) => ["faculty_officer", "faculty_head", "lecturer"].includes(role)) ? user.unit_id : null;
  const unitId = ownUnit ?? requestedId ?? (canChoose ? stats.data?.by_unit[0]?.unit_id ?? null : null);
  const openPeriod = periods.data?.find((period) => period.state === "DangMo");
  const overview = useUnitOverview(unitId, openPeriod?.id);

  if (me.isLoading || stats.isLoading || periods.isLoading || (unitId !== null && overview.isLoading)) return <><PageHeader title="Góc nhìn khoa" /><LoadingView label="Đang tải số liệu khoa…" /></>;
  if (stats.isError) return <><PageHeader title="Góc nhìn khoa" /><ErrorView error={stats.error} retry={() => stats.refetch()} /></>;
  if (periods.isError) return <><PageHeader title="Góc nhìn khoa" /><ErrorView error={periods.error} retry={() => periods.refetch()} /></>;
  if (overview.isError) return <><PageHeader title="Góc nhìn khoa" /><ErrorView error={overview.error} retry={() => overview.refetch()} /></>;
  if (unitId === null) return <><PageHeader title="Góc nhìn khoa" /><EmptyView title="Chưa xác định khoa" description="Tài khoản chưa gắn với đơn vị và không có quyền chọn khoa khác." /></>;
  if (!overview.data) return <><PageHeader title="Góc nhìn khoa" /><EmptyView description="Chưa có số liệu cho khoa này. Hãy thử lại sau lần đồng bộ tiếp theo." /></>;

  const data = overview.data;
  const unitSelector = canChoose ? <Select value={String(unitId)} onValueChange={(value) => router.replace("/khoa/?id=" + value)}><SelectTrigger aria-label="Chọn đơn vị" className="w-full sm:w-72"><SelectValue>{(value) => stats.data?.by_unit.find((item) => item.unit_id === Number(value))?.name ?? "Chọn đơn vị"}</SelectValue></SelectTrigger><SelectContent>{stats.data?.by_unit.map((item) => <SelectItem key={item.unit_id} value={String(item.unit_id)}>{item.code} — {item.name}</SelectItem>)}</SelectContent></Select> : undefined;
  return <>
    <PageHeader title={data.unit.name} description={openPeriod ? "Số liệu công trình và hồ sơ kê khai trong " + openPeriod.name + "." : "Số liệu công trình và liên kết tác giả của đơn vị."} action={unitSelector} />
    <section aria-label="Chỉ số khoa" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Tổng công trình" value={data.works_total} icon={BookOpenCheck} /><MetricCard label="Đã liên kết" value={data.linked_works ?? "—"} icon={Link2} /><MetricCard label="Chờ xác nhận" value={data.pending_links} icon={UserRoundCheck} /><MetricCard label="Giảng viên chưa có công trình" value={data.lecturers_without_works} icon={UsersRound} /></section>

    <section className="mt-7" aria-labelledby="faculty-chart-title"><div className="mb-3"><h2 id="faculty-chart-title" className="text-base font-semibold">Công trình 5 năm theo loại tài liệu</h2><p className="text-xs text-muted-foreground">Số công trình đã gắn với đơn vị theo năm công bố.</p></div>{data.by_year.length ? <YearTypeChart data={data.by_year} label="Biểu đồ công trình 5 năm theo loại tài liệu" /> : <EmptyView description="Chưa có dữ liệu theo năm để vẽ biểu đồ." />}</section>

    <div className="mt-7 grid items-start gap-7 xl:grid-cols-2"><section aria-labelledby="faculty-top-title"><h2 id="faculty-top-title" className="mb-3 text-base font-semibold">10 giảng viên có nhiều công trình nhất</h2>{data.top_persons.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Giảng viên</TableHead><TableHead className="text-right">Công trình</TableHead></TableRow></TableHeader><TableBody>{data.top_persons.map((person) => <TableRow key={person.person_id}><TableCell><Link href={"/giang-vien/?id=" + person.person_id} className="font-medium text-primary hover:underline">{person.display_name}</Link></TableCell><TableCell className="text-right font-semibold tabular-nums">{person.works.toLocaleString("vi-VN")}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Chưa có dữ liệu xếp hạng giảng viên." />}</section>
      <section aria-labelledby="faculty-declarations-title"><h2 id="faculty-declarations-title" className="mb-3 text-base font-semibold">Hồ sơ kê khai theo trạng thái</h2>{openPeriod && Object.keys(data.declarations_by_state).length ? <div className="flex min-h-28 flex-wrap content-start gap-2 rounded-lg border bg-card p-4">{Object.entries(data.declarations_by_state).map(([state, count]) => <Badge key={state} render={<Link href={"/ky-bao-cao/chi-tiet/?id=" + openPeriod.id} />} variant="outline" className="h-8 gap-2 px-3">{stateLabels[state] ?? state}<strong className="tabular-nums">{count}</strong></Badge>)}</div> : <EmptyView description={openPeriod ? "Khoa chưa có hồ sơ trong kỳ đang mở." : "Hiện không có kỳ báo cáo đang mở."} />}</section></div>

    <section className="mt-7" aria-labelledby="without-works-title"><div className="mb-3"><h2 id="without-works-title" className="text-base font-semibold">Giảng viên chưa có công trình liên kết</h2><p className="text-xs text-muted-foreground">Mở hồ sơ để kiểm tra thông tin hoặc <Link href="/doi-soat/tac-gia/" className="font-medium text-primary hover:underline">kiểm tra hàng đợi tác giả</Link>.</p></div>{data.lecturers_without_works_items?.length ? <ul className="divide-y rounded-lg border bg-card">{data.lecturers_without_works_items.map((person) => <li key={person.person_id} className="flex items-center justify-between gap-4 p-3"><Link href={"/giang-vien/?id=" + person.person_id} className="font-medium text-primary hover:underline">{person.display_name}</Link><span className="text-xs text-muted-foreground">Chưa có công trình liên kết</span></li>)}</ul> : <EmptyView title={data.lecturers_without_works ? data.lecturers_without_works + " giảng viên chưa có công trình" : "Tất cả giảng viên đã có công trình"} description={data.lecturers_without_works ? "API hiện chưa cung cấp danh sách chi tiết; hãy kiểm tra hàng đợi tác giả." : "Không cần xử lý thêm ở thời điểm này."} />}</section>
  </>;
}

export default function FacultyPage() {
  return <Suspense fallback={<LoadingView label="Đang tải số liệu khoa…" />}><FacultyContent /></Suspense>;
}
