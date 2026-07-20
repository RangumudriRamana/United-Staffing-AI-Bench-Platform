import { useQuery } from "@tanstack/react-query";
import { requirementsApi } from "../api/requirementsApi";
export const useRequirements = (params) => {
    return useQuery({
        queryKey: ["requirements", params],
        queryFn: () => requirementsApi.list(params),
        placeholderData: (previousData) => previousData,
    });
};
