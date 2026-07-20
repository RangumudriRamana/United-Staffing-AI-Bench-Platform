import { useMutation, useQueryClient } from "@tanstack/react-query";
import { requirementsApi } from "../api/requirementsApi";
export const useRequirementMutations = () => {
    const queryClient = useQueryClient();
    const createMutation = useMutation({
        mutationFn: (data) => requirementsApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["requirements"] });
        },
    });
    const updateMutation = useMutation({
        mutationFn: ({ id, payload }) => requirementsApi.update(id, payload),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["requirements"] });
        },
    });
    const archiveMutation = useMutation({
        mutationFn: (id) => requirementsApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["requirements"] });
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
