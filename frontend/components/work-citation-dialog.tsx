// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Copy, Download } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, ApiError } from "@/lib/api";
import { useCitation } from "@/lib/queries";

export function WorkCitationDialog({ workId, open, onOpenChange }: { workId: number; open: boolean; onOpenChange: (open: boolean) => void }) {
  const [style, setStyle] = useState<"apa" | "ieee" | "bibtex">("apa");
  const citation = useCitation(workId, style, open);

  async function copyCitation() {
    if (!citation.data) return;
    try { await navigator.clipboard.writeText(citation.data); toast.success("Đã sao chép trích dẫn."); }
    catch { toast.error("Không thể sao chép. Hãy chọn và sao chép thủ công."); }
  }

  async function downloadBib() {
    try {
      const text = style === "bibtex" && citation.data ? citation.data : await api.getCitation(workId, "bibtex");
      const url = URL.createObjectURL(new Blob([text], { type: "application/x-bibtex;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = `ictu-cris-${workId}.bib`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) { toast.error(error instanceof ApiError ? error.detail : "Không thể tải tệp BibTeX."); }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader><DialogTitle>Trích dẫn công trình</DialogTitle><DialogDescription>Chọn định dạng phù hợp, sau đó sao chép hoặc tải BibTeX.</DialogDescription></DialogHeader>
        <Tabs value={style} onValueChange={(value) => setStyle(value as typeof style)}><TabsList><TabsTrigger value="apa">APA</TabsTrigger><TabsTrigger value="ieee">IEEE</TabsTrigger><TabsTrigger value="bibtex">BibTeX</TabsTrigger></TabsList></Tabs>
        {citation.isLoading ? <LoadingView label="Đang tạo trích dẫn…" /> : citation.isError ? <ErrorView error={citation.error} retry={() => citation.refetch()} /> : <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-md border bg-muted/50 p-4 text-sm leading-6">{citation.data}</pre>}
        <DialogFooter><Button type="button" variant="outline" onClick={() => void downloadBib()}><Download />Tải .bib</Button><Button type="button" onClick={() => void copyCitation()} disabled={!citation.data}><Copy />Sao chép</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
