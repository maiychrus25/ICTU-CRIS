// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import {
  BarChart3, BookOpenCheck, CalendarRange, CopyCheck, Info, LayoutDashboard, LogIn, LogOut, Menu, Moon,
  RefreshCw, Scale, ScrollText, Search, Sun, Tags, UserRound, UserRoundCheck,
} from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { ApiError } from "@/lib/api";
import { userRoleLabels } from "@/lib/labels";
import { useLogout, useMe } from "@/lib/queries";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/tong-quan/", label: "Tổng quan", icon: LayoutDashboard },
  { href: "/tra-cuu/", label: "Tra cứu", icon: Search },
  { href: "/chu-de/", label: "Chủ đề", icon: Tags },
  { href: "/doi-chieu/", label: "Đối chiếu đề tài", icon: Scale },
  { href: "/doi-soat/tac-gia/", label: "Hàng đợi tác giả", icon: UserRoundCheck },
  { href: "/doi-soat/trung-lap/", label: "Hàng đợi nghi trùng", icon: CopyCheck },
  { href: "/ky-bao-cao/", label: "Kỳ báo cáo", icon: CalendarRange },
  { href: "/chat-luong-du-lieu/", label: "Chất lượng dữ liệu", icon: BarChart3 },
  { href: "/dong-bo/", label: "Đồng bộ", icon: RefreshCw },
  { href: "/nhat-ky/", label: "Nhật ký", icon: ScrollText },
  { href: "/ve/", label: "Về hệ thống", icon: Info },
];

const routeTitles = [
  ["/ke-khai", "Chi tiết hồ sơ kê khai"],
  ["/dong-bo/chi-tiet", "Chi tiết lượt đồng bộ"],
  ["/chu-de/chi-tiet", "Chi tiết chủ đề"],
  ["/ky-bao-cao/chi-tiet", "Chi tiết kỳ báo cáo"],
  ["/doi-chieu/ra-soat", "Rà soát theo khoá"],
  ["/doi-soat/trung-lap/chi-tiet", "Chi tiết nhóm nghi trùng"],
  ["/doi-soat/trung-lap", "Hàng đợi nghi trùng"],
  ["/doi-soat/tac-gia", "Hàng đợi tác giả"],
  ["/chat-luong-du-lieu", "Chất lượng dữ liệu"],
  ["/dong-bo", "Đồng bộ"],
  ["/chu-de", "Chủ đề"],
  ["/ky-bao-cao", "Kỳ báo cáo"],
  ["/nhat-ky", "Nhật ký"],
  ["/tong-quan", "Tổng quan"],
  ["/cong-trinh", "Chi tiết công trình"],
  ["/giang-vien", "Hồ sơ giảng viên"],
  ["/doi-chieu", "Đối chiếu đề tài"],
  ["/tra-cuu", "Tra cứu"],
  ["/dang-nhap", "Đăng nhập"],
  ["/ve", "Về hệ thống"],
] as const;

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/tong-quan/" className="flex h-16 items-center gap-3 px-4 text-sidebar-foreground">
      <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"><BookOpenCheck className="size-5" /></span>
      {!compact && <span><strong className="block text-sm tracking-wide">ICTU-CRIS</strong><span className="block text-[11px] text-muted-foreground">Thông tin nghiên cứu</span></span>}
    </Link>
  );
}

function Navigation({ compact = false }: { compact?: boolean }) {
  const pathname = usePathname();
  return (
    <nav aria-label="Điều hướng chính" className="space-y-1 px-2 py-3">
      {navigation.map(({ href, label, icon: Icon }) => {
        const active = pathname.startsWith(href.replace(/\/$/, ""));
        return (
          <Link key={href} href={href} title={compact ? label : undefined} aria-current={active ? "page" : undefined}
            className={cn("flex h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium text-sidebar-foreground/75 transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground", active && "bg-sidebar-accent text-sidebar-accent-foreground", compact && "justify-center px-0")}>
            <Icon className="size-[18px] shrink-0" />
            {!compact && <span>{label}</span>}
          </Link>
        );
      })}
    </nav>
  );
}

function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  return (
    <Button variant="ghost" size="icon" title="Đổi giao diện sáng/tối" aria-label="Đổi giao diện sáng/tối" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
      <Sun className="size-4 dark:hidden" /><Moon className="hidden size-4 dark:block" />
    </Button>
  );
}

function Account({ compact = false }: { compact?: boolean }) {
  const me = useMe();
  const logout = useLogout();
  const queryClient = useQueryClient();
  const router = useRouter();

  async function signOut() {
    try {
      await logout.mutateAsync();
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      router.push("/tong-quan/");
    } catch (error) {
      if (!(error instanceof ApiError && error.handled)) toast.error(error instanceof ApiError ? error.detail : "Không thể đăng xuất.");
    }
  }

  if (me.isLoading) return <div className="border-t border-sidebar-border p-3 text-center text-[11px] text-muted-foreground">Đang tải tài khoản…</div>;
  if (me.data?.user) {
    const user = me.data.user;
    const roles = user.roles.map((role) => userRoleLabels[role] ?? role).join(", ");
    return compact ? <div className="border-t border-sidebar-border p-3 text-center" title={`${user.display_name} · ${roles}`}><Button type="button" variant="ghost" size="icon" aria-label="Đăng xuất" onClick={() => void signOut()} disabled={logout.isPending}><LogOut /></Button></div> : <div className="border-t border-sidebar-border p-3"><div className="flex items-center gap-2"><UserRound className="size-5 shrink-0 text-primary" /><div className="min-w-0 flex-1"><p className="truncate text-xs font-semibold">{user.display_name}</p><p className="truncate text-[11px] text-muted-foreground">{roles || "Chưa có vai trò"}</p></div><Button type="button" variant="ghost" size="icon-sm" title="Đăng xuất" aria-label="Đăng xuất" onClick={() => void signOut()} disabled={logout.isPending}><LogOut /></Button></div></div>;
  }
  if (me.data?.auth_required) return <div className="border-t border-sidebar-border p-3"><Button render={<Link href="/dang-nhap/" />} variant="outline" size={compact ? "icon" : "default"} className="w-full" title={compact ? "Đăng nhập" : undefined}><LogIn />{!compact && "Đăng nhập"}</Button></div>;
  return <div className="border-t border-sidebar-border p-3 text-center text-[11px] text-muted-foreground"><span className="hidden lg:inline">AI gợi ý, người quyết</span><span className="lg:hidden">v0.1</span></div>;
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const title = routeTitles.find(([route]) => pathname.startsWith(route))?.[1] ?? "ICTU-CRIS";

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r border-sidebar-border bg-sidebar lg:flex lg:flex-col">
        <div className="lg:hidden"><Brand compact /></div><div className="hidden lg:block"><Brand /></div>
        <div className="border-t border-sidebar-border lg:hidden"><Navigation compact /></div><div className="hidden border-t border-sidebar-border lg:block"><Navigation /></div>
        <div className="mt-auto lg:hidden"><Account compact /></div><div className="mt-auto hidden lg:block"><Account /></div>
      </aside>

      <div className="lg:pl-60">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b bg-background/95 px-4 backdrop-blur md:px-6">
          <Sheet>
            <SheetTrigger render={<Button variant="ghost" size="icon" className="lg:hidden" aria-label="Mở điều hướng" />}><Menu /></SheetTrigger>
            <SheetContent side="left" className="flex w-72 flex-col bg-sidebar p-0">
              <SheetHeader className="sr-only"><SheetTitle>Điều hướng</SheetTitle><SheetDescription>Các khu vực của hệ thống</SheetDescription></SheetHeader>
              <Brand /><div className="flex-1 overflow-y-auto border-t border-sidebar-border"><Navigation /></div><Account />
            </SheetContent>
          </Sheet>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold">{title}</p>
            <p className="hidden truncate text-[11px] text-muted-foreground sm:block">ICTU-CRIS <span aria-hidden>·</span> {title}</p>
          </div>
          <form action="/tra-cuu/" className="relative hidden w-64 sm:block">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input name="q" aria-label="Tìm nhanh công trình" placeholder="Tìm nhanh công trình…" className="pl-8" />
          </form>
          <ThemeToggle />
        </header>
        <main className="mx-auto w-full max-w-[1440px] p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
