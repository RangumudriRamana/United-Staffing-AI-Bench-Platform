import { useQuery } from "@tanstack/react-query";
import taskService from "@/services/task.service";

export function useTasks() {
  return useQuery({
    queryKey: ["tasks", "my"],
    queryFn: () => taskService.getMyTasks(),
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}