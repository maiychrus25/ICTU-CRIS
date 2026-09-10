// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AlertTriangle, ArrowUpRight, Bot, Info, SearchCheck } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { AspectMatrix } from "@/components/aspect-matrix";
import { CompareModeTabs } from "@/components/compare-mode-tabs";
import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { aspectLabels, docTypeLabels } from "@/lib/labels";
import { useComparison, useCreateComparison } from "@/lib/queries";
import type { CompareOut } from "@/lib/types";

const aspectKeys = Object.keys(aspectLabels);
const selectableDocTypes = Object.entries(docTypeLabels).slice(0, 5);

function Results({ data }: { data: CompareOut }) {
  return (
    <div className="space-y-4">
      {data.fallback && <Alert className="border-status-warning/30 bg-status-warning/10"><AlertTriangle /><AlertTitle>AI chưa bật</AlertTitle><AlertDescription>Đang dùng tìm theo từ khoá vì AI chưa bật.</AlertDescription></Alert>}
      <Alert className="border-primary/25 bg-primary/5"><Info /><AlertTitle>Phạm vi kết quả</AlertTitle><AlertDescription>{data.note}</AlertDescription></Alert>
      {!data.results.length ? <EmptyView title="Chưa có kết quả tương đồng" description="Hãy bổ sung mô tả hoặc các khía cạnh cụ thể hơn rồi đối chiếu lại." /> : data.results.map((result, index) => (
        <article key={result.work_id} className="rounded-lg border bg-card p-4 shadow-sm shadow-primary/5">
          <div className="flex items-start gap-3"><span className="grid size-7 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-semibold text-primary tabular-nums">{index + 1}</span><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><StatusBadge value={result.doc_type} kind="docType" />{result.year && <span className="text-xs text-muted-foreground tabular-nums">{result.year}</span>}{result.ai_generated && <Badge variant="outline" className="text-muted-foreground"><Bot />AI giải thích</Badge>}</div><h3 className="mt-2 text-[15px] font-semibold leading-6"><Link href={result.url ?? `/cong-trinh/?id=${result.work_id}`} className="hover:text-primary hover:underline">{result.title ?? "Chưa có tiêu đề"}<ArrowUpRight className="ml-1 inline size-3.5" /></Link></h3></div></div>
          <div className="mt-4"><AspectMatrix aspects={result.aspects} /></div>
          {result.explanation && <p className="mt-3 border-l-2 border-primary/25 pl-3 text-sm leading-6 text-muted-foreground">{result.explanation}</p>}
        </article>
      ))}
    </div>
  );
}

function CompareContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const rawId = searchParams.get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const saved = useComparison(id);
  const create = useCreateComparison();
  const [created, setCreated] = useState<CompareOut | null>(null);
  const [title, setTitle] = useState(searchParams.get("title") ?? "");
  const [description, setDescription] = useState("");
  const [aspects, setAspects] = useState<Record<string, string>>({ bai_toan: "", doi_tuong: "", pham_vi: "", phuong_phap: "" });
  const [docTypes, setDocTypes] = useState<string[]>(selectableDocTypes.map(([value]) => value));
  const output = created ?? saved.data;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (title.trim().length < 3) { toast.error("Tiêu đề cần có ít nhất 3 ký tự."); return; }
    try {
      const result = await create.mutateAsync({ title: title.trim(), description: description.trim(), aspects, doc_types: docTypes.length ? docTypes : undefined, k: 5 });
      setCreated(result);
      router.replace(`/doi-chieu/?id=${result.query_id}`);
      toast.success("Đã lưu kết quả đối chiếu để chia sẻ.");
    } catch {
      // Error detail is rendered beside the results.
    }
  }

  return (
    <>
      <PageHeader title="Đối chiếu đề tài" description="AI gợi ý các công trình liên quan theo từng khía cạnh; người dùng tự đánh giá và quyết định." />
      <CompareModeTabs active="compare" />
      <div className="grid items-start gap-6 xl:grid-cols-[390px_minmax(0,1fr)]">
        <form onSubmit={submit} className="space-y-5 rounded-lg border bg-card p-5 xl:sticky xl:top-20">
          <div><label htmlFor="compare-title" className="mb-1.5 block text-sm font-medium">Tiêu đề đề tài <span className="text-status-danger">*</span></label><Input id="compare-title" required minLength={3} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Nhập tiêu đề cần đối chiếu" /></div>
          <div><label htmlFor="compare-description" className="mb-1.5 block text-sm font-medium">Mô tả</label><Textarea id="compare-description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Mục tiêu, dữ liệu và kết quả dự kiến…" className="min-h-24" /></div>
          <fieldset><legend className="mb-2 text-sm font-medium">Bốn khía cạnh</legend><div className="space-y-3">{aspectKeys.map((key) => <div key={key}><label htmlFor={`aspect-${key}`} className="mb-1 block text-xs text-muted-foreground">{aspectLabels[key]}</label><Input id={`aspect-${key}`} value={aspects[key]} onChange={(event) => setAspects((current) => ({ ...current, [key]: event.target.value }))} placeholder={`Mô tả ${aspectLabels[key].toLocaleLowerCase("vi")}…`} /></div>)}</div></fieldset>
          <fieldset><legend className="mb-2 text-sm font-medium">Loại tài liệu</legend><div className="grid grid-cols-2 gap-2">{selectableDocTypes.map(([value, label]) => <label key={value} className="flex cursor-pointer items-center gap-2 text-sm"><Checkbox checked={docTypes.includes(value)} onCheckedChange={(checked) => setDocTypes((current) => checked ? [...current, value] : current.filter((item) => item !== value))} />{label}</label>)}</div></fieldset>
          <Button type="submit" className="w-full" disabled={create.isPending}><SearchCheck />{create.isPending ? "Đang đối chiếu…" : "Đối chiếu đề tài"}</Button>
          <p className="text-xs leading-5 text-muted-foreground">Kết quả là gợi ý hỗ trợ sàng lọc, không thay thế quyết định chuyên môn.</p>
        </form>
        <section aria-label="Kết quả đối chiếu">
          {create.isError ? <ErrorView error={create.error} retry={() => create.reset()} /> : id !== null && saved.isLoading && !created ? <LoadingView label="Đang tải kết quả đối chiếu…" /> : saved.isError && !created ? <ErrorView error={saved.error} retry={() => saved.refetch()} /> : output ? <Results data={output} /> : <EmptyView title="Sẵn sàng đối chiếu" description="Nhập tiêu đề và mô tả ở bên trái. Càng nêu rõ bốn khía cạnh, kết quả càng dễ đánh giá." />}
        </section>
      </div>
    </>
  );
}

export default function ComparePage() {
  return <Suspense fallback={<LoadingView label="Đang chuẩn bị trang đối chiếu…" />}><CompareContent /></Suspense>;
}
