// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0
export { cn } from "cn"

export function formatFileSize(bytes: number | null) {
  if (bytes === null) return "—";
  const value = bytes >= 1024 * 1024 ? bytes / (1024 * 1024) : bytes / 1024;
  return `${value.toLocaleString("vi-VN", { maximumFractionDigits: 2 })} ${bytes >= 1024 * 1024 ? "MB" : "KB"}`;
}
