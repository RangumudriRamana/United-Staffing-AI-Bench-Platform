import React, { useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import { AppProviders } from "./providers";
import { AppRoutes } from "@/routes/AppRoutes";
import { useAuthStore } from "@/store/authStore";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

export const App: React.FC = () => {
  const { setSession, isLoading, setLoading } = useAuthStore();

  useEffect(() => {
    const initializeAuth = async () => {
      const savedToken = localStorage.getItem("auth_token");
      
      if (savedToken) {
        setLoading(true);
        try {
          // TODO: Replace this timeout with your real generated API current user endpoint later:
          // const currentUser = await UserService.getCurrentUser();
          await new Promise((resolve) => setTimeout(resolve, 500));
          
          const verifiedUser = {
            id: "usr_100",
            email: "operator@unitedstaffing.ai",
            firstName: "Raghu",
            lastName: "Operator",
            role: "ADMIN" as const,
          };
          
          setSession(savedToken, verifiedUser);
        } catch (error) {
          // If token is invalid/expired, wipe it out
          localStorage.removeItem("auth_token");
        } finally {
          setLoading(false);
        }
      }
    };

    initializeAuth();
  }, [setSession, setLoading]);

  return (
    <AppProviders>
      {isLoading ? (
        /* Smooth loading spinner using our active theme provider while verifying session */
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", backgroundColor: "background.default" }}>
          <CircularProgress size={50} />
        </Box>
      ) : (
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      )}
    </AppProviders>
  );
};

export default App;