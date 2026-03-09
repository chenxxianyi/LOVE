<template>
  <el-dialog
    v-model="visible"
    title="设置你的账号"
    width="min(480px, 94vw)"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    class="account-setup-dialog"
  >
    <div class="setup-intro">
      <div class="setup-icon">🔑</div>
      <p class="setup-title">保存你的账号</p>
      <p class="setup-desc">
        你现在使用的是临时账号，换设备后将无法找回。<br />
        设置账号密码后，随时可以重新登录。
      </p>
    </div>

    <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
      <el-form-item label="账号名" prop="account">
        <el-input
          v-model="form.account"
          placeholder="设置唯一的账号名（字母/数字）"
          maxlength="32"
          prefix-icon="User"
        />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="至少 6 位"
          maxlength="32"
          show-password
          prefix-icon="Lock"
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="再次输入密码"
          maxlength="32"
          show-password
          prefix-icon="Lock"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button class="skip-btn" text @click="handleSkip">稍后再说</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确认设置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { authApi } from "../../api/auth";
import { useAuthStore } from "../../stores/useAuthStore";

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits<{
  (e: "update:modelValue", val: boolean): void;
  (e: "done"): void;
  (e: "skip"): void;
}>();

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

import { computed } from "vue";
const authStore = useAuthStore();
const formRef = ref<FormInstance>();
const loading = ref(false);

const form = reactive({
  account: "",
  password: "",
  confirmPassword: "",
});

const rules: FormRules = {
  account: [
    { required: true, message: "请输入账号名", trigger: "blur" },
    { min: 2, max: 32, message: "账号名 2-32 位", trigger: "blur" },
    {
      pattern: /^[a-zA-Z0-9_]+$/,
      message: "只能包含字母、数字和下划线",
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "请设置密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请再次输入密码", trigger: "blur" },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

async function handleSubmit() {
  if (!formRef.value) return;
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    const session = await authApi.setupAccount({
      account: form.account.trim(),
      password: form.password,
    });
    authStore.setSession(session);
    ElMessage.success("账号设置成功！下次可以用账号密码登录");
    emit("done");
    visible.value = false;
  } catch (e: any) {
    const msg = e?.response?.data?.detail || "设置失败，请重试";
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
}

function handleSkip() {
  ElMessage.info("你可以之后在设置中完善账号信息");
  emit("skip");
  visible.value = false;
}
</script>

<style scoped>
.account-setup-dialog :deep(.el-dialog__header) {
  padding-bottom: 0;
}

.setup-intro {
  text-align: center;
  margin-bottom: 20px;
}

.setup-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.setup-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 6px;
}

.setup-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
}

.skip-btn {
  color: var(--el-text-color-secondary);
}
</style>
