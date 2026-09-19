import { useQuery } from "@tanstack/react-query";
import consultantService from "@/services/consultant.service";

export function useConsultants() {
  return useQuery({
    queryKey: ["consultants"],
    queryFn: () => consultantService.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}