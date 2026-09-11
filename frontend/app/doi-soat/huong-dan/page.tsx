// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Info, LockKeyhole, Sparkles } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { AuthorQueueTabs } from "@/components/author-queue-tabs";
import { PageHeader } from "@/components/page-header";
import { Pager } from "@/components/pager";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ApiError } from "@/lib/api";
import { officerRoleRequired } from "@/lib/labels";
import { useAcceptMentor, useMentors, useOfficerAccess, useStats } from "@/lib/queries";

const scoreFormatter = new Intl.NumberFormat("vi-VN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function MentorSuggestionsPage() {
  const queryClient = useQueryClient();
  const [unit, setUnit] = useState("all");
  const [minVotes, setMinVotes] = useState("2");
  const [page, setPage] = useState(1);
  const stats = useStats();
  const parsedVotes = Number(minVotes);
  const validVotes = Number.isInteger(parsedVotes) && parsedVotes >= 1;
  const mentors = useMentors({ unit: unit === "all" ? undefined : unit, min_votes: validVotes ? parsedVotes : undefined, page }, validVotes);
  const accept = useAcceptMentor();
  const canDecide = useOfficerAccess();
  const rows = mentors.data?.items.flatMap((item) => [...item.candidates].sort((a, b) => b.score - a.score).map((candidate) => ({ item, candidate }))) ?? [];

  async function acceptCandidate(workId: number, personId: number) {
    try {
      await accept.mutateAsync({ workId, personId });
      await Promise.all([queryClient.invalidateQueries({ queryKey: ["mentors"] }), queryClient.invalidateQueries({ queryKey: ["author-queue"] })]);
      toast.success("Đã đưa gợi ý vào hàng đợi tác giả.");
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể đưa gợi ý vào hàng đợi.");
    }
  }

  return (
    <>
      <PageHeader title="Hàng đợi tác giả" description="Rà soát liên kết hiện có và đưa gợi ý người hướng dẫn vào hàng đợi để người dùng quyết định." />
      <AuthorQueueTabs active="mentors" />
      <Alert className="mb-5 border-primary/25 bg-primary/5"><Info /><AlertTitle>AI chỉ đưa ra ứng viên</AlertTitle><AlertDescription>4.621/5.375 đồ án ở kho nguồn ghi người hướng dẫn là <code className="rounded bg-background px-1 font-mono text-xs">ICTU_TEACHER</code>. AI gợi ý ứng viên từ các đồ án gần nhất đã có người hướng dẫn thật; đưa vào hàng đợi rồi người quyết.</AlertDescription></Alert>
      <div className="mb-5 grid gap-3 rounded-lg border bg-card p-4 sm:grid-cols-[minmax(260px,1fr)_220px]">
        <div><label htmlFor="mentor-unit" className="mb-1.5 block text-xs font-medium">Đơn vị</label><Select value={unit} onValueChange={(value) => { setUnit(String(value)); setPage(1); }}><SelectTrigger id="mentor-unit" aria-label="Đơn vị" className="w-full"><SelectValue>{(value) => value === "all" ? "Tất cả đơn vị" : stats.data?.by_unit.find((item) => String(item.unit_id) === String(value))?.name ?? "Chọn đơn vị"}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả đơn vị</SelectItem>{stats.data?.by_unit.map((item) => <SelectItem key={item.unit_id} value={String(item.unit_id)}>{item.code} — {item.name}</SelectItem>)}</SelectContent></Select></div>
        <div><label htmlFor="mentor-min-votes" className="mb-1.5 block text-xs font-medium">Số phiếu tối thiểu</label><Input id="mentor-min-votes" type="number" min="1" step="1" inputMode="numeric" value={minVotes} onChange={(event) => { setMinVotes(event.target.value); setPage(1); }} aria-invalid={!validVotes} /></div>
      </div>
      {!validVotes ? <Alert variant="destructive"><Info /><AlertTitle>Số phiếu chưa hợp lệ</AlertTitle><AlertDescription>Số phiếu tối thiểu phải là số nguyên từ 1 trở lên.</AlertDescription></Alert>
        : stats.isLoading || mentors.isLoading ? <LoadingView label="Đang tải gợi ý người hướng dẫn…" />
          : stats.isError ? <ErrorView error={stats.error} retry={() => stats.refetch()} />
            : mentors.isError ? <ErrorView error={mentors.error} retry={() => mentors.refetch()} />
              : !rows.length ? <EmptyView title="Chưa có gợi ý" description="Chưa có gợi ý — chạy `python -m cris ai mentors`." />
                : <section aria-label="Gợi ý người hướng dẫn" className="overflow-x-auto rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead className="min-w-72">Đồ án</TableHead><TableHead>Ứng viên</TableHead><TableHead className="text-right">Phiếu</TableHead><TableHead className="text-right">Điểm</TableHead><TableHead className="min-w-72">Đồ án dẫn chứng</TableHead><TableHead>Hành động</TableHead></TableRow></TableHeader><TableBody>{rows.map(({ item, candidate }) => <TableRow key={`${item.work_id}-${candidate.person_id}`}><TableCell className="whitespace-normal"><Link href={`/cong-trinh/?id=${item.work_id}`} className="font-medium text-primary hover:underline">{item.title ?? `Đồ án #${item.work_id}`}</Link><p className="mt-1 inline-flex items-center gap-1 text-xs text-muted-foreground"><LockKeyhole className="size-3" />Khoá {item.cohort ?? "chưa rõ"}</p></TableCell><TableCell><Link href={`/giang-vien/?id=${candidate.person_id}`} className="font-medium text-primary hover:underline">{candidate.display_name}</Link><p className="mt-1 text-xs text-muted-foreground">{candidate.degree ?? "Chưa rõ học vị"}</p></TableCell><TableCell className="text-right font-medium tabular-nums">{candidate.votes}</TableCell><TableCell className="text-right tabular-nums">{scoreFormatter.format(candidate.score)}</TableCell><TableCell className="whitespace-normal"><ul className="space-y-1">{candidate.evidence.slice(0, 2).map((evidence) => <li key={evidence.work_id}><Link href={`/cong-trinh/?id=${evidence.work_id}`} className="text-xs text-primary hover:underline">{evidence.title ?? `Đồ án #${evidence.work_id}`}</Link></li>)}</ul></TableCell><TableCell>{item.pending_link ? <Link href="/doi-soat/tac-gia/" className="inline-flex items-center gap-1 font-medium text-primary hover:underline"><Sparkles className="size-4" />Đang chờ xác nhận</Link> : <span title={canDecide ? undefined : officerRoleRequired}><Button type="button" size="sm" onClick={() => void acceptCandidate(item.work_id, candidate.person_id)} disabled={!canDecide || accept.isPending}><Sparkles />Đưa vào hàng đợi</Button></span>}</TableCell></TableRow>)}</TableBody></Table><Pager page={mentors.data!.page.page} perPage={mentors.data!.page.per_page} total={mentors.data!.page.total} onPageChange={setPage} /></section>}
    </>
  );
}
