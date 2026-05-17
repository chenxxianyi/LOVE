/**
 * Media feature API module.
 */
import { apiClient } from "@/api/client";
import type { AxiosProgressEvent } from "axios";

export interface MediaUploadResponse {
  url: string;
  filename: string;
  size: number;
}

export interface MediaAsset {
  id: string;
  url: string;
  filename: string;
  size: number;
  mimeType: string;
}

export const mediaApi = {
  upload: (file: File, onProgress?: (event: AxiosProgressEvent) => void) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<MediaUploadResponse>("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onProgress,
    });
  },

  uploadMultiple: (files: File[], onProgress?: (event: AxiosProgressEvent) => void) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    return apiClient.post<MediaUploadResponse[]>("/upload-multiple", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onProgress,
    });
  },

  delete: (url: string) =>
    apiClient.delete(`/delete/${encodeURIComponent(url)}`),
};