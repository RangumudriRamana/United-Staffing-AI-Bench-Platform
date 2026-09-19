import api from "@/api/axios";
import type { PlannerResponse } from "@/features/planner/types";

class PlannerService {
  async getDailyPlanner(
    plannerDate?: string
  ): Promise<PlannerResponse> {
    const response = await api.get("/planner/daily", {
      params: plannerDate
        ? { planner_date: plannerDate }
        : undefined,
    });

    return response.data;
  }
}

export default new PlannerService();