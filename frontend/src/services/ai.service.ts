import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";
import type {
  BatchMatchRequest,
  BatchMatchResponse,
  MatchHistoryResponse,
} from "@/features/ai/types";

class AIService {
  async match(request: BatchMatchRequest): Promise<BatchMatchResponse> {
    const response = await api.post(ENDPOINTS.AI.MATCH, request);
    return response.data;
  }

  async getHistory(): Promise<MatchHistoryResponse> {
    const response = await api.get(ENDPOINTS.AI.HISTORY);
    return response.data;
  }

  async batchMatch(
    request: BatchMatchRequest,
  ): Promise<BatchMatchResponse> {
    const response = await api.post(ENDPOINTS.AI.BATCH, request);
    return response.data;
  }
}

export default new AIService();