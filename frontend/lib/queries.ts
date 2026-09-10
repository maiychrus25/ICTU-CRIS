// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { AuditFilters, CompareIn, DecideAuthorsIn, DecideDupIn, PeriodOpenIn, ScreenFilters, WorkFilters } from "@/lib/types";

export const useWorks = (filters: WorkFilters) => useQuery({ queryKey: ["works", filters], queryFn: () => api.getWorks(filters) });
export const useWork = (id: number | null) => useQuery({ queryKey: ["work", id], queryFn: () => api.getWork(id!), enabled: id !== null });
export const usePerson = (id: number | null) => useQuery({ queryKey: ["person", id], queryFn: () => api.getPerson(id!), enabled: id !== null });
export const useTopics = () => useQuery({ queryKey: ["topics"], queryFn: api.getTopics });
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
export const useOpenPeriod = () => useMutation({ mutationFn: (input: PeriodOpenIn) => api.openPeriod(input) });
export const useClosePeriod = (id: number) => useMutation({ mutationFn: () => api.closePeriod(id) });
export const useCancelPeriod = (id: number) => useMutation({ mutationFn: () => api.cancelPeriod(id) });
export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: api.getHealth });
