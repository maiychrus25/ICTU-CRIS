// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AlertTriangle, ArrowUpRight, CircleAlert, CircleMinus, Info, SearchCheck } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { AspectMatrix } from "@/components/aspect-matrix";
import { CompareModeTabs } from "@/components/compare-mode-tabs";
import { PageHeader } from "@/components/page-header";
import { Pager } from "@/components/pager";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { aspectLevelLabels, type AspectLevel } from "@/lib/labels";
import { useScreen, useScreenCohorts } from "@/lib/queries";
import type { ScreenCohortSummary, ScreenItem, ScreenLevel } from "@/lib/types";
import { cn } from "@/lib/utils";

const scoreFormatter = new Intl.NumberFormat("vi-VN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const levelConfig = {
  cao: { icon: AlertTriangle, className: "border-status-danger/25 bg-status-danger/10 text-status-danger" },
  vua: { icon: CircleAlert, className: "border-status-warning/30 bg-status-warning/10 text-status-warning" },
  thap: { icon: CircleMinus, className: "bg-muted text-muted-foreground" },
} as const;

function LevelBadge({ level }: { level: string }) {
  const config = levelConfig[level as ScreenLevel] ?? levelConfig.thap;
  const Icon = config.icon;
  return <Badge variant="outline" className={cn("font-normal", config.className)}><Icon />{aspectLevelLabels[level as AspectLevel] ?? level}</Badge>;
}

function cohortLabel(item: ScreenCohortSummary) {
  return `Khoá ${item.cohort} — ${item.screened.toLocaleString("vi-VN")} đồ án, ${item.flagged.toLocaleString("vi-VN")} gắn cờ`;
}

function ScreenResult({ item }: { item: ScreenItem }) {
  const title = item.title ?? "Chưa có tiêu đề";
  return (
    <article className="overflow-hidden rounded-lg border bg-card">
      <header className="flex flex-wrap items-start justify-between gap-3 border-b bg-muted/20 px-4 py-4">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2"><span className="text-xs text-muted-foreground">Khoá {item.cohort ?? "chưa rõ"}</span><LevelBadge level={item.level} /><span className="text-xs font-medium tabular-nums">Tương đồng tóm tắt {scoreFormatter.format(item.max_score)}</span></div>
          <h2 className="text-[15px] font-semibold leading-6"><Link href={`/cong-trinh/?id=${item.work_id}`} className="hover:text-primary hover:underline">{title}<ArrowUpRight className="ml-1 inline size-3.5" /></Link></h2>
        </div>
        <Button render={<Link href={`/doi-chieu/?title=${encodeURIComponent(title)}`} />} variant="outline" size="sm"><SearchCheck />Đối chiếu chi tiết</Button>
      </header>
      {!item.neighbours.length ? <p className="px-4 py-5 text-sm text-muted-foreground">Chưa có công trình ở khoá khác để đối chiếu.</p> : <ol className="divide-y">{item.neighbours.map((neighbour) => (
        <li key={neighbour.work_id} className="px-4 py-4">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div><p className="text-xs text-muted-foreground">Khoá {neighbour.cohort ?? "chưa rõ"}</p><Link href={`/cong-trinh/?id=${neighbour.work_id}`} className="mt-1 inline-block font-medium leading-6 text-primary hover:underline">{neighbour.title ?? "Chưa có tiêu đề"}</Link></div>
            <span className="text-xs text-muted-foreground tabular-nums">Điểm {scoreFormatter.format(neighbour.score)}</span>
          </div>
          {Object.keys(neighbour.aspects).length > 0 && <div className="mt-3"><AspectMatrix aspects={neighbour.aspects} /></div>}
        </li>
      ))}</ol>}
    </article>
  );
}

export default function ScreenPage() {
  const cohorts = useScreenCohorts();
  const [cohort, setCohort] = useState("");
  const [level, setLevel] = useState<ScreenLevel>("cao");
  const [minScore, setMinScore] = useState("");
  const [page, setPage] = useState(1);
  const selectedCohort = cohort || cohorts.data?.[0]?.cohort || "";
  const parsedMinScore = minScore === "" ? undefined : Number(minScore);
  const validScore = parsedMinScore === undefined || (Number.isFinite(parsedMinScore) && parsedMinScore >= 0 && parsedMinScore <= 1);
  const screen = useScreen({ cohort: selectedCohort || undefined, min: level, min_score: validScore ? parsedMinScore : undefined, page }, Boolean(selectedCohort) && validScore);

  return (
    <>
      <PageHeader title="Rà soát trùng đề tài theo khoá" description="Xem các cặp công trình cần giảng viên lưu ý giữa các khoá, theo gợi ý đã được hệ thống tính trước." />
      <CompareModeTabs active="screen" />
      <Alert className="mb-5 border-primary/25 bg-primary/5"><Info /><AlertTitle>Phạm vi rà soát</AlertTitle><AlertDescription>AI gợi ý, người quyết. So trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn. Điểm tương đồng cao chỉ là dấu hiệu để giảng viên xem xét.</AlertDescription></Alert>
      <div className="mb-5 grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-[minmax(280px,1fr)_180px_180px]">
        <div><label htmlFor="screen-cohort" className="mb-1.5 block text-xs font-medium">Khoá</label><Select value={selectedCohort} onValueChange={(value) => { setCohort(String(value)); setPage(1); }} disabled={cohorts.isLoading || !cohorts.data?.length}><SelectTrigger id="screen-cohort" aria-label="Khoá rà soát" className="w-full"><SelectValue>{(value) => cohorts.data?.find((item) => item.cohort === String(value)) ? cohortLabel(cohorts.data.find((item) => item.cohort === String(value))!) : "Chọn khoá"}</SelectValue></SelectTrigger><SelectContent>{cohorts.data?.map((item) => <SelectItem key={item.cohort} value={item.cohort}>{cohortLabel(item)}</SelectItem>)}</SelectContent></Select></div>
        <div><label htmlFor="screen-level" className="mb-1.5 block text-xs font-medium">Mức tối thiểu</label><Select value={level} onValueChange={(value) => { setLevel(value === "vua" ? "vua" : "cao"); setPage(1); }}><SelectTrigger id="screen-level" aria-label="Mức tối thiểu" className="w-full"><SelectValue>{(value) => value === "cao" ? "Cao" : "Vừa"}</SelectValue></SelectTrigger><SelectContent><SelectItem value="cao">Cao</SelectItem><SelectItem value="vua">Vừa</SelectItem></SelectContent></Select></div>
        <div><label htmlFor="screen-score" className="mb-1.5 block text-xs font-medium">Điểm tối thiểu <span className="font-normal text-muted-foreground">(tuỳ chọn)</span></label><Input id="screen-score" type="number" min="0" max="1" step="0.01" inputMode="decimal" value={minScore} onChange={(event) => { setMinScore(event.target.value); setPage(1); }} aria-invalid={!validScore} placeholder="0,90" /></div>
      </div>
      {!validScore ? <Alert variant="destructive"><AlertTriangle /><AlertTitle>Điểm chưa hợp lệ</AlertTitle><AlertDescription>Điểm tối thiểu phải nằm trong khoảng từ 0 đến 1.</AlertDescription></Alert> : cohorts.isLoading ? <LoadingView label="Đang tải danh sách khoá…" /> : cohorts.isError ? <ErrorView error={cohorts.error} retry={() => cohorts.refetch()} /> : !cohorts.data?.length ? <EmptyView title="Chưa rà soát khoá nào" description="Chạy `python -m cris ai screen --cohort <mã>` để tạo dữ liệu rà soát." /> : screen.isLoading ? <LoadingView label="Đang tải kết quả rà soát…" /> : screen.isError ? <ErrorView error={screen.error} retry={() => screen.refetch()} /> : !screen.data?.items.length ? <EmptyView title="Không có công trình ở mức đã chọn" description="Hãy hạ mức tối thiểu hoặc bỏ điểm tối thiểu để xem thêm kết quả." /> : <section aria-label="Kết quả rà soát" className="space-y-4">{screen.data.items.map((item) => <ScreenResult key={item.work_id} item={item} />)}<Pager page={screen.data.page.page} perPage={screen.data.page.per_page} total={screen.data.page.total} onPageChange={setPage} /></section>}
    </>
  );
}
