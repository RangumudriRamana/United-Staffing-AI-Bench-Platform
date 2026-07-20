import { useMutation, useQueryClient } from "@tanstack/react-query";
import { submissionsApi } from "../api/submissionsApi";
export const useSubmissionMutations = () => {
    const queryClient = useQueryClient();
    const createMutation = useMutation({
        mutationFn: (data) => submissionsApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["submissions"] });
        },
    });
    const updateMutation = useMutation({
        mutationFn: ({ id, payload }) => submissionsApi.update(id, payload),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["submissions"] });
        },
    });
    const archiveMutation = useMutation({
        mutationFn: (id) => submissionsApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["submissions"] });
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
