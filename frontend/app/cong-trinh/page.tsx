// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, BookMarked, Building2, ExternalLink, FileText, History, PenLine, UserRound } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { StatusBadge } from "@/components/status-badge";
import { WorkCitationDialog } from "@/components/work-citation-dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { getFieldValueLabel, labelSourceText, roleLabels } from "@/lib/labels";
import { useEditWorkField, useOfficerAccess, useUnits, useWork } from "@/lib/queries";
import type { FieldRow } from "@/lib/types";

const editableFields = new Set(["title", "doi", "year_issue", "journal", "volume", "pub_type_raw", "cohort", "abstract", "keywords_raw"]);

function SourceReference({ source, url }: { source: string; url?: string | null }) {
  const repositorySource = /\brepository\b|repository\.ictu\.edu\.vn/i.test(source);
  const sourceUrl = source.match(/https?:\/\/[^\s)]+/)?.[0] ?? (repositorySource ? url : null);
  const time = source.match(/(?:lúc|·)\s*(.+)$/i)?.[1];
  const label = repositorySource ? `Kho ICTU${time ? ` · ${time}` : ""}` : labelSourceText(source);
  const content = <><ExternalLink className="size-3 shrink-0 text-muted-foreground" />{label}</>;
  return sourceUrl ? <a href={sourceUrl} target="_blank" rel="noreferrer" title={source} className="inline-flex items-center gap-1.5 text-primary hover:underline">{content}</a> : <span title={source} className="inline-flex items-center gap-1.5">{content}</span>;
}

function WorkContent() {
  const rawId = useSearchParams().get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;
  const queryClient = useQueryClient();
  const query = useWork(id);
  const units = useUnits();
  const edit = useEditWorkField(id ?? 0);
  const canEdit = useOfficerAccess();
  const [editing, setEditing] = useState<FieldRow | null>(null);
  const [citationOpen, setCitationOpen] = useState(false);
  const [showMissing, setShowMissing] = useState(false);

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
  const missingFields = work.fields.filter((field) => !field.value && !field.raw && field.source === "Chưa ghi nhận nguồn");
  const visibleFields = showMissing ? work.fields : work.fields.filter((field) => !missingFields.includes(field));

  return (
    <>
      <PageHeader title="Chi tiết công trình" description="Mỗi giá trị đều có thể truy ngược về nguồn hình thành." action={<div className="flex flex-wrap gap-2"><StatusBadge value={work.doc_type} kind="docType" /><StatusBadge value={work.state} /></div>} />
      <div className="mb-7"><p className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">Mã công trình #{work.id}</p><div className="mt-2 flex flex-wrap items-center gap-2"><h2 className="max-w-4xl text-xl font-semibold leading-8">{work.title ?? "Chưa có tiêu đề"}</h2>{work.has_manual && <Badge variant="outline" className="border-primary/25 bg-primary/10 text-primary"><PenLine />Đã chỉnh tay</Badge>}</div>{work.units?.length ? <div className="mt-2 flex flex-wrap items-center gap-1.5 text-sm"><span className="mr-1 inline-flex items-center gap-1.5 text-muted-foreground"><Building2 className="size-4" />Khoa:</span>{work.units.map((unit) => <Link key={unit.id} href={`/tra-cuu/?unit=${encodeURIComponent(unit.code)}`} title={units.data?.find((item) => item.id === unit.id || item.code === unit.code)?.name}><Badge variant="outline" className="hover:border-primary hover:text-primary">{unit.code}</Badge></Link>)}</div> : null}<div className="mt-3 flex flex-wrap gap-2">{work.pdf_url && <Button render={<a href={work.pdf_url} target="_blank" rel="noreferrer" />} variant="outline"><FileText />Mở PDF ở kho</Button>}<Button type="button" variant="outline" onClick={() => setCitationOpen(true)}><BookMarked />Trích dẫn</Button></div>{work.keywords?.length ? <div className="mt-3 flex flex-wrap gap-1.5" aria-label="Từ khoá">{work.keywords.map((keyword) => <Link key={keyword} href={`/tra-cuu/?keyword=${encodeURIComponent(keyword)}`} className="max-w-full"><Badge variant="outline" className="h-auto max-w-full whitespace-normal py-1 text-left font-normal hover:border-primary hover:text-primary">{keyword}</Badge></Link>)}</div> : null}{work.needs_review && <Alert className="mt-4 border-status-warning/30 bg-status-warning/10 text-status-warning"><AlertTriangle /><AlertTitle>Cần đối soát</AlertTitle><AlertDescription>Bản ghi còn thông tin cần người dùng kiểm tra và quyết định.</AlertDescription></Alert>}</div>
      {work.has_manual && <Link href="/nhat-ky/" className="mb-7 flex items-center justify-between rounded-lg border bg-card px-4 py-3 hover:bg-muted/50"><span><strong className="block text-sm">Lịch sử chỉnh sửa</strong><span className="text-xs text-muted-foreground">Bản ghi có giá trị do người dùng chỉnh sửa; mở nhật ký để đối chiếu.</span></span><History className="size-4 text-primary" /></Link>}
      <section className="mb-8" aria-labelledby="provenance-title">
        <div className="mb-3"><h2 id="provenance-title" className="text-base font-semibold">Xuất xứ dữ liệu</h2><p className="text-xs text-muted-foreground">So sánh giá trị đang sử dụng với dữ liệu gốc từ từng nguồn.</p></div>
        {work.fields.length ? <><div className="hidden overflow-hidden rounded-lg border bg-card md:block"><Table><TableHeader><TableRow><TableHead>Trường</TableHead><TableHead>Giá trị đang dùng</TableHead><TableHead>Giá trị gốc</TableHead><TableHead>Nguồn</TableHead></TableRow></TableHeader><TableBody>{visibleFields.map((field) => <TableRow key={field.field}><TableCell className="font-medium"><span className="inline-flex items-center gap-1.5">{field.label}{canEdit && editableFields.has(field.field) && <Button type="button" variant="ghost" size="icon-xs" aria-label={`Chỉnh sửa ${field.label}`} onClick={() => setEditing(field)}><PenLine /></Button>}</span></TableCell><TableCell className="max-w-sm whitespace-normal break-words">{field.value ? getFieldValueLabel(field.field, field.value) : "—"}</TableCell><TableCell className="max-w-sm whitespace-normal break-words text-muted-foreground">{field.raw ?? "—"}</TableCell><TableCell className="max-w-xs whitespace-normal text-xs"><SourceReference source={field.source} url={work.source_url} /></TableCell></TableRow>)}</TableBody></Table></div><div className="space-y-3 md:hidden">{visibleFields.map((field) => <article key={field.field} className="rounded-lg border bg-card p-4"><div className="flex items-center justify-between gap-2"><h3 className="font-semibold">{field.label}</h3>{canEdit && editableFields.has(field.field) && <Button type="button" variant="ghost" size="icon-sm" aria-label={`Chỉnh sửa ${field.label}`} onClick={() => setEditing(field)}><PenLine /></Button>}</div><dl className="mt-3 grid gap-3"><div><dt className="text-xs text-muted-foreground">Đang dùng</dt><dd className="mt-0.5 break-words">{field.value ? getFieldValueLabel(field.field, field.value) : "—"}</dd></div><div><dt className="text-xs text-muted-foreground">Gốc</dt><dd className="mt-0.5 break-words">{field.raw ?? "—"}</dd></div><div><dt className="text-xs text-muted-foreground">Nguồn</dt><dd className="mt-0.5 text-xs"><SourceReference source={field.source} url={work.source_url} /></dd></div></dl></article>)}</div>{missingFields.length > 0 && <Button type="button" variant="ghost" size="sm" className="mt-2" aria-expanded={showMissing} onClick={() => setShowMissing((current) => !current)}>{showMissing ? "Ẩn" : "Hiện"} {missingFields.length} trường chưa có dữ liệu</Button>}</> : <EmptyView description="Bản ghi chưa có thông tin xuất xứ. Hãy chờ lần đồng bộ tiếp theo." />}
        <p className="mt-2 text-xs text-muted-foreground">Tác giả, khoa, minh chứng không sửa ở đây — sai thì trả về khoa.</p>
      </section>
      <section aria-labelledby="authors-title">
        <div className="mb-3"><h2 id="authors-title" className="text-base font-semibold">Tác giả</h2><p className="text-xs text-muted-foreground">Liên kết tác giả chỉ có hiệu lực sau khi hệ thống hoặc người dùng xác nhận.</p></div>
        {work.mentions.length ? <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Vị trí</TableHead><TableHead>Tên trong nguồn</TableHead><TableHead>Vai trò</TableHead><TableHead>Giảng viên liên kết</TableHead><TableHead>Trạng thái</TableHead><TableHead>Ứng viên chờ</TableHead></TableRow></TableHeader><TableBody>{work.mentions.map((mention) => <TableRow key={mention.mention_id}><TableCell className="tabular-nums">{mention.position}</TableCell><TableCell className="font-medium">{mention.raw_name}</TableCell><TableCell>{roleLabels[mention.role] ?? mention.role_label}</TableCell><TableCell>{mention.linked_person_id ? <Link href={`/giang-vien/?id=${mention.linked_person_id}`} className="inline-flex items-center gap-1.5 text-primary hover:underline"><UserRound className="size-3.5" />{mention.linked_person_name}</Link> : "Chưa liên kết"}</TableCell><TableCell>{mention.link_state ? <StatusBadge value={mention.link_state} /> : "—"}</TableCell><TableCell className="tabular-nums">{mention.pending_count}</TableCell></TableRow>)}</TableBody></Table></div> : <EmptyView description="Chưa có tác giả trong nguồn. Hãy kiểm tra lại bản ghi gốc." />}
      </section>
      <Dialog open={editing !== null} onOpenChange={(open) => { if (!open) setEditing(null); }}><DialogContent className="sm:max-w-xl"><form key={editing?.field} onSubmit={(event) => void submitEdit(event)}><DialogHeader><DialogTitle>Chỉnh {editing?.label.toLocaleLowerCase("vi")}</DialogTitle><DialogDescription>Giá trị mới sẽ được lưu cùng người chỉnh, thời điểm và lý do để bảo toàn xuất xứ.</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div><label htmlFor="field-current" className="mb-1.5 block font-medium">Giá trị hiện tại</label><Textarea id="field-current" value={editing?.value ?? ""} readOnly className="min-h-20 bg-muted" /></div><div><label htmlFor="field-new" className="mb-1.5 block font-medium">Giá trị mới <span className="text-status-danger">*</span></label>{editing && ["abstract", "keywords_raw"].includes(editing.field) ? <Textarea id="field-new" name="value" required defaultValue={editing.value ?? ""} className="min-h-28" /> : <Input id="field-new" name="value" required defaultValue={editing?.value ?? ""} inputMode={editing?.field === "year_issue" ? "numeric" : undefined} />}</div><div><label htmlFor="field-reason" className="mb-1.5 block font-medium">Lý do <span className="text-status-danger">*</span></label><Textarea id="field-reason" name="reason" required placeholder="Nêu nguồn đối chiếu hoặc lý do cần sửa…" /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setEditing(null)}>Huỷ</Button><Button type="submit" disabled={!canEdit || edit.isPending}>Lưu chỉnh sửa</Button></DialogFooter></form></DialogContent></Dialog>
      <WorkCitationDialog workId={work.id} open={citationOpen} onOpenChange={setCitationOpen} />
    </>
  );
}

export default function WorkPage() {
  return <Suspense fallback={<LoadingView label="Đang tải chi tiết công trình…" />}><WorkContent /></Suspense>;
}
