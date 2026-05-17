<script setup lang="ts">
/**
 * App Shell - Main application layout wrapper.
 * Contains the main navigation, content area, and global components.
 */
import { computed } from "vue";
import SideNav from "@/components/admin/SideNav.vue";
import FallingHearts from "@/components/FallingHearts.vue";
import BGMPlayer from "@/components/BGMPlayer.vue";
import GlobalDialogs from "@/components/GlobalDialogs.vue";

interface Props {
  showNav?: boolean;
  showHearts?: boolean;
  showPlayer?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showNav: true,
  showHearts: true,
  showPlayer: true,
});
</script>

<template>
  <div class="app-shell">
    <!-- Side Navigation -->
    <SideNav v-if="showNav" />

    <!-- Main Content Area -->
    <main class="app-shell__content">
      <slot />
    </main>

    <!-- Global Effects -->
    <FallingHearts v-if="showHearts" />
    <BGMPlayer v-if="showPlayer" />
    <GlobalDialogs />
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  position: relative;
}

.app-shell__content {
  flex: 1;
  margin-left: var(--nav-width, 240px);
  min-height: 100vh;
}

@media (max-width: 768px) {
  .app-shell__content {
    margin-left: 0;
    padding-bottom: var(--bottom-nav-height, 60px);
  }
}
</style>