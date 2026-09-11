# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kiểu dữ liệu vào/ra của API — mọi endpoint có response_model để OpenAPI đầy đủ."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DOC_TYPE_LABELS = {
    "bai_bao": "Bài báo", "do_an": "Đồ án", "luan_van": "Luận văn", "luan_an": "Luận án",
    "hoc_lieu": "Học liệu", "giang_vien": "Giảng viên", "dang_ky_do_an": "Đăng ký đồ án",
}


class Page(BaseModel):
    page: int
    per_page: int
    total: int


# ---------- tra cứu ----------
class WorkSummary(BaseModel):
    id: int
    title: str | None
    doc_type: str
    doc_type_label: str
    year: int | None = None
    doi: str | None = None
    state: str
    needs_review: bool = False
    score: float | None = None    # cosine 0..1, chỉ có ở mode=semantic
    keywords: list[str] = Field(default_factory=list)   # tách keywords_raw, tối đa 6 đầu tiên


class WorkList(BaseModel):
    items: list[WorkSummary]
    page: Page
    mode: Literal["keyword", "semantic"] = "keyword"
    note: str | None = None       # vd rơi về từ khoá vì AI chưa bật


class FieldRow(BaseModel):
    field: str
    label: str
    value: str | None          # giá trị đang dùng
    raw: str | None            # giá trị gốc
    source: str                # nguồn: đồng bộ từ đâu / chuẩn hoá / chỉnh tay bởi ai


class MentionRow(BaseModel):
    mention_id: int
    role: str
    role_label: str
    position: int
    raw_name: str
    is_placeholder: bool
    is_truncated: bool
    linked_person_id: int | None = None
    linked_person_name: str | None = None
    link_state: str | None = None
    pending_count: int = 0


class WorkDetail(BaseModel):
    id: int
    title: str | None
    doc_type: str
    doc_type_label: str
    state: str
    needs_review: bool
    has_manual: bool
    fields: list[FieldRow]
    mentions: list[MentionRow]
    pdf_url: str | None = None     # đầu tiên trong detail.pdf của bản ghi nguồn hiện hành
    source_url: str | None = None  # detail.url hoặc archive.url
    keywords: list[str] = Field(default_factory=list)   # tách keywords_raw theo [,;], không trùng


# ---------- bộ lọc/thống kê công trình (K1) ----------
class FacetValue(BaseModel):
    value: str
    label: str
    n: int


class FacetYear(BaseModel):
    value: int
    n: int


class FacetUnit(BaseModel):
    value: int
    code: str
    name: str
    n: int


class WorksFacetsOut(BaseModel):
    pub_types: list[FacetValue]
    quartiles: list[FacetValue]
    cohorts: list[FacetValue]
    years: list[FacetYear]
    units: list[FacetUnit]


class FieldEditIn(BaseModel):
    field: str
    value: Any = None
    reason: str | None = None      # tầng nghiệp vụ (cris.edit) từ chối nếu rỗng → 409


class FieldEditOut(BaseModel):
    field: str
    old: Any
    new: Any


class PersonPublication(BaseModel):
    work_id: int
    title: str | None
    doc_type: str
    year: int | None
    doi: str | None
    link_state: str
    confidence: str | None


class LastSync(BaseModel):
    id: int
    source: str
    scope: str
    status: str
    started_at: datetime | None
    finished_at: datetime | None


class PersonProfile(BaseModel):
    id: int
    display_name: str
    degree: str | None
    email: str | None
    orcid: str | None
    by_type: dict[str, int]
    by_year: dict[str, int]
    publications: list[PersonPublication]
    pending_count: int
    last_sync: LastSync | None
    rank: str | None = None            # học hàm (PGS/GS), cột person.rank
    scholar_url: str | None = None
    citation_stats: dict[str, Any] | None = None   # chưa tính — luôn null


class PersonSearchRow(BaseModel):
    id: int
    display_name: str
    degree: str | None = None
    unit_code: str | None = None
    kind: str
    works: int


class Topic(BaseModel):
    id: int
    label: str
    size: int
    keywords: list[str] = Field(default_factory=list)   # 8 từ khoá nặng nhất
    built_at: datetime | None = None


class TopicKeyword(BaseModel):
    keyword: str
    weight: float


class TopicDetail(BaseModel):
    id: int
    label: str
    size: int
    keywords: list[TopicKeyword]
    works: list[WorkSummary]


# ---------- hàng đợi tác giả ----------
class AuthorQueueRow(BaseModel):
    link_id: int
    raw_name: str
    work_id: int
    work_title: str | None
    candidate_person_id: int
    candidate_name: str
    confidence: str
    degree_conflict: bool
    group_work_count: int
    ai_rank: int | None = None
    ai_score: float | None = None
    ai_reason: str | None = None


class AuthorQueueList(BaseModel):
    items: list[AuthorQueueRow]
    page: Page
    state: str


class DecideAuthorsIn(BaseModel):
    link_ids: list[int] = Field(min_length=1)
    decision: Literal["confirm", "reject", "reassign"]
    reason: str | None = None
    person_id: int | None = None


class DecideResult(BaseModel):
    ok: bool
    processed: list[int]
    failed_id: int | None = None
    detail: str | None = None


# ---------- hàng đợi nghi trùng ----------
class DupGroupSummary(BaseModel):
    id: int
    doc_type: str
    basis: str
    basis_label: str
    hint: str | None
    state: str
    member_count: int
    created_at: datetime | None


class DupGroupList(BaseModel):
    items: list[DupGroupSummary]
    page: Page


class DupMember(BaseModel):
    id: int
    state: str
    title: str | None
    fields: dict[str, Any]         # các trường trong dedup.COMPARE
    diff: dict[str, Any] | None    # đã tính sẵn lúc find_duplicates


class DupGroupDetail(BaseModel):
    id: int
    doc_type: str
    basis: str
    basis_label: str
    hint: str | None
    state: str
    compare_fields: list[str]
    field_labels: dict[str, str]
    diff_fields: list[str]
    members: list[DupMember]
    ai_similarity: dict[str, Any] | None = None
    decided_by: int | None = None
    decided_at: datetime | None = None
    reason: str | None = None
    survivor_work_id: int | None = None


class DecideDupIn(BaseModel):
    decision: Literal["merge", "keep", "skip"]
    survivor_id: int | None = None
    field_choices: dict[str, int] = Field(default_factory=dict)
    reason: str | None = None


# ---------- đối chiếu đề tài ----------
class CompareIn(BaseModel):
    title: str = Field(min_length=3)
    description: str = ""
    aspects: dict[str, str] = Field(default_factory=dict)   # bai_toan / doi_tuong / pham_vi / phuong_phap
    doc_types: list[str] | None = None
    k: int = Field(default=10, ge=1, le=50)


class CompareResultItem(BaseModel):
    work_id: int
    title: str | None
    doc_type: str
    year: int | None = None
    score: float
    aspects: dict[str, str]
    url: str | None = None
    explanation: str | None = None
    ai_generated: bool = False


class CompareOut(BaseModel):
    query_id: int
    provider: str
    fallback: bool
    note: str
    input: dict[str, Any]
    results: list[CompareResultItem]
    created_at: datetime | None = None


# ---------- tìm chuyên gia (J1) ----------
class ExpertsIn(BaseModel):
    title: str = Field(min_length=3)
    description: str = ""
    aspects: dict[str, str] = Field(default_factory=dict)
    k: int = Field(default=10, ge=1, le=50)
    exclude_person_ids: list[int] = Field(default_factory=list)
    min_degree: Literal["TS", "ThS"] | None = None
    unit: int | None = None
    recent_years: int = Field(default=3, ge=0, le=50)


class ExpertEvidence(BaseModel):
    work_id: int
    title: str | None
    doc_type: str
    year: int | None = None
    score: float


class ExpertResult(BaseModel):
    person_id: int
    display_name: str
    degree: str | None = None
    unit_code: str | None = None
    score: float
    works_matched: int
    evidence: list[ExpertEvidence]


class ExpertsOut(BaseModel):
    query_id: int | None = None
    provider: str
    fallback: bool
    note: str
    results: list[ExpertResult]


# ---------- cổng công khai kiểm tra đề tài ----------
class CheckTopicIn(BaseModel):
    title: str = Field(min_length=3)
    description: str = ""


class CheckTopicSimilar(BaseModel):
    work_id: int
    title: str | None
    doc_type: str
    cohort: str | None = None
    year: int | None = None
    score: float
    level: str


class CheckTopicExpert(BaseModel):
    person_id: int
    display_name: str
    degree: str | None = None
    unit_code: str | None = None
    score: float


class CheckTopicOut(BaseModel):
    similar: list[CheckTopicSimilar]
    experts: list[CheckTopicExpert]
    note: str


# ---------- chất lượng, về hệ thống ----------
class QualityMetric(BaseModel):
    key: str
    label: str
    value: Any
    queue_url: str | None = None


class QualityOut(BaseModel):
    metrics: list[QualityMetric]
    works_by_type: dict[str, int]
    works_with_link_pct: float
    last_sync: dict[str, Any] | None


class AboutOut(BaseModel):
    source_url: str
    repo_url: str
    last_sync: LastSync | None
    works: int
    works_by_type: dict[str, int]
    ai: dict[str, Any]
    limits: list[str]
    auth_required: bool = False


# ---------- đăng nhập ----------
class LoginIn(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str
    roles: list[str] = Field(default_factory=list)
    unit_id: int | None = None
    unit_code: str | None = None
    person_id: int | None = None


class MeOut(BaseModel):
    user: UserOut | None
    auth_required: bool


# ---------- tổng quan / thống kê ----------
class YearTypeRow(BaseModel):
    year: int
    bai_bao: int = 0
    do_an: int = 0
    luan_van: int = 0
    luan_an: int = 0
    hoc_lieu: int = 0


class UnknownYearRow(BaseModel):
    bai_bao: int = 0
    do_an: int = 0
    luan_van: int = 0
    luan_an: int = 0
    hoc_lieu: int = 0


class UnitWorks(BaseModel):
    unit_id: int
    code: str
    name: str
    works: int


class TopPerson(BaseModel):
    person_id: int
    display_name: str
    unit_code: str | None = None
    works: int


class StatsQueues(BaseModel):
    authors_pending: int
    dup_groups_open: int


class StatsCoverage(BaseModel):
    works_with_link_pct: float
    works_without_unit: int


class StatsOut(BaseModel):
    by_year_type: list[YearTypeRow]
    unknown_year: UnknownYearRow
    by_unit: list[UnitWorks]
    top_persons: list[TopPerson]
    queues: StatsQueues
    coverage: StatsCoverage
    last_sync: LastSync | None


# ---------- nhật ký thao tác ----------
class AuditRow(BaseModel):
    id: int
    at: datetime
    actor_name: str | None = None
    action: str
    action_label: str
    entity: str
    entity_id: int
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None


class AuditList(BaseModel):
    items: list[AuditRow]
    page: Page


# ---------- kỳ báo cáo ----------
class PeriodOut(BaseModel):
    id: int
    code: str
    name: str
    scope: dict[str, Any]
    criteria: str | None = None
    state: str
    opens_at: datetime | None = None
    due_at: datetime
    created_at: datetime


class PeriodOpenIn(BaseModel):
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    scope: dict[str, Any]
    criteria: str | None = None
    due_at: datetime


class PeriodUnitProgress(BaseModel):
    unit_id: int
    unit_code: str
    unit_name: str
    counts: dict[str, int]
    total: int


class PeriodProgress(BaseModel):
    period_id: int
    state: str
    due_at: datetime | None = None
    days_remaining: int | None = None
    units: list[PeriodUnitProgress]


class PeriodFinalizeSkipped(BaseModel):
    id: int
    state: str


class PeriodFinalizeOut(BaseModel):
    finalized: int
    skipped: list[PeriodFinalizeSkipped]


# ---------- kê khai công trình vào kỳ (G3) ----------
class DeclarationRow(BaseModel):
    id: int
    period_id: int
    work_id: int
    work_title: str | None
    doc_type: str
    doc_type_label: str
    unit_id: int
    unit_code: str
    state: str
    note: str | None = None
    evidence_count: int
    last_event_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DeclarationList(BaseModel):
    items: list[DeclarationRow]


class DeclarationCreateIn(BaseModel):
    work_id: int
    unit_id: int
    note: str | None = None


# ---------- công trình/hồ sơ của tôi (H3, giảng viên tự kê khai) ----------
class MyWorkRow(BaseModel):
    work_id: int
    title: str | None
    doc_type: str
    doc_type_label: str
    year: int | None = None
    doi: str | None = None
    link_state: str
    declared_in: list[int] = Field(default_factory=list)


class MyWorkList(BaseModel):
    items: list[MyWorkRow]
    page: Page


class MyDeclarationCreateIn(BaseModel):
    period_id: int
    work_id: int
    note: str | None = None


class DeclarationStateIn(BaseModel):
    to_state: Literal["Nhap", "ChoBoSung", "ChoKhoaDuyet", "KhoaDaDuyet", "ChoPhongKiemTra", "DatYeuCau", "Rut"]
    reason: str | None = None


class DeclarationEvidenceIn(BaseModel):
    kind: Literal["link", "file", "note"]
    url: str | None = None
    file_name: str | None = None
    note: str | None = None


class EvidenceOut(BaseModel):
    id: int
    kind: str
    url: str | None = None
    file_name: str | None = None
    note: str | None = None
    added_by: int | None = None
    added_at: datetime
    size_bytes: int | None = None
    sha256: str | None = None
    content_type: str | None = None


# ---------- minh chứng dạng tệp (I2) ----------
class EvidenceFileOut(BaseModel):
    id: int
    file_name: str | None = None
    size_bytes: int
    sha256: str
    content_type: str


class DeclarationEventOut(BaseModel):
    id: int
    from_state: str | None = None
    to_state: str
    actor_id: int | None = None
    reason: str | None = None
    at: datetime


class DeclarationDetail(BaseModel):
    id: int
    period_id: int
    work_id: int
    work_title: str | None
    doc_type: str
    doc_type_label: str
    unit_id: int
    unit_code: str
    state: str
    note: str | None = None
    created_at: datetime
    updated_at: datetime
    events: list[DeclarationEventOut]
    evidence: list[EvidenceOut]


# ---------- rà soát trùng đề tài theo khoá ----------
class ScreenNeighbour(BaseModel):
    work_id: int
    title: str | None
    cohort: str | None
    score: float
    aspects: dict[str, str]


class ScreenItem(BaseModel):
    work_id: int
    title: str | None
    cohort: str | None
    neighbours: list[ScreenNeighbour]
    max_score: float
    level: str


class ScreenList(BaseModel):
    items: list[ScreenItem]
    page: Page
    cohorts: list[str]


class ScreenCohortSummary(BaseModel):
    cohort: str
    screened: int
    flagged: int


# ---------- bản đồ tri thức, xu hướng chủ đề, đồ thị đồng tác giả (J2) ----------
class MapPoint(BaseModel):
    id: int
    x: float
    y: float
    topic_id: int | None = None
    unit_id: int | None = None
    year: int | None = None
    doc_type: str
    title: str | None


class MapTopic(BaseModel):
    id: int
    label: str
    size: int
    cx: float
    cy: float


class MapUnit(BaseModel):
    id: int
    code: str
    name: str


class MapOut(BaseModel):
    points: list[MapPoint]
    topics: list[MapTopic]
    units: list[MapUnit]
    built_at: datetime
    method: str


class TrendValue(BaseModel):
    key: int | str
    count: int
    share: float


class TrendSeries(BaseModel):
    topic_id: int | None = None
    label: str
    values: list[TrendValue]


class TrendsOut(BaseModel):
    series: list[TrendSeries]
    keys: list[int | str]


class CoauthorNode(BaseModel):
    person_id: int
    display_name: str | None
    unit_code: str | None = None
    works: int


class CoauthorEdge(BaseModel):
    a: int
    b: int
    weight: int


class CoauthorsOut(BaseModel):
    nodes: list[CoauthorNode]
    edges: list[CoauthorEdge]


# ---------- gợi ý người hướng dẫn (ICTU_TEACHER) ----------
class MentorEvidence(BaseModel):
    work_id: int
    title: str | None
    score: float


class MentorCandidate(BaseModel):
    person_id: int
    display_name: str
    degree: str | None
    votes: int
    score: float
    evidence: list[MentorEvidence]


class MentorPendingLink(BaseModel):
    link_id: int
    person_id: int
    state: str


class MentorItem(BaseModel):
    work_id: int
    title: str | None
    cohort: str | None
    mention_id: int
    candidates: list[MentorCandidate]
    pending_link: MentorPendingLink | None = None


class MentorList(BaseModel):
    items: list[MentorItem]
    page: Page


class AcceptMentorIn(BaseModel):
    person_id: int


class AcceptMentorResult(BaseModel):
    ok: bool
    link_id: int
    person_id: int
    state: str


# ---------- lịch sử đồng bộ ----------
class SyncRunSummary(BaseModel):
    id: int
    source: str
    scope: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    duration_s: float | None
    added: int
    changed: int
    vanished: int
    errors: list[Any]
    warnings: list[Any]


class SyncRunList(BaseModel):
    items: list[SyncRunSummary]
    page: Page


class SourceRecordRow(BaseModel):
    id: int
    source_key: str
    doc_type: str
    version: int
    fetched_at: datetime | None


class SyncRunDetail(SyncRunSummary):
    expected_count: dict[str, Any] | None = None
    fetched_count: dict[str, Any] | None = None
    triggered_by: int | None = None
    records: list[SourceRecordRow]


# ---------- mới cập nhật từ kho (K1) ----------
class RecentAddedRow(WorkSummary):
    first_seen_at: datetime


class RecentChangedRow(WorkSummary):
    version: int


class RecentOut(BaseModel):
    added: list[RecentAddedRow]
    changed: list[RecentChangedRow]
    run: LastSync | None
