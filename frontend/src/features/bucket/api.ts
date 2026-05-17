/**
 * Bucket items feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface BucketItem {
  id: number;
  title: string;
  description?: string;
  status: "pending" | "planned" | "completed";
  icon: string;
  images: string[];
  createdAt: string;
  completedAt?: string;
}

export interface CreateBucketItemRequest {
  title: string;
  description?: string;
  status?: string;
  icon?: string;
  images?: string[];
}

export interface UpdateBucketItemRequest {
  status?: string;
  images?: string[];
}

export interface BucketStats {
  total: number;
  pending: number;
  planned: number;
  completed: number;
  completionRate: number;
}

export const bucketApi = {
  getAll: (status?: string) =>
    unwrap(apiClient.get<BucketItem[]>("/", { params: status ? { status } : {} })),

  create: (data: CreateBucketItemRequest) =>
    unwrap(apiClient.post<BucketItem>("/", data)),

  update: (id: number, data: UpdateBucketItemRequest) =>
    unwrap(apiClient.put<BucketItem>(`/${id}`, data)),

  delete: (id: number) =>
    unwrap(apiClient.delete(`/${id}`)),

  getStats: () =>
    unwrap(apiClient.get<BucketStats>("/stats")),
};