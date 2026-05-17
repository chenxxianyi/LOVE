/**
 * Media feature types.
 */

/**
 * 上传响应
 */
export interface MediaUploadResponse {
  url: string;
  filename: string;
  size: number;
}

/**
 * 媒体资产
 */
export interface MediaAsset {
  id: string;
  url: string;
  filename: string;
  size: number;
  mimeType: string;
}

/**
 * 允许的文件类型
 */
export const ALLOWED_FILE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
  "video/mp4",
  "video/webm",
];

/**
 * 文件大小限制 (10MB)
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024;