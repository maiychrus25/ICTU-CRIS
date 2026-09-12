// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { ArrowRight, BookOpenCheck, Info, SearchCheck, UserRound } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { EmptyView, LoadingView } from "@/components/state-views";
import { DataNoticeFooter } from "@/components/data-notice-footer";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useCheckPublicTopic } from "@/lib/queries";
import type { PublicTopicCheckOut } from "@/lib/types";
import { cn } from "@/lib/utils";

const levelText = { cao: "Cao", vua: "Vừa", thap: "Thấp" } as const;
const levelStyle = { cao: "border-status-danger/30 bg-status-danger/10 text-status-danger", vua: "border-status-warning/30 bg-status-warning/10 text-status-warning", thap: "border-status-success/30 bg-status-success/10 text-status-success" } as const;

function Results({ data }: { data: PublicTopicCheckOut }) {
  return <section aria-label="Kết quả kiểm tra đề tài" className="mt-8">
    <Alert className="mb-5 border-primary/25 bg-primary/5"><Info /><AlertTitle>Phạm vi kiểm tra</AlertTitle><AlertDescription>{data.note}</AlertDescription></Alert>
    <div className="grid items-start gap-6 lg:grid-cols-2">
      <div><h2 className="text-lg font-semibold">Đề tài tương tự các khoá trước</h2><p className="mb-3 mt-1 text-sm text-muted-foreground">Mức cao là rất giống, nên đổi hướng hoặc trao đổi với GVHD.</p>{data.similar.length ? <div className="space-y-3">{data.similar.map((work) => <article key={work.work_id} className="rounded-lg border bg-card p-4"><div className="mb-2 flex flex-wrap items-center gap-2"><Badge variant="outline" className={cn(levelStyle[work.level])}>{levelText[work.level]}</Badge><span className="text-xs text-muted-foreground">Khoá {work.cohort ?? "—"} · {work.year ?? "Chưa rõ năm"}</span></div><h3 className="font-medium leading-6">{work.title ?? "Chưa có tiêu đề"}</h3></article>)}</div> : <EmptyView title="Chưa thấy đề tài tương tự" description="Bạn vẫn nên trao đổi hướng nghiên cứu với giảng viên hướng dẫn." />}</div>
      <div><h2 className="text-lg font-semibold">Giảng viên gần chuyên môn</h2><p className="mb-3 mt-1 text-sm text-muted-foreground">Danh sách chỉ hiển thị thông tin chuyên môn công khai.</p>{data.experts.length ? <div className="overflow-hidden rounded-lg border bg-card divide-y">{data.experts.map((person) => <article key={person.person_id} className="flex items-center gap-3 p-4"><span className="grid size-9 place-items-center rounded-full bg-primary/10 text-primary"><UserRound className="size-4" /></span><div><h3 className="font-medium">{person.display_name}</h3><p className="text-sm text-muted-foreground">{person.degree ?? "Chưa rõ học vị"} · {person.unit_code ?? "Chưa rõ đơn vị"}</p></div></article>)}</div> : <EmptyView title="Chưa có giảng viên phù hợp" description="Hãy bổ sung mô tả cụ thể hơn rồi kiểm tra lại." />}</div>
    </div>
  </section>;
}

export default function PublicTopicPage() {
  const check = useCheckPublicTopic();
  const [result, setResult] = useState<PublicTopicCheckOut | null>(null);
  const error = check.error instanceof ApiError && check.error.status === 429 ? "Bạn đã kiểm tra nhiều lần, thử lại sau 5 phút" : check.error instanceof ApiError ? check.error.detail : check.isError ? "Không thể kiểm tra lúc này. Hãy thử lại." : "";

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try { setResult(await check.mutateAsync({ title: String(form.get("title")).trim(), description: String(form.get("description")).trim() || undefined })); }
    catch { setResult(null); }
  }

  return <div className="data-footer-layout flex min-h-screen flex-col bg-background">
    <header className="border-b bg-card"><div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 md:px-6"><Link href="/kiem-tra-de-tai/" className="flex items-center gap-3"><span className="grid size-9 place-items-center rounded-lg bg-primary text-primary-foreground"><BookOpenCheck className="size-5" /></span><span><strong className="block text-sm">ICTU-CRIS</strong><span className="text-xs text-muted-foreground">Cổng kiểm tra đề tài</span></span></Link><Button render={<Link href="/tong-quan/" />} variant="outline">Vào hệ thống<ArrowRight /></Button></div></header>
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-10 md:px-6 md:py-14">
      <div className="mx-auto max-w-3xl text-center"><p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Dành cho sinh viên ICTU</p><h1 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">Kiểm tra đề tài trước khi đăng ký</h1><p className="mx-auto mt-3 max-w-2xl text-muted-foreground">Nhanh chóng xem đề tài gần với các khoá trước và giảng viên có chuyên môn liên quan. Không cần đăng nhập.</p></div>
      <form onSubmit={(event) => void submit(event)} className="mx-auto mt-8 max-w-3xl space-y-4 rounded-xl border bg-card p-5 shadow-sm md:p-6"><div><label htmlFor="topic-title" className="mb-1.5 block font-medium">Tên đề tài dự định <span className="text-status-danger">*</span></label><Input id="topic-title" name="title" required minLength={5} className="h-12 text-base" placeholder="Ví dụ: Xây dựng ứng dụng hỗ trợ trẻ em luyện phát âm" autoFocus /></div><div><label htmlFor="topic-description" className="mb-1.5 block font-medium">Mô tả <span className="font-normal text-muted-foreground">(tuỳ chọn)</span></label><Textarea id="topic-description" name="description" className="min-h-28" placeholder="Nêu mục tiêu, đối tượng và cách thực hiện dự kiến…" /></div>{error && <Alert variant="destructive"><AlertTitle>Chưa thể kiểm tra</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}<Button type="submit" size="lg" className="w-full" disabled={check.isPending}><SearchCheck />{check.isPending ? "Đang kiểm tra…" : "Kiểm tra"}</Button></form>
      {check.isPending ? <div className="mt-8"><LoadingView label="Đang đối chiếu đề tài và chuyên môn giảng viên…" /></div> : result ? <Results data={result} /> : !check.isError && <div className="mx-auto mt-8 max-w-3xl"><EmptyView title="Sẵn sàng kiểm tra" description="Nhập tên đề tài càng cụ thể, kết quả càng dễ tham khảo." /></div>}
    </main>
    <p className="border-t px-4 py-3 text-center text-xs text-muted-foreground">AI chạy cục bộ trên dữ liệu tóm tắt; kết quả không thay thế trao đổi với giảng viên hướng dẫn.</p>
    <DataNoticeFooter />
  </div>;
}
