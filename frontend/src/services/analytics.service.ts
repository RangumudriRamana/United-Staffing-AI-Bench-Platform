import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";
import type {
  ExecutiveDashboardResponse,
  RecruiterDashboardResponse,
  VendorAnalyticsSummaryResponse,
} from "@/features/analytics/types";

class AnalyticsService {
  async getExecutiveDashboard(): Promise<ExecutiveDashboardResponse> {
    const response = await api.get(
      ENDPOINTS.ANALYTICS.EXECUTIVE_DASHBOARD
    );

    return response.data;
  }

  async getRecruiterDashboard(): Promise<RecruiterDashboardResponse> {
    const response = await api.get(
      ENDPOINTS.ANALYTICS.RECRUITER_DASHBOARD
    );

    return response.data;
  }

  async getVendorAnalytics(
    vendorPublicId: string
  ): Promise<VendorAnalyticsSummaryResponse> {
    const response = await api.get(
      `${ENDPOINTS.ANALYTICS.VENDOR_ANALYTICS}/${vendorPublicId}`
    );

    return response.data;
  }
}

export default new AnalyticsService();