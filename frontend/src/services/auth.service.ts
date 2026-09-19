import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";

import type {
  LoginRequest,
  LoginResponse,
} from "@/auth/types";

class AuthService {
  async login(
    payload: LoginRequest,
  ): Promise<LoginResponse> {

    const response =
      await api.post<LoginResponse>(
        ENDPOINTS.AUTH.LOGIN,
        payload,
      );

    return response.data;
  }
}

export default new AuthService();