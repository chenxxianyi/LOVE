<template>
  <section class="soft-card card">
    <h3>邀请码</h3>
    <div class="code">{{ code || "--" }}</div>
    <p class="hint">有效期至：{{ expiresAt || "--" }}</p>
    <el-input :model-value="link" readonly />
    <div class="actions">
      <el-button size="small" @click="$emit('copy-code')">复制邀请码</el-button>
      <el-button size="small" @click="$emit('copy-link')">复制邀请链接</el-button>
      <el-button size="small" @click="$emit('refresh')">重新生成</el-button>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  code: string;
  link: string;
  expiresAt: string;
}>();

defineEmits<{
  (e: "copy-code"): void;
  (e: "copy-link"): void;
  (e: "refresh"): void;
}>();
</script>

<style scoped>
.card {
  padding: 20px;
}

.code {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 2px;
  margin: 6px 0;
}

.hint {
  margin: 0 0 12px;
  color: var(--text-sub);
  font-size: 13px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
</style>
