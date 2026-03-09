<template>
  <div class="login-page">
    <div class="login-card soft-card fade-up">
      <div class="icon">🔒</div>
      <h2>私人恋爱档案馆</h2>
      <p>请输入我们的专属暗号</p>
      
      <div class="input-wrapper">
        <el-input
          v-model="password"
          type="password"
          placeholder="暗号是..."
          show-password
          @keyup.enter="handleLogin"
        />
      </div>
      
      <el-button type="primary" round size="large" class="login-btn" @click="handleLogin">
        解锁回忆
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const router = useRouter();
const store = useLoveStore();
const password = ref("");

// Hardcoded password for simplicity - in production this should be validated by backend
const SECRET_CODE = "5201314"; 

const handleLogin = () => {
  if (password.value === SECRET_CODE) {
    store.login();
    ElMessage.success("欢迎回来！");
    router.push("/");
  } else {
    ElMessage.error("暗号错误，是不是把纪念日忘了？😠");
    password.value = "";
  }
};
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff0f3 0%, #fff 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

.icon {
  font-size: 48px;
  margin-bottom: 20px;
}

h2 {
  margin: 0 0 10px;
  color: var(--text-main);
  font-family: "Ma Shan Zheng", cursive;
}

p {
  color: var(--text-sub);
  margin-bottom: 30px;
}

.input-wrapper {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  font-weight: bold;
  letter-spacing: 2px;
}
</style>
