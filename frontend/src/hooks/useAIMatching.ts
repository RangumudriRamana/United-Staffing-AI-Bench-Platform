import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import aiService from "@/services/ai.service";
import type { BatchMatchRequest } from "@/features/ai/types";

export function useAIMatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: BatchMatchRequest) =>
      aiService.match(request),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["ai-match-history"],
      });
    },
  });
}

export function useAIBatchMatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: BatchMatchRequest) =>
      aiService.batchMatch(request),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["ai-match-history"],
      });
    },
  });
}

export function useAIMatchHistory() {
  return useQuery({
    queryKey: ["ai-match-history"],
    queryFn: () => aiService.getHistory(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}