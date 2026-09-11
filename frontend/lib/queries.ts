// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type {
  AuditFilters, CompareIn, DeclarationCreateIn, DeclarationEvidenceIn, DeclarationStateIn,
  DecideAuthorsIn, DecideDupIn, FieldEditIn, LoginIn, PeriodOpenIn, ScreenFilters, WorkFilters,
} from "@/lib/types";

export const useMe = () => useQuery({ queryKey: ["me"], queryFn: api.getMe, staleTime: 60_000 });
export const useLogin = () => useMutation({ mutationFn: (input: LoginIn) => api.login(input) });
export const useLogout = () => useMutation({ mutationFn: api.logout });
export function useOfficerAccess() {
  const me = useMe();
  return me.data ? !me.data.auth_required || Boolean(me.data.user?.roles.includes("rd_officer")) : false;
}

export const useWorks = (filters: WorkFilters, enabled = true) => useQuery({ queryKey: ["works", filters], queryFn: () => api.getWorks(filters), enabled });
export const useWork = (id: number | null) => useQuery({ queryKey: ["work", id], queryFn: () => api.getWork(id!), enabled: id !== null });
export const useEditWorkField = (id: number) => useMutation({ mutationFn: (input: FieldEditIn) => api.editWorkField(id, input) });
export const usePerson = (id: number | null) => useQuery({ queryKey: ["person", id], queryFn: () => api.getPerson(id!), enabled: id !== null });
export const usePersonSearch = (q: string) => useQuery({ queryKey: ["person-search", q], queryFn: () => api.searchPersons(q), enabled: q.length > 0 });
export const useTopics = () => useQuery({ queryKey: ["topics"], queryFn: api.getTopics });
export const useTopic = (id: number | null) => useQuery({ queryKey: ["topic", id], queryFn: () => api.getTopic(id!), enabled: id !== null });
export const useAuthorQueue = (state: string, q: string, page: number) => useQuery({ queryKey: ["author-queue", state, q, page], queryFn: () => api.getAuthorQueue(state, q, page) });
export const useDecideAuthors = () => useMutation({ mutationFn: (input: DecideAuthorsIn) => api.decideAuthors(input) });
export const useDuplicateGroups = (state: string, page: number) => useQuery({ queryKey: ["duplicate-groups", state, page], queryFn: () => api.getDuplicateGroups(state, page) });
export const useDuplicateGroup = (id: number | null) => useQuery({ queryKey: ["duplicate-group", id], queryFn: () => api.getDuplicateGroup(id!), enabled: id !== null });
export const useDecideDuplicate = (id: number) => useMutation({ mutationFn: (input: DecideDupIn) => api.decideDuplicate(id, input) });
export const useComparison = (id: number | null) => useQuery({ queryKey: ["comparison", id], queryFn: () => api.getComparison(id!), enabled: id !== null });
export const useCreateComparison = () => useMutation({ mutationFn: (input: CompareIn) => api.compare(input) });
export const useScreenCohorts = () => useQuery({ queryKey: ["screen-cohorts"], queryFn: api.getScreenCohorts });
export const useScreen = (filters: ScreenFilters, enabled = true) => useQuery({ queryKey: ["screen", filters], queryFn: () => api.getScreen(filters), enabled });
export const useQuality = () => useQuery({ queryKey: ["quality"], queryFn: api.getQuality });
export const useAbout = () => useQuery({ queryKey: ["about"], queryFn: api.getAbout });
export const useStats = () => useQuery({ queryKey: ["stats", 5], queryFn: () => api.getStats(5) });
export const useAudit = (filters: AuditFilters) => useQuery({ queryKey: ["audit", filters], queryFn: () => api.getAudit(filters) });
export const usePeriods = () => useQuery({ queryKey: ["periods"], queryFn: api.getPeriods });
export const usePeriodProgress = (id: number | null) => useQuery({ queryKey: ["period-progress", id], queryFn: () => api.getPeriodProgress(id!), enabled: id !== null });
export const useDeclarations = (periodId: number | null, unitId?: number) => useQuery({ queryKey: ["declarations", periodId, unitId], queryFn: () => api.getDeclarations(periodId!, unitId), enabled: periodId !== null });
export const useAddDeclaration = (periodId: number) => useMutation({ mutationFn: (input: DeclarationCreateIn) => api.addDeclaration(periodId, input) });
export const useDeclaration = (id: number | null) => useQuery({ queryKey: ["declaration", id], queryFn: () => api.getDeclaration(id!), enabled: id !== null });
export const useSetDeclarationState = () => useMutation({ mutationFn: ({ id, input }: { id: number; input: DeclarationStateIn }) => api.setDeclarationState(id, input) });
export const useAddDeclarationEvidence = () => useMutation({ mutationFn: ({ id, input }: { id: number; input: DeclarationEvidenceIn }) => api.addDeclarationEvidence(id, input) });
export const useOpenPeriod = () => useMutation({ mutationFn: (input: PeriodOpenIn) => api.openPeriod(input) });
export const useClosePeriod = (id: number) => useMutation({ mutationFn: () => api.closePeriod(id) });
export const useCancelPeriod = (id: number) => useMutation({ mutationFn: () => api.cancelPeriod(id) });
export const useFinalizePeriod = (id: number) => useMutation({ mutationFn: () => api.finalizePeriod(id) });
export const useSyncRuns = (page: number) => useQuery({ queryKey: ["sync-runs", page], queryFn: () => api.getSyncRuns(page) });
export const useSyncRun = (id: number | null) => useQuery({ queryKey: ["sync-run", id], queryFn: () => api.getSyncRun(id!), enabled: id !== null });
export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: api.getHealth });
