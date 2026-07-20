import { useQuery } from "@tanstack/react-query";
import { consultantApi } from "../api/consultantApi";

export const useConsultants = (params: { page: number; limit: number; search?: string }) => {
  return useQuery({
    queryKey: ["consultants", params],
    queryFn: () => consultantApi.list(params),
    placeholderData: (previousData) => previousData,
  });
};