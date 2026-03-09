import { apiClient, unwrap } from "./client";
import type {
  CoupleCreatePayload,
  CoupleCreateResponse,
  CoupleInviteResponse,
  CoupleJoinPayload,
  CoupleJoinResponse,
  CoupleSpace,
  UnbindConfirmPayload,
  UnbindRequestPayload,
} from "../types/couple";

export const coupleApi = {
  createSpace(payload: CoupleCreatePayload) {
    return unwrap(apiClient.post<CoupleCreateResponse>("/couple-space/create", payload));
  },
  createInvite() {
    return unwrap(apiClient.post<CoupleInviteResponse>("/couple-space/invite"));
  },
  joinSpace(payload: CoupleJoinPayload) {
    return unwrap(apiClient.post<CoupleJoinResponse>("/couple-space/join", payload));
  },
  fetchMySpace() {
    return unwrap(apiClient.get<CoupleSpace>("/couple-space/me"));
  },
  requestUnbind(payload: UnbindRequestPayload) {
    return unwrap(apiClient.post<{ success: boolean }>("/couple-space/unbind/request", payload));
  },
  confirmUnbind(payload: UnbindConfirmPayload) {
    return unwrap(apiClient.post<{ success: boolean }>("/couple-space/unbind/confirm", payload));
  },
};
