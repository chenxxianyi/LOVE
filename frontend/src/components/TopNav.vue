<template>
  <header class="nav-wrap soft-card">
    <div class="left">
      <RouterLink to="/" class="brand">
        <span class="heart">❤</span>
        <span class="title-font">LOVE Memory</span>
      </RouterLink>
      <span class="motto">{{ store.todayMood }}</span>
    </div>

    <div class="right-wrapper">
      <nav class="right">
        <RouterLink to="/" class="link" active-class="active">首页</RouterLink>
        <RouterLink to="/timeline" class="link" active-class="active">时间线</RouterLink>
        <RouterLink to="/map" class="link" active-class="active">地图</RouterLink>
        <RouterLink to="/bucket" class="link" active-class="active">愿望</RouterLink>
        <RouterLink to="/capsule" class="link" active-class="active">胶囊</RouterLink>
        <RouterLink to="/anniversary" class="link" active-class="active">纪念日</RouterLink>
        <RouterLink to="/report" class="link" active-class="active">报告</RouterLink>
        <RouterLink to="/wheel" class="link" active-class="active">转盘</RouterLink>
        <RouterLink to="/question" class="link" active-class="active">问答</RouterLink>
        <RouterLink to="/reminders" class="link" active-class="active">提醒</RouterLink>
        <RouterLink to="/notifications" class="link" active-class="active">消息</RouterLink>
        <RouterLink to="/settings/security" class="link" active-class="active">安全</RouterLink>
      </nav>

      <el-button type="primary" round @click="store.showAddMomentDialog = true" class="add-btn">
        新增回忆
      </el-button>
      <el-button round @click="logout">退出</el-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useLoveStore } from "../stores/useLoveStore";
import { useAuthStore } from "../stores/useAuthStore";

const store = useLoveStore();
const authStore = useAuthStore();
const router = useRouter();

function logout() {
  authStore.logout();
  router.push("/auth");
}
</script>

<style scoped>
.nav-wrap {
  position: sticky;
  top: 12px;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 14px auto 0;
  width: min(1200px, 92vw);
  padding: 14px 18px;
  backdrop-filter: blur(4px);
}

.left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-main);
  font-size: 24px;
  font-weight: 600;
}

.heart {
  color: var(--pink-deep);
  font-size: 18px;
}

.motto {
  color: var(--text-sub);
  font-size: 13px;
  display: block;
}

.right-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.right {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}

.right::-webkit-scrollbar {
  display: none;
}

.link {
  padding: 6px 10px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-sub);
  white-space: nowrap;
  font-size: 14px;
}

.link:hover {
  color: var(--text-main);
  background: #fff2f6;
}

.active {
  color: var(--text-main);
  background: #ffe9ef;
  font-weight: 500;
}

.add-btn {
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .motto {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-wrap {
    width: 94vw;
    padding: 12px 14px;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .right-wrapper {
    width: 100%;
    justify-content: space-between;
  }

  .right {
    flex: 1;
    margin-right: 10px;
  }
}
</style>
