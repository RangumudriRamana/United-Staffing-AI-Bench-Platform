import { useQuery } from "@tanstack/react-query";
import consultantService from "@/services/consultant.service";

export interface MarketingHistoryRecord {
  public_id: string;
  status: string;
  effective_from: string;
  effective_until: string | null;
  changed_by: number;
  reason: string | null;
  notes: string | null;
}

export function useMarketingHistory(publicId: string | null) {
  return useQuery({
    queryKey: ["consultant-marketing-history", publicId],
    queryFn: async (): Promise<MarketingHistoryRecord[]> => {
      const response = await consultantService.getMarketingHistory(publicId!);
      return response;
    },
    enabled: Boolean(publicId),
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}