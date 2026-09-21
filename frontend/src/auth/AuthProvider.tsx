import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { AuthContext } from "./AuthContext";
import type { User } from "./types";
import authService from "@/services/auth.service";

interface Props {
  children: ReactNode;
}

export default function AuthProvider({ children }: Props) {
  const [user, setUser] = useState<User | null>(null);

  const [isAuthenticated, setAuthenticated] = useState(
    !!localStorage.getItem("access_token"),
  );

  const [isLoading, setIsLoading] = useState(
    !!localStorage.getItem("access_token"),
  );

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setIsLoading(false);
      return;
    }

    authService
      .getCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        setAuthenticated(true);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        setUser(null);
        setAuthenticated(false);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,

      login(token: string, loggedInUser: User) {
        localStorage.setItem("access_token", token);
        setUser(loggedInUser);
        setAuthenticated(true);
      },

      logout() {
        localStorage.removeItem("access_token");
        setUser(null);
        setAuthenticated(false);
      },
    }),
    [user, isAuthenticated, isLoading],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}