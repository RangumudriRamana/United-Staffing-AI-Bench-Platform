import { useQuery } from "@tanstack/react-query";

import vendorService from "@/services/vendor.service";

export function useClients(vendorPublicId?: string) {
  return useQuery({
    queryKey: ["clients", vendorPublicId],
    queryFn: () => vendorService.getClients(vendorPublicId as string),
    enabled: Boolean(vendorPublicId),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}