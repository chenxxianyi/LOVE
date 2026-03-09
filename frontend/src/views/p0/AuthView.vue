<template>
  <section class="p0-page">
    <div class="auth-card soft-card">
      <h1 class="title-font">账号登录</h1>
      <p class="sub">登录后继续创建或加入你们的专属空间</p>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" label-position="top">
            <el-form-item label="账号">
              <el-input v-model="loginForm.account" placeholder="请输入手机号或邮箱" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input
                v-model="loginForm.password"
                type="password"
                show-password
                placeholder="请输入密码"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
          </el-form>
          <div class="actions">
            <el-button type="primary" :loading="authStore.loading" @click="handleLogin">
              登录
            </el-button>
            <el-button link @click="router.push('/auth/forgot')">忘记密码</el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" label-position="top">
            <el-form-item label="账号">
              <el-input v-model="registerForm.account" placeholder="请输入手机号或邮箱" />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="registerForm.nickname" placeholder="请输入昵称（可选）" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input
                v-model="registerForm.password"
                type="password"
                show-password
                placeholder="请输入8-20位密码"
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="registerForm.agreePolicy">
                我已阅读并同意《用户协议》《隐私政策》
              </el-checkbox>
            </el-form-item>
          </el-form>
          <div class="actions">
            <el-button
              type="primary"
              :loading="authStore.loading"
              :disabled="!registerForm.agreePolicy"
              @click="handleRegister"
            >
              注册
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="footer-link">
        <el-button type="primary" plain @click="handleJoinByInvite">
          使用邀请码加入
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../../stores/useAuthStore";
import { useCoupleStore } from "../../stores/useCoupleStore";
import type { AuthSession } from "../../types/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const coupleStore = useCoupleStore();

const DEV_ACCOUNT = "dev@local";
const DEV_PASSWORD = "Dev123456!";
const enableAuthMock =
  import.meta.env.DEV || import.meta.env.VITE_ENABLE_AUTH_MOCK === "true";

const activeTab = ref<"login" | "register">("login");
const loginForm = reactive({
  account: "",
  password: "",
});
const registerForm = reactive({
  account: "",
  nickname: "",
  password: "",
  agreePolicy: false,
});

async function afterAuth(session: AuthSession) {
  if (session.pair_status === "paired") {
    coupleStore.setPairState("paired");
    router.push("/");
    return;
  }

  const nextPath = typeof route.query.next === "string" ? route.query.next : "";
  if (nextPath === "/couple/join") {
    router.push("/couple/join");
    return;
  }

  try {
    await coupleStore.fetchSpace();
  } catch {
    // no-op: fallback to create page
  }

  if (coupleStore.isPaired) {
    router.push("/");
  } else {
    router.push("/couple/create");
  }
}

function handleJoinByInvite() {
  router.push("/couple/join");
}

function tryDevMockLogin(): boolean {
  if (
    !enableAuthMock ||
    loginForm.account.trim() !== DEV_ACCOUNT ||
    loginForm.password !== DEV_PASSWORD
  ) {
    return false;
  }

  authStore.setSession({
    user: {
      id: "dev-1",
      account: DEV_ACCOUNT,
      nickname: "开发者",
    },
    access_token: "dev-token",
    refresh_token: "dev-refresh-token",
    pair_status: "paired",
  });

  coupleStore.setPairState("paired", {
    id: "space-dev",
    space_name: "开发测试空间",
    start_date: "2024-04-21",
    privacy_level: "couple_only",
    members: [
      { id: "dev-1", nickname: "开发者" },
      { id: "dev-2", nickname: "测试搭子" },
    ],
    pair_status: "paired",
  });

  ElMessage.success("开发模式登录成功");
  router.push("/");
  return true;
}

async function handleLogin() {
  if (!loginForm.account || !loginForm.password) {
    ElMessage.warning("请填写账号和密码");
    return;
  }

  try {
    const session = await authStore.login({
      account: loginForm.account.trim(),
      password: loginForm.password,
    });
    ElMessage.success("欢迎回来");
    await afterAuth(session);
  } catch (e: any) {
    if (tryDevMockLogin()) return;
    ElMessage.error(e?.response?.data?.detail || "账号或密码错误");
  }
}

async function handleRegister() {
  if (!registerForm.account || !registerForm.password) {
    ElMessage.warning("请填写账号和密码");
    return;
  }
  if (registerForm.password.length < 8) {
    ElMessage.warning("密码至少 8 位");
    return;
  }
  if (!registerForm.agreePolicy) {
    ElMessage.warning("请先同意协议");
    return;
  }

  try {
    const session = await authStore.register({
      account: registerForm.account.trim(),
      password: registerForm.password,
      nickname: registerForm.nickname || undefined,
    });
    ElMessage.success("注册成功");
    await afterAuth(session);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "注册失败");
  }
}
</script>

<style scoped>
.p0-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card {
  width: min(520px, 94vw);
  padding: 24px;
}

h1 {
  margin: 0;
  font-size: 40px;
}

.sub {
  color: var(--text-sub);
  margin: 4px 0 14px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-link {
  margin-top: 16px;
}
</style>
