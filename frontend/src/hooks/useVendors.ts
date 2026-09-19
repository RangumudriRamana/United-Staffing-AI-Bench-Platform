import { useQuery } from "@tanstack/react-query";

import vendorService from "@/services/vendor.service";

export function useVendors() {
  return useQuery({
    queryKey: ["vendors"],
    queryFn: () => vendorService.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}