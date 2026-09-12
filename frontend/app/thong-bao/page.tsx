// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { CheckCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/page-header";
import { Pager } from "@/components/pager";
import { EmptyView, ErrorView, LoadingView } from "@/components/state-views";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ApiError } from "@/lib/api";
import { useNotifications, useReadAllNotifications, useReadNotification } from "@/lib/queries";
import { cn, formatRelativeTime } from "@/lib/utils";

export default function NotificationsPage() {
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [page, setPage] = useState(1);
  const query = useNotifications(unreadOnly, page);
  const read = useReadNotification();
  const readAll = useReadAllNotifications();
  const queryClient = useQueryClient();
  const router = useRouter();

  async function invalidate() {
    await queryClient.invalidateQueries({ queryKey: ["notifications"] });
  }

  async function open(id: number, link: string | null) {
    try {
      await read.mutateAsync(id);
      await invalidate();
      if (link) router.push(link);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể mở thông báo.");
    }
  }

  async function markAllRead() {
    try {
      await readAll.mutateAsync();
      await invalidate();
      toast.success("Đã đánh dấu tất cả thông báo là đã đọc.");
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể cập nhật thông báo.");
    }
  }

  const pageInfo = query.data?.page ?? { page, per_page: 50, total: query.data?.items.length ?? 0 };
  return (
    <>
      <PageHeader title="Thông báo" description="Theo dõi thay đổi hồ sơ, kỳ báo cáo và liên kết công trình của bạn." action={query.data?.unread ? <Button type="button" variant="outline" onClick={() => void markAllRead()} disabled={readAll.isPending}><CheckCheck />Đánh dấu tất cả đã đọc</Button> : undefined} />
      <label className="mb-4 flex w-fit cursor-pointer items-center gap-2 text-sm font-medium"><Checkbox checked={unreadOnly} onCheckedChange={(checked) => { setUnreadOnly(checked === true); setPage(1); }} />Chỉ hiện chưa đọc</label>
      {query.isLoading ? <LoadingView label="Đang tải danh sách thông báo…" />
        : query.isError ? <ErrorView error={query.error} retry={() => query.refetch()} />
          : !query.data?.items.length ? <EmptyView title={unreadOnly ? "Không còn thông báo chưa đọc" : "Chưa có thông báo"} description={unreadOnly ? "Bỏ lọc chưa đọc để xem lại toàn bộ thông báo." : "Thông báo mới về hồ sơ và kỳ báo cáo sẽ xuất hiện tại đây."} action={unreadOnly ? <Button type="button" variant="outline" onClick={() => setUnreadOnly(false)}>Xem tất cả</Button> : undefined} />
            : <div className="overflow-hidden rounded-lg border bg-card"><Table><TableHeader><TableRow><TableHead>Thông báo</TableHead><TableHead>Nội dung</TableHead><TableHead>Thời gian</TableHead><TableHead>Trạng thái</TableHead></TableRow></TableHeader><TableBody>{query.data.items.map((item) => <TableRow key={item.id}><TableCell className="whitespace-normal"><button type="button" className={cn("text-left text-primary hover:underline", item.read_at ? "font-normal" : "font-semibold")} onClick={() => void open(item.id, item.link)}>{item.title}</button></TableCell><TableCell className="max-w-xl whitespace-normal text-muted-foreground">{item.body}</TableCell><TableCell><time dateTime={item.created_at} className="tabular-nums">{formatRelativeTime(item.created_at)}</time></TableCell><TableCell>{item.read_at ? "Đã đọc" : <span className="font-medium">Chưa đọc</span>}</TableCell></TableRow>)}</TableBody></Table><Pager page={pageInfo.page} perPage={pageInfo.per_page} total={pageInfo.total} onPageChange={setPage} /></div>}
    </>
  );
}
