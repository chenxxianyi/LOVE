/**
 * Memories feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface Memory {
  id: number;
  title: string;
  date: string;
  location: string;
  latitude?: string;
  longitude?: string;
  mood: string;
  summary: string;
  images: string[];
  hasVideo: boolean;
}

export interface CreateMemoryRequest {
  title: string;
  date: string;
  location?: string;
  latitude?: string;
  longitude?: string;
  mood: string;
  summary: string;
  images: string[];
  hasVideo: boolean;
}

export interface UpdateMemoryRequest {
  title?: string;
  date?: string;
  location?: string;
  latitude?: string;
  longitude?: string;
  mood?: string;
  summary?: string;
  images?: string[];
  hasVideo?: boolean;
}

export const memoriesApi = {
  getAll: (limit = 50, offset = 0) =>
    unwrap(apiClient.get<Memory[]>("/", { params: { limit, offset } })),

  getById: (id: number) =>
    unwrap(apiClient.get<Memory>(`/${id}`)),

  create: (data: CreateMemoryRequest) =>
    unwrap(apiClient.post<Memory>("/", data)),

  update: (id: number, data: UpdateMemoryRequest) =>
    unwrap(apiClient.patch<Memory>(`/${id}`, data)),

  delete: (id: number) =>
    unwrap(apiClient.delete(`/${id}`)),

  getMapPoints: () =>
    unwrap(apiClient.get<Array<{
      id: number;
      title: string;
      date: string;
      location: string;
      latitude: string;
      longitude: string;
      mood: string;
    }>>("/map/points")),
};