// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0
export { cn } from "cn"

export function formatFileSize(bytes: number | null) {
  if (bytes === null) return "—";
  const value = bytes >= 1024 * 1024 ? bytes / (1024 * 1024) : bytes / 1024;
  return `${value.toLocaleString("vi-VN", { maximumFractionDigits: 2 })} ${bytes >= 1024 * 1024 ? "MB" : "KB"}`;
}

export function formatRelativeTime(value: string, now = Date.now()) {
  const elapsed = new Date(value).getTime() - now;
  const formatter = new Intl.RelativeTimeFormat("vi", { numeric: "auto" });
  const minutes = Math.round(elapsed / 60_000);
  if (Math.abs(minutes) < 60) return formatter.format(minutes, "minute");
  const hours = Math.round(elapsed / 3_600_000);
  if (Math.abs(hours) < 24) return formatter.format(hours, "hour");
  return formatter.format(Math.round(elapsed / 86_400_000), "day");
}
