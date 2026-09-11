// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ThemeProvider } from "next-themes";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { ApiError } from "@/lib/api";

function ApiErrorHandler() {
  const router = useRouter();
  useEffect(() => {
    function handle(event: Event) {
      const status = (event as CustomEvent<{ status: number }>).detail.status;
      if (status === 403) return void toast.error("Bạn không có quyền");
      toast.error("Cần đăng nhập");
      if (!window.location.pathname.startsWith("/dang-nhap")) {
        const next = `${window.location.pathname}${window.location.search}`;
        router.replace(`/dang-nhap/?${new URLSearchParams({ next })}`);
      }
    }
    window.addEventListener("cris:api-error", handle);
    return () => window.removeEventListener("cris:api-error", handle);
  }, [router]);
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 30_000, retry: (count, error) => error instanceof ApiError && [401, 403].includes(error.status) ? false : count < 1 } },
  }));

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <ApiErrorHandler />
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </ThemeProvider>
  );
}
