import { useMutation, useQueryClient } from "@tanstack/react-query";

import consultantService from "@/services/consultant.service";

export function useCreateConsultant() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: consultantService.create,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["consultants"],
      });
    },
  });
}