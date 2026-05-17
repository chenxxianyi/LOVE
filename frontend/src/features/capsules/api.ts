/**
 * Time capsules feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface TimeCapsule {
  id: number;
  sender: string;
  receiver: string;
  content: string;
  openAt: string;
  createdAt: string;
  isOpened: boolean;
  isLocked: boolean;
}

export interface CreateCapsuleRequest {
  sender: string;
  receiver: string;
  content: string;
  openAt: string;
}

export interface UpcomingCapsule {
  id: number;
  sender: string;
  receiver: string;
  openAt: string;
  daysUntilOpen: number;
}

export const capsulesApi = {
  getAll: () =>
    unwrap(apiClient.get<TimeCapsule[]>("/")),

  getById: (id: number) =>
    unwrap(apiClient.get<TimeCapsule>(`/${id}`)),

  create: (data: CreateCapsuleRequest) =>
    unwrap(apiClient.post<TimeCapsule>("/", data)),

  delete: (id: number) =>
    unwrap(apiClient.delete(`/${id}`)),

  getUpcoming: () =>
    unwrap(apiClient.get<UpcomingCapsule[]>("/upcoming/list")),
};