import { useQuery } from "@tanstack/react-query";

import submissionService from "@/services/submission.service";

import type {
  SubmissionDetail,
  SubmissionSearchFilters,
} from "@/features/submissions/types";

export function useSubmissions(
  params?: SubmissionSearchFilters
) {
  return useQuery({
    queryKey: ["submissions", params],
    queryFn: () => submissionService.getAll(params),

    placeholderData: (previousData) => previousData,

    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}


export function useSubmission(
  publicId: string | undefined
) {
  return useQuery<SubmissionDetail>({
    queryKey: ["submission", publicId],
    queryFn: () => submissionService.getById(publicId as string),

    enabled: Boolean(publicId),

    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}