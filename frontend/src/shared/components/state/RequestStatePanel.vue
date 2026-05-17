<script setup lang="ts">
/**
 * Request State Panel - Loading, error, or success state display.
 */
interface Props {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyIcon?: string;
  emptyTitle?: string;
  emptyDescription?: string;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  empty: false,
  emptyIcon: "📭",
  emptyTitle: "暂无数据",
  emptyDescription: "",
});

const emit = defineEmits<{
  retry: [];
}>();
</script>

<template>
  <!-- Loading State -->
  <div v-if="loading" class="request-state-panel request-state-panel--loading">
    <div class="request-state-panel__spinner"></div>
    <span>加载中...</span>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="request-state-panel request-state-panel--error">
    <span class="request-state-panel__error-icon">⚠️</span>
    <p>{{ error }}</p>
    <button class="request-state-panel__retry" @click="emit('retry')">重试</button>
  </div>

  <!-- Empty State -->
  <div v-else-if="empty" class="request-state-panel request-state-panel--empty">
    <span class="request-state-panel__empty-icon">{{ emptyIcon }}</span>
    <h3>{{ emptyTitle }}</h3>
    <p v-if="emptyDescription">{{ emptyDescription }}</p>
  </div>

  <!-- Content -->
  <slot v-else />
</template>

<style scoped>
.request-state-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.request-state-panel--loading {
  color: var(--color-text-secondary, #6b7280);
}

.request-state-panel__spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #ec4899);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.request-state-panel--error {
  color: var(--color-error, #ef4444);
}

.request-state-panel__error-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.request-state-panel__retry {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary, #ec4899);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.request-state-panel--empty {
  color: var(--color-text-muted, #9ca3af);
}

.request-state-panel__empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}
</style>