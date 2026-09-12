// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { ArrowLeft, Copy, Printer } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";
import { toast } from "sonner";

import { DataNoticeFooter } from "@/components/data-notice-footer";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { usePerson, usePersonCv } from "@/lib/queries";

function CvContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const person = usePerson(id);
  const cv = usePersonCv(id);
  const content = useMemo(() => {
    if (!cv.data || typeof DOMParser === "undefined") return { body: "", citations: [] as string[] };
    const document = new DOMParser().parseFromString(cv.data, "text/html");
    document.querySelector("footer")?.remove();
    return { body: document.body.innerHTML, citations: [...document.querySelectorAll(".pub")].map((item) => item.textContent?.trim() ?? "").filter(Boolean) };
  }, [cv.data]);

  async function copyAllCitations() {
    if (!content.citations.length) return;
    try {
      await navigator.clipboard.writeText(content.citations.join("\n"));
      toast.success(`Đã sao chép ${content.citations.length} trích dẫn APA.`);
    } catch { toast.error("Không thể sao chép. Hãy chọn và sao chép thủ công."); }
  }

  if (id === null) return <main className="mx-auto max-w-3xl p-6"><EmptyView title="Chưa chọn giảng viên" description="Mở lý lịch khoa học từ một hồ sơ giảng viên." action={<Link href="/tra-cuu/" className="font-medium text-primary hover:underline">Đi đến tra cứu</Link>} /></main>;
  if (person.isLoading || cv.isLoading) return <main className="mx-auto max-w-3xl p-6"><LoadingView label="Đang dựng lý lịch khoa học…" /></main>;
  if (person.isError || cv.isError) return <main className="mx-auto max-w-3xl p-6"><ErrorView error={person.error ?? cv.error} retry={() => { void person.refetch(); void cv.refetch(); }} /></main>;
  if (!person.data || !content.body) return <main className="mx-auto max-w-3xl p-6"><EmptyView description="Không có dữ liệu lý lịch khoa học cho giảng viên này." /></main>;

  return (
    <div className="cv-page data-footer-layout min-h-screen bg-muted/40 py-5 print:bg-white print:py-0">
      <nav aria-label="Thao tác lý lịch khoa học" className="cv-toolbar mx-auto mb-4 flex max-w-[210mm] flex-wrap items-center justify-between gap-2 px-4 print:hidden">
        <Button render={<Link href={`/giang-vien/?id=${id}`} />} variant="ghost"><ArrowLeft />Về hồ sơ</Button>
        <div className="flex flex-wrap gap-2"><Button type="button" variant="outline" onClick={() => void copyAllCitations()} disabled={!content.citations.length}><Copy />Sao chép trích dẫn tất cả</Button><Button type="button" onClick={() => window.print()}><Printer />In / Lưu PDF</Button></div>
      </nav>
      <main className="cv-sheet mx-auto max-w-[210mm] bg-white px-[18mm] py-[16mm] text-neutral-950 shadow-sm print:max-w-none print:p-0 print:shadow-none">
        <article className="cv-document" dangerouslySetInnerHTML={{ __html: content.body }} />
        <DataNoticeFooter className="mt-8 px-0 text-neutral-600" />
      </main>
    </div>
  );
}

export default function PersonCvPage() {
  return <Suspense fallback={<main className="mx-auto max-w-3xl p-6"><LoadingView label="Đang mở lý lịch khoa học…" /></main>}><CvContent /></Suspense>;
}
