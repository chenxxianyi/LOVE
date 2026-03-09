import { apiClient, unwrap } from "./client";
import type {
  AuthSession,
  ChangePasswordPayload,
  ForgotResetPayload,
  ForgotSendCodePayload,
  LoginPayload,
  RegisterPayload,
  UserProfile,
} from "../types/auth";

export const authApi = {
  login(payload: LoginPayload) {
    return unwrap(apiClient.post<AuthSession>("/auth/login", payload));
  },
  register(payload: RegisterPayload) {
    return unwrap(apiClient.post<AuthSession>("/auth/register", payload));
  },
  sendResetCode(payload: ForgotSendCodePayload) {
    return unwrap(apiClient.post<{ success: boolean }>("/auth/forgot/send-code", payload));
  },
  resetPassword(payload: ForgotResetPayload) {
    return unwrap(apiClient.post<{ success: boolean }>("/auth/forgot/reset", payload));
  },
  changePassword(payload: ChangePasswordPayload) {
    return unwrap(apiClient.post<{ success: boolean }>("/auth/change-password", payload));
  },
  fetchMe() {
    return unwrap(apiClient.get<UserProfile>("/auth/me"));
  },
};
