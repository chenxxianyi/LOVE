/**
 * Anniversaries feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface Anniversary {
  id: number;
  title: string;
  date: string;
  type: "anniversary" | "event";
  icon: string;
  daysLeft: number;
}

export interface CreateAnniversaryRequest {
  title: string;
  date: string;
  type: "anniversary" | "event";
  icon?: string;
}

export interface UpdateAnniversaryRequest extends CreateAnniversaryRequest {}

export const anniversariesApi = {
  getAll: () =>
    unwrap(apiClient.get<Anniversary[]>("/")),

  create: (data: CreateAnniversaryRequest) =>
    unwrap(apiClient.post<Anniversary>("/", data)),

  update: (id: number, data: UpdateAnniversaryRequest) =>
    unwrap(apiClient.put<Anniversary>(`/${id}`, data)),

  delete: (id: number) =>
    unwrap(apiClient.delete(`/${id}`)),

  getUpcoming: (days = 30) =>
    unwrap(apiClient.get<Anniversary[]>("/upcoming", { params: { days } })),
};