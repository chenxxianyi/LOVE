<script setup lang="ts">
/**
 * Compact Item Card - Compact card for lists.
 */
interface Props {
  title: string;
  subtitle?: string;
  icon?: string;
  value?: string;
}

defineProps<Props>();

const emit = defineEmits<{
  click: [];
}>();
</script>

<template>
  <div class="compact-item-card" @click="emit('click')">
    <span v-if="icon" class="compact-item-card__icon">{{ icon }}</span>
    <div class="compact-item-card__content">
      <span class="compact-item-card__title">{{ title }}</span>
      <span v-if="subtitle" class="compact-item-card__subtitle">{{ subtitle }}</span>
    </div>
    <span v-if="value" class="compact-item-card__value">{{ value }}</span>
    <span class="compact-item-card__arrow">→</span>
  </div>
</template>

<style scoped>
.compact-item-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface, #fff);
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.compact-item-card:hover {
  background: var(--color-bg, #f9fafb);
}

.compact-item-card__icon {
  font-size: 1.5rem;
}

.compact-item-card__content {
  flex: 1;
  min-width: 0;
}

.compact-item-card__title {
  display: block;
  font-weight: 500;
}

.compact-item-card__subtitle {
  display: block;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 0.25rem;
}

.compact-item-card__value {
  font-size: 0.875rem;
  color: var(--color-primary, #ec4899);
  font-weight: 500;
}

.compact-item-card__arrow {
  color: var(--color-text-muted, #9ca3af);
}
</style>