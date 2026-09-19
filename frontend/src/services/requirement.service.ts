import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";

import type {
  CreateRequirementRequest,
  OwnerReassignmentRequest,
  Requirement,
  RequirementDocumentRequest,
  RequirementSearchCriteria,
  RequirementTechnologyRequest,
  RequirementTransitionRequest,
} from "@/features/requirements/types";

class RequirementService {
  async getAll(
    params?: RequirementSearchCriteria
  ): Promise<Requirement[]> {
    const response = await api.get(
      ENDPOINTS.REQUIREMENTS,
      { params }
    );

    return response.data;
  }

  async getById(publicId: string): Promise<Requirement> {
    const response = await api.get(
      `${ENDPOINTS.REQUIREMENTS}/${publicId}`
    );

    return response.data;
  }

  async create(
    payload: CreateRequirementRequest
  ): Promise<Requirement> {
    const response = await api.post(
      ENDPOINTS.REQUIREMENTS,
      payload
    );

    return response.data;
  }

  async transition(
    publicId: string,
    payload: RequirementTransitionRequest
  ): Promise<Requirement> {
    const response = await api.post(
      `${ENDPOINTS.REQUIREMENTS}/${publicId}/transition`,
      payload
    );

    return response.data;
  }

  async addTechnology(
    publicId: string,
    payload: RequirementTechnologyRequest
  ) {
    const response = await api.post(
      `${ENDPOINTS.REQUIREMENTS}/${publicId}/technologies`,
      payload
    );

    return response.data;
  }

  async addDocument(
    publicId: string,
    payload: RequirementDocumentRequest
  ) {
    const response = await api.post(
      `${ENDPOINTS.REQUIREMENTS}/${publicId}/documents`,
      payload
    );

    return response.data;
  }

  async reassignOwner(
    publicId: string,
    payload: OwnerReassignmentRequest
  ): Promise<Requirement> {
    const response = await api.post(
      `${ENDPOINTS.REQUIREMENTS}/${publicId}/owner`,
      payload
    );

    return response.data;
  }
}

export default new RequirementService();