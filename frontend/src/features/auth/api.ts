/**
 * Auth feature API module.
 */
import { apiClient } from "@/api/client";

export interface User {
  id: number;
  account: string;
  nickname?: string;
  avatar?: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
  user: User;
}

export interface RegisterRequest {
  account: string;
  password: string;
  nickname?: string;
}

export interface LoginRequest {
  account: string;
  password: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface ResetPasswordRequest {
  account: string;
  code: string;
  newPassword: string;
}

export const authApi = {
  register: (data: RegisterRequest) =>
    apiClient.post<{ success: boolean; userId: number; account: string }>("/auth/register", data),

  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>("/auth/login", data),

  refreshToken: (data: RefreshTokenRequest) =>
    apiClient.post<{ accessToken: string; expiresAt: string }>("/auth/refresh", data),

  logout: () =>
    apiClient.post("/auth/logout"),

  getMe: () =>
    apiClient.get<User>("/auth/me"),

  updateMe: (data: Partial<User>) =>
    apiClient.put<User>("/auth/me", data),

  sendResetCode: (account: string) =>
    apiClient.post<{ success: boolean; message: string; debugCode?: string }>("/auth/forgot/send-code", { account }),

  resetPassword: (data: ResetPasswordRequest) =>
    apiClient.post<{ success: boolean }>("/auth/forgot/reset", data),
};