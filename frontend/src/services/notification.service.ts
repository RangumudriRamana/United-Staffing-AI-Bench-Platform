import api from "@/api/axios";
import type { Notification } from "@/features/notifications/types";

class NotificationService {
  async getUnread(): Promise<Notification[]> {
    const response = await api.get("/notifications/unread");
    return response.data;
  }

  async markAsRead(publicId: string): Promise<Notification> {
    const response = await api.post(
      `/notifications/${publicId}/read`
    );

    return response.data;
  }
}

export default new NotificationService();