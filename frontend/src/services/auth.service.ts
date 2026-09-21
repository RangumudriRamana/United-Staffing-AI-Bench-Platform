import api from "@/api/axios";
import { ENDPOINTS } from "@/api/endpoints";

import type {
  LoginRequest,
  LoginResponse,
  User,
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

  async getCurrentUser(): Promise<User> {
    const response =
      await api.get<{
        success: boolean;
        message: string;
        data: {
          user: User;
        };
      }>(
        ENDPOINTS.AUTH.ME,
      );

    return response.data.data.user;
  }
}

export default new AuthService();