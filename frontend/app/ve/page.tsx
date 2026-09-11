// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Bot, CheckCircle2, Database, ExternalLink, GitBranch, ShieldAlert } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { docTypeLabels } from "@/lib/labels";
import { useAbout, useMe, useScreenCohorts } from "@/lib/queries";

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return <div className="border-b py-3 last:border-0"><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 font-medium tabular-nums">{value}</dd></div>;
}

function totalCount(value: number | Record<string, number>) {
  return typeof value === "number" ? value : Object.values(value).reduce((total, count) => total + count, 0);
}

export default function AboutPage() {
  const query = useAbout();
  const cohorts = useScreenCohorts();
  const me = useMe();
  if (query.isLoading || cohorts.isLoading) return <><PageHeader title="Về hệ thống" /><LoadingView /></>;
  if (query.isError || cohorts.isError) return <><PageHeader title="Về hệ thống" /><ErrorView error={query.error ?? cohorts.error} retry={() => { query.refetch(); cohorts.refetch(); }} /></>;
  if (!query.data) return <><PageHeader title="Về hệ thống" /><EmptyView description="Chưa có thông tin hệ thống. Hãy thử lại sau lần đồng bộ tiếp theo." /></>;
  const about = query.data;
  const screenedCohorts = cohorts.data?.length ?? 0;
  const flaggedWorks = cohorts.data?.reduce((total, item) => total + item.flagged, 0) ?? 0;
  return (
    <>
      <PageHeader title="Về hệ thống" description="ICTU-CRIS hợp nhất dữ liệu công bố khoa học, giữ xuất xứ rõ ràng và đặt quyết định trong tay người dùng." />
      {me.data && !me.data.auth_required && <Alert className="mb-6 border-status-warning/30 bg-status-warning/10 text-status-warning"><ShieldAlert /><AlertTitle>Chưa bật đăng nhập</AlertTitle><AlertDescription>Đặt mật khẩu bằng <code className="rounded bg-background/70 px-1 py-0.5 font-mono text-xs">python -m cris user set-password</code>.</AlertDescription></Alert>}
      <div className="grid gap-8 lg:grid-cols-[1fr_1.15fr]">
        <div className="space-y-7">
          <section><div className="mb-3 flex items-center gap-2"><Database className="size-4 text-primary" /><h2 className="text-base font-semibold">Nguồn và đồng bộ</h2></div><dl className="rounded-lg border bg-card px-4"><Metric label="Tổng số công trình" value={about.works.toLocaleString("vi-VN")} /><Metric label="Nguồn dữ liệu" value={<a href={about.source_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-primary hover:underline">Kho dữ liệu ICTU <ExternalLink className="size-3" /></a>} /><Metric label="Mã nguồn" value={<a href={about.repo_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-primary hover:underline">Kho ICTU-CRIS <GitBranch className="size-3" /></a>} /><Metric label="Lần đồng bộ gần nhất" value={about.last_sync?.finished_at ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(about.last_sync.finished_at)) : "Chưa có"} /></dl></section>
          <section><h2 className="mb-3 text-base font-semibold">Công trình theo loại</h2><div className="divide-y rounded-lg border bg-card px-4">{Object.entries(about.works_by_type).map(([type, count]) => <div key={type} className="flex items-center justify-between py-3"><span>{docTypeLabels[type] ?? type}</span><span className="font-semibold tabular-nums">{count.toLocaleString("vi-VN")}</span></div>)}</div></section>
        </div>
        <div className="space-y-7">
          <section><div className="mb-3 flex items-center gap-2"><Bot className="size-4 text-primary" /><h2 className="text-base font-semibold">AI trong hệ thống</h2><Badge variant="outline" className="ml-auto"><CheckCircle2 />Chỉ gợi ý</Badge></div><div className="rounded-lg border bg-card p-5"><div className="grid gap-x-8 sm:grid-cols-2"><Metric label="Nhà cung cấp" value={about.ai.provider} /><Metric label="Mô hình" value={about.ai.model} /><Metric label="Giấy phép" value={about.ai.licence} /><Metric label="Kích thước / số chiều" value={`${about.ai.size} · ${about.ai.dim}`} /><Metric label="Vector đã tạo" value={totalCount(about.ai.embeddings).toLocaleString("vi-VN")} /><Metric label="Chủ đề / gợi ý" value={`${about.ai.topics.toLocaleString("vi-VN")} / ${totalCount(about.ai.suggestions).toLocaleString("vi-VN")}`} /><Metric label="Rà soát theo khoá" value={`${screenedCohorts.toLocaleString("vi-VN")} khoá · ${flaggedWorks.toLocaleString("vi-VN")} gắn cờ`} /></div><a href={about.ai.repo} target="_blank" rel="noreferrer" className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">Xem mô hình và giấy phép <ExternalLink className="size-3.5" /></a></div></section>
          <section><div className="mb-3 flex items-center gap-2"><ShieldAlert className="size-4 text-muted-foreground" /><h2 className="text-base font-semibold">Giới hạn cần lưu ý</h2></div><ol className="space-y-3 rounded-lg border bg-card p-5">{about.limits.map((limit, index) => <li key={limit} className="flex gap-3 text-sm leading-6"><span className="grid size-6 shrink-0 place-items-center rounded-full bg-muted text-xs font-semibold tabular-nums">{index + 1}</span><span>{limit}</span></li>)}</ol></section>
        </div>
      </div>
    </>
  );
}
