import { useQuery } from "@tanstack/react-query";
import { requirementsApi } from "../api/requirementsApi";

export const useRequirements = (params: { page: number; limit: number; search?: string }) => {
  return useQuery({
    queryKey: ["requirements", params],
    queryFn: () => requirementsApi.list(params),
    placeholderData: (previousData) => previousData,
  });
};