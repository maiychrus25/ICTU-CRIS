// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useRouter } from "next/navigation";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function AuthorQueueTabs({ active }: { active: "queue" | "mentors" }) {
  const router = useRouter();
  return (
    <Tabs value={active} onValueChange={(value) => router.push(value === "mentors" ? "/doi-soat/huong-dan/" : "/doi-soat/tac-gia/")} className="mb-5">
      <TabsList variant="line"><TabsTrigger value="queue">Hàng đợi tác giả</TabsTrigger><TabsTrigger value="mentors">Gợi ý người hướng dẫn (AI)</TabsTrigger></TabsList>
    </Tabs>
  );
}
