// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { ApiError } from "@/lib/api";
import { useMe, useNotifications, useReadAllNotifications, useReadNotification } from "@/lib/queries";
import { cn, formatRelativeTime } from "@/lib/utils";

export function NotificationCenter() {
  const me = useMe();
  const enabled = Boolean(me.data && !(me.data.auth_required && !me.data.user));
  const notifications = useNotifications(true, 1, enabled, true);
  const latest = useNotifications(false, 1, enabled);
  const read = useReadNotification();
  const readAll = useReadAllNotifications();
  const queryClient = useQueryClient();
  const router = useRouter();
  const unread = notifications.data?.unread ?? 0;

  if (!enabled) return null;

  async function invalidate() {
    await queryClient.invalidateQueries({ queryKey: ["notifications"] });
  }

  async function openNotification(id: number, link: string | null) {
    try {
      await read.mutateAsync(id);
      await invalidate();
      if (link) router.push(link);
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể đánh dấu thông báo đã đọc.");
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

  const label = unread > 0 ? `${unread} thông báo chưa đọc` : "Không có thông báo chưa đọc";
  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" aria-label={label} title="Thông báo" className="relative" />}>
        <Bell className="size-4" />
        {unread > 0 && <span className="absolute right-0.5 top-0.5 grid min-w-4 place-items-center rounded-full bg-primary px-1 text-[10px] font-semibold leading-4 text-primary-foreground tabular-nums">{unread > 99 ? "99+" : unread}</span>}
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[min(24rem,calc(100vw-2rem))] p-0">
        <div className="flex items-center justify-between border-b px-3 py-2.5"><p className="font-semibold">Thông báo</p>{unread > 0 && <Button type="button" variant="ghost" size="sm" onClick={() => void markAllRead()} disabled={readAll.isPending}><CheckCheck />Đánh dấu tất cả đã đọc</Button>}</div>
        <div className="max-h-[28rem] overflow-y-auto">
          {latest.isLoading ? <p role="status" className="p-4 text-sm text-muted-foreground">Đang tải thông báo…</p>
            : latest.isError ? <div className="p-4 text-sm text-destructive"><p>{latest.error instanceof ApiError ? latest.error.detail : "Không thể tải thông báo."}</p><Button type="button" variant="outline" size="sm" className="mt-2" onClick={() => latest.refetch()}>Thử lại</Button></div>
              : latest.data?.items.length ? latest.data.items.slice(0, 8).map((item) => <button key={item.id} type="button" className="block w-full border-b px-4 py-3 text-left last:border-0 hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" onClick={() => void openNotification(item.id, item.link)}><span className={cn("block text-sm", item.read_at ? "font-normal" : "font-semibold")}>{item.title}</span><span className="mt-1 block line-clamp-2 text-xs text-muted-foreground">{item.body}</span><time className="mt-1.5 block text-[11px] text-muted-foreground" dateTime={item.created_at}>{formatRelativeTime(item.created_at)}</time></button>)
                : <p className="p-6 text-center text-sm text-muted-foreground">Bạn đã đọc hết thông báo.</p>}
        </div>
        <div className="border-t p-2"><Button render={<Link href="/thong-bao/" />} variant="ghost" size="sm" className="w-full">Xem tất cả</Button></div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
