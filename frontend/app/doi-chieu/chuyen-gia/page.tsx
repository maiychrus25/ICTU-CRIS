// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AlertTriangle, ArrowUpRight, Clipboard, Info, Search, Share2, X } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { toast } from "sonner";

import { CompareModeTabs } from "@/components/compare-mode-tabs";
import { PageHeader } from "@/components/page-header";
import { PersonCombobox } from "@/components/person-combobox";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useExperts, useFindExperts, useStats } from "@/lib/queries";
import type { ExpertOut, PersonSearchRow } from "@/lib/types";

function ExpertResults({ data }: { data: ExpertOut }) {
  const maximum = Math.max(...data.results.map((item) => item.score), 1);

  async function copyList() {
    const text = data.results.map((item, index) => `${index + 1}. ${item.display_name} — ${item.degree ?? "Chưa rõ học vị"}, ${item.unit_code ?? "Chưa rõ đơn vị"} (${item.works_matched} bài liên quan)`).join("\n");
    try { await navigator.clipboard.writeText(text); toast.success("Đã sao chép danh sách chuyên gia."); }
    catch { toast.error("Không thể sao chép danh sách."); }
  }

  async function share() {
    const url = window.location.href;
    try {
      if (navigator.share) await navigator.share({ title: "Gợi ý chuyên gia ICTU-CRIS", url });
      else { await navigator.clipboard.writeText(url); toast.success("Đã sao chép liên kết chia sẻ."); }
    } catch { /* Người dùng có thể huỷ bảng chia sẻ. */ }
  }

  return <div className="space-y-4">
    <div className="flex flex-wrap justify-end gap-2"><Button type="button" variant="outline" onClick={() => void copyList()}><Clipboard />Sao chép danh sách</Button><Button type="button" variant="outline" onClick={() => void share()}><Share2 />Chia sẻ</Button></div>
    {data.fallback && <Alert className="border-status-warning/30 bg-status-warning/10"><AlertTriangle /><AlertTitle>AI chưa bật</AlertTitle><AlertDescription>Kết quả đang dùng phương án tìm theo từ khoá.</AlertDescription></Alert>}
    <Alert className="border-primary/25 bg-primary/5"><Info /><AlertTitle>Phạm vi gợi ý</AlertTitle><AlertDescription>{data.note}</AlertDescription></Alert>
    {!data.results.length ? <EmptyView title="Chưa tìm thấy chuyên gia phù hợp" description="Hãy bổ sung mô tả chuyên môn hoặc nới bộ lọc rồi tìm lại." /> : data.results.map((person, index) => {
      const relative = Math.round(person.score / maximum * 100);
      return <article key={person.person_id} className="rounded-lg border bg-card p-4">
        <div className="flex items-start gap-3"><span className="grid size-8 shrink-0 place-items-center rounded-full bg-primary/10 font-semibold text-primary tabular-nums">{index + 1}</span><div className="min-w-0 flex-1"><Link href={`/giang-vien/?id=${person.person_id}`} className="text-base font-semibold hover:text-primary hover:underline">{person.display_name}<ArrowUpRight className="ml-1 inline size-4" /></Link><p className="mt-0.5 text-sm text-muted-foreground">{person.degree ?? "Chưa rõ học vị"} · {person.unit_code ?? "Chưa rõ đơn vị"}</p></div><Badge variant="outline">{person.works_matched} bài liên quan</Badge></div>
        <div className="mt-4"><div className="mb-1 flex justify-between text-xs text-muted-foreground"><span>Mức phù hợp tương đối</span><span className="tabular-nums">{relative}%</span></div><div className="h-2 overflow-hidden rounded-full bg-muted" role="progressbar" aria-label={`Mức phù hợp tương đối ${relative} phần trăm`} aria-valuenow={relative} aria-valuemin={0} aria-valuemax={100}><div className="h-full rounded-full bg-primary" style={{ width: `${relative}%` }} /></div></div>
        <div className="mt-4 border-t pt-3"><h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Ba dẫn chứng gần nhất</h3><ol className="space-y-2">{person.evidence.slice(0, 3).map((work) => <li key={work.work_id} className="flex items-start justify-between gap-3 text-sm"><Link href={`/cong-trinh/?id=${work.work_id}`} className="hover:text-primary hover:underline">{work.title ?? "Chưa có tiêu đề"}</Link><span className="shrink-0 tabular-nums text-muted-foreground">{work.score.toFixed(2)}</span></li>)}</ol></div>
      </article>;
    })}
  </div>;
}

function ExpertsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const rawId = searchParams.get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const saved = useExperts(id);
  const find = useFindExperts();
  const stats = useStats();
  const [created, setCreated] = useState<ExpertOut | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [degree, setDegree] = useState("all");
  const [unit, setUnit] = useState("all");
  const [excluded, setExcluded] = useState<PersonSearchRow[]>([]);
  // Chỉ bật nút sau khi hydrate: bấm trước đó sẽ submit form theo kiểu HTML (tải lại trang với "?"),
  // mất mutation — thấy trên CI chậm.
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const timeout = window.setTimeout(() => setReady(true), 0);
    return () => window.clearTimeout(timeout);
  }, []);
  const output = created ?? saved.data;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    try {
      const data = await find.mutateAsync({ title: title.trim(), description: description.trim() || undefined, k: 10, min_degree: degree === "all" ? null : degree as "TS" | "ThS", unit: unit === "all" ? undefined : Number(unit), exclude_person_ids: excluded.map((person) => person.id), recent_years: 3 });
      setCreated(data); router.replace(`/doi-chieu/chuyen-gia/?id=${data.query_id}`); toast.success("Đã tạo danh sách chuyên gia để chia sẻ.");
    } catch { /* Error detail is rendered below. */ }
  }

  return <>
    <PageHeader title="Tìm chuyên gia" description="Tìm giảng viên gần chuyên môn từ các công trình đã công bố; điểm chỉ có ý nghĩa tương đối trong danh sách." />
    <CompareModeTabs active="experts" />
    <div className="grid items-start gap-6 xl:grid-cols-[390px_minmax(0,1fr)]">
      <form onSubmit={(event) => void submit(event)} className="space-y-4 rounded-lg border bg-card p-5 xl:sticky xl:top-20">
        <div><label htmlFor="expert-title" className="mb-1.5 block font-medium">Tiêu đề đề tài <span className="text-status-danger">*</span></label><Input id="expert-title" required minLength={3} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Ví dụ: Ứng dụng AI hỗ trợ học phát âm" /></div>
        <div><label htmlFor="expert-description" className="mb-1.5 block font-medium">Mô tả</label><Textarea id="expert-description" value={description} onChange={(event) => setDescription(event.target.value)} className="min-h-28" placeholder="Nêu bài toán, đối tượng và phương pháp dự kiến…" /></div>
        <details className="rounded-md border px-3 py-2"><summary className="cursor-pointer font-medium">Bộ lọc nâng cao</summary><div className="mt-3 space-y-3 border-t pt-3">
          <div className="grid grid-cols-2 gap-3"><div><label className="mb-1 block text-xs font-medium">Học vị tối thiểu</label><Select value={degree} onValueChange={(value) => setDegree(String(value))}><SelectTrigger aria-label="Học vị tối thiểu" className="w-full"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">Không giới hạn</SelectItem><SelectItem value="ThS">Thạc sĩ</SelectItem><SelectItem value="TS">Tiến sĩ</SelectItem></SelectContent></Select></div><div><label className="mb-1 block text-xs font-medium">Đơn vị</label><Select value={unit} onValueChange={(value) => setUnit(String(value))}><SelectTrigger aria-label="Đơn vị chuyên gia" className="w-full"><SelectValue>{(value) => value === "all" ? "Tất cả" : stats.data?.by_unit.find((item) => item.unit_id === Number(value))?.code}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">Tất cả</SelectItem>{stats.data?.by_unit.map((item) => <SelectItem key={item.unit_id} value={String(item.unit_id)}>{item.code} — {item.name}</SelectItem>)}</SelectContent></Select></div></div>
          <div><label htmlFor="exclude-person" className="mb-1 block text-xs font-medium">Loại trừ giảng viên</label><PersonCombobox id="exclude-person" onValueChange={() => undefined} onSelect={(person) => setExcluded((current) => current.some((item) => item.id === person.id) ? current : [...current, person])} /><div className="mt-2 flex flex-wrap gap-1">{excluded.map((person) => <Badge key={person.id} variant="outline">{person.display_name}<button type="button" aria-label={`Bỏ ${person.display_name}`} onClick={() => setExcluded((current) => current.filter((item) => item.id !== person.id))}><X className="size-3" /></button></Badge>)}</div></div>
          <p className="text-xs text-muted-foreground">Ưu tiên công trình trong 3 năm gần đây.</p>
        </div></details>
        <Button type="submit" className="w-full" disabled={!ready || find.isPending}><Search />{find.isPending ? "Đang tìm…" : "Tìm chuyên gia"}</Button>
      </form>
      <section aria-label="Kết quả tìm chuyên gia">{find.isError ? <ErrorView error={find.error} retry={() => find.reset()} /> : id !== null && saved.isLoading && !created ? <LoadingView label="Đang tải danh sách chuyên gia…" /> : saved.isError && !created ? <ErrorView error={saved.error} retry={() => saved.refetch()} /> : output ? <ExpertResults data={output} /> : <EmptyView title="Sẵn sàng tìm chuyên gia" description="Nhập tiêu đề đề tài để nhận danh sách xếp hạng và dẫn chứng liên quan." />}</section>
    </div>
  </>;
}

export default function ExpertsPage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị trang tìm chuyên gia…" />}><ExpertsContent /></Suspense>;
}
