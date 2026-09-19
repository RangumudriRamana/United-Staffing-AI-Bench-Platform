import { useMutation, useQueryClient } from "@tanstack/react-query";

import consultantService from "@/services/consultant.service";

interface MarketingTransitionPayload {
  target_status: string;
  reason?: string | null;
  notes?: string | null;
}

export function useMarketingTransition() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      publicId,
      payload,
    }: {
      publicId: string;
      payload: MarketingTransitionPayload;
    }) =>
      consultantService.transitionMarketingStatus(
        publicId,
        payload
      ),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["consultants"],
      });
    },
  });
}