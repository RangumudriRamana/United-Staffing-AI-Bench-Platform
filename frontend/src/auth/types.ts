export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  public_id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  data: {
    access_token: string;
    token_type: string;
    user: User;
  };
}