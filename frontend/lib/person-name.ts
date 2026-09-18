// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

const titlePattern = /^(?:(?:GS|PGS)\.)?(?:(?:TS|ThS)\.)?\s*/i;

function abbreviation(value: string | null | undefined, kind: "rank" | "degree") {
  const normalized = value?.toLocaleLowerCase("vi-VN").replaceAll(".", "").trim();
  if (kind === "rank") {
    if (normalized === "pgs" || normalized?.includes("phó giáo sư")) return "PGS";
    if (normalized === "gs" || normalized?.includes("giáo sư")) return "GS";
  }
  if (kind === "degree") {
    if (normalized === "ts" || normalized?.includes("tiến sĩ")) return "TS";
    if (normalized === "ths" || normalized?.includes("thạc sĩ")) return "ThS";
  }
  return null;
}

export function formatPersonName(name: string, rank?: string | null, degree?: string | null) {
  const titles = [abbreviation(rank, "rank"), abbreviation(degree, "degree")].filter(Boolean);
  return titles.length ? `${titles.join(".")}. ${name.replace(titlePattern, "")}` : name;
}
