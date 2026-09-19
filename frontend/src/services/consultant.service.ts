import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";

class ConsultantService {
  async getAll() {
    const response = await api.get(ENDPOINTS.CONSULTANTS);
    return response.data;
  }

  async getById(publicId: string) {
    const response = await api.get(
      `${ENDPOINTS.CONSULTANTS}/${publicId}`
    );

    return response.data;
  }

  async create(payload: unknown) {
    const response = await api.post(
      ENDPOINTS.CONSULTANTS,
      payload
    );

    return response.data;
  }

  async update(publicId: string, payload: unknown) {
    const response = await api.patch(
      `${ENDPOINTS.CONSULTANTS}/${publicId}`,
      payload
    );

    return response.data;
  }

  async transitionMarketingStatus(
    publicId: string,
    payload: {
      target_status: string;
      reason?: string | null;
      notes?: string | null;
    }
  ) {
    const response = await api.post(
      `${ENDPOINTS.CONSULTANTS}/${publicId}/marketing/transition`,
      payload
    );

    return response.data;
  }

  async getMarketingHistory(publicId: string) {
    const response = await api.get(
      `${ENDPOINTS.CONSULTANTS}/${publicId}/marketing/history`
    );

    return response.data;
  }

  async createMarketingActivity(payload: {
    consultant_public_id: string;
    vendor_public_id: string;
    vendor_contact_public_id?: string | null;
    client_public_id?: string | null;
    activity_type: string;
    channel: string;
    outcome: string;
    subject?: string | null;
    notes?: string | null;
    follow_up_required?: boolean;
    occurred_at?: string | null;
  }) {
    const response = await api.post(
      "/marketing/activities",
      payload
    );

    return response.data;
  }

  async getMarketingActivities(consultantPublicId: string) {
    const response = await api.get(
      `/marketing/activities/consultant/${consultantPublicId}`
    );

    return response.data;
  }

  async archive(publicId: string) {
    await api.delete(
      `${ENDPOINTS.CONSULTANTS}/${publicId}`
    );
  }
}

export default new ConsultantService();