// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { FileUp, UploadCloud } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useAddDeclarationEvidence, useUploadDeclarationEvidence } from "@/lib/queries";
import type { EvidenceKind } from "@/lib/types";
import { formatFileSize } from "@/lib/utils";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

export function EvidenceDialog({ declarationId, open, onOpenChange, onSaved }: {
  declarationId: number | null; open: boolean; onOpenChange: (open: boolean) => void; onSaved: () => Promise<void>;
}) {
  const addEvidence = useAddDeclarationEvidence();
  const uploadEvidence = useUploadDeclarationEvidence();
  const [tab, setTab] = useState("details");
  const [kind, setKind] = useState<Exclude<EvidenceKind, "file">>("link");
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState("");

  function chooseFile(nextFile: File | null) {
    setFile(nextFile);
    setFileError(nextFile && nextFile.size > MAX_FILE_SIZE ? "Tệp vượt quá giới hạn 10 MB." : "");
  }

  function close() {
    setTab("details");
    setKind("link");
    setFile(null);
    setFileError("");
    onOpenChange(false);
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (declarationId === null) return;
    const form = new FormData(event.currentTarget);
    try {
      if (tab === "upload") {
        if (!file) return setFileError("Hãy chọn một tệp minh chứng.");
        if (file.size > MAX_FILE_SIZE) return setFileError("Tệp vượt quá giới hạn 10 MB.");
        const body = new FormData();
        body.set("file", file);
        const note = String(form.get("upload_note") || "").trim();
        if (note) body.set("note", note);
        await uploadEvidence.mutateAsync({ id: declarationId, body });
      } else {
        await addEvidence.mutateAsync({ id: declarationId, input: {
          kind, url: kind === "link" ? String(form.get("url") || "").trim() : null,
          file_name: null, note: String(form.get("note") || "").trim() || null,
        } });
      }
      await onSaved();
      toast.success(tab === "upload" ? "Đã tải tệp minh chứng lên." : "Đã thêm minh chứng.");
      close();
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể thêm minh chứng.");
    }
  }

  const pending = addEvidence.isPending || uploadEvidence.isPending;
  return (
    <Dialog open={open} onOpenChange={(nextOpen) => nextOpen ? onOpenChange(true) : close()}>
      <DialogContent className="sm:max-w-xl">
        <form onSubmit={(event) => void submit(event)}>
          <DialogHeader><DialogTitle>Thêm minh chứng</DialogTitle><DialogDescription>Gắn đường dẫn, ghi chú hoặc tệp cho hồ sơ #{declarationId}.</DialogDescription></DialogHeader>
          <Tabs value={tab} onValueChange={(value) => setTab(String(value))} className="py-4">
            <TabsList className="grid w-full grid-cols-2"><TabsTrigger value="details">Đường dẫn / ghi chú</TabsTrigger><TabsTrigger value="upload">Tải tệp lên</TabsTrigger></TabsList>
            <TabsContent value="details" className="space-y-4 pt-4">
              <div><label className="mb-1.5 block font-medium">Loại minh chứng</label><Select value={kind} onValueChange={(value) => setKind(value === "note" ? "note" : "link")}><SelectTrigger aria-label="Loại minh chứng" className="w-full"><SelectValue>{(value) => value === "note" ? "Ghi chú" : "Đường dẫn"}</SelectValue></SelectTrigger><SelectContent><SelectItem value="link">Đường dẫn</SelectItem><SelectItem value="note">Ghi chú</SelectItem></SelectContent></Select></div>
              {kind === "link" && <div><label htmlFor="evidence-url" className="mb-1.5 block font-medium">URL <span className="text-status-danger">*</span></label><Input id="evidence-url" name="url" type="url" required placeholder="https://…" /></div>}
              <div><label htmlFor="evidence-note" className="mb-1.5 block font-medium">Ghi chú{kind === "note" && <span className="text-status-danger"> *</span>}</label><Textarea id="evidence-note" name="note" required={kind === "note"} /></div>
            </TabsContent>
            <TabsContent value="upload" className="space-y-4 pt-4">
              <div className="rounded-lg border border-dashed bg-muted/25 p-6 text-center" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); chooseFile(event.dataTransfer.files[0] ?? null); }}>
                <UploadCloud className="mx-auto size-8 text-primary" />
                <p className="mt-2 font-medium">Kéo và thả tệp vào đây</p>
                <p className="mt-1 text-xs text-muted-foreground">PDF, PNG, JPG hoặc DOCX · tối đa 10 MB</p>
                <label htmlFor="evidence-upload" className="mt-3 inline-flex h-8 cursor-pointer items-center gap-1.5 rounded-lg border bg-background px-2.5 text-sm font-medium hover:bg-muted"><FileUp className="size-4" />Chọn tệp</label>
                <input id="evidence-upload" aria-label="Chọn tệp minh chứng" className="sr-only" type="file" accept=".pdf,.png,.jpg,.jpeg,.docx" onChange={(event) => chooseFile(event.target.files?.[0] ?? null)} />
              </div>
              {file && <div className="rounded-lg border bg-card px-3 py-2"><p className="font-medium">{file.name}</p><p className="text-xs text-muted-foreground tabular-nums">{formatFileSize(file.size)}</p></div>}
              {fileError && <p role="alert" className="text-sm text-destructive">{fileError}</p>}
              <div><label htmlFor="evidence-upload-note" className="mb-1.5 block font-medium">Ghi chú</label><Textarea id="evidence-upload-note" name="upload_note" /></div>
            </TabsContent>
          </Tabs>
          <DialogFooter><Button type="button" variant="outline" onClick={close}>Huỷ</Button><Button type="submit" disabled={pending || (tab === "upload" && (!file || Boolean(fileError)))}>Thêm minh chứng</Button></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
