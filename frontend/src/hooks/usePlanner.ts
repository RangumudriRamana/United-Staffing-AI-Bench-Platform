import { useQuery } from "@tanstack/react-query";
import plannerService from "@/services/planner.service";

export function usePlanner(plannerDate?: string) {
  return useQuery({
    queryKey: ["planner", "daily", plannerDate],
    queryFn: () => plannerService.getDailyPlanner(plannerDate),
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}