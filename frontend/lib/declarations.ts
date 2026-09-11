// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import type { DeclarationState, DeclarationTransitionState, MeOut } from "@/lib/types";

export interface DeclarationAction {
  to: DeclarationTransitionState;
  label: string;
  roles: string[];
  reasonRequired?: boolean;
  destructive?: boolean;
}

const actions: Partial<Record<DeclarationState, DeclarationAction[]>> = {
  Nhap: [
    { to: "ChoKhoaDuyet", label: "Trình khoa duyệt", roles: ["faculty_officer", "rd_officer"] },
    { to: "ChoBoSung", label: "Yêu cầu bổ sung", roles: ["faculty_officer", "rd_officer"], reasonRequired: true },
    { to: "Rut", label: "Rút", roles: ["faculty_officer", "rd_officer"], reasonRequired: true, destructive: true },
  ],
  ChoBoSung: [
    { to: "Nhap", label: "Trả về nháp", roles: ["faculty_officer", "rd_officer"] },
    { to: "Rut", label: "Rút", roles: ["faculty_officer", "rd_officer"], reasonRequired: true, destructive: true },
  ],
  ChoKhoaDuyet: [
    { to: "KhoaDaDuyet", label: "Khoa duyệt", roles: ["faculty_head"] },
    { to: "Nhap", label: "Trả về", roles: ["faculty_head"], reasonRequired: true },
  ],
  KhoaDaDuyet: [
    { to: "ChoPhongKiemTra", label: "Gửi phòng kiểm tra", roles: ["faculty_head", "rd_officer"] },
  ],
  ChoPhongKiemTra: [
    { to: "DatYeuCau", label: "Đạt yêu cầu", roles: ["rd_officer"] },
    { to: "Nhap", label: "Trả về", roles: ["rd_officer"], reasonRequired: true },
  ],
};

const preCloseOnly = new Set(["Nhap:ChoBoSung", "ChoBoSung:Nhap", "Nhap:Rut", "ChoBoSung:Rut"]);

export function getDeclarationActions(state: DeclarationState, me: MeOut | undefined, unitCode: string, periodState?: string) {
  if (!me) return [];
  const roles = me.auth_required ? me.user?.roles ?? [] : ["rd_officer"];
  if (!roles.includes("rd_officer") && me.user?.unit_code !== unitCode) return [];
  return (actions[state] ?? []).filter((action) =>
    action.roles.some((role) => roles.includes(role))
    && (periodState === undefined || periodState !== "Huy")
    && (periodState === undefined || periodState === "DangMo" || !preCloseOnly.has(`${state}:${action.to}`)),
  );
}
