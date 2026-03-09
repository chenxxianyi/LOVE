import { defineStore } from "pinia";
import axios from "axios";

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
  latitude?: string;
  longitude?: string;
  mood: string;
  summary: string;
  images: string[];
  hasVideo: boolean;
}

export interface BucketItem {
  id: number;
  title: string;
  description?: string;
  status: "pending" | "planned" | "completed";
  icon: string;
  images: string[];
  created_at: string;
  completed_at?: string;
}

export interface TimeCapsule {
  id: number;
  sender: string;
  receiver: string;
  content: string;
  open_at: string;
  created_at: string;
  is_opened: boolean;
}

export interface MusicItem {
  id: number;
  title: string;
  artist: string;
  url: string;
  cover?: string;
}

export interface AnniversaryItem {
  id: number;
  title: string;
  date: string;
  type: "anniversary" | "event";
  icon: string;
  days_left: number;
}

export interface CoverItem {
  id: number;
  url: string;
}

export interface ReportData {
  total_moments: number;
  top_mood: string | null;
  total_locations: number;
  total_images: number;
  days_together: number;
  latest_moment_date: string | null;
}

export interface WheelOption {
  id: number;
  text: string;
  color: string;
}

export interface DailyQuestion {
  id: number;
  date: string;
  content: string;
  answer_a: string | null;
  answer_b: string | null;
}

export const useLoveStore = defineStore("love", {
  state: () => ({
    coupleName: "小鹿 & 小棠",
    startDate: "2024-04-21",
    todayMood: "今天也要认真相爱",
    dashboardStats: [] as DashboardStat[],
    moments: [] as MomentItem[],
    bucketList: [] as BucketItem[],
    capsules: [] as TimeCapsule[],
    musicList: [] as MusicItem[],
    anniversaries: [] as AnniversaryItem[],
    covers: [] as CoverItem[],
    reportData: null as ReportData | null,
    dailyQuestion: null as DailyQuestion | null,
    questionHistory: [] as DailyQuestion[],
    wheelOptions: [
      { id: 1, text: "看电影", color: "#FF9A9E" },
      { id: 2, text: "吃火锅", color: "#FECFEF" },
      { id: 3, text: "去公园", color: "#A18CD1" },
      { id: 4, text: "喝奶茶", color: "#FBC2EB" },
      { id: 5, text: "打游戏", color: "#8EC5FC" },
      { id: 6, text: "按摩", color: "#E0C3FC" },
    ] as WheelOption[],
    currentCover: "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?auto=format&fit=crop&w=1400&q=80",
    showAddMomentDialog: false,
    isLoggedIn: localStorage.getItem("isLoggedIn") === "true",
    loading: false,
    error: null as string | null,
  }),
  actions: {
    login() {
      this.isLoggedIn = true;
      localStorage.setItem("isLoggedIn", "true");
      this.setRandomCover();
    },
    setRandomCover() {
      if (this.covers.length > 0) {
        const randomIndex = Math.floor(Math.random() * this.covers.length);
        this.currentCover = this.covers[randomIndex].url;
      }
    },
    logout() {
      this.isLoggedIn = false;
      localStorage.removeItem("isLoggedIn");
    },
    async fetchInfo() {
      try {
        const response = await axios.get("http://localhost:8000/api/info");
        this.coupleName = response.data.coupleName;
        this.todayMood = response.data.todayMood;
        this.dashboardStats = response.data.dashboardStats;
        this.startDate = response.data.start_date;
      } catch (err: any) {
        console.error("Failed to fetch info:", err);
        this.error = err.message;
      }
    },
    async updateInfo(data: { couple_names?: string; start_date?: string }) {
      try {
        await axios.post("http://localhost:8000/api/info", data);
        await this.fetchInfo();
      } catch (err: any) {
        console.error("Failed to update info:", err);
        throw err;
      }
    },
    async fetchMoments() {
      try {
        const response = await axios.get("http://localhost:8000/api/moments");
        this.moments = response.data;
      } catch (err: any) {
        console.error("Failed to fetch moments:", err);
        this.error = err.message;
      }
    },
    async fetchBucketList() {
      try {
        const response = await axios.get("http://localhost:8000/api/bucket");
        this.bucketList = response.data;
      } catch (err: any) {
        console.error("Failed to fetch bucket list:", err);
        this.error = err.message;
      }
    },
    async fetchCapsules() {
      try {
        const response = await axios.get("http://localhost:8000/api/capsules");
        this.capsules = response.data;
      } catch (err: any) {
        console.error("Failed to fetch capsules:", err);
        this.error = err.message;
      }
    },
    async fetchMusicList() {
      try {
        const response = await axios.get("http://localhost:8000/api/music");
        this.musicList = response.data;
      } catch (err: any) {
        console.error("Failed to fetch music list:", err);
        this.error = err.message;
      }
    },
    async fetchAnniversaries() {
      try {
        const response = await axios.get("http://localhost:8000/api/anniversaries");
        this.anniversaries = response.data;
      } catch (err: any) {
        console.error("Failed to fetch anniversaries:", err);
        this.error = err.message;
      }
    },
    async fetchCovers() {
      try {
        const response = await axios.get("http://localhost:8000/api/covers");
        this.covers = response.data;
        this.setRandomCover();
      } catch (err: any) {
        console.error("Failed to fetch covers:", err);
        this.error = err.message;
      }
    },
    async fetchReport() {
      try {
        const response = await axios.get("http://localhost:8000/api/report");
        this.reportData = response.data;
      } catch (err: any) {
        console.error("Failed to fetch report:", err);
        this.error = err.message;
      }
    },
    async fetchDailyQuestion() {
      try {
        const response = await axios.get("http://localhost:8000/api/questions/today");
        this.dailyQuestion = response.data;
      } catch (err: any) {
        console.error("Failed to fetch daily question:", err);
        this.error = err.message;
      }
    },
    async answerQuestion(id: number, answer: { answer_a?: string; answer_b?: string }) {
      try {
        const response = await axios.post(`http://localhost:8000/api/questions/${id}/answer`, answer);
        this.dailyQuestion = response.data;
        return response.data;
      } catch (err: any) {
        console.error("Failed to answer question:", err);
        throw err;
      }
    },
    async fetchQuestionHistory() {
      try {
        const response = await axios.get("http://localhost:8000/api/questions/history");
        this.questionHistory = response.data;
      } catch (err: any) {
        console.error("Failed to fetch question history:", err);
        this.error = err.message;
      }
    },
    async fetchAll() {
      this.loading = true;
      this.error = null;
      await Promise.all([
        this.fetchInfo(), 
        this.fetchMoments(), 
        this.fetchBucketList(),
        this.fetchCapsules(),
        this.fetchMusicList(),
        this.fetchAnniversaries(),
        this.fetchCovers(),
        this.fetchDailyQuestion()
      ]);
      this.loading = false;
    },
    async createMoment(moment: Omit<MomentItem, "id">) {
      try {
        const response = await axios.post("http://localhost:8000/api/moments", moment);
        this.moments.unshift(response.data);
        // Refresh stats to update count
        this.fetchInfo();
        return response.data;
      } catch (err: any) {
        console.error("Failed to create moment:", err);
        throw err;
      }
    },
    async createBucketItem(item: Omit<BucketItem, "id" | "created_at">) {
      try {
        const response = await axios.post("http://localhost:8000/api/bucket", item);
        this.bucketList.unshift(response.data);
        return response.data;
      } catch (err: any) {
        console.error("Failed to create bucket item:", err);
        throw err;
      }
    },
    async updateBucketItem(id: number, update: Partial<BucketItem>) {
      try {
        const response = await axios.put(`http://localhost:8000/api/bucket/${id}`, update);
        const index = this.bucketList.findIndex(i => i.id === id);
        if (index !== -1) {
          this.bucketList[index] = response.data;
        }
        return response.data;
      } catch (err: any) {
        console.error("Failed to update bucket item:", err);
        throw err;
      }
    },
    async createCapsule(capsule: Omit<TimeCapsule, "id" | "created_at" | "is_opened">) {
      try {
        const response = await axios.post("http://localhost:8000/api/capsules", capsule);
        this.capsules.push(response.data);
        return response.data;
      } catch (err: any) {
        console.error("Failed to create capsule:", err);
        throw err;
      }
    },
    async addMusic(music: Omit<MusicItem, "id">) {
      try {
        const response = await axios.post("http://localhost:8000/api/music", music);
        this.musicList.push(response.data);
        return response.data;
      } catch (err: any) {
        console.error("Failed to add music:", err);
        throw err;
      }
    },
    async deleteMusic(id: number) {
      try {
        await axios.delete(`http://localhost:8000/api/music/${id}`);
        this.musicList = this.musicList.filter(m => m.id !== id);
      } catch (err: any) {
        console.error("Failed to delete music:", err);
        throw err;
      }
    },
    async createAnniversary(item: Omit<AnniversaryItem, "id" | "days_left">) {
      try {
        const response = await axios.post("http://localhost:8000/api/anniversaries", item);
        this.anniversaries.push(response.data);
        // Sort again
        this.anniversaries.sort((a, b) => a.days_left - b.days_left);
        return response.data;
      } catch (err: any) {
        console.error("Failed to create anniversary:", err);
        throw err;
      }
    },
    async deleteAnniversary(id: number) {
      try {
        await axios.delete(`http://localhost:8000/api/anniversaries/${id}`);
        this.anniversaries = this.anniversaries.filter(a => a.id !== id);
      } catch (err: any) {
        console.error("Failed to delete anniversary:", err);
        throw err;
      }
    },
    async addCover(url: string) {
      try {
        const response = await axios.post("http://localhost:8000/api/covers", { url });
        this.covers.push(response.data);
        return response.data;
      } catch (err: any) {
        console.error("Failed to add cover:", err);
        throw err;
      }
    },
    async deleteCover(id: number) {
      try {
        await axios.delete(`http://localhost:8000/api/covers/${id}`);
        this.covers = this.covers.filter(c => c.id !== id);
      } catch (err: any) {
        console.error("Failed to delete cover:", err);
        throw err;
      }
    },
    updateWheelOptions(options: WheelOption[]) {
      this.wheelOptions = options;
    },
    async uploadImage(file: File) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await axios.post("http://localhost:8000/api/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        return response.data.url;
      } catch (err: any) {
        console.error("Failed to upload image:", err);
        throw err;
      }
    }
  }
});
