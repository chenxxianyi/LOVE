<template>
  <div class="app-shell">
    <!-- 侧边栏 (桌面端) + 底部 Tab (移动端) -->
    <SideNav v-if="showLegacyShell" />
    <FallingHearts v-if="showLegacyShell" />

    <!-- 主内容区 -->
    <main class="app-main" :class="{ 'with-sidebar': showLegacyShell }">
      <RouterView />
    </main>

    <!-- 底部浮动: 音乐 -->
    <BGMPlayer v-if="showLegacyShell" />
    <!-- 新建回忆弹窗 -->
    <AddMomentForm v-if="showLegacyShell" v-model="legacyStore.showAddMomentDialog" />
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute } from "vue-router";
import SideNav from "./components/SideNav.vue";
import FallingHearts from "./components/FallingHearts.vue";
import BGMPlayer from "./components/BGMPlayer.vue";
import AddMomentForm from "./components/AddMomentForm.vue";
import { useLoveStore } from "./stores/useLoveStore";
import { useAuthStore } from "./stores/useAuthStore";
import { useCoupleStore } from "./stores/useCoupleStore";
import { useThemeStore } from "./stores/useThemeStore";

const route = useRoute();
const authStore = useAuthStore();
const coupleStore = useCoupleStore();
const legacyStore = useLoveStore();
const themeStore = useThemeStore();

if (typeof window !== "undefined") {
  themeStore.applyTheme();
}

const showLegacyShell = computed(
  () =>
    authStore.isAuthenticated &&
    coupleStore.isPaired &&
    !Boolean(route.meta.hideLegacyShell)
);

watch(
  () => authStore.isAuthenticated,
  (authed) => {
    legacyStore.isLoggedIn = authed;
  },
  { immediate: true }
);
</script>
