// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { CalendarPlus, ExternalLink } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useOpenPeriod, usePeriods } from "@/lib/queries";

const defaultScope = '{"doc_types":["bai_bao"]}';

function formatDate(value: string | null) {
  return value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Chưa mở";
}

export default function PeriodsPage() {
  const queryClient = useQueryClient();
  const query = usePeriods();
  const mutation = useOpenPeriod();
  const [open, setOpen] = useState(false);
  const [scope, setScope] = useState(defaultScope);
  const [scopeError, setScopeError] = useState("");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    let parsedScope: unknown;
    try { parsedScope = JSON.parse(scope); } catch { setScopeError("Phạm vi phải là JSON hợp lệ."); return; }
    if (!parsedScope || typeof parsedScope !== "object" || Array.isArray(parsedScope)) { setScopeError("Phạm vi phải là một đối tượng JSON."); return; }
    setScopeError("");
    try {
      const created = await mutation.mutateAsync({
        code: String(form.get("code")).trim(), name: String(form.get("name")).trim(),
        scope: parsedScope as Record<string, unknown>, criteria: String(form.get("criteria")).trim() || null,
        due_at: new Date(String(form.get("due_at"))).toISOString(),
      });
      queryClient.setQueryData(["periods"], (current: typeof query.data) => current ? [created, ...current] : [created]);
      toast.success("Đã mở kỳ báo cáo mới.");
      setOpen(false);
      setScope(defaultScope);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.detail : "Không thể mở kỳ báo cáo.");
    }
  }

  return (
    <>
      <PageHeader title="Kỳ báo cáo" description="Theo dõi các kỳ kê khai công trình và thời hạn nộp của toàn trường." action={<Button type="button" onClick={() => setOpen(true)}><CalendarPlus />Mở kỳ mới</Button>} />
      {query.isLoading ? <LoadingView /> : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} /> : !query.data?.length ? <EmptyView title="Chưa có kỳ báo cáo" description="Mở kỳ mới để các đơn vị bắt đầu kê khai công trình." action={<Button type="button" variant="outline" onClick={() => setOpen(true)}>Mở kỳ mới</Button>} /> : <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Mã</TableHead><TableHead>Tên kỳ</TableHead><TableHead>Trạng thái</TableHead><TableHead>Hạn nộp</TableHead><TableHead>Ngày mở</TableHead><TableHead><span className="sr-only">Mở</span></TableHead></TableRow></TableHeader><TableBody>{query.data.map((period) => <TableRow key={period.id}><TableCell className="font-semibold tabular-nums">{period.code}</TableCell><TableCell><Link href={`/ky-bao-cao/chi-tiet/?id=${period.id}`} className="font-medium text-primary hover:underline">{period.name}</Link></TableCell><TableCell><StatusBadge value={period.state} /></TableCell><TableCell className="whitespace-nowrap tabular-nums">{formatDate(period.due_at)}</TableCell><TableCell className="whitespace-nowrap text-muted-foreground tabular-nums">{formatDate(period.opens_at)}</TableCell><TableCell><Button render={<Link href={`/ky-bao-cao/chi-tiet/?id=${period.id}`} aria-label={`Mở ${period.name}`} />} variant="ghost" size="icon-sm"><ExternalLink /></Button></TableCell></TableRow>)}</TableBody></Table></div>}

      <Dialog open={open} onOpenChange={setOpen}><DialogContent className="sm:max-w-xl"><form onSubmit={submit}><DialogHeader><DialogTitle>Mở kỳ báo cáo mới</DialogTitle><DialogDescription>Kỳ được mở ngay sau khi tạo. Kiểm tra phạm vi và hạn nộp trước khi xác nhận.</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div className="grid gap-4 sm:grid-cols-2"><div><label htmlFor="period-code" className="mb-1.5 block font-medium">Mã kỳ <span className="text-status-danger">*</span></label><Input id="period-code" name="code" required /></div><div><label htmlFor="period-name" className="mb-1.5 block font-medium">Tên kỳ <span className="text-status-danger">*</span></label><Input id="period-name" name="name" required /></div></div><div><label htmlFor="period-scope" className="mb-1.5 block font-medium">Phạm vi (JSON) <span className="text-status-danger">*</span></label><Textarea id="period-scope" required value={scope} onChange={(event) => setScope(event.target.value)} aria-invalid={Boolean(scopeError)} />{scopeError && <p className="mt-1 text-xs text-status-danger">{scopeError}</p>}</div><div><label htmlFor="period-criteria" className="mb-1.5 block font-medium">Tiêu chí (tuỳ chọn)</label><Textarea id="period-criteria" name="criteria" /></div><div><label htmlFor="period-due-at" className="mb-1.5 block font-medium">Hạn nộp <span className="text-status-danger">*</span></label><Input id="period-due-at" name="due_at" type="datetime-local" required /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setOpen(false)}>Huỷ</Button><Button type="submit" disabled={mutation.isPending}>Mở kỳ</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}
