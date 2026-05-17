<script setup lang="ts">
/**
 * Page Header - Consistent page header component.
 */
interface Props {
  title: string;
  subtitle?: string;
  showBack?: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  back: [];
}>();
</script>

<template>
  <header class="page-header">
    <div class="page-header__left">
      <button v-if="showBack" class="page-header__back" @click="emit('back')">
        ←
      </button>
    </div>
    <div class="page-header__content">
      <h1 class="page-header__title">{{ title }}</h1>
      <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
    </div>
    <div class="page-header__right">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  padding: 1.5rem 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.page-header__left,
.page-header__right {
  flex: 0 0 auto;
}

.page-header__content {
  flex: 1;
}

.page-header__title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.page-header__subtitle {
  color: var(--color-text-secondary, #6b7280);
  margin: 0.25rem 0 0;
}

.page-header__back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}
</style>