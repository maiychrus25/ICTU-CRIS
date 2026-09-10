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


class WorkList(BaseModel):
    items: list[WorkSummary]
    page: Page


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


class Topic(BaseModel):
    id: int
    label: str
    size: int


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
