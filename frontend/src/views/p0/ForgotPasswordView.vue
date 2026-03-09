<template>
  <section class="p0-page">
    <div class="card soft-card">
      <h2 class="title-font">重置密码</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="账号">
          <el-input v-model="form.account" placeholder="请输入手机号或邮箱" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="line">
            <el-input v-model="form.code" placeholder="请输入验证码" />
            <el-button :disabled="countdown > 0" @click="sendCode">
              {{ countdown > 0 ? `${countdown}s` : "发送验证码" }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="form.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <div class="line">
        <el-button @click="router.push('/auth')">返回登录</el-button>
        <el-button type="primary" :loading="loading" @click="resetPassword">重置密码</el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../../stores/useAuthStore";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const countdown = ref(0);
let timer: number | null = null;

const form = reactive({
  account: "",
  code: "",
  new_password: "",
});

function startCountdown() {
  countdown.value = 60;
  timer = window.setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0 && timer) {
      window.clearInterval(timer);
      timer = null;
    }
  }, 1000);
}

async function sendCode() {
  if (!form.account) {
    ElMessage.warning("请输入账号");
    return;
  }
  try {
    await authStore.sendResetCode({ account: form.account.trim() });
    ElMessage.success("验证码已发送");
    startCountdown();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "发送失败");
  }
}

async function resetPassword() {
  if (!form.account || !form.code || !form.new_password) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  loading.value = true;
  try {
    await authStore.resetPassword({
      account: form.account.trim(),
      code: form.code.trim(),
      new_password: form.new_password,
    });
    ElMessage.success("密码已重置，请重新登录");
    router.push("/auth");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "重置失败");
  } finally {
    loading.value = false;
  }
}

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<style scoped>
.p0-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  width: min(520px, 94vw);
  padding: 24px;
}

.line {
  display: flex;
  gap: 8px;
}
</style>
