import { create } from "zustand";

export type UserRole = "ADMIN" | "MANAGER" | "RECRUITER";

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setSession: (token: string, user: User) => void;
  clearSession: () => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem("auth_token"),
  isAuthenticated: !!localStorage.getItem("auth_token"),
  isLoading: false,

  setSession: (token, user) => {
    localStorage.setItem("auth_token", token);
    set({ token, user, isAuthenticated: true, isLoading: false });
  },

  clearSession: () => {
    localStorage.removeItem("auth_token");
    set({ token: null, user: null, isAuthenticated: false, isLoading: false });
  },

  setLoading: (isLoading) => set({ isLoading }),
}));