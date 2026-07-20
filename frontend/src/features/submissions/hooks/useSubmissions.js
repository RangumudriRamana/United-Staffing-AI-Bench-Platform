import { useQuery } from "@tanstack/react-query";
import { submissionsApi } from "../api/submissionsApi";
export const useSubmissions = (params) => {
    return useQuery({
        queryKey: ["submissions", params],
        queryFn: () => submissionsApi.list(params),
        placeholderData: (previousData) => previousData,
    });
};
