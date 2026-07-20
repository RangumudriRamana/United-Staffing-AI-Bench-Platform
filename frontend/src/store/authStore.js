import { create } from "zustand";
export const useAuthStore = create((set) => ({
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
