import { useQuery } from "@tanstack/react-query";
import { submissionsApi } from "../api/submissionsApi";

export const useSubmissions = (params: { page: number; limit: number; search?: string }) => {
  return useQuery({
    queryKey: ["submissions", params],
    queryFn: () => submissionsApi.list(params),
    placeholderData: (previousData) => previousData,
  });
};