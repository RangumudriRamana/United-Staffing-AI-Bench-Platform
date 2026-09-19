import { useMemo, useState } from "react";
import type { ReactNode } from "react";

import { AuthContext } from "./AuthContext";
import type { User } from "./types";

interface Props {
  children: ReactNode;
}

export default function AuthProvider({ children }: Props) {
  const [user, setUser] = useState<User | null>(null);

  const [isAuthenticated, setAuthenticated] = useState(
    !!localStorage.getItem("access_token"),
  );

  const value = useMemo(
    () => ({
      user,

      isAuthenticated,

      isLoading: false,

      login(token: string, user: User) {
        localStorage.setItem("access_token", token);

        setUser(user);

        setAuthenticated(true);
      },

      logout() {
        localStorage.removeItem("access_token");

        setUser(null);

        setAuthenticated(false);
      },
    }),
    [user, isAuthenticated],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}