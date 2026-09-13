// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useAddUnitAlias, useMe, useRenameUnit, useUnits } from "@/lib/queries";
import type { Unit } from "@/lib/types";

type UnitAction = { kind: "rename" | "alias"; unit: Unit } | null;

export default function UnitsPage() {
  const me = useMe();
  const units = useUnits();
  const rename = useRenameUnit();
  const addAlias = useAddUnitAlias();
  const queryClient = useQueryClient();
  const [action, setAction] = useState<UnitAction>(null);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!action) return;
    const form = new FormData(event.currentTarget);
    const value = String(form.get("value")).trim();
    const reason = String(form.get("reason")).trim() || undefined;
    try {
      if (action.kind === "rename") await rename.mutateAsync({ id: action.unit.id, name: value, reason });
      else await addAlias.mutateAsync({ id: action.unit.id, alias: value, reason });
      await queryClient.invalidateQueries({ queryKey: ["units"] });
      toast.success(action.kind === "rename" ? "Đã đổi tên đơn vị." : "Đã thêm bí danh đơn vị.");
      setAction(null);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể cập nhật đơn vị.");
    }
  }

  if (me.isLoading || units.isLoading) return <><PageHeader title="Quản trị đơn vị" /><LoadingView label="Đang tải danh mục đơn vị…" /></>;
  if (me.isError) return <><PageHeader title="Quản trị đơn vị" /><ErrorView error={me.error} retry={() => me.refetch()} /></>;
  if (!me.data?.user?.roles.includes("rd_officer")) return <><PageHeader title="Quản trị đơn vị" /><EmptyView title="Không có quyền truy cập" description="Cần vai trò Chuyên viên KHCN để quản trị danh mục đơn vị." /></>;
  if (units.isError) return <><PageHeader title="Quản trị đơn vị" /><ErrorView error={units.error} retry={() => units.refetch()} /></>;

  return <>
    <PageHeader title="Quản trị đơn vị" description="Đặt tên dễ hiểu cho các mã đơn vị được đồng bộ từ kho nguồn." />
    <Alert className="mb-5"><AlertDescription>Mã đơn vị lấy từ kho nguồn; tên do Phòng KH-CN đặt.</AlertDescription></Alert>
    {!units.data?.length ? <EmptyView title="Chưa có đơn vị" description="Hãy đồng bộ kho nguồn trước khi đặt tên hoặc bí danh đơn vị." /> : <div className="overflow-x-auto rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Mã</TableHead><TableHead>Tên</TableHead><TableHead>Bí danh</TableHead><TableHead className="text-right">Công trình</TableHead><TableHead className="text-right">Giảng viên</TableHead><TableHead className="text-right">Hành động</TableHead></TableRow></TableHeader><TableBody>{units.data.map((unit) => <TableRow key={unit.id}><TableCell className="font-semibold">{unit.code}</TableCell><TableCell>{unit.name}</TableCell><TableCell><div className="flex flex-wrap gap-1">{unit.aliases?.length ? unit.aliases.map((alias) => <Badge key={alias} variant="outline">{alias}</Badge>) : "—"}</div></TableCell><TableCell className="text-right tabular-nums">{unit.works.toLocaleString("vi-VN")}</TableCell><TableCell className="text-right tabular-nums">{unit.persons.toLocaleString("vi-VN")}</TableCell><TableCell><div className="flex justify-end gap-1"><Button type="button" size="sm" variant="ghost" onClick={() => setAction({ kind: "rename", unit })}><Pencil />Đổi tên</Button><Button type="button" size="sm" variant="ghost" onClick={() => setAction({ kind: "alias", unit })}><Plus />Thêm bí danh</Button></div></TableCell></TableRow>)}</TableBody></Table></div>}
    <Dialog open={action !== null} onOpenChange={(open) => { if (!open) setAction(null); }}><DialogContent><form key={`${action?.kind}-${action?.unit.id}`} onSubmit={(event) => void submit(event)}><DialogHeader><DialogTitle>{action?.kind === "rename" ? "Đổi tên đơn vị" : "Thêm bí danh"}</DialogTitle><DialogDescription>{action?.unit.code} — {action?.unit.name}</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div><label htmlFor="unit-value" className="mb-1.5 block font-medium">{action?.kind === "rename" ? "Tên mới" : "Bí danh"} <span className="text-status-danger">*</span></label><Input id="unit-value" name="value" required defaultValue={action?.kind === "rename" ? action.unit.name : ""} autoFocus /></div><div><label htmlFor="unit-reason" className="mb-1.5 block font-medium">Lý do <span className="font-normal text-muted-foreground">(không bắt buộc)</span></label><Textarea id="unit-reason" name="reason" rows={3} placeholder="Ghi chú để thuận tiện đối chiếu lịch sử thay đổi" /></div></div><DialogFooter><Button type="button" variant="outline" onClick={() => setAction(null)}>Huỷ</Button><Button type="submit" disabled={rename.isPending || addAlias.isPending}>{action?.kind === "rename" ? "Lưu tên" : "Thêm bí danh"}</Button></DialogFooter></form></DialogContent></Dialog>
  </>;
}
