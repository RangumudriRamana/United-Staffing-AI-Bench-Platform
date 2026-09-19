import { useNavigate } from "react-router-dom";

import authService from "@/services/auth.service";

import { useAuth } from "@/auth/useAuth";

import type { LoginFormData } from "@/schemas/login.schema";

export function useLogin() {
  const navigate = useNavigate();

  const auth = useAuth();

  async function login(data: LoginFormData) {
    const response =
      await authService.login(data);

    auth.login(
      response.data.access_token,
      response.data.user,
    );

    navigate("/");
  }

  return {
    login,
  };
}