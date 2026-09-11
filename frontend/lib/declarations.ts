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
    { to: "ChoKhoaDuyet", label: "Trình khoa duyệt", roles: ["faculty_officer", "rd_officer", "lecturer"] },
    { to: "ChoBoSung", label: "Yêu cầu bổ sung", roles: ["faculty_officer", "rd_officer"], reasonRequired: true },
    { to: "Rut", label: "Rút", roles: ["faculty_officer", "rd_officer", "lecturer"], reasonRequired: true, destructive: true },
  ],
  ChoBoSung: [
    { to: "Nhap", label: "Trả về nháp", roles: ["faculty_officer", "rd_officer"] },
    { to: "Rut", label: "Rút", roles: ["faculty_officer", "rd_officer", "lecturer"], reasonRequired: true, destructive: true },
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

export function getDeclarationActions(state: DeclarationState, me: MeOut | undefined, unitCode: string, periodState?: string, ownedByCurrentUser = false) {
  if (!me) return [];
  const roles = me.auth_required ? me.user?.roles ?? [] : ["rd_officer"];
  const ownershipScoped = roles.includes("lecturer") && !roles.some((role) => ["faculty_officer", "rd_officer"].includes(role));
  if (ownershipScoped && !ownedByCurrentUser) return [];
  const effectiveRoles = ownedByCurrentUser ? roles : roles.filter((role) => role !== "lecturer");
  if (!effectiveRoles.includes("rd_officer") && !(ownedByCurrentUser && effectiveRoles.includes("lecturer")) && me.user?.unit_code !== unitCode) return [];
  return (actions[state] ?? []).filter((action) =>
    action.roles.some((role) => effectiveRoles.includes(role))
    && (periodState === undefined || periodState !== "Huy")
    && (periodState === undefined || periodState === "DangMo" || !preCloseOnly.has(`${state}:${action.to}`)),
  );
}
