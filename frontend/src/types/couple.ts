export type PairStatus = "none" | "pending" | "paired";

export interface CoupleMember {
  id: number | string;
  nickname: string;
  role?: "A" | "B";
}

export interface CoupleSpace {
  id: number | string;
  space_name: string;
  start_date: string;
  privacy_level: "couple_only";
  members: CoupleMember[];
  pair_status?: PairStatus;
}

export interface CoupleCreatePayload {
  space_name: string;
  my_nickname: string;
  start_date: string;
  privacy_level: "couple_only";
}

export interface CoupleCreateResponse {
  space: CoupleSpace;
  pair_status: PairStatus;
}

export interface CoupleInviteResponse {
  invite_code: string;
  invite_link: string;
  expires_at: string;
}

export interface CoupleJoinPayload {
  invite_code: string;
  my_nickname: string;
}

export interface CoupleJoinResponse {
  space: CoupleSpace;
  pair_status: PairStatus;
}

export interface UnbindRequestPayload {
  reason?: string;
}

export interface UnbindConfirmPayload {
  verify_code: string;
}
