// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useQueryClient } from "@tanstack/react-query";
import { CircleHelp, LogIn, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { LoadingView } from "@/components/state-views";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api";
import { useLogin } from "@/lib/queries";
import type { MeOut } from "@/lib/types";

function LoginContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const login = useLogin();
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const user = await login.mutateAsync({ email: String(form.get("email")).trim(), password: String(form.get("password")) });
      queryClient.setQueryData<MeOut>(["me"], { user, auth_required: true });
      const requested = searchParams.get("next");
      const target = requested ? new URL(requested, window.location.origin) : null;
      router.replace(target?.origin === window.location.origin ? `${target.pathname}${target.search}${target.hash}` : "/tong-quan/");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.detail : "Không thể đăng nhập. Hãy thử lại.");
    }
  }

  return (
    <>
      <PageHeader title="Đăng nhập" description="Dùng tài khoản cục bộ ICTU-CRIS để thực hiện các thao tác nghiệp vụ." />
      <div className="mx-auto max-w-md rounded-lg border bg-card p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-3"><span className="grid size-10 place-items-center rounded-lg bg-primary/10 text-primary"><ShieldCheck className="size-5" /></span><div><h2 className="font-semibold">Tài khoản ICTU-CRIS</h2><p className="text-xs text-muted-foreground">Phiên đăng nhập được bảo vệ bằng cookie HttpOnly.</p></div></div>
        {error && <Alert variant="destructive" className="mb-4"><AlertTitle>Đăng nhập không thành công</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}
        <form className="space-y-4" onSubmit={submit}>
          <div><label htmlFor="login-email" className="mb-1.5 block font-medium">Email</label><Input id="login-email" name="email" type="email" autoComplete="username" required autoFocus /></div>
          <div><label htmlFor="login-password" className="mb-1.5 block font-medium">Mật khẩu</label><Input id="login-password" name="password" type="password" autoComplete="current-password" required /></div>
          <Button type="submit" className="w-full" disabled={login.isPending}><LogIn />{login.isPending ? "Đang đăng nhập…" : "Đăng nhập"}</Button>
        </form>
      </div>
      <p className="mx-auto mt-4 max-w-md text-center text-sm text-muted-foreground"><Link href="/huong-dan/" className="inline-flex items-center gap-1.5 font-medium text-primary underline-offset-4 hover:underline"><CircleHelp className="size-4" />Xem hướng dẫn sử dụng</Link></p>
    </>
  );
}

export default function LoginPage() {
  return <Suspense fallback={<><PageHeader title="Đăng nhập" /><LoadingView label="Đang mở trang đăng nhập…" /></>}><LoginContent /></Suspense>;
}
