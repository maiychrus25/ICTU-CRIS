// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useTopics } from "@/lib/queries";

export default function TopicsPage() {
  const query = useTopics();
  const topics = [...(query.data ?? [])].sort((left, right) => right.size - left.size);

  return (
    <>
      <PageHeader title="Chủ đề nghiên cứu" description="Khám phá các cụm công trình theo từ khoá nổi bật trong kho dữ liệu." />
      <Alert className="mb-5"><Sparkles /><AlertDescription>Cụm chủ đề do AI gom từ từ khoá (k-means, 40 cụm) — nhãn là từ khoá nặng nhất, chỉ để định hướng.</AlertDescription></Alert>
      {query.isLoading ? <LoadingView label="Đang tải các cụm chủ đề…" />
        : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} />
        : !topics.length ? <EmptyView title="Chưa có cụm chủ đề" description="Hãy chạy quy trình phân tích chủ đề rồi tải lại trang." />
        : <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{topics.map((topic) => (
          <Link key={topic.id} href={`/chu-de/chi-tiet/?id=${topic.id}`} aria-label={`${topic.label} — ${topic.size} công trình`} className="rounded-xl focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none">
            <Card className="h-full transition-colors hover:bg-muted/40">
              <CardHeader><CardTitle>{topic.label}</CardTitle></CardHeader>
              <CardContent className="flex flex-1 flex-wrap content-start gap-1.5">{topic.keywords.map((keyword) => <Badge key={keyword} variant="secondary" className="font-normal">{keyword}</Badge>)}</CardContent>
              <CardFooter className="justify-between text-xs text-muted-foreground"><span className="tabular-nums">{topic.size} công trình</span><ArrowRight className="size-4 text-primary" /></CardFooter>
            </Card>
          </Link>
        ))}</div>}
    </>
  );
}
