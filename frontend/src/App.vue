<template>
  <div class="app-shell">
    <FallingHearts v-if="showLegacyShell" />
    <TopNav v-if="showLegacyShell" />
    <main class="app-main">
      <RouterView />
    </main>
    <BGMPlayer v-if="showLegacyShell" />
    <AddMomentForm v-if="showLegacyShell" v-model="legacyStore.showAddMomentDialog" />
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute } from "vue-router";
import TopNav from "./components/TopNav.vue";
import FallingHearts from "./components/FallingHearts.vue";
import BGMPlayer from "./components/BGMPlayer.vue";
import AddMomentForm from "./components/AddMomentForm.vue";
import { useLoveStore } from "./stores/useLoveStore";
import { useAuthStore } from "./stores/useAuthStore";
import { useCoupleStore } from "./stores/useCoupleStore";

const route = useRoute();
const authStore = useAuthStore();
const coupleStore = useCoupleStore();
const legacyStore = useLoveStore();

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
