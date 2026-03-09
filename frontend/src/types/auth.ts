export interface UserProfile {
  id: number | string;
  account: string;
  nickname?: string;
  avatar?: string;
}

export interface LoginPayload {
  account: string;
  password: string;
}

export interface RegisterPayload {
  account: string;
  password: string;
  nickname?: string;
}

export interface ForgotSendCodePayload {
  account: string;
}

export interface ForgotResetPayload {
  account: string;
  code: string;
  new_password: string;
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export interface RefreshPayload {
  refresh_token: string;
}

export interface AuthSession {
  user: UserProfile;
  access_token: string;
  refresh_token: string;
  expires_in?: number;
  pair_status?: "none" | "pending" | "paired";
}
