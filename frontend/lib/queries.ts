// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type {
  AuditFilters, CompareIn, DeclarationCreateIn, DeclarationEvidenceIn, DeclarationStateIn,
  DecideAuthorsIn, DecideDupIn, DismissAnomalyIn, ExpertIn, FieldEditIn, LoginIn, MapColor,
  MentorFilters, MyDeclarationCreateIn, PeriodOpenIn, PublicTopicCheckIn, QualityAnomalyFilters,
  ScreenFilters, WorkFilters,
} from "@/lib/types";

export const useMe = () => useQuery({ queryKey: ["me"], queryFn: api.getMe, staleTime: 60_000 });
export const useLogin = () => useMutation({ mutationFn: (input: LoginIn) => api.login(input) });
export const useLogout = () => useMutation({ mutationFn: api.logout });
export function useOfficerAccess() {
  const me = useMe();
  return me.data ? !me.data.auth_required || Boolean(me.data.user?.roles.includes("rd_officer")) : false;
}

export const useWorks = (filters: WorkFilters, enabled = true) => useQuery({ queryKey: ["works", filters], queryFn: () => api.getWorks(filters), enabled });
export const useWorkFacets = (enabled = true) => useQuery({ queryKey: ["work-facets"], queryFn: api.getWorkFacets, enabled });
export const useWork = (id: number | null) => useQuery({ queryKey: ["work", id], queryFn: () => api.getWork(id!), enabled: id !== null });
export const useCitation = (id: number, style: "apa" | "ieee" | "bibtex", enabled = true) => useQuery({ queryKey: ["citation", id, style], queryFn: () => api.getCitation(id, style), enabled });
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
export const useExperts = (id: number | null) => useQuery({ queryKey: ["experts", id], queryFn: () => api.getExperts(id!), enabled: id !== null });
export const useFindExperts = () => useMutation({ mutationFn: (input: ExpertIn) => api.findExperts(input) });
export const useCheckPublicTopic = () => useMutation({ mutationFn: (input: PublicTopicCheckIn) => api.checkPublicTopic(input) });
export const useKnowledgeMap = (color: MapColor) => useQuery({ queryKey: ["knowledge-map", color], queryFn: () => api.getMap(color) });
export const useTrends = (by: "cohort" | "year") => useQuery({ queryKey: ["trends", by], queryFn: () => api.getTrends(by) });
export const useCoauthors = () => useQuery({ queryKey: ["coauthors"], queryFn: () => api.getCoauthors() });
export const useScreenCohorts = () => useQuery({ queryKey: ["screen-cohorts"], queryFn: api.getScreenCohorts });
export const useScreen = (filters: ScreenFilters, enabled = true) => useQuery({ queryKey: ["screen", filters], queryFn: () => api.getScreen(filters), enabled });
export const useMentors = (filters: MentorFilters, enabled = true) => useQuery({ queryKey: ["mentors", filters], queryFn: () => api.getMentors(filters), enabled });
export const useAcceptMentor = () => useMutation({ mutationFn: ({ workId, personId }: { workId: number; personId: number }) => api.acceptMentor(workId, personId) });
export const useQuality = () => useQuery({ queryKey: ["quality"], queryFn: api.getQuality });
export const useQualityAnomalies = (filters: QualityAnomalyFilters) => useQuery({ queryKey: ["quality-anomalies", filters], queryFn: () => api.getQualityAnomalies(filters) });
export const useDismissQualityAnomaly = () => useMutation({ mutationFn: ({ id, input }: { id: number; input: DismissAnomalyIn }) => api.dismissQualityAnomaly(id, input) });
export const useRecent = () => useQuery({ queryKey: ["recent"], queryFn: () => api.getRecent() });
export const usePersonCv = (id: number | null) => useQuery({ queryKey: ["person-cv", id], queryFn: () => api.getPersonCv(id!), enabled: id !== null });
export const useFeed = () => useQuery({ queryKey: ["feed"], queryFn: api.getFeed });
export const useAbout = () => useQuery({ queryKey: ["about"], queryFn: api.getAbout });
export const useStats = () => useQuery({ queryKey: ["stats", 5], queryFn: () => api.getStats(5) });
export const useAudit = (filters: AuditFilters) => useQuery({ queryKey: ["audit", filters], queryFn: () => api.getAudit(filters) });
export const usePeriods = () => useQuery({ queryKey: ["periods"], queryFn: api.getPeriods });
export const useMyWorks = (page: number) => useQuery({ queryKey: ["my-works", page], queryFn: () => api.getMyWorks(page) });
export const useMyDeclarations = () => useQuery({ queryKey: ["my-declarations"], queryFn: api.getMyDeclarations });
export const useAddMyDeclaration = () => useMutation({ mutationFn: (input: MyDeclarationCreateIn) => api.addMyDeclaration(input) });
export const usePeriodProgress = (id: number | null) => useQuery({ queryKey: ["period-progress", id], queryFn: () => api.getPeriodProgress(id!), enabled: id !== null });
export const useDeclarations = (periodId: number | null, unitId?: number) => useQuery({ queryKey: ["declarations", periodId, unitId], queryFn: () => api.getDeclarations(periodId!, unitId), enabled: periodId !== null });
export const useAddDeclaration = (periodId: number) => useMutation({ mutationFn: (input: DeclarationCreateIn) => api.addDeclaration(periodId, input) });
export const useDeclaration = (id: number | null) => useQuery({ queryKey: ["declaration", id], queryFn: () => api.getDeclaration(id!), enabled: id !== null });
export const useSetDeclarationState = () => useMutation({ mutationFn: ({ id, input }: { id: number; input: DeclarationStateIn }) => api.setDeclarationState(id, input) });
export const useAddDeclarationEvidence = () => useMutation({ mutationFn: ({ id, input }: { id: number; input: DeclarationEvidenceIn }) => api.addDeclarationEvidence(id, input) });
export const useUploadDeclarationEvidence = () => useMutation({ mutationFn: ({ id, body }: { id: number; body: FormData }) => api.uploadDeclarationEvidence(id, body) });
export const useOpenPeriod = () => useMutation({ mutationFn: (input: PeriodOpenIn) => api.openPeriod(input) });
export const useClosePeriod = (id: number) => useMutation({ mutationFn: () => api.closePeriod(id) });
export const useCancelPeriod = (id: number) => useMutation({ mutationFn: () => api.cancelPeriod(id) });
export const useFinalizePeriod = (id: number) => useMutation({ mutationFn: () => api.finalizePeriod(id) });
export const useSyncRuns = (page: number) => useQuery({ queryKey: ["sync-runs", page], queryFn: () => api.getSyncRuns(page) });
export const useSyncRun = (id: number | null) => useQuery({ queryKey: ["sync-run", id], queryFn: () => api.getSyncRun(id!), enabled: id !== null });
export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: api.getHealth });
