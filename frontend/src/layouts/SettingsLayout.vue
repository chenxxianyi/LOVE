<script setup lang="ts">
/**
 * Settings Layout - Layout for settings-related pages.
 */
</script>

<template>
  <div class="settings-layout">
    <div class="settings-layout__sidebar">
      <slot name="sidebar" />
    </div>
    <main class="settings-layout__content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.settings-layout {
  display: flex;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  gap: 2rem;
}

.settings-layout__sidebar {
  width: 240px;
  flex-shrink: 0;
}

.settings-layout__content {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .settings-layout {
    flex-direction: column;
    padding: 1rem;
  }

  .settings-layout__sidebar {
    width: 100%;
  }
}
</style>