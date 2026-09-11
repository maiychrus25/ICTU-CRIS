// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export const docTypeLabels: Record<string, string> = {
  bai_bao: "Bài báo", do_an: "Đồ án", luan_van: "Luận văn", luan_an: "Luận án",
  hoc_lieu: "Học liệu", giang_vien: "Giảng viên", dang_ky_do_an: "Đăng ký đồ án",
};

export const docTypeColors: Record<string, string> = {
  bai_bao: "#2563eb", do_an: "#0891b2", luan_van: "#7c3aed", luan_an: "#c2410c", hoc_lieu: "#64748b",
};

export const stateLabels: Record<string, string> = {
  DaNoiTuDong: "Đã nối tự động", ChoXacNhan: "Chờ xác nhận", DaXacNhan: "Đã xác nhận",
  DaBacBo: "Đã bác bỏ", NghiTrung: "Nghi trùng", DaGop: "Đã gộp", GiuRieng: "Giữ riêng",
  BoQua: "Đã bỏ qua", Tho: "Dữ liệu thô", DaChuanHoa: "Đã chuẩn hoá",
  ChuanBi: "Chuẩn bị", DangMo: "Đang mở", DaDongNop: "Đã đóng nộp", Huy: "Đã huỷ",
  Nhap: "Nháp", ChoBoSung: "Chờ bổ sung", Rut: "Đã rút",
  active: "Đang hoạt động", vanished: "Đã biến mất",
  running: "Đang chạy", ok: "Thành công", success: "Thành công", warning: "Có cảnh báo", failed: "Thất bại",
};

export const entityLabels: Record<string, string> = {
  author_link: "Liên kết tác giả", duplicate_group: "Nhóm nghi trùng", period: "Kỳ báo cáo", declaration: "Hồ sơ kê khai",
  source_record: "Bản ghi nguồn", author_mention: "Lượt tên",
};

export const roleLabels: Record<string, string> = {
  author: "Tác giả", mentor: "Người hướng dẫn", student: "Sinh viên thực hiện",
  tac_gia: "Tác giả", huong_dan: "Giảng viên hướng dẫn", phan_bien: "Giảng viên phản biện",
  chu_bien: "Chủ biên",
};

export const userRoleLabels: Record<string, string> = {
  rd_officer: "Chuyên viên KHCN", lecturer: "Giảng viên", school_leader: "Lãnh đạo",
  admin: "Quản trị", faculty_officer: "Chuyên viên khoa",
};

export const officerRoleRequired = "Cần vai trò Chuyên viên KHCN";

export const confidenceLabels: Record<string, string> = {
  ten_day_du_duy_nhat: "Tên đầy đủ, một ứng viên",
  ten_day_du_nhieu_ung_vien: "Tên đầy đủ, nhiều ứng viên",
  ten_mot_phan: "Khớp một phần tên",
  orcid: "Khớp ORCID",
  cao: "Cao", vua: "Vừa", thap: "Thấp",
};

export const setKindLabels: Record<string, string> = {
  sync: "Đồng bộ", normalize: "Chuẩn hoá", merge: "Gộp bản ghi", manual: "Chỉnh tay",
};

export const venueKindLabels: Record<string, string> = {
  conference_intl: "Hội thảo quốc tế", conference_natl: "Hội thảo trong nước",
  journal_domestic: "Tạp chí trong nước", journal_intl: "Tạp chí quốc tế",
};

export const sourceLabels: Record<string, string> = {
  repository: "kho dữ liệu ICTU", excel_faculty: "bảng tính khoa",
  sheet_registration: "phiếu đăng ký", manual: "nhập tay",
};

export const syncScopeLabels: Record<string, string> = {
  "bai-bao": "Bài báo", "do-an": "Đồ án", "luan-van": "Luận văn", "luan-an": "Luận án",
  "hoc-lieu-so": "Học liệu số", "giang-vien": "Giảng viên", all: "Toàn bộ dữ liệu",
};

export const aspectLabels: Record<string, string> = {
  bai_toan: "Bài toán", doi_tuong: "Đối tượng", pham_vi: "Phạm vi", phuong_phap: "Phương pháp",
};

export type AspectLevel = "cao" | "vua" | "thap";

export function getAspectLevel(value: string): AspectLevel {
  const numeric = Number(value);
  if (value.trim() !== "" && Number.isFinite(numeric)) return numeric >= 0.55 ? "cao" : numeric >= 0.35 ? "vua" : "thap";
  const normalized = value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  return normalized === "cao" ? "cao" : normalized === "vua" ? "vua" : "thap";
}

export const aspectLevelLabels: Record<AspectLevel, string> = { cao: "Cao", vua: "Vừa", thap: "Thấp" };

export function getFieldValueLabel(field: string, value: string) {
  const labels = field === "doc_type" || field === "doc_types" ? docTypeLabels
    : field === "state" || field === "link_state" || field === "status" ? stateLabels
    : field === "role" ? roleLabels
    : field === "confidence" ? confidenceLabels
    : field === "set_kind" ? setKindLabels
    : field === "venue_kind" ? venueKindLabels
    : field === "level" ? aspectLevelLabels as Record<string, string>
    : field === "source" ? sourceLabels
    : undefined;
  return labels?.[value] ?? value;
}

export function labelDataCodes(value: unknown, field = ""): unknown {
  if (Array.isArray(value)) return value.map((item) => labelDataCodes(item, field));
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, labelDataCodes(item, key)]));
  }
  return typeof value === "string" ? getFieldValueLabel(field, value) : value;
}

export function labelSourceText(value: string) {
  return value.replace(/\b(repository|excel_faculty|sheet_registration|manual)\b/g, (code) => sourceLabels[code] ?? code);
}
