/**
 * Couple space feature types.
 */

/**
 * 情侣空间信息
 */
export interface CoupleSpace {
  spaceId: number;
  spaceName: string;
  startDate: string;
  role: string;
  nickname: string;
  partner?: PartnerInfo;
  joinedAt: string;
}

/**
 * 伴侣信息
 */
export interface PartnerInfo {
  userId: number;
  nickname: string;
  avatar?: string;
}

/**
 * 空间信息（包含是否有空间）
 */
export interface SpaceInfo {
  hasSpace: boolean;
  space: CoupleSpace | null;
}

/**
 * 空间成员
 */
export interface SpaceMember {
  userId: number;
  nickname: string;
  role: string;
  avatar?: string;
  joinedAt: string;
}

/**
 * 邀请响应
 */
export interface InviteResponse {
  inviteCode: string;
  expiresAt: string;
}