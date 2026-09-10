// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type {
  AboutOut, AuthorQueueList, CompareOut, DupGroupDetail, DupGroupList, HealthOut,
  PersonProfile, QualityOut, Topic, WorkDetail, WorkList, WorkSummary,
} from "@/lib/types";

export const workItems: WorkSummary[] = [
  { id: 1, title: "Xây dựng website quản lý thư viện trường THPT Lương Ngọc Quyến", doc_type: "do_an", doc_type_label: "Đồ án", year: 2025, doi: null, state: "DaXacNhan", needs_review: false },
  { id: 2, title: "Ứng dụng học sâu trong nhận dạng bệnh trên lá chè Thái Nguyên", doc_type: "bai_bao", doc_type_label: "Bài báo", year: 2025, doi: "10.15625/ictu.2025.102", state: "DaXacNhan", needs_review: false },
  { id: 3, title: "Phát triển hệ thống điểm danh sinh viên bằng nhận diện khuôn mặt", doc_type: "do_an", doc_type_label: "Đồ án", year: 2024, doi: null, state: "ChoXacNhan", needs_review: true },
  { id: 4, title: "Mô hình dự báo chất lượng không khí tại thành phố Thái Nguyên", doc_type: "luan_van", doc_type_label: "Luận văn", year: 2024, doi: null, state: "DaNoiTuDong", needs_review: false },
  { id: 5, title: "Giáo trình cơ sở dữ liệu phân tán", doc_type: "hoc_lieu", doc_type_label: "Học liệu", year: 2023, doi: null, state: "DaXacNhan", needs_review: false },
  { id: 6, title: "Phương pháp phát hiện xâm nhập mạng dựa trên học máy", doc_type: "bai_bao", doc_type_label: "Bài báo", year: 2023, doi: "10.1109/ictu.2023.208", state: "DaXacNhan", needs_review: false },
  { id: 7, title: "Xây dựng ứng dụng quản lý ký túc xá trên nền tảng web", doc_type: "do_an", doc_type_label: "Đồ án", year: 2025, doi: null, state: "NghiTrung", needs_review: true },
  { id: 8, title: "Nghiên cứu tối ưu mạng cảm biến không dây cho nông nghiệp", doc_type: "luan_an", doc_type_label: "Luận án", year: 2022, doi: null, state: "DaXacNhan", needs_review: false },
  { id: 9, title: "Phân tích cảm xúc phản hồi sinh viên bằng mô hình ngôn ngữ", doc_type: "bai_bao", doc_type_label: "Bài báo", year: 2024, doi: "10.15625/ictu.2024.067", state: "ChoXacNhan", needs_review: true },
  { id: 10, title: "Thiết kế hệ thống tưới cây tự động sử dụng IoT", doc_type: "do_an", doc_type_label: "Đồ án", year: 2023, doi: null, state: "DaXacNhan", needs_review: false },
  { id: 11, title: "Bài giảng nhập môn trí tuệ nhân tạo", doc_type: "hoc_lieu", doc_type_label: "Học liệu", year: 2025, doi: null, state: "DaXacNhan", needs_review: false },
  { id: 12, title: "Bảo đảm an toàn dữ liệu trong điện toán biên", doc_type: "luan_van", doc_type_label: "Luận văn", year: 2022, doi: null, state: "DaBacBo", needs_review: false },
];

export const worksFixture: WorkList = { items: workItems, page: { page: 1, per_page: 50, total: workItems.length } };

export const workDetailsFixture: Record<number, WorkDetail> = Object.fromEntries(workItems.map((work) => [work.id, {
  id: work.id,
  title: work.title,
  doc_type: work.doc_type,
  doc_type_label: work.doc_type_label,
  state: work.state,
  needs_review: work.needs_review,
  has_manual: work.id === 1,
  fields: [
    { field: "title", label: "Tiêu đề", value: work.title, raw: work.id === 1 ? "XAY DUNG WEBSITE QUAN LY THU VIEN TRUONG THPT LUONG NGOC QUYEN" : work.title, source: work.id === 1 ? "Chuẩn hoá từ kho đồ án ICTU" : "Đồng bộ kho dữ liệu ICTU" },
    { field: "doc_type", label: "Loại tài liệu", value: work.doc_type_label, raw: work.doc_type, source: "Ánh xạ danh mục chuẩn" },
    { field: "year", label: "Năm công bố", value: work.year?.toString() ?? null, raw: work.year?.toString() ?? null, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "doi", label: "DOI", value: work.doi, raw: work.doi, source: work.doi ? "Crossref" : "Không có trong nguồn gốc" },
  ],
  mentions: work.id === 1 ? [
    { mention_id: 101, role: "tac_gia", role_label: "Tác giả", position: 1, raw_name: "Nguyễn Minh Anh", is_placeholder: false, is_truncated: false, linked_person_id: null, linked_person_name: null, link_state: "ChoXacNhan", pending_count: 2 },
    { mention_id: 102, role: "huong_dan", role_label: "Giảng viên hướng dẫn", position: 2, raw_name: "TS. Nguyễn Văn A", is_placeholder: false, is_truncated: false, linked_person_id: 1, linked_person_name: "TS. Nguyễn Văn A", link_state: "DaXacNhan", pending_count: 0 },
  ] : [
    { mention_id: 100 + work.id, role: "tac_gia", role_label: "Tác giả", position: 1, raw_name: "TS. Nguyễn Văn A", is_placeholder: false, is_truncated: false, linked_person_id: 1, linked_person_name: "TS. Nguyễn Văn A", link_state: "DaNoiTuDong", pending_count: 0 },
  ],
}])) as Record<number, WorkDetail>;

export const topicsFixture: Topic[] = [
  { id: 1, label: "Trí tuệ nhân tạo", size: 38 },
  { id: 2, label: "Hệ thống thông tin", size: 27 },
  { id: 3, label: "An toàn thông tin", size: 19 },
  { id: 4, label: "Internet vạn vật", size: 16 },
];

export const personFixture: PersonProfile = {
  id: 1, display_name: "TS. Nguyễn Văn A", degree: "Tiến sĩ", email: "nguyenvana@ictu.edu.vn",
  orcid: "0000-0002-1825-0097", by_type: { bai_bao: 8, do_an: 14, hoc_lieu: 2 },
  by_year: { "2022": 3, "2023": 5, "2024": 7, "2025": 9 },
  publications: workItems.slice(0, 6).map((work) => ({ work_id: work.id, title: work.title, doc_type: work.doc_type, year: work.year, doi: work.doi, link_state: "DaXacNhan", confidence: "cao" })),
  pending_count: 2,
  last_sync: { id: 18, source: "Kho dữ liệu ICTU", scope: "Hồ sơ giảng viên", status: "success", started_at: "2026-09-10T01:00:00Z", finished_at: "2026-09-10T01:04:12Z" },
};

export const authorQueueFixture: AuthorQueueList = {
  state: "ChoXacNhan", page: { page: 1, per_page: 50, total: 6 },
  items: [
    [201, "Nguyễn Văn A", 1, "TS. Nguyễn Văn A", "Tên và đơn vị công tác trùng khớp"],
    [202, "N.V. An", 2, "TS. Nguyễn Văn An", "Tên viết tắt, có cùng chuỗi công trình"],
    [203, "Trần Thị Bình", 3, "ThS. Trần Thị Bình", "Tên đầy đủ trùng khớp"],
    [204, "Lê Hoàng", 4, "TS. Lê Văn Hoàng", "Cùng đơn vị nhưng tên chưa đủ"],
    [205, "Phạm Minh Đức", 5, "ThS. Phạm Minh Đức", "Tên và học vị phù hợp"],
    [206, "Đỗ Thu Hà", 6, "TS. Đỗ Thu Hà", "ORCID trong nguồn liên quan"],
  ].map(([linkId, rawName, workId, candidateName, reason], index) => ({
    link_id: Number(linkId), raw_name: String(rawName), work_id: Number(workId), work_title: workItems[index].title,
    candidate_person_id: index + 1, candidate_name: String(candidateName), confidence: index < 3 ? "cao" : "vua",
    degree_conflict: index === 3, group_work_count: 2 + index, ai_rank: index + 1,
    ai_score: 0.92 - index * 0.08, ai_reason: String(reason),
  })),
};

export const duplicateGroupsFixture: DupGroupList = {
  page: { page: 1, per_page: 50, total: 3 },
  items: [
    { id: 301, doc_type: "do_an", basis: "normalized_title", basis_label: "Tiêu đề chuẩn hoá", hint: "đồ án nhóm", state: "NghiTrung", member_count: 3, created_at: "2026-09-09T08:12:00Z" },
    { id: 302, doc_type: "bai_bao", basis: "doi", basis_label: "Trùng DOI", hint: null, state: "NghiTrung", member_count: 2, created_at: "2026-09-08T07:10:00Z" },
    { id: 303, doc_type: "hoc_lieu", basis: "title_year", basis_label: "Tiêu đề và năm", hint: null, state: "GiuRieng", member_count: 2, created_at: "2026-09-07T03:25:00Z" },
  ],
};

export const duplicateDetailFixture: DupGroupDetail = {
  id: 301, doc_type: "do_an", basis: "normalized_title", basis_label: "Tiêu đề chuẩn hoá",
  hint: "đồ án nhóm", state: "NghiTrung", compare_fields: ["title", "year", "authors", "unit"],
  field_labels: { title: "Tiêu đề", year: "Năm", authors: "Tác giả", unit: "Đơn vị" },
  diff_fields: ["authors"], ai_similarity: { title: 0.91 }, decided_by: null, decided_at: null, reason: null, survivor_work_id: null,
  members: [
    { id: 1, state: "active", title: workItems[0].title, fields: { title: workItems[0].title, year: 2025, authors: "Nguyễn Minh Anh; Trần Thu Hà", unit: "Khoa CNTT" }, diff: { authors: true } },
    { id: 13, state: "active", title: workItems[0].title, fields: { title: workItems[0].title, year: 2025, authors: "Lê Đức Huy; Phạm Quang Minh", unit: "Khoa CNTT" }, diff: { authors: true } },
    { id: 14, state: "active", title: workItems[0].title, fields: { title: workItems[0].title, year: 2025, authors: "Vũ Thị Lan", unit: "Khoa CNTT" }, diff: { authors: true } },
  ],
};

export const compareFixture: CompareOut = {
  query_id: 101, provider: "sentence-transformers", fallback: false,
  note: "Kết quả đối chiếu dựa trên tiêu đề, tóm tắt và siêu dữ liệu; không phải toàn văn.",
  input: { title: "Xây dựng hệ thống quản lý thư viện thông minh", description: "Ứng dụng web hỗ trợ quản lý mượn trả và gợi ý tài liệu." },
  created_at: "2026-09-11T02:00:00Z",
  results: [
    { work_id: 1, title: workItems[0].title, doc_type: "do_an", year: 2025, score: 0.82, aspects: { bai_toan: "0.78", doi_tuong: "cao", pham_vi: "0.46", phuong_phap: "thap" }, url: "/cong-trinh/?id=1", explanation: "Cùng giải quyết nghiệp vụ thư viện trường học; khác cách gợi ý tài liệu.", ai_generated: true },
    { work_id: 7, title: workItems[6].title, doc_type: "do_an", year: 2025, score: 0.61, aspects: { bai_toan: "vua", doi_tuong: "0.42", pham_vi: "thap", phuong_phap: "0.59" }, url: "/cong-trinh/?id=7", explanation: "Cùng mô hình ứng dụng quản lý nhưng khác miền nghiệp vụ.", ai_generated: true },
    { work_id: 5, title: workItems[4].title, doc_type: "hoc_lieu", year: 2023, score: 0.44, aspects: { bai_toan: "thap", doi_tuong: "vua", pham_vi: "0.38", phuong_phap: "thap" }, url: "/cong-trinh/?id=5", explanation: "Liên quan cơ sở dữ liệu, không trực tiếp giải quyết quản lý thư viện.", ai_generated: true },
    { work_id: 3, title: workItems[2].title, doc_type: "do_an", year: 2024, score: 0.39, aspects: { bai_toan: "0.31", doi_tuong: "thap", pham_vi: "vua", phuong_phap: "cao" }, url: "/cong-trinh/?id=3", explanation: "Tương đồng về phạm vi trường học và triển khai hệ thống web.", ai_generated: true },
    { work_id: 10, title: workItems[9].title, doc_type: "do_an", year: 2023, score: 0.28, aspects: { bai_toan: "thap", doi_tuong: "0.21", pham_vi: "thap", phuong_phap: "vua" }, url: "/cong-trinh/?id=10", explanation: "Chỉ gần ở cách xây dựng hệ thống; bài toán và đối tượng khác nhau.", ai_generated: true },
  ],
};

export const qualityFixture: QualityOut = {
  metrics: [
    { key: "pending_authors", label: "Liên kết tác giả chờ xác nhận", value: 6, queue_url: "/doi-soat/tac-gia" },
    { key: "duplicate_groups", label: "Nhóm nghi trùng", value: 2, queue_url: "/doi-soat/trung-lap" },
    { key: "missing_doi", label: "Công trình chưa có DOI", value: 8, queue_url: null },
  ],
  works_by_type: { bai_bao: 3, do_an: 4, luan_van: 2, luan_an: 1, hoc_lieu: 2 },
  works_with_link_pct: 83.3,
  last_sync: { source: "Kho dữ liệu ICTU", finished_at: "2026-09-10T01:04:12Z" },
};

export const aboutFixture: AboutOut = {
  source_url: "https://ictu.edu.vn/", repo_url: "https://github.com/maiychrus25/ICTU-CRIS", works: 1248,
  works_by_type: { bai_bao: 326, do_an: 704, luan_van: 98, luan_an: 24, hoc_lieu: 96 },
  last_sync: { id: 18, source: "Kho dữ liệu ICTU", scope: "Toàn bộ dữ liệu", status: "success", started_at: "2026-09-10T01:00:00Z", finished_at: "2026-09-10T01:04:12Z" },
  ai: { provider: "Hugging Face", model: "AITeamVN/Vietnamese_Embedding", dim: 768, repo: "https://huggingface.co/AITeamVN/Vietnamese_Embedding", licence: "Apache-2.0", size: "1.1 GB", runs: 12, embeddings: 1186, topics: 24, suggestions: 137 },
  limits: [
    "Gợi ý AI chỉ hỗ trợ sàng lọc; người dùng chịu trách nhiệm xác nhận hoặc bác bỏ.",
    "Đối chiếu đề tài dựa trên siêu dữ liệu và tóm tắt, không phải toàn văn.",
    "Dữ liệu phụ thuộc chất lượng và thời điểm đồng bộ của nguồn gốc.",
  ],
};

export const healthFixture: HealthOut = { status: "ok" };
