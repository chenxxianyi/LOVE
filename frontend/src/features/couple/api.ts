/**
 * Couple space feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface CoupleSpace {
  spaceId: number;
  spaceName: string;
  startDate: string;
  role: string;
  nickname: string;
  partner?: {
    userId: number;
    nickname: string;
    avatar?: string;
  };
  joinedAt: string;
}

export interface SpaceInfo {
  hasSpace: boolean;
  space: CoupleSpace | null;
}

export interface CreateSpaceRequest {
  spaceName: string;
  startDate: string;
  nickname?: string;
}

export interface JoinSpaceRequest {
  inviteCode: string;
  nickname?: string;
}

export interface InviteResponse {
  inviteCode: string;
  expiresAt: string;
}

export interface SpaceMember {
  userId: number;
  nickname: string;
  role: string;
  avatar?: string;
  joinedAt: string;
}

export const coupleApi = {
  createSpace: (data: CreateSpaceRequest) =>
    unwrap(apiClient.post<{ spaceId: number; spaceName: string; startDate: string }>("/create", data)),

  getMySpace: () =>
    unwrap(apiClient.get<SpaceInfo>("/me")),

  generateInvite: () =>
    unwrap(apiClient.post<InviteResponse>("/generate-invite")),

  joinSpace: (data: JoinSpaceRequest) =>
    unwrap(apiClient.post<{ success: boolean; spaceId: number; spaceName: string }>("/join", data)),

  leaveSpace: () =>
    unwrap(apiClient.delete("/leave")),

  getMembers: () =>
    unwrap(apiClient.get<{ members: SpaceMember[]; count: number }>("/members")),
};