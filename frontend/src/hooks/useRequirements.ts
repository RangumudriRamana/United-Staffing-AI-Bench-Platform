import { useQuery } from "@tanstack/react-query";

import requirementService from "@/services/requirement.service";

import type { RequirementSearchCriteria } from "@/features/requirements/types";

export function useRequirements(
  params?: RequirementSearchCriteria
) {
  return useQuery({
    queryKey: ["requirements", params],
    queryFn: () => requirementService.getAll(params),

    // Keep the previous results visible while a new search request runs.
    placeholderData: (previousData) => previousData,

    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}