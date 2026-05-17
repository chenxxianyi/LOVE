/**
 * Reports feature types.
 */

/**
 * 完整报告数据
 */
export interface ReportData {
  totalMoments: number;
  topMood: string | null;
  totalLocations: number;
  totalImages: number;
  daysTogether: number;
  latestMomentDate: string | null;
  moodPatterns: MoodPattern[];
  monthlyPatterns: MonthlyPattern[];
  locationPatterns: LocationPattern[];
}

/**
 * 仪表盘摘要
 */
export interface DashboardSummary {
  daysTogether: number;
  totalMoments: number;
  totalBucketItems: number;
  pendingBucketItems: number;
  totalAnniversaries: number;
  totalCapsules: number;
}

/**
 * 心情分布
 */
export interface MoodPattern {
  name: string;
  count: number;
}

/**
 * 月度分布
 */
export interface MonthlyPattern {
  month: string;
  count: number;
}

/**
 * 地点分布
 */
export interface LocationPattern {
  name: string;
  count: number;
}