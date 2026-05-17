import { defineStore } from "pinia";

export type ThemeMode = "warm" | "glass" | "glass-dark";

export const useThemeStore = defineStore("theme", {
  state: () => ({
    mode: (localStorage.getItem("love-theme") || "warm") as ThemeMode,
  }),
  actions: {
    setTheme(mode: ThemeMode) {
      this.mode = mode;
      localStorage.setItem("love-theme", mode);
      this.applyTheme();
    },
    applyTheme() {
      const html = document.documentElement;
      const body = document.body;
      if (this.mode === "warm") {
        delete html.dataset.theme;
        delete body.dataset.theme;
      } else {
        html.dataset.theme = this.mode;
        body.dataset.theme = this.mode;
      }
    },
  },
});