import { useQuery } from "@tanstack/react-query";

import analyticsService from "@/services/analytics.service";

export function useExecutiveDashboard() {
  return useQuery({
    queryKey: ["analytics", "executive"],
    queryFn: () => analyticsService.getExecutiveDashboard(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}

export function useRecruiterDashboard() {
  return useQuery({
    queryKey: ["analytics", "recruiter"],
    queryFn: () => analyticsService.getRecruiterDashboard(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}

export function useVendorAnalytics(vendorPublicId: string) {
  return useQuery({
    queryKey: ["analytics", "vendor", vendorPublicId],
    queryFn: () =>
      analyticsService.getVendorAnalytics(vendorPublicId),
    enabled: Boolean(vendorPublicId),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}