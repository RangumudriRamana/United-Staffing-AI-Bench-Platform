import { useMutation, useQueryClient } from "@tanstack/react-query";
import { consultantApi } from "../api/consultantApi";

export const useConsultantMutations = () => {
  const queryClient = useQueryClient();

  // Common invalidation logic
  const invalidateConsultants = () => {
    queryClient.invalidateQueries({ queryKey: ["consultants"] });
  };

  const createMutation = useMutation({
    mutationFn: consultantApi.create,
    onSuccess: () => {
      invalidateConsultants();
      // Add toast notification logic here
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: { id: string; payload: any }) => 
      consultantApi.update(data.id, data.payload),
    onSuccess: () => {
      invalidateConsultants();
    },
  });

  const archiveMutation = useMutation({
    mutationFn: (id: string) => consultantApi.delete(id), // or archive endpoint
    onSuccess: () => {
      invalidateConsultants();
    },
  });

  return {
    create: createMutation.mutate,
    update: updateMutation.mutate,
    archive: archiveMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isArchiving: archiveMutation.isPending,
  };
};