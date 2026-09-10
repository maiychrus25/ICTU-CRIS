// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { PageHeader } from "@/components/page-header";
import { EmptyView } from "@/components/state-views";

export function PhaseBPlaceholder({ title, description }: { title: string; description: string }) {
  return <><PageHeader title={title} description={description} /><EmptyView title="Sẽ có ở Đợt B" description="Đường dẫn đã sẵn sàng. Dữ liệu và thao tác nghiệp vụ sẽ được hoàn thiện trong Đợt B." /></>;
}
