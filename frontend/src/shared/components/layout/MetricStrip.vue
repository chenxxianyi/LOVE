<script setup lang="ts">
/**
 * Metric Strip - Display key metrics in a row.
 */
interface Metric {
  label: string;
  value: string;
  hint?: string;
}

interface Props {
  metrics: Metric[];
}

defineProps<Props>();
</script>

<template>
  <div class="metric-strip">
    <div v-for="(metric, index) in metrics" :key="index" class="metric-strip__item">
      <span class="metric-strip__value">{{ metric.value }}</span>
      <span class="metric-strip__label">{{ metric.label }}</span>
      <span v-if="metric.hint" class="metric-strip__hint">{{ metric.hint }}</span>
    </div>
  </div>
</template>

<style scoped>
.metric-strip {
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
  background: var(--color-surface, #fff);
  border-radius: 12px;
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.metric-strip__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.metric-strip__value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary, #ec4899);
}

.metric-strip__label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 0.25rem;
}

.metric-strip__hint {
  font-size: 0.75rem;
  color: var(--color-text-muted, #9ca3af);
  margin-top: 0.125rem;
}
</style>