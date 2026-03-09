export interface DashboardStat {
  label: string;
  value: string;
  hint: string;
}

export interface MomentItem {
  id: number;
  title: string;
  date: string;
  location: string;
  mood: string;
  summary: string;
  images: string[];
  hasVideo: boolean;
}

export const dashboardStats: DashboardStat[] = [
  { label: "在一起", value: "682 天", hint: "从 2024-04-21 到今天" },
  { label: "共同回忆", value: "146 条", hint: "照片 + 视频 + 文字" },
  { label: "纪念日倒计时", value: "26 天", hint: "下一次月纪念日" },
];

export const featuredMoments: MomentItem[] = [
  {
    id: 101,
    title: "海边日落散步",
    date: "2026-02-14 18:20",
    location: "青岛石老人海水浴场",
    mood: "心动",
    summary:
      "风很柔，海浪很慢。你说以后每年都要来一次海边，我们在落日下拍了很多张笨拙但好看的合照。",
    images: [
      "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1495567720989-cebdbdd97913?auto=format&fit=crop&w=1200&q=80",
    ],
    hasVideo: true,
  },
  {
    id: 102,
    title: "凌晨厨房小夜宵",
    date: "2026-01-22 00:42",
    location: "家里",
    mood: "治愈",
    summary:
      "临时起意煮了面，番茄和鸡蛋都切得歪歪扭扭。你说这比任何餐厅都好吃，因为是我们一起做的。",
    images: [
      "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80",
    ],
    hasVideo: false,
  },
  {
    id: 103,
    title: "第一次一起看雪",
    date: "2025-12-09 21:15",
    location: "南京玄武湖",
    mood: "浪漫",
    summary:
      "雪落在围巾和肩膀上，手机镜头雾蒙蒙的。我们拍了十几段短视频，决定做成年度回忆片。",
    images: [
      "https://images.unsplash.com/photo-1453306458620-5bbef13a5bca?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1515792677823-30f151e09dcd?auto=format&fit=crop&w=1200&q=80",
    ],
    hasVideo: true,
  },
];
