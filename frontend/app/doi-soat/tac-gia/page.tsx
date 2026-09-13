// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Bot, Check, CornerDownRight, Search, Sparkles, UserRoundX } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { AuthorQueueTabs } from "@/components/author-queue-tabs";
import { PageHeader } from "@/components/page-header";
import { Pager } from "@/components/pager";
import { PersonCombobox } from "@/components/person-combobox";
import { ErrorView, LoadingView } from "@/components/state-views";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { confidenceLabels, officerRoleRequired, stateLabels } from "@/lib/labels";
import { useAuthorQueue, useDecideAuthors, useOfficerAccess } from "@/lib/queries";
import type { AuthorQueueRow, DecideAuthorsIn } from "@/lib/types";

const states = ["ChoXacNhan", "DaNoiTuDong", "DaXacNhan", "DaBacBo"] as const;

function groupRows(items: AuthorQueueRow[]) {
  const groups = new Map<string, AuthorQueueRow[]>();
  for (const item of items) {
    const key = `${item.raw_name}\u0000${item.work_id}`;
    groups.set(key, [...(groups.get(key) ?? []), item]);
  }
  return [...groups].map(([key, candidates]) => ({ key, candidates: [...candidates].sort((a, b) => (a.ai_rank ?? Number.MAX_SAFE_INTEGER) - (b.ai_rank ?? Number.MAX_SAFE_INTEGER) || a.link_id - b.link_id) }));
}

function hasUsefulSuggestion(candidate: AuthorQueueRow) {
  return candidate.ai_rank !== null && Boolean(candidate.ai_reason && !candidate.ai_reason.toLocaleLowerCase("vi").includes("chưa có công trình đã xác nhận"));
}

export default function AuthorQueuePage() {
  const queryClient = useQueryClient();
  const [state, setState] = useState("ChoXacNhan");
  const [search, setSearch] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [selectedGroups, setSelectedGroups] = useState<Record<string, boolean>>({});
  const [candidateChoices, setCandidateChoices] = useState<Record<string, number>>({});
  const [rejectOpen, setRejectOpen] = useState(false);
  const [reassignOpen, setReassignOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [personId, setPersonId] = useState<number | null>(null);
  const queue = useAuthorQueue(state, q, page);
  const pendingCount = useAuthorQueue("ChoXacNhan", "", 1);
  const automaticCount = useAuthorQueue("DaNoiTuDong", "", 1);
  const confirmedCount = useAuthorQueue("DaXacNhan", "", 1);
  const rejectedCount = useAuthorQueue("DaBacBo", "", 1);
  const decide = useDecideAuthors();
  const canDecide = useOfficerAccess();
  const groups = useMemo(() => groupRows(queue.data?.items ?? []), [queue.data?.items]);
  const counts = [pendingCount.data?.page.total, automaticCount.data?.page.total, confirmedCount.data?.page.total, rejectedCount.data?.page.total];
  const chosenLink = (key: string, candidates: AuthorQueueRow[]) => candidateChoices[key] ?? candidates[0].link_id;
  const selectedIds = groups.filter((group) => selectedGroups[group.key]).map((group) => chosenLink(group.key, group.candidates));
  const allSelected = groups.length > 0 && groups.every((group) => selectedGroups[group.key]);

  async function submitDecision(input: DecideAuthorsIn) {
    try {
      const result = await decide.mutateAsync(input);
      toast.success(`Đã xử lý ${result.processed.length} liên kết tác giả.`);
      setSelectedGroups({});
      setReason("");
      setPersonId(null);
      setRejectOpen(false);
      setReassignOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["author-queue"] });
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể xử lý các liên kết đã chọn.");
    }
  }

  function resetQueue(nextState?: string) {
    if (nextState) setState(nextState);
    setPage(1);
    setSelectedGroups({});
    setCandidateChoices({});
  }

  return (
    <>
      <PageHeader title="Hàng đợi tác giả" description="AI chỉ đưa ra gợi ý; người dùng xác nhận, bác bỏ hoặc chuyển liên kết cho người khác." />
      <AuthorQueueTabs active="queue" />
      <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <Tabs value={state} onValueChange={(value) => resetQueue(String(value))}>
          <TabsList variant="line" className="max-w-full overflow-x-auto">
            {states.map((value, index) => <TabsTrigger key={value} value={value}>{stateLabels[value]}<Badge variant="secondary" className="tabular-nums">{counts[index] ?? "…"}</Badge></TabsTrigger>)}
          </TabsList>
        </Tabs>
        <form className="flex w-full gap-2 xl:w-80" onSubmit={(event) => { event.preventDefault(); setQ(search.trim()); resetQueue(); }}>
          <div className="relative flex-1"><Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Tìm theo tên thô" value={search} onChange={(event) => setSearch(event.target.value)} className="pl-8" placeholder="Tìm theo tên thô…" /></div>
          <Button type="submit" variant="outline">Tìm</Button>
        </form>
      </div>

      {queue.isLoading ? <LoadingView /> : queue.isError ? <ErrorView error={queue.error} retry={() => queue.refetch()} /> : groups.length === 0 ? <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">Không có liên kết ở trạng thái này. Hãy chọn tab khác hoặc đổi từ khoá tìm kiếm.</div> : <section aria-label="Các lượt tên cần đối soát" className="overflow-hidden rounded-lg border bg-card">
        <div className="flex min-h-10 items-center gap-2 border-b bg-muted/30 px-4 text-sm font-medium"><input type="checkbox" aria-label="Chọn tất cả" checked={allSelected} onChange={(event) => setSelectedGroups(Object.fromEntries(groups.map((group) => [group.key, event.target.checked])))} />Chọn tất cả lượt tên trên trang</div>
        {groups.map(({ key, candidates }) => {
          const first = candidates[0];
          const selectedLinkId = chosenLink(key, candidates);
          return <article key={key} aria-label={`${first.raw_name} – ${first.work_title ?? `Công trình #${first.work_id}`}`} className="border-b p-4 last:border-0">
            <div className="flex items-start gap-3">
              <input type="checkbox" aria-label={`Chọn ${first.raw_name} – ${first.work_title ?? `công trình #${first.work_id}`}`} checked={Boolean(selectedGroups[key])} onChange={(event) => setSelectedGroups((current) => ({ ...current, [key]: event.target.checked }))} />
              <div className="min-w-0 flex-1"><h2 className="font-semibold">{first.raw_name}</h2><Link href={`/cong-trinh/?id=${first.work_id}`} className="mt-1 block break-words text-sm font-medium text-primary hover:underline">{first.work_title ?? "Chưa có tiêu đề"}</Link><p className="mt-1 text-xs text-muted-foreground">Tên này xuất hiện trong <span className="tabular-nums">{first.group_work_count}</span> công trình đang đối soát.</p></div>
            </div>
            <fieldset className="mt-3 space-y-2 pl-7"><legend className="sr-only">Chọn ứng viên cho {first.raw_name}</legend>{candidates.map((candidate) => <label key={candidate.link_id} className="flex min-h-12 cursor-pointer items-start gap-3 rounded-md border p-3 has-checked:border-primary has-checked:bg-primary/5">
              <input type="radio" name={`candidate-${key}`} checked={selectedLinkId === candidate.link_id} onChange={() => setCandidateChoices((current) => ({ ...current, [key]: candidate.link_id }))} />
              <span className="min-w-0 flex-1"><span className="flex flex-wrap items-center gap-2"><Link href={`/giang-vien/?id=${candidate.candidate_person_id}`} className="font-medium text-primary hover:underline">{candidate.candidate_name}</Link><Badge variant="outline" className={candidate.confidence === "ai_mentor" ? "border-primary/30 bg-primary/10 text-primary" : ["cao", "ten_day_du_duy_nhat", "orcid"].includes(candidate.confidence) ? "border-status-success/30 bg-status-success/10 text-status-success" : "border-status-warning/30 bg-status-warning/10 text-status-warning"}>{candidate.confidence === "ai_mentor" && <Sparkles />}{confidenceLabels[candidate.confidence] ?? candidate.confidence}</Badge>{candidate.degree_conflict && <span title="Học vị trong nguồn có dấu hiệu xung đột" className="inline-flex items-center gap-1 text-status-warning"><AlertTriangle className="size-4" />Cần kiểm tra học vị</span>}</span>{hasUsefulSuggestion(candidate) && <span className="mt-2 block rounded-md bg-muted/50 p-2 text-xs leading-5 text-muted-foreground"><span className="mb-0.5 flex items-center gap-1 font-medium text-foreground"><Bot className="size-3.5" />Gợi ý AI · hạng {candidate.ai_rank}</span>{candidate.ai_reason}</span>}</span>
            </label>)}</fieldset>
            {(state === "ChoXacNhan" || state === "DaNoiTuDong") && <div className="mt-3 flex justify-end" title={canDecide ? undefined : officerRoleRequired}><Button type="button" size="sm" aria-label="Xác nhận ứng viên đã chọn" onClick={() => void submitDecision({ link_ids: [selectedLinkId], decision: "confirm" })} disabled={!canDecide || decide.isPending}><Check />Xác nhận</Button></div>}
          </article>;
        })}
        <Pager page={queue.data?.page.page ?? page} perPage={queue.data?.page.per_page ?? 50} total={queue.data?.page.total ?? 0} onPageChange={(nextPage) => { setPage(nextPage); setSelectedGroups({}); setCandidateChoices({}); }} />
      </section>}

      {selectedIds.length > 0 && <div className="sticky bottom-[var(--data-footer-h)] z-10 mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-popover/95 p-3 shadow-lg backdrop-blur"><p className="text-sm font-medium"><span className="tabular-nums">{selectedIds.length}</span> lượt tên đã chọn</p><div className="flex flex-wrap gap-2" title={canDecide ? undefined : officerRoleRequired}><Button type="button" onClick={() => void submitDecision({ link_ids: selectedIds, decision: "confirm" })} disabled={!canDecide || decide.isPending}><Check />Xác nhận</Button><Button type="button" variant="destructive" onClick={() => setRejectOpen(true)} disabled={!canDecide}><UserRoundX />Bác bỏ</Button><Button type="button" variant="outline" onClick={() => setReassignOpen(true)} disabled={!canDecide}><CornerDownRight />Chuyển cho người khác</Button></div></div>}

      <Dialog open={rejectOpen} onOpenChange={setRejectOpen}><DialogContent><form onSubmit={(event) => { event.preventDefault(); if (canDecide) void submitDecision({ link_ids: selectedIds, decision: "reject", reason: reason.trim() }); }}><DialogHeader><DialogTitle>Bác bỏ liên kết tác giả</DialogTitle><DialogDescription>Nhập lý do để quyết định có thể được kiểm tra lại trong nhật ký.</DialogDescription></DialogHeader><div className="py-4"><label htmlFor="reject-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="reject-reason" required value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Nêu lý do bác bỏ…" /></div><DialogFooter><Button type="button" variant="outline" onClick={() => setRejectOpen(false)}>Huỷ</Button><Button type="submit" variant="destructive" disabled={!canDecide || decide.isPending}>Bác bỏ</Button></DialogFooter></form></DialogContent></Dialog>

      <Dialog open={reassignOpen} onOpenChange={setReassignOpen}><DialogContent><form onSubmit={(event) => { event.preventDefault(); if (canDecide && personId !== null) void submitDecision({ link_ids: selectedIds, decision: "reassign", person_id: personId, reason: reason.trim() || undefined }); }}><DialogHeader><DialogTitle>Chuyển cho người khác</DialogTitle><DialogDescription>Tìm và chọn người sẽ nhận các liên kết đã chọn.</DialogDescription></DialogHeader><div className="space-y-3 py-4"><div><label htmlFor="reassign-person" className="mb-1.5 block font-medium">Người nhận <span className="text-status-danger">*</span></label><PersonCombobox id="reassign-person" onValueChange={setPersonId} /></div><div><label htmlFor="reassign-reason" className="mb-1.5 block font-medium">Lý do (tuỳ chọn)</label><Textarea id="reassign-reason" value={reason} onChange={(event) => setReason(event.target.value)} /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setReassignOpen(false)}>Huỷ</Button><Button type="submit" disabled={!canDecide || decide.isPending || personId === null}>Chuyển</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}
