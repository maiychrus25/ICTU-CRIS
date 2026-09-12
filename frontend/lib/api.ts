// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import {
  aboutFixture, auditFixture, authorQueueFixture, compareFixture, declarationDetailsFixture, declarationsFixture,
  anomaliesFixture, citationsFixture, coauthorsFixture, duplicateDetailFixture, duplicateGroupsFixture, expertsFixture,
  facetsFixture, healthFixture, mapFixture, mentorFixture, notificationFixture, periodProgressFixture, periodReportsFixture, periodsFixture, personFixture,
  publicTopicFixture, qualityFixture, recentFixture, reportFixture, statsFixture, trendsFixture, unitOverviewFixture,
  lecturerMeFixture, meFixture, myDeclarationsFixture, myWorksFixture, personsFixture, screenCohortsFixture, screenFixture, syncRunDetailsFixture, syncRunsFixture,
  topicDetailsFixture, topicsFixture, workDetailsFixture, workItems, worksFixture,
} from "@/lib/fixtures";
import type {
  AboutOut, AuditFilters, AuditList, AuthorQueueList, CompareIn, CompareOut, DeclarationCreateIn,
  DeclarationDetail, DeclarationEvidenceIn, DeclarationList, DeclarationRow, DeclarationStateIn,
  AcceptMentorResult, DecideAuthorsIn, DecideDupIn, DecideResult, DupGroupDetail, DupGroupList, EvidenceFileOut, EvidenceOut, HealthOut, MentorFilters, MentorList, PeriodOpenIn, PeriodOut, PeriodProgress,
  CreateReportIn, FieldEditIn, FieldEditOut, LoginIn, LogoutOut, MeOut, MyDeclarationCreateIn, MyWorkList, NotificationList, PeriodFinalizeOut, PeriodReport, PeriodReportListItem, PersonProfile, PersonSearchRow, QualityOut, ReportCreateOut, StatsOut, SyncRunDetail, SyncRunList, Topic, TopicDetail, UnitOverview,
  CoauthorsOut, DismissAnomalyIn, DismissAnomalyOut, ExpertIn, ExpertOut, MapColor, MapOut, PublicTopicCheckIn,
  PublicTopicCheckOut, QualityAnomalyFilters, QualityAnomalyList, RecentOut, TrendsOut, UserOut,
  WorkDetail, WorkFacets, WorkFilters, WorkList,
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
const mockWorks = structuredClone(worksFixture);
const mockWorkDetails = structuredClone(workDetailsFixture);
const mockPeriods = structuredClone(periodsFixture);
const mockDeclarations = structuredClone(declarationsFixture);
const mockDeclarationDetails = structuredClone(declarationDetailsFixture);
const mockPeriodProgress = structuredClone(periodProgressFixture);
const mockMyWorks = structuredClone(myWorksFixture);
const mockMyDeclarationIds = new Set(myDeclarationsFixture.map((row) => row.id));
const mockAuthorQueue = structuredClone(authorQueueFixture);
const mockMentors = structuredClone(mentorFixture);
const mockAnomalies = structuredClone(anomaliesFixture);
const mockNotifications = structuredClone(notificationFixture);
const mockPeriodReports = structuredClone(periodReportsFixture);
const mockReportDetails: Record<number, PeriodReport> = { [reportFixture.id]: structuredClone(reportFixture) };

function createMockReport(periodId: number, note: string | null) {
  const reports = mockPeriodReports[periodId] ??= [];
  const version = Math.max(0, ...reports.map((report) => report.version)) + 1;
  const id = Math.max(900, ...Object.keys(mockReportDetails).map(Number)) + 1;
  const report = structuredClone(reportFixture);
  Object.assign(report, { id, period_id: periodId, version, generated_at: new Date().toISOString(), note, sha256: `${String(id).padStart(8, "0")}${reportFixture.sha256.slice(8)}` });
  mockReportDetails[id] = report;
  reports.unshift({ id, version, generated_at: report.generated_at, generated_by_name: mockUser?.display_name ?? null, note, totals: report.summary.totals });
  return report;
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

  if (url.pathname === "/api/auth/me") data = { ...meFixture, user: mockUser };
  else if (url.pathname === "/api/auth/login") {
    const body = JSON.parse(String(init?.body)) as LoginIn;
    const user = body.email === lecturerMeFixture.user?.email ? lecturerMeFixture.user
      : body.email === meFixture.user?.email ? meFixture.user : null;
    if (!user || body.password !== "demo1234") throw new ApiError(401, "Email hoặc mật khẩu không đúng.");
    mockUser = user;
    data = mockUser;
  }
  else if (url.pathname === "/api/auth/logout") {
    mockUser = null;
    data = { ok: true };
  }
  else if (url.pathname === "/api/works/facets") data = facetsFixture;
  else if (url.pathname === "/api/works") {
    const q = url.searchParams.get("q")?.toLocaleLowerCase("vi").normalize("NFD").replace(/[\u0300-\u036f]/g, "") ?? "";
    const docType = url.searchParams.get("doc_type");
    const year = url.searchParams.get("year");
    const topic = Number(url.searchParams.get("topic")) || null;
    const mode = url.searchParams.get("mode") === "semantic" ? "semantic" : "keyword";
    const pubType = url.searchParams.get("pub_type");
    const quartile = url.searchParams.get("quartile");
    const cohort = url.searchParams.get("cohort");
    const keyword = url.searchParams.get("keyword")?.toLocaleLowerCase("vi");
    const topicWorkIds = topic ? new Set(topicDetailsFixture[topic]?.works.map((work) => work.id) ?? []) : null;
    const items = mockWorks.items.filter((work) => (mode === "semantic" || !q || work.title?.toLocaleLowerCase("vi").normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(q)) && (!docType || work.doc_type === docType) && (!year || work.year === Number(year)) && (!topicWorkIds || topicWorkIds.has(work.id)) && (!pubType || pubType === "journal_intl") && (!quartile || quartile === "Q1") && (!cohort || work.doc_type === "do_an") && (!keyword || work.keywords?.some((item) => item.toLocaleLowerCase("vi").includes(keyword))));
    data = { items, mode, note: mode === "semantic" ? "Tìm theo nghĩa (AI): kết quả có thể không chứa từ đã gõ." : null, page: { ...mockWorks.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  } else if (/^\/api\/works\/\d+\/fields$/.test(url.pathname) && init?.method === "PATCH") {
    const workId = Number(url.pathname.split("/").at(-2));
    const work = mockWorkDetails[workId];
    const body = JSON.parse(String(init.body)) as FieldEditIn;
    const editable = new Set(["title", "doi", "year_issue", "journal", "volume", "pub_type_raw", "cohort", "abstract", "keywords_raw"]);
    if (!editable.has(body.field)) throw new ApiError(400, `không cho phép chỉnh trường '${body.field}'`);
    if (!body.reason?.trim()) throw new ApiError(409, "cần ghi lý do chỉnh sửa");
    if (!work) data = undefined;
    else {
      const field = work.fields.find((item) => item.field === body.field);
      const old = field?.value ?? null;
      const value = body.field === "year_issue" && body.value !== null && String(body.value).trim() !== "" ? Number(body.value) : body.value;
      if (body.field === "year_issue" && typeof value === "number" && !Number.isFinite(value)) throw new ApiError(409, `năm phát hành không hợp lệ: '${String(body.value)}'`);
      if (body.field === "title" && !String(value ?? "").trim()) throw new ApiError(409, "tiêu đề không được để trống");
      if (field) {
        field.value = value === null ? null : String(value);
        field.raw = old;
        field.source = `Chỉnh tay bởi ${mockUser?.display_name ?? "Người dùng"}, lúc ${new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(new Date())}`;
      }
      work.has_manual = true;
      if (body.field === "title") {
        work.title = String(value);
        const summary = mockWorks.items.find((item) => item.id === workId);
        if (summary) summary.title = String(value);
      }
      data = { field: body.field, old, new: value } satisfies FieldEditOut;
    }
  } else if (/^\/api\/works\/\d+\/citation$/.test(url.pathname)) {
    const style = url.searchParams.get("style") as keyof typeof citationsFixture;
    data = citationsFixture[style] ?? citationsFixture.apa;
  } else if (/^\/api\/works\/\d+$/.test(url.pathname)) data = mockWorkDetails[id];
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
    const items = state === "ChoXacNhan" ? mockAuthorQueue.items.filter((row) => !q || row.raw_name.toLocaleLowerCase("vi").includes(q)) : [];
    data = { ...mockAuthorQueue, state, items, page: { ...mockAuthorQueue.page, total: items.length } };
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
  else if (url.pathname === "/api/ai/experts" && init?.method === "POST") data = { ...expertsFixture, query_id: Date.now() };
  else if (/^\/api\/ai\/experts\/\d+$/.test(url.pathname)) data = { ...expertsFixture, query_id: id };
  else if (url.pathname === "/api/public/check-topic") data = publicTopicFixture;
  else if (url.pathname === "/api/ai/map") data = mapFixture;
  else if (url.pathname === "/api/ai/trends") {
    const by = url.searchParams.get("by");
    data = by === "cohort" ? { ...trendsFixture, keys: ["K18", "K19", "K20", "K21"], series: trendsFixture.series.map((series) => ({ ...series, values: series.values.slice(0, 4).map((value, index) => ({ ...value, key: `K${18 + index}` })) })) } : trendsFixture;
  }
  else if (url.pathname === "/api/ai/coauthors") data = coauthorsFixture;
  else if (url.pathname === "/api/ai/screen/cohorts") data = screenCohortsFixture;
  else if (url.pathname === "/api/ai/screen") {
    const cohort = url.searchParams.get("cohort");
    const min = url.searchParams.get("min");
    const minScore = Number(url.searchParams.get("min_score") ?? 0);
    const order = { thap: 0, vua: 1, cao: 2 } as const;
    const items = screenFixture.items.filter((item) => (!cohort || item.cohort === cohort) && (!min || order[item.level as keyof typeof order] >= order[min as keyof typeof order]) && item.max_score >= minScore);
    data = { ...screenFixture, items, page: { ...screenFixture.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  }
  else if (url.pathname === "/api/ai/mentors" && !init?.method) {
    const minVotes = Number(url.searchParams.get("min_votes")) || 0;
    const items = mockMentors.items.filter((item) => !minVotes || item.candidates.some((candidate) => candidate.votes >= minVotes));
    data = { items, page: { ...mockMentors.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  }
  else if (/^\/api\/ai\/mentors\/\d+\/accept$/.test(url.pathname)) {
    const workId = Number(url.pathname.split("/").at(-2));
    const item = mockMentors.items.find((mentor) => mentor.work_id === workId);
    const personId = (JSON.parse(String(init?.body)) as { person_id: number }).person_id;
    const candidate = item?.candidates.find((person) => person.person_id === personId);
    if (!item || !candidate) throw new ApiError(404, `Không có ứng viên #${personId} cho đồ án #${workId}.`);
    if (item.pending_link) throw new ApiError(409, "Lượt tên người hướng dẫn đã có liên kết đang chờ xác nhận.");
    const linkId = 900 + workId;
    item.pending_link = { link_id: linkId, person_id: personId, state: "ChoXacNhan" };
    mockAuthorQueue.items.unshift({
      link_id: linkId, raw_name: "ICTU_TEACHER", work_id: workId, work_title: item.title,
      candidate_person_id: personId, candidate_name: candidate.display_name, confidence: "ai_mentor",
      degree_conflict: false, group_work_count: 1, ai_rank: 1, ai_score: candidate.score,
      ai_reason: `AI tổng hợp ${candidate.votes} phiếu từ các đồ án gần nhất.`,
    });
    mockAuthorQueue.page.total = mockAuthorQueue.items.length;
    data = { ok: true, link_id: linkId, person_id: personId, state: "ChoXacNhan" } satisfies AcceptMentorResult;
  }
  else if (url.pathname === "/api/quality") data = qualityFixture;
  else if (url.pathname === "/api/quality/anomalies") {
    const kind = url.searchParams.get("kind");
    const severity = url.searchParams.get("severity");
    const state = url.searchParams.get("state") ?? "open";
    const items = mockAnomalies.items.filter((item) => (!kind || item.kind === kind) && (!severity || item.severity === severity) && (!state || item.state === state));
    data = { items, summary: mockAnomalies.summary, page: { ...mockAnomalies.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  }
  else if (/^\/api\/quality\/anomalies\/\d+\/dismiss$/.test(url.pathname)) {
    const body = JSON.parse(String(init?.body)) as DismissAnomalyIn;
    if (!body.reason.trim()) throw new ApiError(400, "cần ghi lý do bỏ qua");
    const anomaly = mockAnomalies.items.find((item) => item.id === Number(url.pathname.split("/").at(-2)));
    if (!anomaly) throw new ApiError(404, "Không tìm thấy cảnh báo");
    anomaly.state = "dismissed";
    mockAnomalies.summary[anomaly.kind].open = Math.max(0, mockAnomalies.summary[anomaly.kind].open - 1);
    data = { ok: true, id: anomaly.id, state: "dismissed" } satisfies DismissAnomalyOut;
  }
  else if (url.pathname === "/api/recent") data = recentFixture;
  else if (/^\/api\/persons\/\d+\/cv$/.test(url.pathname)) data = `<!doctype html><html lang="vi"><body><h1>${personFixture.display_name}</h1><h2>Công trình</h2>${citationsFixture.apa.split("\n").map((citation) => `<div class="pub">${citation}</div>`).join("")}<footer>Sinh từ ICTU-CRIS</footer></body></html>`;
  else if (url.pathname === "/api/feed.xml") data = "<?xml version=\"1.0\"?><rss version=\"2.0\"><channel><title>ICTU-CRIS</title></channel></rss>";
  else if (url.pathname === "/api/about") data = aboutFixture;
  else if (url.pathname === "/api/stats") data = statsFixture;
  else if (url.pathname === "/api/notifications" && !init?.method) {
    const unreadOnly = url.searchParams.get("unread") === "1";
    const items = mockNotifications.filter((item) => !unreadOnly || item.read_at === null);
    data = { items, unread: mockNotifications.filter((item) => item.read_at === null).length, page: { page: Number(url.searchParams.get("page") ?? 1), per_page: 50, total: items.length } } satisfies NotificationList;
  }
  else if (url.pathname === "/api/notifications/read-all") {
    const now = new Date().toISOString();
    mockNotifications.forEach((item) => { if (item.read_at === null) item.read_at = now; });
    data = { ok: true };
  }
  else if (/^\/api\/notifications\/\d+\/read$/.test(url.pathname)) {
    const notificationId = Number(url.pathname.split("/").at(-2));
    const notification = mockNotifications.find((item) => item.id === notificationId);
    if (!notification) throw new ApiError(404, "Không tìm thấy thông báo.");
    notification.read_at ??= new Date().toISOString();
    data = { ok: true };
  }
  else if (url.pathname === "/api/audit") {
    const entity = url.searchParams.get("entity");
    const entityId = url.searchParams.get("entity_id");
    const items = auditFixture.items.filter((row) => (!entity || row.entity === entity) && (!entityId || row.entity_id === Number(entityId)));
    data = { items, page: { ...auditFixture.page, page: Number(url.searchParams.get("page") ?? 1), total: items.length } };
  }
  else if (url.pathname === "/api/periods" && !init?.method) data = mockPeriods;
  else if (url.pathname === "/api/periods" && init?.method === "POST") {
    const body = JSON.parse(String(init.body)) as PeriodOpenIn;
    const period = { ...body, id: 404, criteria: body.criteria ?? null, state: "DangMo", opens_at: new Date().toISOString(), created_at: new Date().toISOString() };
    mockPeriods.unshift(period);
    data = period;
  }
  else if (/^\/api\/periods\/\d+\/reports$/.test(url.pathname) && !init?.method) {
    data = mockPeriodReports[Number(url.pathname.split("/").at(-2))] ?? [];
  }
  else if (/^\/api\/periods\/\d+\/reports$/.test(url.pathname) && init?.method === "POST") {
    const periodId = Number(url.pathname.split("/").at(-2));
    const body = JSON.parse(String(init.body)) as CreateReportIn;
    data = createMockReport(periodId, body.note?.trim() || null);
  }
  else if (/^\/api\/reports\/\d+$/.test(url.pathname)) data = mockReportDetails[id];
  else if (/^\/api\/units\/\d+\/overview$/.test(url.pathname)) data = unitOverviewFixture[Number(url.pathname.split("/").at(-2))];
  else if (url.pathname === "/api/me/works") {
    if (mockUser?.person_id === null || mockUser?.person_id === undefined) throw new ApiError(409, "Tài khoản chưa gắn với hồ sơ giảng viên");
    data = { ...mockMyWorks, page: { ...mockMyWorks.page, page: Number(url.searchParams.get("page") ?? 1) } };
  }
  else if (url.pathname === "/api/me/declarations" && !init?.method) {
    data = { items: Object.values(mockDeclarations).flat().filter((row) => mockMyDeclarationIds.has(row.id)) };
  }
  else if (url.pathname === "/api/me/declarations" && init?.method === "POST") {
    const body = JSON.parse(String(init.body)) as MyDeclarationCreateIn;
    const period = mockPeriods.find((item) => item.id === body.period_id);
    const work = mockMyWorks.items.find((item) => item.work_id === body.work_id);
    const unit = statsFixture.by_unit.find((item) => item.unit_id === mockUser?.unit_id);
    if (!mockUser?.roles.some((role) => ["lecturer", "faculty_officer", "rd_officer"].includes(role))) throw new ApiError(403, "cần vai trò: faculty_officer, rd_officer, lecturer");
    if (period?.state !== "DangMo") throw new ApiError(409, "chỉ kê khai được khi kỳ báo cáo đang mở");
    if (!work) throw new ApiError(403, "chỉ kê khai được công trình của chính mình");
    if (!["DaNoiTuDong", "DaXacNhan"].includes(work.link_state)) throw new ApiError(403, "chỉ kê khai được công trình của chính mình");
    if (work.declared_in.includes(body.period_id)) throw new ApiError(409, "đã kê khai");
    if (!unit) throw new ApiError(409, "Không xác định được đơn vị để kê khai");
    const now = new Date().toISOString();
    const row: DeclarationRow = {
      id: Math.max(600, ...Object.keys(mockDeclarationDetails).map(Number)) + 1,
      period_id: period.id, work_id: work.work_id, work_title: work.title, doc_type: work.doc_type,
      doc_type_label: work.doc_type_label, unit_id: unit.unit_id, unit_code: unit.code,
      state: "Nhap", note: body.note ?? null, evidence_count: 0, last_event_at: now, created_at: now, updated_at: now,
    };
    mockDeclarations[period.id] ??= [];
    mockDeclarations[period.id].unshift(row);
    mockDeclarationDetails[row.id] = {
      ...row, events: [{ id: Date.now(), from_state: null, to_state: "Nhap", actor_id: mockUser?.id ?? 1, reason: null, at: now }], evidence: [],
    };
    mockMyDeclarationIds.add(row.id);
    work.declared_in.push(period.id);
    data = row;
  }
  else if (/^\/api\/periods\/\d+\/declarations$/.test(url.pathname) && !init?.method) {
    const periodId = Number(url.pathname.split("/").at(-2));
    const unitId = Number(url.searchParams.get("unit_id")) || null;
    const items = mockDeclarations[periodId];
    data = items ? { items: unitId ? items.filter((row) => row.unit_id === unitId) : items } : undefined;
  }
  else if (/^\/api\/periods\/\d+\/declarations$/.test(url.pathname) && init?.method === "POST") {
    const periodId = Number(url.pathname.split("/").at(-2));
    const period = mockPeriods.find((item) => item.id === periodId);
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
      const transitions: Record<string, { roles: string[]; reason?: boolean }> = {
        "Nhap:ChoKhoaDuyet": { roles: ["faculty_officer", "rd_officer", "lecturer"] },
        "ChoKhoaDuyet:KhoaDaDuyet": { roles: ["faculty_head"] },
        "ChoKhoaDuyet:Nhap": { roles: ["faculty_head"], reason: true },
        "KhoaDaDuyet:ChoPhongKiemTra": { roles: ["faculty_head", "rd_officer"] },
        "ChoPhongKiemTra:DatYeuCau": { roles: ["rd_officer"] },
        "ChoPhongKiemTra:Nhap": { roles: ["rd_officer"], reason: true },
        "Nhap:ChoBoSung": { roles: ["faculty_officer", "rd_officer"], reason: true },
        "ChoBoSung:Nhap": { roles: ["faculty_officer", "rd_officer"] },
        "Nhap:Rut": { roles: ["faculty_officer", "rd_officer", "lecturer"], reason: true },
        "ChoBoSung:Rut": { roles: ["faculty_officer", "rd_officer", "lecturer"], reason: true },
      };
      const transition = transitions[`${detail.state}:${body.to_state}`];
      if (!transition) throw new ApiError(409, `không thể chuyển hồ sơ từ ${detail.state} sang ${body.to_state}`);
      if (!transition.roles.some((role) => mockUser?.roles.includes(role))) throw new ApiError(403, `cần vai trò: ${transition.roles.join(", ")}`);
      if (mockUser?.roles.includes("lecturer") && !mockUser.roles.some((role) => ["faculty_officer", "rd_officer"].includes(role)) && !mockMyDeclarationIds.has(declarationId)) throw new ApiError(403, "chỉ thao tác được hồ sơ do mình tạo");
      if (transition.reason && !body.reason?.trim()) throw new ApiError(409, `chuyển sang ${body.to_state} bắt buộc phải nêu lý do`);
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
      const evidence: EvidenceOut = { id: Date.now(), kind: body.kind, url: body.url ?? null, file_name: body.file_name ?? null, note: body.note ?? null, added_by: mockUser?.id ?? 1, added_at: new Date().toISOString(), size_bytes: null, sha256: null, content_type: null };
      detail.evidence.push(evidence);
      const row = Object.values(mockDeclarations).flat().find((item) => item.id === declarationId)!;
      row.evidence_count += 1;
      data = evidence;
    }
  }
  else if (/^\/api\/declarations\/\d+\/evidence\/file$/.test(url.pathname)) {
    const declarationId = Number(url.pathname.split("/").at(-3));
    const detail = mockDeclarationDetails[declarationId];
    const form = init?.body as FormData;
    const file = form.get("file");
    if (!detail || !(file instanceof File)) data = undefined;
    else {
      const sha256 = "8f14e45fceea167a5a36dedd4bea2543d7c4a0e853ddad8c6d42f72432a07f3e";
      const contentType = file.type || "application/octet-stream";
      const evidence: EvidenceOut = {
        id: Date.now(), kind: "file", url: null, file_name: file.name, note: String(form.get("note") || "") || null,
        added_by: mockUser?.id ?? 1, added_at: new Date().toISOString(), size_bytes: file.size,
        sha256, content_type: contentType,
      };
      detail.evidence.push(evidence);
      const row = Object.values(mockDeclarations).flat().find((item) => item.id === declarationId)!;
      row.evidence_count += 1;
      data = { id: evidence.id, file_name: file.name, size_bytes: file.size, sha256, content_type: contentType } satisfies EvidenceFileOut;
    }
  }
  else if (/^\/api\/declarations\/\d+$/.test(url.pathname)) data = mockDeclarationDetails[id];
  else if (/^\/api\/periods\/\d+\/progress$/.test(url.pathname)) data = mockPeriodProgress[Number(url.pathname.split("/").at(-2))];
  else if (/^\/api\/periods\/\d+\/finalize$/.test(url.pathname)) {
    const periodId = Number(url.pathname.split("/").at(-2));
    const period = mockPeriods.find((item) => item.id === periodId);
    if (period?.state !== "DaDongNop") throw new ApiError(409, "chỉ chốt kỳ khi kỳ báo cáo đã đóng nộp");
    const skipped: PeriodFinalizeOut["skipped"] = [];
    let finalized = 0;
    for (const row of mockDeclarations[periodId] ?? []) {
      if (row.state === "DatYeuCau") {
        row.state = "DaChot";
        const detail = mockDeclarationDetails[row.id];
        const now = new Date().toISOString();
        row.updated_at = now;
        row.last_event_at = now;
        if (detail) {
          detail.state = "DaChot";
          detail.updated_at = now;
          detail.events.push({ id: Date.now(), from_state: "DatYeuCau", to_state: "DaChot", actor_id: mockUser?.id ?? 1, reason: null, at: now });
        }
        const progressUnit = mockPeriodProgress[periodId]?.units.find((item) => item.unit_id === row.unit_id);
        if (progressUnit) {
          progressUnit.counts.DatYeuCau = Math.max(0, (progressUnit.counts.DatYeuCau ?? 0) - 1);
          progressUnit.counts.DaChot = (progressUnit.counts.DaChot ?? 0) + 1;
        }
        finalized += 1;
      } else skipped.push({ id: row.id, state: row.state });
    }
    const report = createMockReport(periodId, "Tự động tạo khi chốt kỳ báo cáo.");
    data = { finalized, skipped, report_id: report.id } satisfies PeriodFinalizeOut;
  }
  else if (/^\/api\/periods\/\d+\/(close|cancel)$/.test(url.pathname)) {
    const periodId = Number(url.pathname.split("/").at(-2));
    const period = mockPeriods.find((item) => item.id === periodId);
    const state = url.pathname.endsWith("/close") ? "DaDongNop" : "Huy";
    if (period) period.state = state;
    if (mockPeriodProgress[periodId]) mockPeriodProgress[periodId].state = state;
    data = period;
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
        window.dispatchEvent(new CustomEvent("cris:api-error", { detail: { status: 401, detail: error.detail } }));
      } else if (error.status === 403) {
        error.handled = true;
        window.dispatchEvent(new CustomEvent("cris:api-error", { detail: { status: 403, detail: error.detail } }));
      }
    }
    throw error;
  }
  return response.json() as Promise<T>;
}

export async function apiTextRequest(path: string, init?: RequestInit): Promise<string> {
  if (MOCK) return mockRequest<string>(path, init);
  const response = await fetch(`${API_BASE}${path}`, { ...init, credentials: "include" });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? response.statusText));
  }
  return response.text();
}

export async function apiHtmlRequest(path: string): Promise<string> {
  if (MOCK) return mockRequest<string>(path);
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include" });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? response.statusText));
  }
  if (!response.headers.get("content-type")?.toLowerCase().startsWith("text/html")) throw new ApiError(502, "API lý lịch khoa học không trả về HTML hợp lệ.");
  return response.text();
}

export async function apiUpload<T>(path: string, body: FormData): Promise<T> {
  if (MOCK) return mockRequest<T>(path, { method: "POST", body });
  const response = await fetch(`${API_BASE}${path}`, { method: "POST", body, credentials: "include" });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail ?? response.statusText));
  }
  return response.json() as Promise<T>;
}

export const evidenceFileUrl = (id: number) => `${API_BASE}/api/evidence/${id}/file`;

export const api = {
  getMe: () => apiRequest<MeOut>("/api/auth/me"),
  login: (input: LoginIn) => apiRequest<UserOut>("/api/auth/login", { method: "POST", body: JSON.stringify(input) }),
  logout: () => apiRequest<LogoutOut>("/api/auth/logout", { method: "POST" }),
  getWorks: (filters: WorkFilters = {}) => apiRequest<WorkList>(`/api/works${queryString({ q: filters.q, mode: filters.mode, doc_type: filters.doc_type, year: filters.year, unit: filters.unit, topic: filters.topic, pub_type: filters.pub_type, quartile: filters.quartile, cohort: filters.cohort, keyword: filters.keyword, page: filters.page })}`),
  getWorkFacets: () => apiRequest<WorkFacets>("/api/works/facets"),
  getWork: (id: number) => apiRequest<WorkDetail>(`/api/works/${id}`),
  getCitation: (id: number, style: "apa" | "ieee" | "bibtex") => apiTextRequest(`/api/works/${id}/citation${queryString({ style })}`),
  editWorkField: (id: number, input: FieldEditIn) => apiRequest<FieldEditOut>(`/api/works/${id}/fields`, { method: "PATCH", body: JSON.stringify(input) }),
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
  findExperts: (input: ExpertIn) => apiRequest<ExpertOut>("/api/ai/experts", { method: "POST", body: JSON.stringify(input) }),
  getExperts: (id: number) => apiRequest<ExpertOut>(`/api/ai/experts/${id}`),
  checkPublicTopic: (input: PublicTopicCheckIn) => apiRequest<PublicTopicCheckOut>("/api/public/check-topic", { method: "POST", body: JSON.stringify(input) }),
  getMap: (color: MapColor) => apiRequest<MapOut>(`/api/ai/map${queryString({ color })}`),
  getTrends: (by: "cohort" | "year") => apiRequest<TrendsOut>(`/api/ai/trends${queryString({ by })}`),
  getCoauthors: (minWorks = 2) => apiRequest<CoauthorsOut>(`/api/ai/coauthors${queryString({ min_works: minWorks })}`),
  getScreenCohorts: () => apiRequest<ScreenCohortSummary[]>("/api/ai/screen/cohorts"),
  getScreen: (filters: ScreenFilters = {}) => apiRequest<ScreenList>(`/api/ai/screen${queryString({ cohort: filters.cohort, min: filters.min, min_score: filters.min_score, page: filters.page })}`),
  getMentors: (filters: MentorFilters = {}) => apiRequest<MentorList>(`/api/ai/mentors${queryString({ unit: filters.unit, min_votes: filters.min_votes, page: filters.page })}`),
  acceptMentor: (workId: number, personId: number) => apiRequest<AcceptMentorResult>(`/api/ai/mentors/${workId}/accept`, { method: "POST", body: JSON.stringify({ person_id: personId }) }),
  getQuality: () => apiRequest<QualityOut>("/api/quality"),
  getQualityAnomalies: (filters: QualityAnomalyFilters = {}) => apiRequest<QualityAnomalyList>(`/api/quality/anomalies${queryString({ kind: filters.kind, severity: filters.severity, state: filters.state, page: filters.page })}`),
  dismissQualityAnomaly: (id: number, input: DismissAnomalyIn) => apiRequest<DismissAnomalyOut>(`/api/quality/anomalies/${id}/dismiss`, { method: "POST", body: JSON.stringify(input) }),
  getRecent: (limit = 20) => apiRequest<RecentOut>(`/api/recent${queryString({ limit })}`),
  getPersonCv: (id: number) => apiHtmlRequest(`/api/persons/${id}/cv?format=html`),
  getFeed: () => apiTextRequest("/api/feed.xml"),
  getAbout: () => apiRequest<AboutOut>("/api/about"),
  getStats: (years = 5) => apiRequest<StatsOut>(`/api/stats${queryString({ years })}`),
  getNotifications: (unread = false, page = 1) => apiRequest<NotificationList>(`/api/notifications${queryString({ unread: unread ? 1 : undefined, page })}`),
  readNotification: (id: number) => apiRequest<{ ok: boolean }>(`/api/notifications/${id}/read`, { method: "POST" }),
  readAllNotifications: () => apiRequest<{ ok: boolean }>("/api/notifications/read-all", { method: "POST" }),
  getAudit: (filters: AuditFilters = {}) => apiRequest<AuditList>(`/api/audit${queryString({ entity: filters.entity, entity_id: filters.entity_id, actor: filters.actor, page: filters.page })}`),
  getPeriods: () => apiRequest<PeriodOut[]>("/api/periods"),
  getMyWorks: (page = 1) => apiRequest<MyWorkList>(`/api/me/works${queryString({ page })}`),
  getMyDeclarations: () => apiRequest<DeclarationList>("/api/me/declarations"),
  addMyDeclaration: (input: MyDeclarationCreateIn) => apiRequest<DeclarationRow>("/api/me/declarations", { method: "POST", body: JSON.stringify(input) }),
  getPeriodProgress: (id: number) => apiRequest<PeriodProgress>(`/api/periods/${id}/progress`),
  getDeclarations: (periodId: number, unitId?: number) => apiRequest<DeclarationList>(`/api/periods/${periodId}/declarations${queryString({ unit_id: unitId })}`),
  addDeclaration: (periodId: number, input: DeclarationCreateIn) => apiRequest<DeclarationRow>(`/api/periods/${periodId}/declarations`, { method: "POST", body: JSON.stringify(input) }),
  getDeclaration: (id: number) => apiRequest<DeclarationDetail>(`/api/declarations/${id}`),
  setDeclarationState: (id: number, input: DeclarationStateIn) => apiRequest<DeclarationRow>(`/api/declarations/${id}/state`, { method: "POST", body: JSON.stringify(input) }),
  addDeclarationEvidence: (id: number, input: DeclarationEvidenceIn) => apiRequest<EvidenceOut>(`/api/declarations/${id}/evidence`, { method: "POST", body: JSON.stringify(input) }),
  uploadDeclarationEvidence: (id: number, body: FormData) => apiUpload<EvidenceFileOut>(`/api/declarations/${id}/evidence/file`, body),
  openPeriod: (input: PeriodOpenIn) => apiRequest<PeriodOut>("/api/periods", { method: "POST", body: JSON.stringify(input) }),
  closePeriod: (id: number) => apiRequest<PeriodOut>(`/api/periods/${id}/close`, { method: "POST" }),
  cancelPeriod: (id: number) => apiRequest<PeriodOut>(`/api/periods/${id}/cancel`, { method: "POST" }),
  finalizePeriod: (id: number) => apiRequest<PeriodFinalizeOut>(`/api/periods/${id}/finalize`, { method: "POST" }),
  getPeriodReports: (id: number) => apiRequest<PeriodReportListItem[]>(`/api/periods/${id}/reports`),
  createPeriodReport: (id: number, input: CreateReportIn) => apiRequest<ReportCreateOut>(`/api/periods/${id}/reports`, { method: "POST", body: JSON.stringify(input) }),
  getReport: (id: number) => apiRequest<PeriodReport>(`/api/reports/${id}`),
  getUnitOverview: (id: number, periodId?: number) => apiRequest<UnitOverview>(`/api/units/${id}/overview${queryString({ period_id: periodId })}`),
  getSyncRuns: (page = 1) => apiRequest<SyncRunList>(`/api/sync/runs${queryString({ page })}`),
  getSyncRun: (id: number) => apiRequest<SyncRunDetail>(`/api/sync/runs/${id}`),
  getHealth: () => apiRequest<HealthOut>("/api/health"),
};

export const reportExportUrl = (id: number, format: "csv" | "xlsx") => `${API_BASE}/api/reports/${id}/export?format=${format}`;
