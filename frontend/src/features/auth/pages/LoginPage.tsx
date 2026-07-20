import axios from 'axios';
import React from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { useSnackbar } from "notistack";

import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import CircularProgress from "@mui/material/CircularProgress";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Avatar from "@mui/material/Avatar";

import { loginSchema, LoginInput } from "../schemas/loginSchema";
import { useAuthStore } from "@/store/authStore";
import { loginApiV1AuthLoginPost } from "@/api/generated"; // ◄— Standalone function import

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const { setSession, isLoading, setLoading } = useAuthStore();

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", rememberMe: false },
  });

  const onSubmit = async (data: LoginInput) => {
    setLoading(true);
    try {
      const response = await axios.post(
        "/api/v1/auth/login",
        {
          email: data.email,
          password: data.password,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      // Handle nested backend response wrappers safely
      const responseBody = response.data;
      const tokenString = 
        responseBody?.data?.access_token || 
        responseBody?.access_token || 
        responseBody;
      
      if (!tokenString || typeof tokenString !== 'string') {
        throw new Error("Authentication succeeded but no valid access token string was returned.");
      }

      // Extract user info from response if available, or fallback gracefully
      const userData = responseBody?.data?.user || {};
      const activeUser = {
        id: userData.id || userData.public_id || "usr_100",
        email: userData.email || data.email,
        firstName: userData.first_name || "Raghu",
        lastName: userData.last_name || "Operator",
        role: userData.role || "ADMIN",
      };

      setSession(tokenString, activeUser);
      
      // Always store in localStorage so API clients can attach it to requests
      localStorage.setItem("auth_token", tokenString);

      enqueueSnackbar("Welcome back! Authentication successful.", { variant: "success" });
      navigate("/dashboard");

    } catch (error: any) {
      console.error("Login failed:", error);
      const errorMessage = 
        error?.response?.data?.detail || 
        error?.message || 
        "Invalid credentials. Access denied.";
        
      enqueueSnackbar(errorMessage, { variant: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "background.default",
        p: 2,
      }}
    >
      <Paper
        elevation={4}
        sx={{
          p: 4,
          width: "100%",
          maxWidth: 400,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          borderRadius: 3,
        }}
      >
        <Avatar sx={{ m: 1, bgcolor: "primary.main", width: 48, height: 48 }}>
          <LockOutlinedIcon />
        </Avatar>
        
        <Typography variant="h5" component="h1" sx={{ fontWeight: "bold", mt: 1 }}>
          United Staffing AI
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          Sign in to access your talent bench dashboard
        </Typography>

        <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ width: "100%" }} noValidate>
          <Controller
            name="email"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                margin="normal"
                fullWidth
                label="Corporate Email Address"
                autoComplete="email"
                autoFocus
                error={!!errors.email}
                helperText={errors.email?.message}
                disabled={isLoading}
              />
            )}
          />

          <Controller
            name="password"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                margin="normal"
                fullWidth
                label="Password"
                type="password"
                autoComplete="current-password"
                error={!!errors.password}
                helperText={errors.password?.message}
                disabled={isLoading}
              />
            )}
          />

          <Controller
            name="rememberMe"
            control={control}
            render={({ field: { value, onChange } }) => (
              <FormControlLabel
                control={
                  <Checkbox 
                    checked={value} 
                    onChange={(e) => onChange(e.target.checked)} 
                    color="primary" 
                    disabled={isLoading}
                  />
                }
                label="Remember this workstation"
                sx={{ mt: 1, display: "block", textAlign: "left" }}
              />
            )}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2, height: 48, fontWeight: "bold" }}
          >
            {isLoading ? <CircularProgress size={24} color="inherit" /> : "Sign In to Platform"}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default LoginPage;
