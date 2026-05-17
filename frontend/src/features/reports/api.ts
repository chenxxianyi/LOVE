/**
 * Reports feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface ReportData {
  totalMoments: number;
  topMood: string | null;
  totalLocations: number;
  totalImages: number;
  daysTogether: number;
  latestMomentDate: string | null;
  moodPatterns: Array<{ name: string; count: number }>;
  monthlyPatterns: Array<{ month: string; count: number }>;
  locationPatterns: Array<{ name: string; count: number }>;
}

export interface DashboardSummary {
  daysTogether: number;
  totalMoments: number;
  totalBucketItems: number;
  pendingBucketItems: number;
  totalAnniversaries: number;
  totalCapsules: number;
}

export interface PatternData {
  moodPatterns: Array<{ name: string; count: number }>;
  monthlyPatterns: Array<{ month: string; count: number }>;
  locationPatterns: Array<{ name: string; count: number }>;
}

export const reportsApi = {
  getFullReport: () =>
    unwrap(apiClient.get<ReportData>("/full")),

  getDashboard: () =>
    unwrap(apiClient.get<DashboardSummary>("/dashboard")),

  getPatterns: () =>
    unwrap(apiClient.get<PatternData>("/patterns")),
};