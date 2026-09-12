// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type {
  AboutOut, AuditList, AuthorQueueList, CompareOut, DeclarationDetail, DeclarationRow, DupGroupDetail, DupGroupList, HealthOut, MeOut,
  NotificationRow, PeriodReport, PeriodReportListItem, UnitOverview,
  CoauthorsOut, ExpertOut, MentorList, MyWorkList, PeriodOut, PeriodProgress, PersonProfile, PersonSearchRow,
  PublicTopicCheckOut, QualityAnomalyList, QualityOut, RecentOut, StatsOut, SyncRunDetail, SyncRunList, Topic,
  TopicDetail, TrendsOut, WorkDetail, WorkFacets, WorkList, WorkSummary, ScreenCohortSummary, ScreenList, MapOut,
} from "@/lib/types";

export const meFixture: MeOut = {
  user: { id: 1, email: "nguyen.minh.anh@ictu.edu.vn", display_name: "Nguyễn Minh Anh", roles: ["rd_officer"], unit_id: 1, unit_code: "CNTT", person_id: null },
  auth_required: true,
};

export const lecturerMeFixture: MeOut = {
  user: { id: 6, email: "giang.vien@ictu.edu.vn", display_name: "TS. Nguyễn Văn A", roles: ["lecturer"], unit_id: 1, unit_code: "CNTT", person_id: 1 },
  auth_required: true,
};

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

workItems.forEach((work, index) => {
  work.keywords = index % 2 ? ["trí tuệ nhân tạo", "dữ liệu"] : ["hệ thống thông tin", "ứng dụng web"];
  work.score = Number((0.93 - index * 0.045).toFixed(3));
});

export const worksFixture: WorkList = { items: workItems, page: { page: 1, per_page: 50, total: workItems.length } };

export const myWorksFixture: MyWorkList = {
  items: [
    { work_id: 2, title: workItems[1].title, doc_type: workItems[1].doc_type, doc_type_label: workItems[1].doc_type_label, year: workItems[1].year, doi: workItems[1].doi, link_state: "DaXacNhan", declared_in: [401] },
    { work_id: 3, title: workItems[2].title, doc_type: workItems[2].doc_type, doc_type_label: workItems[2].doc_type_label, year: workItems[2].year, doi: workItems[2].doi, link_state: "ChoXacNhan", declared_in: [] },
    { work_id: 4, title: workItems[3].title, doc_type: workItems[3].doc_type, doc_type_label: workItems[3].doc_type_label, year: workItems[3].year, doi: workItems[3].doi, link_state: "DaNoiTuDong", declared_in: [] },
  ],
  page: { page: 1, per_page: 50, total: 3 },
};

export const workDetailsFixture: Record<number, WorkDetail> = Object.fromEntries(workItems.map((work) => [work.id, {
  id: work.id,
  title: work.title,
  doc_type: work.doc_type,
  doc_type_label: work.doc_type_label,
  state: work.state,
  needs_review: work.needs_review,
  has_manual: false,
  pdf_url: work.id % 2 ? `https://repository.ictu.edu.vn/works/${work.id}.pdf` : null,
  source_url: `https://repository.ictu.edu.vn/works/${work.id}`,
  keywords: work.keywords,
  fields: [
    { field: "title", label: "Tiêu đề", value: work.title, raw: work.id === 1 ? "XAY DUNG WEBSITE QUAN LY THU VIEN TRUONG THPT LUONG NGOC QUYEN" : work.title, source: work.id === 1 ? "Chuẩn hoá từ kho đồ án ICTU" : "Đồng bộ kho dữ liệu ICTU" },
    { field: "doc_type", label: "Loại tài liệu", value: work.doc_type_label, raw: work.doc_type, source: "Ánh xạ danh mục chuẩn" },
    { field: "doi", label: "DOI", value: work.doi, raw: work.doi, source: work.doi ? "Crossref" : "Không có trong nguồn gốc" },
    { field: "journal", label: "Tạp chí", value: work.doc_type === "bai_bao" ? "Tạp chí Khoa học và Công nghệ" : null, raw: null, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "volume", label: "Tập/số", value: work.doc_type === "bai_bao" ? "12(3)" : null, raw: null, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "year_issue", label: "Năm", value: work.year?.toString() ?? null, raw: work.year?.toString() ?? null, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "abstract", label: "Tóm tắt", value: "Tóm tắt công trình được đồng bộ từ nguồn gốc.", raw: null, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "keywords_raw", label: "Từ khoá", value: "hệ thống thông tin; dữ liệu", raw: null, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "pub_type_raw", label: "Loại xuất bản (thô)", value: work.doc_type_label, raw: work.doc_type_label, source: "Đồng bộ kho dữ liệu ICTU" },
    { field: "cohort", label: "Khoá/đợt", value: work.doc_type === "do_an" ? "21" : null, raw: null, source: "Đồng bộ kho dữ liệu ICTU" },
  ],
  mentions: work.id === 1 ? [
    { mention_id: 101, role: "tac_gia", role_label: "Tác giả", position: 1, raw_name: "Nguyễn Minh Anh", is_placeholder: false, is_truncated: false, linked_person_id: null, linked_person_name: null, link_state: "ChoXacNhan", pending_count: 2 },
    { mention_id: 102, role: "huong_dan", role_label: "Giảng viên hướng dẫn", position: 2, raw_name: "TS. Nguyễn Văn A", is_placeholder: false, is_truncated: false, linked_person_id: 1, linked_person_name: "TS. Nguyễn Văn A", link_state: "DaXacNhan", pending_count: 0 },
  ] : [
    { mention_id: 100 + work.id, role: "tac_gia", role_label: "Tác giả", position: 1, raw_name: "TS. Nguyễn Văn A", is_placeholder: false, is_truncated: false, linked_person_id: 1, linked_person_name: "TS. Nguyễn Văn A", link_state: "DaNoiTuDong", pending_count: 0 },
  ],
}])) as Record<number, WorkDetail>;

export const topicsFixture: Topic[] = [
  { id: 1, label: "Trí tuệ nhân tạo", size: 38, keywords: ["học sâu", "nhận dạng", "thị giác máy tính", "mạng nơ-ron", "xử lý ảnh", "dự báo", "phân loại", "dữ liệu"], built_at: "2026-09-10T02:00:00Z" },
  { id: 2, label: "Hệ thống thông tin", size: 27, keywords: ["quản lý", "website", "cơ sở dữ liệu", "thông tin", "phần mềm", "dịch vụ", "quy trình", "người dùng"], built_at: "2026-09-10T02:00:00Z" },
  { id: 3, label: "An toàn thông tin", size: 19, keywords: ["bảo mật", "xâm nhập", "mã hoá", "mạng", "phát hiện", "tấn công", "dữ liệu", "an toàn"], built_at: "2026-09-10T02:00:00Z" },
  { id: 4, label: "Internet vạn vật", size: 16, keywords: ["IoT", "cảm biến", "thiết bị", "không dây", "giám sát", "điều khiển", "nhúng", "tự động"], built_at: "2026-09-10T02:00:00Z" },
];

export const topicDetailsFixture: Record<number, TopicDetail> = Object.fromEntries(topicsFixture.map((topic) => [topic.id, {
  id: topic.id,
  label: topic.label,
  size: topic.size,
  keywords: topic.keywords.map((keyword, index) => ({ keyword, weight: Number((1 - index * 0.09).toFixed(2)) })),
  works: topic.id === 1 ? workItems.filter((work) => [2, 3, 4, 9].includes(work.id)) : workItems.slice(0, Math.min(topic.size, 5)),
}])) as Record<number, TopicDetail>;

export const personFixture: PersonProfile = {
  id: 1, display_name: "TS. Nguyễn Văn A", degree: "Tiến sĩ", email: "nguyenvana@ictu.edu.vn",
  orcid: "0000-0002-1825-0097", by_type: { bai_bao: 8, do_an: 14, hoc_lieu: 2 },
  by_year: { "2022": 3, "2023": 5, "2024": 7, "2025": 9 },
  publications: workItems.slice(0, 6).map((work) => ({ work_id: work.id, title: work.title, doc_type: work.doc_type, year: work.year, doi: work.doi, link_state: "DaXacNhan", confidence: "cao" })),
  pending_count: 2, rank: "Phó giáo sư", scholar_url: "https://scholar.google.com/", citation_stats: null,
  last_sync: { id: 18, source: "Kho dữ liệu ICTU", scope: "Hồ sơ giảng viên", status: "success", started_at: "2026-09-10T01:00:00Z", finished_at: "2026-09-10T01:04:12Z" },
};

export const personsFixture: PersonSearchRow[] = [
  { id: 1, display_name: "TS. Nguyễn Văn A", degree: "Tiến sĩ", unit_code: "CNTT", kind: "giang_vien", works: 42 },
  { id: 2, display_name: "TS. Nguyễn Văn An", degree: "Tiến sĩ", unit_code: "KHMT", kind: "giang_vien", works: 31 },
  { id: 3, display_name: "ThS. Trần Thị Bình", degree: "Thạc sĩ", unit_code: "HTTT", kind: "giang_vien", works: 24 },
];

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

export const mentorFixture: MentorList = {
  page: { page: 1, per_page: 50, total: 2 },
  items: [
    {
      work_id: 1, title: workItems[0].title, cohort: "K21", mention_id: 1201, pending_link: null,
      candidates: [
        { person_id: 1, display_name: "TS. Nguyễn Văn A", degree: "Tiến sĩ", votes: 4, score: 3.72, evidence: [
          { work_id: 3, title: workItems[2].title, score: 0.94 },
          { work_id: 7, title: workItems[6].title, score: 0.91 },
        ] },
        { person_id: 3, display_name: "ThS. Trần Thị Bình", degree: "Thạc sĩ", votes: 2, score: 1.71, evidence: [
          { work_id: 10, title: workItems[9].title, score: 0.87 },
          { work_id: 12, title: workItems[11].title, score: 0.84 },
        ] },
      ],
    },
    {
      work_id: 7, title: workItems[6].title, cohort: "K21", mention_id: 1207, pending_link: null,
      candidates: [{ person_id: 2, display_name: "TS. Nguyễn Văn An", degree: "Tiến sĩ", votes: 3, score: 2.65, evidence: [
        { work_id: 1, title: workItems[0].title, score: 0.9 },
        { work_id: 10, title: workItems[9].title, score: 0.88 },
      ] }],
    },
  ],
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

export const screenCohortsFixture: ScreenCohortSummary[] = [
  { cohort: "21", screened: 529, flagged: 47 },
  { cohort: "20", screened: 486, flagged: 39 },
];

export const screenFixture: ScreenList = {
  page: { page: 1, per_page: 50, total: 2 }, cohorts: ["20", "21"],
  items: [
    {
      work_id: 3, title: "Phát triển hệ thống điểm danh sinh viên bằng nhận diện khuôn mặt", cohort: "21",
      max_score: 0.951, level: "cao",
      neighbours: [{ work_id: 2, title: "Ứng dụng AI xây dựng hệ thống điểm danh sinh viên dựa trên nhận diện khuôn mặt", cohort: "20", score: 0.951, aspects: { bai_toan: "cao", doi_tuong: "khong_du_du_lieu", pham_vi: "khong_du_du_lieu", phuong_phap: "khong_du_du_lieu" } }],
    },
    {
      work_id: 7, title: "Xây dựng ứng dụng quản lý ký túc xá trên nền tảng web", cohort: "21",
      max_score: 0.864, level: "vua",
      neighbours: [{ work_id: 1, title: workItems[0].title, cohort: "18", score: 0.864, aspects: { bai_toan: "vua", doi_tuong: "khong_du_du_lieu", pham_vi: "khong_du_du_lieu", phuong_phap: "khong_du_du_lieu" } }],
    },
  ],
};

export const qualityFixture: QualityOut = {
  metrics: [
    { key: "pending_authors", label: "Liên kết tác giả chờ xác nhận", value: 6, queue_url: "/doi-soat/tac-gia" },
    { key: "duplicate_groups", label: "Nhóm nghi trùng", value: 2, queue_url: "/doi-soat/trung-lap" },
    { key: "missing_doi", label: "Công trình chưa có DOI", value: 8, queue_url: null },
    { key: "anomalies_open", label: "Cảnh báo bất thường đang mở", value: 2, queue_url: "/chat-luong-du-lieu/canh-bao" },
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

export const statsFixture: StatsOut = {
  by_year_type: [
    { year: 2025, bai_bao: 86, do_an: 174, luan_van: 24, luan_an: 5, hoc_lieu: 18 },
    { year: 2024, bai_bao: 79, do_an: 162, luan_van: 21, luan_an: 4, hoc_lieu: 20 },
    { year: 2023, bai_bao: 71, do_an: 148, luan_van: 19, luan_an: 6, hoc_lieu: 17 },
    { year: 2022, bai_bao: 65, do_an: 136, luan_van: 18, luan_an: 3, hoc_lieu: 15 },
    { year: 2021, bai_bao: 58, do_an: 129, luan_van: 16, luan_an: 4, hoc_lieu: 13 },
  ],
  unknown_year: { bai_bao: 3, do_an: 12, luan_van: 2, luan_an: 0, hoc_lieu: 1 },
  by_unit: [
    { unit_id: 1, code: "CNTT", name: "Khoa Công nghệ thông tin", works: 426 },
    { unit_id: 2, code: "KHMT", name: "Khoa Khoa học máy tính", works: 318 },
    { unit_id: 3, code: "HTTT", name: "Khoa Hệ thống thông tin kinh tế", works: 247 },
  ],
  top_persons: [
    { person_id: 1, display_name: "TS. Nguyễn Văn A", unit_code: "CNTT", works: 42 },
    { person_id: 2, display_name: "PGS.TS. Trần Thị Bình", unit_code: "KHMT", works: 38 },
    { person_id: 3, display_name: "TS. Lê Văn Hoàng", unit_code: "HTTT", works: 35 },
  ],
  queues: { authors_pending: 36, dup_groups_open: 12 },
  coverage: { works_with_link_pct: 83.3, works_without_unit: 27 },
  last_sync: { id: 18, source: "Kho dữ liệu ICTU", scope: "Toàn bộ dữ liệu", status: "success", started_at: "2026-09-10T01:00:00Z", finished_at: "2026-09-10T01:04:12Z" },
};

export const auditFixture: AuditList = {
  page: { page: 1, per_page: 50, total: 5 },
  items: [
    { id: 501, at: "2026-09-11T08:22:00Z", actor_name: "Nguyễn Minh Anh", action: "link.confirm", action_label: "Xác nhận liên kết", entity: "author_link", entity_id: 201, before: { state: "ChoXacNhan" }, after: { state: "DaXacNhan", person_id: 1 } },
    { id: 502, at: "2026-09-11T07:45:00Z", actor_name: "Trần Thu Hà", action: "dup.keep", action_label: "Giữ riêng", entity: "duplicate_group", entity_id: 301, before: { state: "NghiTrung" }, after: { state: "GiuRieng", reason: "Đồ án nhóm" } },
    { id: 503, at: "2026-09-10T09:10:00Z", actor_name: "Phạm Quang Minh", action: "period.open", action_label: "Mở kỳ báo cáo", entity: "period", entity_id: 401, before: null, after: { state: "DangMo", code: "BC-2026" } },
    { id: 504, at: "2026-09-10T06:30:00Z", actor_name: null, action: "source_record.new_version", action_label: "Nguồn có phiên bản mới", entity: "source_record", entity_id: 88, before: { version: 1 }, after: { version: 2 } },
    { id: 505, at: "2026-09-09T04:20:00Z", actor_name: "Đỗ Thu Hà", action: "mention.orphaned", action_label: "Lượt tên mất nguồn", entity: "author_mention", entity_id: 102, before: { work_id: 1 }, after: null },
  ],
};

export const periodsFixture: PeriodOut[] = [
  { id: 401, code: "BC-2026", name: "Báo cáo công trình năm 2026", scope: { doc_types: ["bai_bao"] }, criteria: "Công trình công bố trong năm 2026", state: "DangMo", opens_at: "2026-09-01T00:00:00Z", due_at: "2026-09-30T16:59:59Z", created_at: "2026-08-28T02:00:00Z" },
  { id: 402, code: "BC-2025", name: "Báo cáo công trình năm 2025", scope: { doc_types: ["bai_bao", "hoc_lieu"] }, criteria: null, state: "DaDongNop", opens_at: "2025-09-01T00:00:00Z", due_at: "2025-09-30T16:59:59Z", created_at: "2025-08-27T02:00:00Z" },
  { id: 403, code: "KH-2027", name: "Kế hoạch báo cáo năm 2027", scope: { doc_types: ["bai_bao"] }, criteria: null, state: "ChuanBi", opens_at: null, due_at: "2027-01-31T16:59:59Z", created_at: "2026-09-08T02:00:00Z" },
];

export const periodProgressFixture: Record<number, PeriodProgress> = {
  401: { period_id: 401, state: "DangMo", due_at: "2026-09-30T16:59:59Z", days_remaining: 19, units: [
    { unit_id: 1, unit_code: "CNTT", unit_name: "Khoa Công nghệ thông tin", counts: { Nhap: 1, KhoaDaDuyet: 1, DaChot: 1 }, total: 3 },
    { unit_id: 2, unit_code: "KHMT", unit_name: "Khoa Khoa học máy tính", counts: { ChoBoSung: 1, ChoKhoaDuyet: 1, ChoPhongKiemTra: 1 }, total: 3 },
    { unit_id: 3, unit_code: "HTTT", unit_name: "Khoa Hệ thống thông tin kinh tế", counts: { DatYeuCau: 1, Rut: 1 }, total: 2 },
  ] },
  402: { period_id: 402, state: "DaDongNop", due_at: "2025-09-30T16:59:59Z", days_remaining: -345, units: [
    { unit_id: 1, unit_code: "CNTT", unit_name: "Khoa Công nghệ thông tin", counts: { DatYeuCau: 1, Nhap: 1 }, total: 2 },
  ] },
  403: { period_id: 403, state: "ChuanBi", due_at: "2027-01-31T16:59:59Z", days_remaining: 142, units: [] },
};

export const declarationsFixture: Record<number, DeclarationRow[]> = {
  401: [
    { id: 608, period_id: 401, work_id: 9, work_title: workItems[8].title, doc_type: "bai_bao", doc_type_label: "Bài báo", unit_id: 1, unit_code: "CNTT", state: "DaChot", note: null, evidence_count: 1, last_event_at: "2026-09-11T08:00:00Z", created_at: "2026-09-02T03:10:00Z", updated_at: "2026-09-11T08:00:00Z" },
    { id: 607, period_id: 401, work_id: 8, work_title: workItems[7].title, doc_type: "luan_an", doc_type_label: "Luận án", unit_id: 3, unit_code: "HTTT", state: "DatYeuCau", note: null, evidence_count: 1, last_event_at: "2026-09-11T07:30:00Z", created_at: "2026-09-02T03:10:00Z", updated_at: "2026-09-11T07:30:00Z" },
    { id: 606, period_id: 401, work_id: 7, work_title: workItems[6].title, doc_type: "do_an", doc_type_label: "Đồ án", unit_id: 2, unit_code: "KHMT", state: "ChoPhongKiemTra", note: null, evidence_count: 1, last_event_at: "2026-09-10T08:00:00Z", created_at: "2026-09-02T03:10:00Z", updated_at: "2026-09-10T08:00:00Z" },
    { id: 605, period_id: 401, work_id: 6, work_title: workItems[5].title, doc_type: "bai_bao", doc_type_label: "Bài báo", unit_id: 1, unit_code: "CNTT", state: "KhoaDaDuyet", note: null, evidence_count: 1, last_event_at: "2026-09-10T07:00:00Z", created_at: "2026-09-02T03:10:00Z", updated_at: "2026-09-10T07:00:00Z" },
    { id: 604, period_id: 401, work_id: 5, work_title: workItems[4].title, doc_type: "hoc_lieu", doc_type_label: "Học liệu", unit_id: 2, unit_code: "KHMT", state: "ChoKhoaDuyet", note: null, evidence_count: 1, last_event_at: "2026-09-09T10:00:00Z", created_at: "2026-09-02T03:10:00Z", updated_at: "2026-09-09T10:00:00Z" },
    { id: 603, period_id: 401, work_id: 4, work_title: workItems[3].title, doc_type: "luan_van", doc_type_label: "Luận văn", unit_id: 3, unit_code: "HTTT", state: "Rut", note: "Hồ sơ rút theo đề nghị của đơn vị.", evidence_count: 0, last_event_at: "2026-09-09T09:20:00Z", created_at: "2026-09-04T02:00:00Z", updated_at: "2026-09-09T09:20:00Z" },
    { id: 602, period_id: 401, work_id: 3, work_title: workItems[2].title, doc_type: "do_an", doc_type_label: "Đồ án", unit_id: 2, unit_code: "KHMT", state: "ChoBoSung", note: "Kê khai bổ sung theo đợt tháng 9.", evidence_count: 1, last_event_at: "2026-09-08T08:30:00Z", created_at: "2026-09-03T02:00:00Z", updated_at: "2026-09-08T08:30:00Z" },
    { id: 601, period_id: 401, work_id: 2, work_title: workItems[1].title, doc_type: "bai_bao", doc_type_label: "Bài báo", unit_id: 1, unit_code: "CNTT", state: "Nhap", note: null, evidence_count: 1, last_event_at: "2026-09-02T03:10:00Z", created_at: "2026-09-02T03:10:00Z", updated_at: "2026-09-02T03:10:00Z" },
  ],
  402: [
    { id: 610, period_id: 402, work_id: 11, work_title: workItems[10].title, doc_type: "hoc_lieu", doc_type_label: "Học liệu", unit_id: 1, unit_code: "CNTT", state: "Nhap", note: null, evidence_count: 0, last_event_at: "2025-09-20T03:10:00Z", created_at: "2025-09-20T03:10:00Z", updated_at: "2025-09-20T03:10:00Z" },
    { id: 609, period_id: 402, work_id: 10, work_title: workItems[9].title, doc_type: "do_an", doc_type_label: "Đồ án", unit_id: 1, unit_code: "CNTT", state: "DatYeuCau", note: null, evidence_count: 1, last_event_at: "2025-10-02T08:00:00Z", created_at: "2025-09-20T03:10:00Z", updated_at: "2025-10-02T08:00:00Z" },
  ],
  403: [],
};

export const myDeclarationsFixture: DeclarationRow[] = [declarationsFixture[401][7]];

export const declarationDetailsFixture: Record<number, DeclarationDetail> = Object.fromEntries(
  Object.values(declarationsFixture).flat().map((row) => [row.id, {
    id: row.id, period_id: row.period_id, work_id: row.work_id, work_title: row.work_title,
    doc_type: row.doc_type, doc_type_label: row.doc_type_label, unit_id: row.unit_id,
    unit_code: row.unit_code, state: row.state, note: row.note, created_at: row.created_at,
    updated_at: row.updated_at,
    events: row.id === 602 ? [
      { id: 701, from_state: null, to_state: "Nhap", actor_id: 1, reason: null, at: row.created_at },
      { id: 702, from_state: "Nhap", to_state: "ChoBoSung", actor_id: 1, reason: "Cần bổ sung đường dẫn công bố.", at: row.updated_at },
    ] : [{ id: 700 + row.id, from_state: null, to_state: row.state, actor_id: 1, reason: null, at: row.created_at }],
    evidence: row.evidence_count ? [{ id: 800 + row.id, kind: "link", url: "https://doi.org/10.15625/ictu.2025.102", file_name: null, note: "Đường dẫn DOI của công trình.", added_by: 1, added_at: row.created_at, size_bytes: null, sha256: null, content_type: null }] : [],
  } satisfies DeclarationDetail]),
) as Record<number, DeclarationDetail>;

export const syncRunsFixture: SyncRunList = {
  page: { page: 1, per_page: 20, total: 2 },
  items: [
    { id: 18, source: "Kho dữ liệu ICTU", scope: "Toàn bộ dữ liệu", status: "warning", started_at: "2026-09-10T01:00:00Z", finished_at: "2026-09-10T01:04:12Z", duration_s: 252, added: 47, changed: 12, vanished: 2, errors: [], warnings: ["2 bản ghi thiếu mã đơn vị."] },
    { id: 17, source: "Kho dữ liệu ICTU", scope: "Bài báo", status: "ok", started_at: "2026-09-03T01:00:00Z", finished_at: "2026-09-03T01:02:08Z", duration_s: 128, added: 8, changed: 5, vanished: 0, errors: [], warnings: [] },
  ],
};

export const syncRunDetailsFixture: Record<number, SyncRunDetail> = Object.fromEntries(syncRunsFixture.items.map((run) => [run.id, {
  ...run,
  expected_count: { bai_bao: 326, do_an: 704 },
  fetched_count: { bai_bao: 326, do_an: 702 },
  triggered_by: null,
  records: [
    { id: 901, source_key: "repository:cong-trinh:1", doc_type: "do_an", version: 3, fetched_at: run.finished_at },
    { id: 902, source_key: "repository:cong-trinh:2", doc_type: "bai_bao", version: 2, fetched_at: run.finished_at },
  ],
}])) as Record<number, SyncRunDetail>;

export const facetsFixture: WorkFacets = {
  pub_types: [{ value: "journal_intl", label: "Tạp chí quốc tế", n: 126 }, { value: "conference", label: "Hội thảo", n: 84 }],
  quartiles: ["Q1", "Q2", "Q3", "Q4"].map((value, index) => ({ value, label: value, n: 42 - index * 7 })),
  cohorts: ["21", "20", "19"].map((value, index) => ({ value, label: `Khoá ${value}`, n: 174 - index * 12 })),
  years: [2025, 2024, 2023].map((value, index) => ({ value: String(value), label: String(value), n: 307 - index * 28 })),
  units: statsFixture.by_unit.map((unit) => ({ value: String(unit.unit_id), label: `${unit.code} — ${unit.name}`, n: unit.works })),
};

export const citationsFixture = {
  apa: "Nguyễn, V. A. (2025). Xây dựng website quản lý thư viện trường THPT Lương Ngọc Quyến. Đồ án tốt nghiệp, ICTU.",
  ieee: "V. A. Nguyễn, “Xây dựng website quản lý thư viện trường THPT Lương Ngọc Quyến,” Đồ án tốt nghiệp, ICTU, 2025.",
  bibtex: "@thesis{nguyen2025thuvien,\n  author = {Nguyễn Văn A},\n  title = {Xây dựng website quản lý thư viện trường THPT Lương Ngọc Quyến},\n  school = {ICTU},\n  year = {2025}\n}",
};

export const expertsFixture: ExpertOut = {
  query_id: 701, provider: "sentence-transformers", fallback: false,
  note: "Gợi ý được tính trên tiêu đề và tóm tắt công trình, không phải toàn văn; người dùng quyết định.",
  results: personsFixture.map((person, index) => ({
    person_id: person.id, display_name: person.display_name, degree: person.degree, unit_code: person.unit_code,
    score: [3.84, 3.12, 2.46][index], works_matched: [7, 5, 4][index],
    evidence: [0, 1, 2].map((offset) => {
      const work = workItems[(index * 3 + offset) % workItems.length];
      return { work_id: work.id, title: work.title, doc_type: work.doc_type, year: work.year, score: Number((0.94 - index * 0.07 - offset * 0.06).toFixed(2)) };
    }),
  })),
};

export const publicTopicFixture: PublicTopicCheckOut = {
  similar: workItems.filter((work) => work.doc_type === "do_an").slice(0, 4).map((work, index) => ({
    work_id: work.id, title: work.title, doc_type: work.doc_type, cohort: String(21 - index), year: work.year,
    score: [0.81, 0.58, 0.39, 0.28][index], level: (["cao", "vua", "vua", "thap"] as const)[index],
  })),
  experts: expertsFixture.results.map((person) => ({ person_id: person.person_id, display_name: person.display_name, degree: person.degree, unit_code: person.unit_code, score: person.score })),
  note: "AI cục bộ đối chiếu trên tiêu đề và tóm tắt, không phải toàn văn. Kết quả chỉ để tham khảo.",
};

const mapCenters = [[-0.48, -0.35], [0.42, -0.28], [-0.25, 0.5], [0.52, 0.42]] as const;
export const mapFixture: MapOut = {
  points: Array.from({ length: 96 }, (_, index) => {
    const topicIndex = index % 4;
    const angle = index * 2.399;
    const radius = 0.04 + (index % 12) * 0.018;
    const work = workItems[index % workItems.length];
    return { id: work.id, x: mapCenters[topicIndex][0] + Math.cos(angle) * radius, y: mapCenters[topicIndex][1] + Math.sin(angle) * radius, topic_id: topicIndex + 1, unit_id: index % 3 + 1, year: work.year, doc_type: work.doc_type, title: work.title };
  }),
  topics: topicsFixture.map((topic, index) => ({ id: topic.id, label: topic.label, size: topic.size, cx: mapCenters[index][0], cy: mapCenters[index][1] })),
  built_at: "2026-09-12T02:00:00Z", method: "pca",
};

export const trendsFixture: TrendsOut = {
  keys: ["2021", "2022", "2023", "2024", "2025"],
  series: topicsFixture.concat({ id: 0, label: "Khác", size: 12, keywords: [], built_at: null }).map((topic, topicIndex) => ({
    topic_id: topic.id || null, label: topic.label,
    values: ["2021", "2022", "2023", "2024", "2025"].map((key, keyIndex) => ({ key, count: 8 + topicIndex * 4 + keyIndex * (topicIndex + 2), share: Number((0.08 + topicIndex * 0.025 + keyIndex * 0.008).toFixed(3)) })),
  })),
};

export const coauthorsFixture: CoauthorsOut = {
  nodes: [
    { person_id: 1, display_name: "TS. Nguyễn Văn A", unit_code: "CNTT", works: 42 },
    { person_id: 2, display_name: "TS. Nguyễn Văn An", unit_code: "KHMT", works: 31 },
    { person_id: 3, display_name: "ThS. Trần Thị Bình", unit_code: "HTTT", works: 24 },
    { person_id: 4, display_name: "TS. Lê Văn Hoàng", unit_code: "CNTT", works: 18 },
    { person_id: 5, display_name: "ThS. Phạm Minh Đức", unit_code: "KHMT", works: 14 },
  ],
  edges: [{ a: 1, b: 2, weight: 6 }, { a: 1, b: 4, weight: 4 }, { a: 2, b: 3, weight: 3 }, { a: 2, b: 5, weight: 2 }, { a: 3, b: 4, weight: 2 }],
};

export const recentFixture: RecentOut = {
  added: workItems.slice(0, 3).map((work, index) => ({ ...work, first_seen_at: `2026-09-1${index}T02:00:00Z` })),
  changed: workItems.slice(3, 5).map((work, index) => ({ ...work, version: index + 2 })),
  run: statsFixture.last_sync!,
};

export const anomaliesFixture: QualityAnomalyList = {
  items: [
    { id: 801, kind: "doi_invalid", kind_label: "DOI sai định dạng 10.xxxx/…", work_id: 2, title: workItems[1].title, person_id: null, display_name: null, detail: { doi: "10.1x/sai" }, severity: "cao", state: "open", created_at: "2026-09-11T19:55:20Z" },
    { id: 802, kind: "thesis_title_equals_article", kind_label: "Luận văn/đồ án trùng tiêu đề chuẩn hoá với một bài báo", work_id: 6, title: workItems[5].title, person_id: null, display_name: null, detail: { article_id: 123 }, severity: "vua", state: "open", created_at: "2026-09-11T19:55:20Z" },
    { id: 803, kind: "missing_abstract_article", kind_label: "Bài báo không có tóm tắt", work_id: 7, title: workItems[6].title, person_id: null, display_name: null, detail: {}, severity: "thap", state: "dismissed", created_at: "2026-09-10T19:55:20Z" },
  ],
  page: { page: 1, per_page: 50, total: 2 },
  summary: { scopus_no_doi: { open: 0 }, year_out_of_range: { open: 0 }, thesis_title_equals_article: { open: 1 }, orcid_duplicate: { open: 0 }, doi_invalid: { open: 1 }, missing_abstract_article: { open: 0 } },
};

export const notificationFixture: NotificationRow[] = [
  { id: 1001, kind: "declaration", title: "Hồ sơ đã được khoa duyệt", body: "Hồ sơ #606 đã chuyển sang chờ Phòng KHCN kiểm tra.", link: "/ke-khai/?id=606", created_at: new Date(Date.now() - 5 * 60_000).toISOString(), read_at: null },
  { id: 1002, kind: "period", title: "Kỳ báo cáo sắp hết hạn", body: "Kỳ Báo cáo công trình năm 2026 còn 19 ngày.", link: "/ky-bao-cao/chi-tiet/?id=401", created_at: new Date(Date.now() - 2 * 3_600_000).toISOString(), read_at: null },
  { id: 1003, kind: "author_link", title: "Công trình đã được nối vào hồ sơ", body: `“${workItems[1].title}” đã được nối vào hồ sơ giảng viên.`, link: "/cong-trinh/?id=2", created_at: new Date(Date.now() - 26 * 3_600_000).toISOString(), read_at: null },
  { id: 1004, kind: "declaration", title: "Hồ sơ cần bổ sung", body: "Hồ sơ #602 cần bổ sung đường dẫn công bố.", link: "/ke-khai/?id=602", created_at: new Date(Date.now() - 3 * 86_400_000).toISOString(), read_at: "2026-09-10T08:30:00Z" },
];

export const reportFixture: PeriodReport = {
  id: 901, period_id: 401, version: 1, generated_at: "2026-09-12T03:15:00Z", generated_by: 1,
  note: "Bản đối chiếu nội bộ trước khi trình lãnh đạo.",
  sha256: "6f2a9d31f40b92c58b2068b18a7cd405df72164d56b79f20e943bec47d5fe631",
  summary: {
    units: [
      { unit_id: 1, code: "CNTT", name: "Khoa Công nghệ thông tin", by_state: { Nhap: 1, KhoaDaDuyet: 1, DaChot: 1 }, declared: 3, accepted: 1 },
      { unit_id: 2, code: "KHMT", name: "Khoa Khoa học máy tính", by_state: { ChoBoSung: 1, ChoKhoaDuyet: 1, ChoPhongKiemTra: 1 }, declared: 3, accepted: 0 },
      { unit_id: 3, code: "HTTT", name: "Khoa Hệ thống thông tin kinh tế", by_state: { DatYeuCau: 1, Rut: 1 }, declared: 2, accepted: 1 },
    ],
    by_doc_type: { bai_bao: 3, do_an: 2, luan_van: 1, luan_an: 1, hoc_lieu: 1 },
    totals: { declared: 8, accepted: 2, by_state: { Nhap: 1, ChoBoSung: 1, ChoKhoaDuyet: 1, KhoaDaDuyet: 1, ChoPhongKiemTra: 1, DatYeuCau: 1, DaChot: 1, Rut: 1 } },
  },
  items: declarationsFixture[401].slice(0, 5).map((row) => {
    const work = workItems.find((item) => item.id === row.work_id)!;
    return {
      declaration_id: row.id, state: row.state, unit: { id: row.unit_id, code: row.unit_code, name: statsFixture.by_unit.find((item) => item.unit_id === row.unit_id)?.name ?? row.unit_code },
      work: { id: work.id, title: work.title, doc_type: work.doc_type, year: work.year, doi: work.doi, indexes: work.doc_type === "bai_bao" ? ["Scopus"] : [], quartile: work.doc_type === "bai_bao" ? "Q2" : null, journal: work.doc_type === "bai_bao" ? "Tạp chí Khoa học và Công nghệ" : null },
      authors: ["TS. Nguyễn Văn A"], evidence_count: row.evidence_count, events: [{ state: row.state, at: row.updated_at }],
    };
  }),
};

export const periodReportsFixture: Record<number, PeriodReportListItem[]> = {
  401: [{ id: reportFixture.id, version: reportFixture.version, generated_at: reportFixture.generated_at, generated_by_name: "Nguyễn Minh Anh", note: reportFixture.note, totals: reportFixture.summary.totals }],
  402: [],
  403: [],
};

export const unitOverviewFixture: Record<number, UnitOverview> = {
  1: {
    unit: { id: 1, code: "CNTT", name: "Khoa Công nghệ thông tin" }, works_total: 426, linked_works: 389,
    by_doc_type: { bai_bao: 118, do_an: 224, luan_van: 38, luan_an: 8, hoc_lieu: 38 },
    by_year: [
      { year: 2021, bai_bao: 18, do_an: 37, luan_van: 6, luan_an: 1, hoc_lieu: 7 },
      { year: 2022, bai_bao: 21, do_an: 41, luan_van: 7, luan_an: 2, hoc_lieu: 8 },
      { year: 2023, bai_bao: 23, do_an: 44, luan_van: 8, luan_an: 1, hoc_lieu: 7 },
      { year: 2024, bai_bao: 27, do_an: 49, luan_van: 8, luan_an: 2, hoc_lieu: 8 },
      { year: 2025, bai_bao: 29, do_an: 53, luan_van: 9, luan_an: 2, hoc_lieu: 8 },
    ],
    top_persons: [
      { person_id: 1, display_name: "TS. Nguyễn Văn A", works: 42 },
      { person_id: 2, display_name: "TS. Nguyễn Văn An", works: 31 },
      { person_id: 3, display_name: "ThS. Trần Thị Bình", works: 24 },
    ],
    pending_links: 12, declarations_by_state: { Nhap: 1, KhoaDaDuyet: 1, DaChot: 1 }, lecturers_without_works: 3,
    lecturers_without_works_items: [
      { person_id: 7, display_name: "ThS. Hoàng Thị Lan" },
      { person_id: 8, display_name: "TS. Vũ Đức Long" },
      { person_id: 9, display_name: "ThS. Nguyễn Thu Trang" },
    ],
  },
};

export const healthFixture: HealthOut = { status: "ok", db: "ok", model: "missing", last_sync_age_h: 31, version: "0.6.0" };
