// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import {
  aboutFixture, auditFixture, authorQueueFixture, compareFixture, duplicateDetailFixture, duplicateGroupsFixture,
  healthFixture, periodProgressFixture, periodsFixture, personFixture, qualityFixture, statsFixture,
  topicsFixture, workDetailsFixture, worksFixture,
} from "@/lib/fixtures";
import type {
  AboutOut, AuditFilters, AuditList, AuthorQueueList, CompareIn, CompareOut, DecideAuthorsIn, DecideDupIn,
  DecideResult, DupGroupDetail, DupGroupList, HealthOut, PeriodOpenIn, PeriodOut, PeriodProgress,
  PersonProfile, QualityOut, StatsOut, Topic, WorkDetail, WorkFilters, WorkList,
} from "@/lib/types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";
const MOCK = process.env.NEXT_PUBLIC_MOCK === "1";

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
    this.name = "ApiError";
  }
}

function queryString(params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== "") query.set(key, String(value)); });
  return query.size ? `?${query}` : "";
}

async function mockRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const url = new URL(path, "http://mock.local");
  const id = Number(url.pathname.split("/").at(-1));
  let data: unknown;

  if (url.pathname === "/api/works") {
    const q = url.searchParams.get("q")?.toLocaleLowerCase("vi") ?? "";
    const docType = url.searchParams.get("doc_type");
    const year = url.searchParams.get("year");
    const items = worksFixture.items.filter((work) => (!q || work.title?.toLocaleLowerCase("vi").includes(q)) && (!docType || work.doc_type === docType) && (!year || work.year === Number(year)));
    data = { items, page: { ...worksFixture.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  } else if (/^\/api\/works\/\d+$/.test(url.pathname)) data = workDetailsFixture[id];
  else if (/^\/api\/persons\/\d+$/.test(url.pathname)) data = id === personFixture.id ? personFixture : undefined;
  else if (url.pathname === "/api/topics") data = topicsFixture;
  else if (url.pathname === "/api/queue/authors" && !init?.method) {
    const state = url.searchParams.get("state") ?? "ChoXacNhan";
    const q = url.searchParams.get("q")?.toLocaleLowerCase("vi") ?? "";
    const items = state === "ChoXacNhan" ? authorQueueFixture.items.filter((row) => !q || row.raw_name.toLocaleLowerCase("vi").includes(q)) : [];
    data = { ...authorQueueFixture, state, items, page: { ...authorQueueFixture.page, total: items.length } };
  }
  else if (url.pathname === "/api/queue/authors/decide") data = { ok: true, processed: (JSON.parse(String(init?.body)) as DecideAuthorsIn).link_ids };
  else if (url.pathname === "/api/queue/duplicates") {
    const state = url.searchParams.get("state") ?? "NghiTrung";
    const items = state === "all" ? duplicateGroupsFixture.items : duplicateGroupsFixture.items.filter((group) => group.state === state);
    data = { items, page: { ...duplicateGroupsFixture.page, total: items.length } };
  }
  else if (/^\/api\/queue\/duplicates\/\d+$/.test(url.pathname) && !init?.method) data = { ...duplicateDetailFixture, id };
  else if (/^\/api\/queue\/duplicates\/\d+\/decide$/.test(url.pathname)) data = { ok: true, processed: [Number(url.pathname.split("/").at(-2))] };
  else if (url.pathname === "/api/compare" && init?.method === "POST") data = { ...compareFixture, query_id: Date.now(), input: JSON.parse(String(init.body)) };
  else if (/^\/api\/compare\/\d+$/.test(url.pathname)) data = { ...compareFixture, query_id: id };
  else if (url.pathname === "/api/quality") data = qualityFixture;
  else if (url.pathname === "/api/about") data = aboutFixture;
  else if (url.pathname === "/api/stats") data = statsFixture;
  else if (url.pathname === "/api/audit") {
    const entity = url.searchParams.get("entity");
    const entityId = url.searchParams.get("entity_id");
    const items = auditFixture.items.filter((row) => (!entity || row.entity === entity) && (!entityId || row.entity_id === Number(entityId)));
    data = { items, page: { ...auditFixture.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  }
  else if (url.pathname === "/api/periods" && !init?.method) data = periodsFixture;
  else if (url.pathname === "/api/periods" && init?.method === "POST") {
    const body = JSON.parse(String(init.body)) as PeriodOpenIn;
    data = { ...body, id: 404, criteria: body.criteria ?? null, state: "DangMo", opens_at: new Date().toISOString(), created_at: new Date().toISOString() };
  }
  else if (/^\/api\/periods\/\d+\/progress$/.test(url.pathname)) data = periodProgressFixture[Number(url.pathname.split("/").at(-2))];
  else if (/^\/api\/periods\/\d+\/(close|cancel)$/.test(url.pathname)) {
    const periodId = Number(url.pathname.split("/").at(-2));
    const period = periodsFixture.find((item) => item.id === periodId);
    data = period ? { ...period, state: url.pathname.endsWith("/close") ? "DaDongNop" : "Huy" } : undefined;
  }
  else if (url.pathname === "/api/health") data = healthFixture;

  if (data === undefined) throw new ApiError(404, "Không tìm thấy dữ liệu yêu cầu.");
  return structuredClone(data) as T;
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  if (MOCK) return mockRequest<T>(path, init);
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? response.statusText));
  }
  return response.json() as Promise<T>;
}

export const api = {
  getWorks: (filters: WorkFilters = {}) => apiRequest<WorkList>(`/api/works${queryString({ q: filters.q, doc_type: filters.doc_type, year: filters.year, unit: filters.unit, topic: filters.topic, page: filters.page })}`),
  getWork: (id: number) => apiRequest<WorkDetail>(`/api/works/${id}`),
  getPerson: (id: number) => apiRequest<PersonProfile>(`/api/persons/${id}`),
  getTopics: () => apiRequest<Topic[]>("/api/topics"),
  getAuthorQueue: (state = "ChoXacNhan", q = "", page = 1) => apiRequest<AuthorQueueList>(`/api/queue/authors${queryString({ state, q, page })}`),
  decideAuthors: (input: DecideAuthorsIn) => apiRequest<DecideResult>("/api/queue/authors/decide", { method: "POST", body: JSON.stringify(input) }),
  getDuplicateGroups: (state = "NghiTrung", page = 1) => apiRequest<DupGroupList>(`/api/queue/duplicates${queryString({ state, page })}`),
  getDuplicateGroup: (id: number) => apiRequest<DupGroupDetail>(`/api/queue/duplicates/${id}`),
  decideDuplicate: (id: number, input: DecideDupIn) => apiRequest<DecideResult>(`/api/queue/duplicates/${id}/decide`, { method: "POST", body: JSON.stringify(input) }),
  compare: (input: CompareIn) => apiRequest<CompareOut>("/api/compare", { method: "POST", body: JSON.stringify(input) }),
  getComparison: (id: number) => apiRequest<CompareOut>(`/api/compare/${id}`),
  getQuality: () => apiRequest<QualityOut>("/api/quality"),
  getAbout: () => apiRequest<AboutOut>("/api/about"),
  getStats: (years = 5) => apiRequest<StatsOut>(`/api/stats${queryString({ years })}`),
  getAudit: (filters: AuditFilters = {}) => apiRequest<AuditList>(`/api/audit${queryString({ entity: filters.entity, entity_id: filters.entity_id, actor: filters.actor, page: filters.page })}`),
  getPeriods: () => apiRequest<PeriodOut[]>("/api/periods"),
  getPeriodProgress: (id: number) => apiRequest<PeriodProgress>(`/api/periods/${id}/progress`),
  openPeriod: (input: PeriodOpenIn) => apiRequest<PeriodOut>("/api/periods", { method: "POST", body: JSON.stringify(input) }),
  closePeriod: (id: number) => apiRequest<PeriodOut>(`/api/periods/${id}/close`, { method: "POST" }),
  cancelPeriod: (id: number) => apiRequest<PeriodOut>(`/api/periods/${id}/cancel`, { method: "POST" }),
  getHealth: () => apiRequest<HealthOut>("/api/health"),
};
