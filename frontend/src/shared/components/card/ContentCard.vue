<script setup lang="ts">
/**
 * Content Card - Generic content card container.
 */
interface Props {
  title?: string;
  padding?: string;
}

withDefaults(defineProps<Props>(), {
  padding: "1.5rem",
});
</script>

<template>
  <div class="content-card">
    <header v-if="title || $slots.header" class="content-card__header">
      <slot name="header">
        <h3>{{ title }}</h3>
      </slot>
    </header>
    <div class="content-card__body" :style="{ padding }">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="content-card__footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<style scoped>
.content-card {
  background: var(--color-surface, #fff);
  border-radius: 16px;
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
  overflow: hidden;
}

.content-card__header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.content-card__header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.content-card__footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-bg, #f9fafb);
}
</style>