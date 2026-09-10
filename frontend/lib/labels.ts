// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export const docTypeLabels: Record<string, string> = {
  bai_bao: "Bài báo", do_an: "Đồ án", luan_van: "Luận văn", luan_an: "Luận án",
  hoc_lieu: "Học liệu", giang_vien: "Giảng viên", dang_ky_do_an: "Đăng ký đồ án",
};

export const stateLabels: Record<string, string> = {
  DaNoiTuDong: "Đã nối tự động", ChoXacNhan: "Chờ xác nhận", DaXacNhan: "Đã xác nhận",
  DaBacBo: "Đã bác bỏ", NghiTrung: "Nghi trùng", DaGop: "Đã gộp", GiuRieng: "Giữ riêng",
};

export const roleLabels: Record<string, string> = {
  tac_gia: "Tác giả", huong_dan: "Giảng viên hướng dẫn", phan_bien: "Giảng viên phản biện",
  chu_bien: "Chủ biên",
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
