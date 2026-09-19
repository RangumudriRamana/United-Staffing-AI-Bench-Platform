import { useQuery } from "@tanstack/react-query";
import notificationService from "@/services/notification.service";

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: () => notificationService.getUnread(),
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });
}