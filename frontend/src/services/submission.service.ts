import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";

import type {
  CreateSubmissionRequest,
  InterviewCreateRequest,
  Interview,
  OfferCreateRequest,
  Offer,
  PlacementCreateRequest,
  Placement,
  Submission,
  SubmissionDetail,
  SubmissionSearchFilters,
  SubmissionTransitionRequest,
} from "@/features/submissions/types";

class SubmissionService {
  async getAll(
  params?: SubmissionSearchFilters
): Promise<Submission[]> {
    const response = await api.get(
      ENDPOINTS.SUBMISSIONS,
      { params }
    );

    return response.data;
  }

  async getById(
    publicId: string
  ): Promise<SubmissionDetail> {
    const response = await api.get(
      `${ENDPOINTS.SUBMISSIONS}/${publicId}`
    );

    return response.data;
  }

  async create(
    payload: CreateSubmissionRequest
  ): Promise<Submission> {
    const response = await api.post(
      ENDPOINTS.SUBMISSIONS,
      payload
    );

    return response.data;
  }

  async transition(
    publicId: string,
    payload: SubmissionTransitionRequest
  ): Promise<Submission> {
    const response = await api.post(
      `${ENDPOINTS.SUBMISSIONS}/${publicId}/transition`,
      payload
    );

    return response.data;
  }

  async scheduleInterview(
    publicId: string,
    payload: InterviewCreateRequest
  ): Promise<Interview> {
    const response = await api.post(
      `${ENDPOINTS.SUBMISSIONS}/${publicId}/interviews`,
      payload
    );

    return response.data;
  }

  async createOffer(
    publicId: string,
    payload: OfferCreateRequest
  ): Promise<Offer> {
    const response = await api.post(
      `${ENDPOINTS.SUBMISSIONS}/${publicId}/offer`,
      payload
    );

    return response.data;
  }

  async createPlacement(
    publicId: string,
    payload: PlacementCreateRequest
  ): Promise<Placement> {
    const response = await api.post(
      `${ENDPOINTS.SUBMISSIONS}/${publicId}/placement`,
      payload
    );

    return response.data;
  }
}

export default new SubmissionService();