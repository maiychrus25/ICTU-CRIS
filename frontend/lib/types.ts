// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export interface PageInfo { page: number; per_page: number; total: number }

export interface WorkSummary {
  id: number; title: string | null; doc_type: string; doc_type_label: string;
  year: number | null; doi: string | null; state: string; needs_review: boolean;
  score?: number | null; keywords?: string[]; first_seen_at?: string; version?: number;
}
export interface WorkList { items: WorkSummary[]; page: PageInfo; mode?: "keyword" | "semantic"; note?: string | null }
export interface FieldRow { field: string; label: string; value: string | null; raw: string | null; source: string }
export interface MentionRow {
  mention_id: number; role: string; role_label: string; position: number; raw_name: string;
  is_placeholder: boolean; is_truncated: boolean; linked_person_id: number | null;
  linked_person_name: string | null; link_state: string | null; pending_count: number;
}
export interface WorkDetail {
  id: number; title: string | null; doc_type: string; doc_type_label: string; state: string;
  needs_review: boolean; has_manual: boolean; fields: FieldRow[]; mentions: MentionRow[];
  pdf_url?: string | null; source_url?: string | null; keywords?: string[];
}
export interface FieldEditIn { field: string; value: unknown; reason: string }
export interface FieldEditOut { field: string; old: unknown; new: unknown }
export interface PersonPublication {
  work_id: number; title: string | null; doc_type: string; year: number | null; doi: string | null;
  link_state: string; confidence: string | null;
}
export interface LastSync {
  id: number; source: string; scope: string; status: string;
  started_at: string | null; finished_at: string | null;
}
export interface PersonProfile {
  id: number; display_name: string; degree: string | null; email: string | null; orcid: string | null;
  by_type: Record<string, number>; by_year: Record<string, number>; publications: PersonPublication[];
  pending_count: number; last_sync: LastSync | null;
  rank?: string | null; scholar_url?: string | null; citation_stats?: Record<string, number> | null;
}
export interface PersonSearchRow {
  id: number; display_name: string; degree: string | null; unit_code: string | null; kind: string; works: number;
}
export interface Topic { id: number; label: string; size: number; keywords: string[]; built_at: string | null }
export interface TopicKeyword { keyword: string; weight: number }
export interface TopicDetail { id: number; label: string; size: number; keywords: TopicKeyword[]; works: WorkSummary[] }
export interface AuthorQueueRow {
  link_id: number; raw_name: string; work_id: number; work_title: string | null;
  candidate_person_id: number; candidate_name: string; confidence: string; degree_conflict: boolean;
  group_work_count: number; ai_rank: number | null; ai_score: number | null; ai_reason: string | null;
}
export interface AuthorQueueList { items: AuthorQueueRow[]; page: PageInfo; state: string }
export interface DecideAuthorsIn {
  link_ids: number[]; decision: "confirm" | "reject" | "reassign"; reason?: string; person_id?: number;
}
export interface DecideResult { ok: boolean; processed: number[]; failed_id?: number | null; detail?: string | null }
export interface DupGroupSummary {
  id: number; doc_type: string; basis: string; basis_label: string; hint: string | null;
  state: string; member_count: number; created_at: string | null;
}
export interface DupGroupList { items: DupGroupSummary[]; page: PageInfo }
export interface DupMember { id: number; state: string; title: string | null; fields: Record<string, unknown>; diff: Record<string, unknown> | null }
export interface DupGroupDetail {
  id: number; doc_type: string; basis: string; basis_label: string; hint: string | null; state: string;
  compare_fields: string[]; field_labels: Record<string, string>; diff_fields: string[]; members: DupMember[];
  ai_similarity: Record<string, unknown> | null; decided_by: number | null; decided_at: string | null;
  reason: string | null; survivor_work_id: number | null;
}
export interface DecideDupIn {
  decision: "merge" | "keep" | "skip"; survivor_id?: number;
  field_choices?: Record<string, number>; reason?: string;
}
export interface CompareIn {
  title: string; description: string; aspects: Record<string, string>; doc_types?: string[]; k?: number;
}
export interface CompareResultItem {
  work_id: number; title: string | null; doc_type: string; year: number | null; score: number;
  aspects: Record<string, string>; url: string | null; explanation: string | null; ai_generated: boolean;
}
export interface CompareOut {
  query_id: number; provider: string; fallback: boolean; note: string; input: Record<string, unknown>;
  results: CompareResultItem[]; created_at: string | null;
}
export type ScreenLevel = "cao" | "vua" | "thap";
export interface ScreenNeighbour {
  work_id: number; title: string | null; cohort: string | null; score: number; aspects: Record<string, string>;
}
export interface ScreenItem {
  work_id: number; title: string | null; cohort: string | null; neighbours: ScreenNeighbour[];
  max_score: number; level: string;
}
export interface ScreenList { items: ScreenItem[]; page: PageInfo; cohorts: string[] }
export interface ScreenCohortSummary { cohort: string; screened: number; flagged: number }
export interface ScreenFilters { cohort?: string; min?: ScreenLevel; min_score?: number; page?: number }
export interface MentorEvidence { work_id: number; title: string | null; score: number }
export interface MentorCandidate {
  person_id: number; display_name: string; degree: string | null; votes: number; score: number;
  evidence: MentorEvidence[];
}
export interface MentorPendingLink { link_id: number; person_id: number; state: string }
export interface MentorItem {
  work_id: number; title: string | null; cohort: string | null; mention_id: number;
  candidates: MentorCandidate[]; pending_link: MentorPendingLink | null;
}
export interface MentorList { items: MentorItem[]; page: PageInfo }
export interface MentorFilters { unit?: string; min_votes?: number; page?: number }
export interface AcceptMentorResult { ok: boolean; link_id: number; person_id: number; state: string }
export interface QualityMetric { key: string; label: string; value: unknown; queue_url: string | null }
export interface QualityOut {
  metrics: QualityMetric[]; works_by_type: Record<string, number>; works_with_link_pct: number;
  last_sync: Record<string, unknown> | null;
}
export interface AboutAI {
  provider: string; model: string; dim: number; repo: string; licence: string; size: string;
  runs: number | string; embeddings: number | Record<string, number>; topics: number;
  suggestions: number | Record<string, number>; mentor_suggestions?: number;
}
export interface AboutOut {
  source_url: string; repo_url: string; last_sync: LastSync | null; works: number;
  works_by_type: Record<string, number>; ai: AboutAI; limits: string[];
}
export interface LoginIn { email: string; password: string }
export interface UserOut {
  id: number; email: string; display_name: string; roles: string[]; unit_id: number | null; unit_code: string | null;
  person_id: number | null;
}
export interface MeOut { user: UserOut | null; auth_required: boolean }
export interface LogoutOut { ok: boolean }
export interface YearTypeRow {
  year: number; bai_bao: number; do_an: number; luan_van: number; luan_an: number; hoc_lieu: number;
}
export type UnknownYearRow = Omit<YearTypeRow, "year">;
export interface UnitWorks { unit_id: number; code: string; name: string; works: number }
export interface TopPerson { person_id: number; display_name: string; unit_code: string | null; works: number }
export interface StatsOut {
  by_year_type: YearTypeRow[]; unknown_year: UnknownYearRow; by_unit: UnitWorks[];
  top_persons: TopPerson[]; queues: { authors_pending: number; dup_groups_open: number };
  coverage: { works_with_link_pct: number; works_without_unit: number }; last_sync: LastSync | null;
}
export interface AuditRow {
  id: number; at: string; actor_name: string | null; action: string; action_label: string;
  entity: string; entity_id: number; before: Record<string, unknown> | null; after: Record<string, unknown> | null;
}
export interface AuditList { items: AuditRow[]; page: PageInfo }
export interface AuditFilters { entity?: string; entity_id?: number; actor?: number; page?: number }
export interface PeriodOut {
  id: number; code: string; name: string; scope: Record<string, unknown>; criteria: string | null;
  state: string; opens_at: string | null; due_at: string; created_at: string;
}
export interface PeriodOpenIn {
  code: string; name: string; scope: Record<string, unknown>; criteria?: string | null; due_at: string;
}
export interface PeriodUnitProgress {
  unit_id: number; unit_code: string; unit_name: string; counts: Record<string, number>; total: number;
}
export interface PeriodProgress {
  period_id: number; state: string; due_at: string | null; days_remaining: number | null; units: PeriodUnitProgress[];
}
export interface PeriodFinalizeOut { finalized: number; skipped: { id: number; state: string }[] }
export type DeclarationState = "Nhap" | "ChoBoSung" | "ChoKhoaDuyet" | "KhoaDaDuyet" | "ChoPhongKiemTra" | "DatYeuCau" | "DaChot" | "Rut";
export type DeclarationTransitionState = Exclude<DeclarationState, "DaChot">;
export type EvidenceKind = "link" | "file" | "note";
export interface DeclarationRow {
  id: number; period_id: number; work_id: number; work_title: string | null; doc_type: string;
  doc_type_label: string; unit_id: number; unit_code: string; state: DeclarationState;
  note: string | null; evidence_count: number; last_event_at: string | null; created_at: string; updated_at: string;
}
export interface DeclarationList { items: DeclarationRow[] }
export interface DeclarationCreateIn { work_id: number; unit_id: number; note?: string | null }
export interface MyWorkRow {
  work_id: number; title: string | null; doc_type: string; doc_type_label: string;
  year: number | null; doi: string | null; link_state: string; declared_in: number[];
}
export interface MyWorkList { items: MyWorkRow[]; page: PageInfo }
export interface MyDeclarationCreateIn { period_id: number; work_id: number; note?: string | null }
export interface DeclarationStateIn { to_state: DeclarationTransitionState; reason?: string | null }
export interface DeclarationEvidenceIn {
  kind: EvidenceKind; url?: string | null; file_name?: string | null; note?: string | null;
}
export interface EvidenceOut {
  id: number; kind: string; url: string | null; file_name: string | null; note: string | null;
  added_by: number | null; added_at: string; size_bytes: number | null; sha256: string | null;
  content_type: string | null;
}
export interface EvidenceFileOut {
  id: number; file_name: string | null; size_bytes: number; sha256: string; content_type: string;
}
export interface DeclarationEventOut {
  id: number; from_state: string | null; to_state: string; actor_id: number | null; reason: string | null; at: string;
}
export interface DeclarationDetail {
  id: number; period_id: number; work_id: number; work_title: string | null; doc_type: string;
  doc_type_label: string; unit_id: number; unit_code: string; state: DeclarationState; note: string | null;
  created_at: string; updated_at: string; events: DeclarationEventOut[]; evidence: EvidenceOut[];
}
export interface SyncRunSummary {
  id: number; source: string; scope: string; status: string; started_at: string; finished_at: string | null;
  duration_s: number | null; added: number; changed: number; vanished: number; errors: unknown[]; warnings: unknown[];
}
export interface SyncRunList { items: SyncRunSummary[]; page: PageInfo }
export interface SourceRecordRow { id: number; source_key: string; doc_type: string; version: number; fetched_at: string | null }
export interface SyncRunDetail extends SyncRunSummary {
  expected_count: Record<string, unknown> | null; fetched_count: Record<string, unknown> | null;
  triggered_by: number | null; records: SourceRecordRow[];
}
export interface HealthOut { status: "ok" }
export interface FacetOption { value: string; label: string; n: number }
export interface WorkFacets {
  pub_types: FacetOption[]; quartiles: FacetOption[]; cohorts: FacetOption[];
  years: FacetOption[]; units: FacetOption[];
}
export interface WorkFilters {
  q?: string; mode?: "keyword" | "semantic"; doc_type?: string; year?: number; unit?: string;
  topic?: number; pub_type?: string; quartile?: string; cohort?: string; keyword?: string; page?: number;
}
export interface ExpertEvidence { work_id: number; title: string | null; doc_type: string; year: number | null; score: number }
export interface ExpertResult {
  person_id: number; display_name: string; degree: string | null; unit_code: string | null;
  score: number; works_matched: number; evidence: ExpertEvidence[];
}
export interface ExpertIn {
  title: string; description?: string; aspects?: Record<string, string>; k?: number;
  exclude_person_ids?: number[]; min_degree?: "TS" | "ThS" | null; unit?: number; recent_years?: number;
}
export interface ExpertOut {
  query_id: number; provider: string; fallback: boolean; note: string; results: ExpertResult[];
}
export interface PublicSimilar {
  work_id: number; title: string | null; doc_type: string; cohort: string | null;
  year: number | null; score: number; level: "cao" | "vua" | "thap";
}
export interface PublicExpert {
  person_id: number; display_name: string; degree: string | null; unit_code: string | null; score: number;
}
export interface PublicTopicCheckIn { title: string; description?: string }
export interface PublicTopicCheckOut { similar: PublicSimilar[]; experts: PublicExpert[]; note: string }
export type MapColor = "topic" | "unit" | "year" | "doc_type";
export interface MapPoint {
  id: number; x: number; y: number; topic_id: number | null; unit_id: number | null;
  year: number | null; doc_type: string; title: string | null;
}
export interface MapTopic { id: number; label: string; size: number; cx: number; cy: number }
export interface MapOut { points: MapPoint[]; topics: MapTopic[]; built_at: string; method: "pca" }
export interface TrendValue { key: string; count: number; share: number }
export interface TrendSeries { topic_id: number | null; label: string; values: TrendValue[] }
export interface TrendsOut { series: TrendSeries[]; keys: string[] }
export interface CoauthorNode { person_id: number; display_name: string; unit_code: string | null; works: number }
export interface CoauthorEdge { a: number; b: number; weight: number }
export interface CoauthorsOut { nodes: CoauthorNode[]; edges: CoauthorEdge[] }
export interface RecentAdded extends WorkSummary { first_seen_at: string }
export interface RecentChanged extends WorkSummary { version: number }
export interface RecentOut { added: RecentAdded[]; changed: RecentChanged[]; run: LastSync | null }
export interface QualityAnomaly {
  id: number; kind: string; kind_label: string; work_id: number | null; title: string | null;
  person_id: number | null; display_name: string | null; detail: Record<string, unknown>;
  severity: "cao" | "vua" | "thap"; state: "open" | "dismissed" | "resolved"; created_at: string;
}
export interface QualityAnomalyList { items: QualityAnomaly[]; page: PageInfo; summary: Record<string, { open: number }> }
export interface QualityAnomalyFilters { kind?: string; severity?: string; state?: string; page?: number }
export interface DismissAnomalyIn { reason: string }
export interface DismissAnomalyOut { ok: boolean; id: number; state: "dismissed" }
