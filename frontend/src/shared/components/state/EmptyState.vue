<script setup lang="ts">
/**
 * Empty State - Display when there's no content.
 */
interface Props {
  icon?: string;
  title: string;
  description?: string;
}

withDefaults(defineProps<Props>(), {
  icon: "📭",
});

const emit = defineEmits<{
  action: [];
}>();
</script>

<template>
  <div class="empty-state">
    <span class="empty-state__icon">{{ icon }}</span>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p v-if="description" class="empty-state__description">{{ description }}</p>
    <button v-if="$slots.action" class="empty-state__action" @click="emit('action')">
      <slot name="action" />
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-state__icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state__title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}

.empty-state__description {
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
  max-width: 280px;
}

.empty-state__action {
  margin-top: 1.5rem;
}
</style>