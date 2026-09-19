import { useQuery } from "@tanstack/react-query";
import consultantService from "@/services/consultant.service";

export function useMarketingActivities(consultantPublicId: string | null) {
  return useQuery({
    queryKey: ["marketing-activities", consultantPublicId],
    queryFn: () =>
      consultantService.getMarketingActivities(consultantPublicId!),
    enabled: Boolean(consultantPublicId),
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}