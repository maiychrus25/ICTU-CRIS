// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { docTypeColors, docTypeLabels } from "@/lib/labels";
import type { YearTypeRow } from "@/lib/types";

const docTypes = ["bai_bao", "do_an", "luan_van", "luan_an", "hoc_lieu"] as const;

export function YearTypeChart({ data, label }: { data: YearTypeRow[]; label: string }) {
  return <div className="h-88 rounded-lg border bg-card p-4" role="img" aria-label={label}><ResponsiveContainer width="100%" height="100%"><BarChart data={[...data].sort((a, b) => a.year - b.year)} margin={{ top: 8, right: 12, left: 10, bottom: 22 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="year" tickLine={false} axisLine={false} label={{ value: "Năm công bố", position: "insideBottom", offset: -14 }} /><YAxis allowDecimals={false} tickLine={false} axisLine={false} label={{ value: "Số công trình", angle: -90, position: "insideLeft" }} /><Tooltip cursor={{ fill: "var(--muted)" }} /><Legend verticalAlign="top" height={38} />{docTypes.map((type) => <Bar key={type} dataKey={type} name={docTypeLabels[type]} stackId="works" fill={docTypeColors[type]} />)}</BarChart></ResponsiveContainer></div>;
}
