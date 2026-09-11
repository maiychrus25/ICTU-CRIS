// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import {
  aboutFixture, auditFixture, authorQueueFixture, compareFixture, declarationDetailsFixture, declarationsFixture,
  duplicateDetailFixture, duplicateGroupsFixture, healthFixture, periodProgressFixture, periodsFixture, personFixture, qualityFixture, statsFixture,
  meFixture, personsFixture, screenCohortsFixture, screenFixture, syncRunDetailsFixture, syncRunsFixture,
  topicDetailsFixture, topicsFixture, workDetailsFixture, workItems, worksFixture,
} from "@/lib/fixtures";
import type {
  AboutOut, AuditFilters, AuditList, AuthorQueueList, CompareIn, CompareOut, DeclarationCreateIn,
  DeclarationDetail, DeclarationEvidenceIn, DeclarationList, DeclarationRow, DeclarationStateIn,
  DecideAuthorsIn, DecideDupIn, DecideResult, DupGroupDetail, DupGroupList, EvidenceOut, HealthOut, PeriodOpenIn, PeriodOut, PeriodProgress,
  LoginIn, LogoutOut, MeOut, PersonProfile, PersonSearchRow, QualityOut, StatsOut, SyncRunDetail, SyncRunList, Topic, TopicDetail,
  UserOut,
  WorkDetail, WorkFilters, WorkList,
  ScreenCohortSummary, ScreenFilters, ScreenList,
} from "@/lib/types";
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";
const MOCK = process.env.NEXT_PUBLIC_MOCK === "1";

export class ApiError extends Error {
  constructor(public status: number, public detail: string, public handled = false) {
    super(detail);
    this.name = "ApiError";
  }
}

let mockUser = meFixture.user;
const mockDeclarations = structuredClone(declarationsFixture);
const mockDeclarationDetails = structuredClone(declarationDetailsFixture);
const mockPeriodProgress = structuredClone(periodProgressFixture);

function queryString(params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== "") query.set(key, String(value)); });
  return query.size ? `?${query}` : "";
}

async function mockRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const url = new URL(path, "http://mock.local");
  const id = Number(url.pathname.split("/").at(-1));
  let data: unknown;

  if (url.pathname === "/api/auth/me") data = { ...meFixture, user: mockUser };
  else if (url.pathname === "/api/auth/login") {
    const body = JSON.parse(String(init?.body)) as LoginIn;
    if (body.email !== meFixture.user?.email || body.password !== "demo1234") throw new ApiError(401, "Email hoặc mật khẩu không đúng.");
    mockUser = meFixture.user;
    data = mockUser;
  }
  else if (url.pathname === "/api/auth/logout") {
    mockUser = null;
    data = { ok: true };
  }
  else if (url.pathname === "/api/works") {
    const q = url.searchParams.get("q")?.toLocaleLowerCase("vi") ?? "";
    const docType = url.searchParams.get("doc_type");
    const year = url.searchParams.get("year");
    const topic = Number(url.searchParams.get("topic")) || null;
    const topicWorkIds = topic ? new Set(topicDetailsFixture[topic]?.works.map((work) => work.id) ?? []) : null;
    const items = worksFixture.items.filter((work) => (!q || work.title?.toLocaleLowerCase("vi").includes(q)) && (!docType || work.doc_type === docType) && (!year || work.year === Number(year)) && (!topicWorkIds || topicWorkIds.has(work.id)));
    data = { items, page: { ...worksFixture.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  } else if (/^\/api\/works\/\d+$/.test(url.pathname)) data = workDetailsFixture[id];
  else if (/^\/api\/persons\/\d+$/.test(url.pathname)) data = id === personFixture.id ? personFixture : undefined;
  else if (url.pathname === "/api/persons") {
    const q = url.searchParams.get("q")?.toLocaleLowerCase("vi") ?? "";
    data = personsFixture.filter((person) => person.display_name.toLocaleLowerCase("vi").includes(q));
  }
  else if (url.pathname === "/api/topics") data = topicsFixture;
  else if (/^\/api\/topics\/\d+$/.test(url.pathname)) data = topicDetailsFixture[id];
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
  else if (url.pathname === "/api/ai/screen/cohorts") data = screenCohortsFixture;
  else if (url.pathname === "/api/ai/screen") {
    const cohort = url.searchParams.get("cohort");
    const min = url.searchParams.get("min");
    const minScore = Number(url.searchParams.get("min_score") ?? 0);
    const order = { thap: 0, vua: 1, cao: 2 } as const;
    const items = screenFixture.items.filter((item) => (!cohort || item.cohort === cohort) && (!min || order[item.level as keyof typeof order] >= order[min as keyof typeof order]) && item.max_score >= minScore);
    data = { ...screenFixture, items, page: { ...screenFixture.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  }
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
  else if (/^\/api\/periods\/\d+\/declarations$/.test(url.pathname) && !init?.method) {
    const periodId = Number(url.pathname.split("/").at(-2));
    const unitId = Number(url.searchParams.get("unit_id")) || null;
    const items = mockDeclarations[periodId];
    data = items ? { items: unitId ? items.filter((row) => row.unit_id === unitId) : items } : undefined;
  }
  else if (/^\/api\/periods\/\d+\/declarations$/.test(url.pathname) && init?.method === "POST") {
    const periodId = Number(url.pathname.split("/").at(-2));
    const period = periodsFixture.find((item) => item.id === periodId);
    const body = JSON.parse(String(init.body)) as DeclarationCreateIn;
    const work = workItems.find((item) => item.id === body.work_id);
    const unit = statsFixture.by_unit.find((item) => item.unit_id === body.unit_id);
    if (period?.state !== "DangMo") throw new ApiError(409, "chỉ kê khai được khi kỳ báo cáo đang mở");
    if (mockDeclarations[periodId]?.some((row) => row.work_id === body.work_id && row.unit_id === body.unit_id)) throw new ApiError(409, "đã kê khai");
    if (!work || !unit) throw new ApiError(409, "công trình hoặc đơn vị không hợp lệ");
    const now = new Date().toISOString();
    const row: DeclarationRow = {
      id: Math.max(600, ...Object.keys(mockDeclarationDetails).map(Number)) + 1,
      period_id: periodId, work_id: work.id, work_title: work.title, doc_type: work.doc_type,
      doc_type_label: work.doc_type_label, unit_id: unit.unit_id, unit_code: unit.code,
      state: "Nhap", note: body.note ?? null, evidence_count: 0, last_event_at: now, created_at: now, updated_at: now,
    };
    mockDeclarations[periodId] ??= [];
    mockDeclarations[periodId].unshift(row);
    mockDeclarationDetails[row.id] = {
      ...row, events: [{ id: Date.now(), from_state: null, to_state: "Nhap", actor_id: mockUser?.id ?? 1, reason: null, at: now }], evidence: [],
    };
    const progress = mockPeriodProgress[periodId];
    const progressUnit = progress?.units.find((item) => item.unit_id === unit.unit_id);
    if (progressUnit) {
      progressUnit.counts.Nhap = (progressUnit.counts.Nhap ?? 0) + 1;
      progressUnit.total += 1;
    }
    data = row;
  }
  else if (/^\/api\/declarations\/\d+\/state$/.test(url.pathname)) {
    const declarationId = Number(url.pathname.split("/").at(-2));
    const detail = mockDeclarationDetails[declarationId];
    const body = JSON.parse(String(init?.body)) as DeclarationStateIn;
    if (!detail) data = undefined;
    else {
      const allowed = new Set(["Nhap:ChoBoSung", "ChoBoSung:Nhap", "Nhap:Rut", "ChoBoSung:Rut"]);
      if (!allowed.has(`${detail.state}:${body.to_state}`)) throw new ApiError(409, `không thể chuyển hồ sơ từ ${detail.state} sang ${body.to_state}`);
      if ((body.to_state === "ChoBoSung" || body.to_state === "Rut") && !body.reason?.trim()) throw new ApiError(409, `chuyển sang ${body.to_state} bắt buộc phải nêu lý do`);
      const fromState = detail.state;
      const now = new Date().toISOString();
      detail.state = body.to_state;
      detail.updated_at = now;
      detail.events.push({ id: Date.now(), from_state: fromState, to_state: body.to_state, actor_id: mockUser?.id ?? 1, reason: body.reason ?? null, at: now });
      const row = Object.values(mockDeclarations).flat().find((item) => item.id === declarationId)!;
      row.state = body.to_state;
      row.updated_at = now;
      row.last_event_at = now;
      const progressUnit = mockPeriodProgress[detail.period_id]?.units.find((item) => item.unit_id === detail.unit_id);
      if (progressUnit) {
        progressUnit.counts[fromState] = Math.max(0, (progressUnit.counts[fromState] ?? 0) - 1);
        progressUnit.counts[body.to_state] = (progressUnit.counts[body.to_state] ?? 0) + 1;
      }
      data = row;
    }
  }
  else if (/^\/api\/declarations\/\d+\/evidence$/.test(url.pathname)) {
    const declarationId = Number(url.pathname.split("/").at(-2));
    const detail = mockDeclarationDetails[declarationId];
    const body = JSON.parse(String(init?.body)) as DeclarationEvidenceIn;
    if (!detail) data = undefined;
    else {
      const evidence: EvidenceOut = { id: Date.now(), kind: body.kind, url: body.url ?? null, file_name: body.file_name ?? null, note: body.note ?? null, added_by: mockUser?.id ?? 1, added_at: new Date().toISOString() };
      detail.evidence.push(evidence);
      const row = Object.values(mockDeclarations).flat().find((item) => item.id === declarationId)!;
      row.evidence_count += 1;
      data = evidence;
    }
  }
  else if (/^\/api\/declarations\/\d+$/.test(url.pathname)) data = mockDeclarationDetails[id];
  else if (/^\/api\/periods\/\d+\/progress$/.test(url.pathname)) data = mockPeriodProgress[Number(url.pathname.split("/").at(-2))];
  else if (/^\/api\/periods\/\d+\/(close|cancel)$/.test(url.pathname)) {
    const periodId = Number(url.pathname.split("/").at(-2));
    const period = periodsFixture.find((item) => item.id === periodId);
    data = period ? { ...period, state: url.pathname.endsWith("/close") ? "DaDongNop" : "Huy" } : undefined;
  }
  else if (url.pathname === "/api/sync/runs") data = { ...syncRunsFixture, page: { ...syncRunsFixture.page, page: Number(url.searchParams.get("page") ?? 1) } };
  else if (/^\/api\/sync\/runs\/\d+$/.test(url.pathname)) data = syncRunDetailsFixture[id];
  else if (url.pathname === "/api/health") data = healthFixture;

  if (data === undefined) throw new ApiError(404, "Không tìm thấy dữ liệu yêu cầu.");
  return structuredClone(data) as T;
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  if (MOCK) return mockRequest<T>(path, init);
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    const error = new ApiError(response.status, typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? response.statusText));
    if (typeof window !== "undefined" && path !== "/api/auth/login") {
      if (error.status === 401) {
        error.handled = true;
        window.dispatchEvent(new CustomEvent("cris:api-error", { detail: { status: 401 } }));
      } else if (error.status === 403) {
        error.handled = true;
        window.dispatchEvent(new CustomEvent("cris:api-error", { detail: { status: 403 } }));
      }
    }
    throw error;
  }
  return response.json() as Promise<T>;
}

export const api = {
  getMe: () => apiRequest<MeOut>("/api/auth/me"),
  login: (input: LoginIn) => apiRequest<UserOut>("/api/auth/login", { method: "POST", body: JSON.stringify(input) }),
  logout: () => apiRequest<LogoutOut>("/api/auth/logout", { method: "POST" }),
  getWorks: (filters: WorkFilters = {}) => apiRequest<WorkList>(`/api/works${queryString({ q: filters.q, doc_type: filters.doc_type, year: filters.year, unit: filters.unit, topic: filters.topic, page: filters.page })}`),
  getWork: (id: number) => apiRequest<WorkDetail>(`/api/works/${id}`),
  getPerson: (id: number) => apiRequest<PersonProfile>(`/api/persons/${id}`),
  searchPersons: (q: string, limit = 20) => apiRequest<PersonSearchRow[]>(`/api/persons${queryString({ q, limit })}`),
  getTopics: () => apiRequest<Topic[]>("/api/topics"),
  getTopic: (id: number) => apiRequest<TopicDetail>(`/api/topics/${id}`),
  getAuthorQueue: (state = "ChoXacNhan", q = "", page = 1) => apiRequest<AuthorQueueList>(`/api/queue/authors${queryString({ state, q, page })}`),
  decideAuthors: (input: DecideAuthorsIn) => apiRequest<DecideResult>("/api/queue/authors/decide", { method: "POST", body: JSON.stringify(input) }),
  getDuplicateGroups: (state = "NghiTrung", page = 1) => apiRequest<DupGroupList>(`/api/queue/duplicates${queryString({ state, page })}`),
  getDuplicateGroup: (id: number) => apiRequest<DupGroupDetail>(`/api/queue/duplicates/${id}`),
  decideDuplicate: (id: number, input: DecideDupIn) => apiRequest<DecideResult>(`/api/queue/duplicates/${id}/decide`, { method: "POST", body: JSON.stringify(input) }),
  compare: (input: CompareIn) => apiRequest<CompareOut>("/api/compare", { method: "POST", body: JSON.stringify(input) }),
  getComparison: (id: number) => apiRequest<CompareOut>(`/api/compare/${id}`),
  getScreenCohorts: () => apiRequest<ScreenCohortSummary[]>("/api/ai/screen/cohorts"),
  getScreen: (filters: ScreenFilters = {}) => apiRequest<ScreenList>(`/api/ai/screen${queryString({ cohort: filters.cohort, min: filters.min, min_score: filters.min_score, page: filters.page })}`),
  getQuality: () => apiRequest<QualityOut>("/api/quality"),
  getAbout: () => apiRequest<AboutOut>("/api/about"),
  getStats: (years = 5) => apiRequest<StatsOut>(`/api/stats${queryString({ years })}`),
  getAudit: (filters: AuditFilters = {}) => apiRequest<AuditList>(`/api/audit${queryString({ entity: filters.entity, entity_id: filters.entity_id, actor: filters.actor, page: filters.page })}`),
  getPeriods: () => apiRequest<PeriodOut[]>("/api/periods"),
  getPeriodProgress: (id: number) => apiRequest<PeriodProgress>(`/api/periods/${id}/progress`),
  getDeclarations: (periodId: number, unitId?: number) => apiRequest<DeclarationList>(`/api/periods/${periodId}/declarations${queryString({ unit_id: unitId })}`),
  addDeclaration: (periodId: number, input: DeclarationCreateIn) => apiRequest<DeclarationRow>(`/api/periods/${periodId}/declarations`, { method: "POST", body: JSON.stringify(input) }),
  getDeclaration: (id: number) => apiRequest<DeclarationDetail>(`/api/declarations/${id}`),
  setDeclarationState: (id: number, input: DeclarationStateIn) => apiRequest<DeclarationRow>(`/api/declarations/${id}/state`, { method: "POST", body: JSON.stringify(input) }),
  addDeclarationEvidence: (id: number, input: DeclarationEvidenceIn) => apiRequest<EvidenceOut>(`/api/declarations/${id}/evidence`, { method: "POST", body: JSON.stringify(input) }),
  openPeriod: (input: PeriodOpenIn) => apiRequest<PeriodOut>("/api/periods", { method: "POST", body: JSON.stringify(input) }),
  closePeriod: (id: number) => apiRequest<PeriodOut>(`/api/periods/${id}/close`, { method: "POST" }),
  cancelPeriod: (id: number) => apiRequest<PeriodOut>(`/api/periods/${id}/cancel`, { method: "POST" }),
  getSyncRuns: (page = 1) => apiRequest<SyncRunList>(`/api/sync/runs${queryString({ page })}`),
  getSyncRun: (id: number) => apiRequest<SyncRunDetail>(`/api/sync/runs/${id}`),
  getHealth: () => apiRequest<HealthOut>("/api/health"),
};
