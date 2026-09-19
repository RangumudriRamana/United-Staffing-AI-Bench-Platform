import { useMutation, useQueryClient } from "@tanstack/react-query";
import taskService from "@/services/task.service";

export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (publicId: string) =>
      taskService.complete(publicId),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["tasks", "my"],
      });
    },
  });
}