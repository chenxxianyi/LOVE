/**
 * Auth feature types.
 */

/**
 * 用户信息
 */
export interface User {
  id: number;
  account: string;
  nickname?: string;
  avatar?: string;
}

/**
 * Token 响应
 */
export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
  user: User;
}

/**
 * 登录请求
 */
export interface LoginRequest {
  account: string;
  password: string;
}

/**
 * 注册请求
 */
export interface RegisterRequest {
  account: string;
  password: string;
  nickname?: string;
}