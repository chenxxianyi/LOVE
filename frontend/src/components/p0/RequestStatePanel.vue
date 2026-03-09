<template>
  <div v-if="loading" class="state-wrap soft-card">正在加载...</div>
  <div v-else-if="error" class="state-wrap soft-card state-error">
    <p>{{ error }}</p>
    <el-button size="small" @click="$emit('retry')">重试</el-button>
  </div>
  <div v-else-if="empty" class="state-wrap soft-card">{{ emptyText }}</div>
  <slot v-else />
</template>

<script setup lang="ts">
defineProps<{
  loading: boolean;
  error: string | null;
  empty?: boolean;
  emptyText?: string;
}>();

defineEmits<{
  (e: "retry"): void;
}>();
</script>

<style scoped>
.state-wrap {
  padding: 24px;
  text-align: center;
  color: var(--text-sub);
}

.state-error {
  color: #d9534f;
}
</style>
