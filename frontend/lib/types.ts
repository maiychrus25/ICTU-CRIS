// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export interface PageInfo { page: number; per_page: number; total: number }

export interface WorkSummary {
  id: number; title: string | null; doc_type: string; doc_type_label: string;
  year: number | null; doi: string | null; state: string; needs_review: boolean;
}
export interface WorkList { items: WorkSummary[]; page: PageInfo }
export interface FieldRow { field: string; label: string; value: string | null; raw: string | null; source: string }
export interface MentionRow {
  mention_id: number; role: string; role_label: string; position: number; raw_name: string;
  is_placeholder: boolean; is_truncated: boolean; linked_person_id: number | null;
  linked_person_name: string | null; link_state: string | null; pending_count: number;
}
export interface WorkDetail {
  id: number; title: string | null; doc_type: string; doc_type_label: string; state: string;
  needs_review: boolean; has_manual: boolean; fields: FieldRow[]; mentions: MentionRow[];
}
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
}
export interface Topic { id: number; label: string; size: number }
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
export interface QualityMetric { key: string; label: string; value: unknown; queue_url: string | null }
export interface QualityOut {
  metrics: QualityMetric[]; works_by_type: Record<string, number>; works_with_link_pct: number;
  last_sync: Record<string, unknown> | null;
}
export interface AboutAI {
  provider: string; model: string; dim: number; repo: string; licence: string; size: string;
  runs: number | string; embeddings: number | Record<string, number>; topics: number;
  suggestions: number | Record<string, number>;
}
export interface AboutOut {
  source_url: string; repo_url: string; last_sync: LastSync | null; works: number;
  works_by_type: Record<string, number>; ai: AboutAI; limits: string[];
}
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
export interface HealthOut { status: "ok" }
export interface WorkFilters { q?: string; doc_type?: string; year?: number; unit?: string; topic?: number; page?: number }
