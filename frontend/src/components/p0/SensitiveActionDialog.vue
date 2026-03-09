<template>
  <el-dialog :model-value="modelValue" :title="title" width="420px" @close="$emit('update:modelValue', false)">
    <p class="content">{{ content }}</p>
    <el-input
      v-if="requireVerifyToken"
      v-model="verifyTokenLocal"
      placeholder="请输入验证口令或验证码"
      clearable
    />
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="danger" :loading="loading" @click="onConfirm">
        {{ confirmText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    modelValue: boolean;
    title?: string;
    content?: string;
    confirmText?: string;
    loading?: boolean;
    requireVerifyToken?: boolean;
  }>(),
  {
    title: "请确认此操作",
    content: "执行后不可直接撤销，是否继续？",
    confirmText: "确认执行",
    loading: false,
    requireVerifyToken: false,
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "confirm", verifyToken?: string): void;
}>();

const verifyTokenLocal = ref("");

watch(
  () => props.modelValue,
  (open) => {
    if (open) verifyTokenLocal.value = "";
  }
);

function onConfirm() {
  emit("confirm", verifyTokenLocal.value || undefined);
}
</script>

<style scoped>
.content {
  margin: 0 0 16px;
  color: var(--text-sub);
}
</style>
