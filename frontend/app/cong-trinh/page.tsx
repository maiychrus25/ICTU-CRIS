// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ExternalLink, History, PenLine, UserRound } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { getFieldValueLabel, labelSourceText, roleLabels } from "@/lib/labels";
import { useEditWorkField, useOfficerAccess, useWork } from "@/lib/queries";
import type { FieldRow } from "@/lib/types";

const editableFields = new Set(["title", "doi", "year_issue", "journal", "volume", "pub_type_raw", "cohort", "abstract", "keywords_raw"]);

function WorkContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const queryClient = useQueryClient();
  const query = useWork(id);
  const edit = useEditWorkField(id ?? 0);
  const canEdit = useOfficerAccess();
  const [editing, setEditing] = useState<FieldRow | null>(null);

  async function submitEdit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editing || id === null || !canEdit) return;
    const form = new FormData(event.currentTarget);
    try {
      await edit.mutateAsync({ field: editing.field, value: String(form.get("value")), reason: String(form.get("reason")).trim() });
      await queryClient.invalidateQueries({ queryKey: ["work", id] });
      toast.success(`Đã chỉnh trường ${editing.label.toLocaleLowerCase("vi")}.`);
      setEditing(null);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể chỉnh dữ liệu công trình.");
    }
  }

  if (id === null) return <><PageHeader title="Chi tiết công trình" description="Xem dữ liệu đang dùng và xuất xứ của từng trường." /><EmptyView title="Chưa chọn công trình" description="Mở một công trình từ trang tra cứu để xem chi tiết." action={<Link className="text-sm font-medium text-primary hover:underline" href="/tra-cuu/">Đi đến tra cứu</Link>} /></>;
  if (query.isLoading) return <><PageHeader title="Chi tiết công trình" /><LoadingView /></>;
  if (query.isError) return <><PageHeader title="Chi tiết công trình" /><ErrorView error={query.error} retry={() => query.refetch()} /></>;
  if (!query.data) return <><PageHeader title="Chi tiết công trình" /><EmptyView description="Bản ghi này không còn tồn tại. Hãy quay lại trang tra cứu." /></>;
  const work = query.data;

  return (
    <>
      <PageHeader title="Chi tiết công trình" description="Mỗi giá trị đều có thể truy ngược về nguồn hình thành." action={<div className="flex flex-wrap gap-2"><StatusBadge value={work.doc_type} kind="docType" /><StatusBadge value={work.state} /></div>} />
      <div className="mb-7"><p className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">Mã công trình #{work.id}</p><div className="mt-2 flex flex-wrap items-center gap-2"><h2 className="max-w-4xl text-xl font-semibold leading-8">{work.title ?? "Chưa có tiêu đề"}</h2>{work.has_manual && <Badge variant="outline" className="border-primary/25 bg-primary/10 text-primary"><PenLine />Đã chỉnh tay</Badge>}</div>{work.needs_review && <Alert className="mt-4 border-status-warning/30 bg-status-warning/10 text-status-warning"><AlertTriangle /><AlertTitle>Cần đối soát</AlertTitle><AlertDescription>Bản ghi còn thông tin cần người dùng kiểm tra và quyết định.</AlertDescription></Alert>}</div>
      {work.has_manual && <Link href="/nhat-ky/" className="mb-7 flex items-center justify-between rounded-lg border bg-card px-4 py-3 hover:bg-muted/50"><span><strong className="block text-sm">Lịch sử chỉnh sửa</strong><span className="text-xs text-muted-foreground">Bản ghi có giá trị do người dùng chỉnh sửa; mở nhật ký để đối chiếu.</span></span><History className="size-4 text-primary" /></Link>}
      <section className="mb-8" aria-labelledby="provenance-title">
        <div className="mb-3"><h2 id="provenance-title" className="text-base font-semibold">Xuất xứ dữ liệu</h2><p className="text-xs text-muted-foreground">So sánh giá trị đang sử dụng với dữ liệu gốc từ từng nguồn.</p></div>
        {work.fields.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Trường</TableHead><TableHead>Giá trị đang dùng</TableHead><TableHead>Giá trị gốc</TableHead><TableHead>Nguồn</TableHead></TableRow></TableHeader><TableBody>{work.fields.map((field) => <TableRow key={field.field}><TableCell className="font-medium"><span className="inline-flex items-center gap-1.5">{field.label}{canEdit && editableFields.has(field.field) && <Button type="button" variant="ghost" size="icon-xs" aria-label={`Chỉnh sửa ${field.label}`} onClick={() => setEditing(field)}><PenLine /></Button>}</span></TableCell><TableCell className="max-w-sm whitespace-normal">{field.value ? getFieldValueLabel(field.field, field.value) : "—"}</TableCell><TableCell className="max-w-sm whitespace-normal text-muted-foreground">{field.raw ?? "—"}</TableCell><TableCell className="max-w-xs whitespace-normal text-xs"><span className="inline-flex items-start gap-1.5"><ExternalLink className="mt-0.5 size-3 shrink-0 text-muted-foreground" />{labelSourceText(field.source)}</span></TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Bản ghi chưa có thông tin xuất xứ. Hãy chờ lần đồng bộ tiếp theo." />}
        <p className="mt-2 text-xs text-muted-foreground">Tác giả, đơn vị, minh chứng không sửa ở đây — sai thì trả về khoa.</p>
      </section>
      <section aria-labelledby="authors-title">
        <div className="mb-3"><h2 id="authors-title" className="text-base font-semibold">Tác giả</h2><p className="text-xs text-muted-foreground">Liên kết tác giả chỉ có hiệu lực sau khi hệ thống hoặc người dùng xác nhận.</p></div>
        {work.mentions.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Vị trí</TableHead><TableHead>Tên trong nguồn</TableHead><TableHead>Vai trò</TableHead><TableHead>Giảng viên liên kết</TableHead><TableHead>Trạng thái</TableHead><TableHead>Ứng viên chờ</TableHead></TableRow></TableHeader><TableBody>{work.mentions.map((mention) => <TableRow key={mention.mention_id}><TableCell className="tabular-nums">{mention.position}</TableCell><TableCell className="font-medium">{mention.raw_name}</TableCell><TableCell>{roleLabels[mention.role] ?? mention.role_label}</TableCell><TableCell>{mention.linked_person_id ? <Link href={`/giang-vien/?id=${mention.linked_person_id}`} className="inline-flex items-center gap-1.5 text-primary hover:underline"><UserRound className="size-3.5" />{mention.linked_person_name}</Link> : "Chưa liên kết"}</TableCell><TableCell>{mention.link_state ? <StatusBadge value={mention.link_state} /> : "—"}</TableCell><TableCell className="tabular-nums">{mention.pending_count}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Chưa có tác giả trong nguồn. Hãy kiểm tra lại bản ghi gốc." />}
      </section>
      <Dialog open={editing !== null} onOpenChange={(open) => { if (!open) setEditing(null); }}><DialogContent className="sm:max-w-xl"><form key={editing?.field} onSubmit={(event) => void submitEdit(event)}><DialogHeader><DialogTitle>Chỉnh {editing?.label.toLocaleLowerCase("vi")}</DialogTitle><DialogDescription>Giá trị mới sẽ được lưu cùng người chỉnh, thời điểm và lý do để bảo toàn xuất xứ.</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div><label htmlFor="field-current" className="mb-1.5 block font-medium">Giá trị hiện tại</label><Textarea id="field-current" value={editing?.value ?? ""} readOnly className="min-h-20 bg-muted" /></div><div><label htmlFor="field-new" className="mb-1.5 block font-medium">Giá trị mới <span className="text-status-danger">*</span></label>{editing && ["abstract", "keywords_raw"].includes(editing.field) ? <Textarea id="field-new" name="value" required defaultValue={editing.value ?? ""} className="min-h-28" /> : <Input id="field-new" name="value" required defaultValue={editing?.value ?? ""} inputMode={editing?.field === "year_issue" ? "numeric" : undefined} />}</div><div><label htmlFor="field-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="field-reason" name="reason" required placeholder="Nêu nguồn đối chiếu hoặc lý do cần sửa…" /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setEditing(null)}>Huỷ</Button><Button type="submit" disabled={!canEdit || edit.isPending}>Lưu chỉnh sửa</Button></DialogFooter></form></DialogContent></Dialog>
    </>
  );
}

export default function WorkPage() {
  return <Suspense fallback={<LoadingView label="Đang tải chi tiết công trình…" />}><WorkContent /></Suspense>;
}
