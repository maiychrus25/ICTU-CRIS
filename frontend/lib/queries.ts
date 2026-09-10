// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { CompareIn, DecideAuthorsIn, DecideDupIn, WorkFilters } from "@/lib/types";

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
export const useQuality = () => useQuery({ queryKey: ["quality"], queryFn: api.getQuality });
export const useAbout = () => useQuery({ queryKey: ["about"], queryFn: api.getAbout });
export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: api.getHealth });
