/**
 * Memories feature types.
 */

/**
 * 回忆/时刻数据模型
 */
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

/**
 * 心情选项
 */
export const MOOD_OPTIONS = [
  { value: "心动", emoji: "💕", color: "#FF6B6B" },
  { value: "治愈", emoji: "🌸", color: "#4ECDC4" },
  { value: "浪漫", emoji: "✨", color: "#FFB6C1" },
  { value: "温馨", emoji: "🏠", color: "#FFE66D" },
  { value: "欢乐", emoji: "🎉", color: "#95E1D3" },
  { value: "甜蜜", emoji: "🍯", color: "#F38181" },
  { value: "平静", emoji: "🌿", color: "#AA96DA" },
  { value: "思念", emoji: "💭", color: "#FCBAD3" },
] as const;

/**
 * 地图点标记
 */
export interface MapPoint {
  id: number;
  title: string;
  date: string;
  location: string;
  latitude: string;
  longitude: string;
  mood: string;
}