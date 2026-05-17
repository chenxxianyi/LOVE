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

      <el-dropdown trigger="click" @command="handleCommand" class="user-dropdown">
        <div class="user-entry" title="账号管理">
          <el-avatar :size="32" :src="authStore.user?.avatar || defaultAvatar" class="user-avatar" />
          <span class="user-name">{{ authStore.user?.nickname || '我' }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>个人中心
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <button class="theme-toggle" :title="themeHint" @click="cycleTheme">
        {{ themeIcon }}
      </button>

      <el-button type="primary" round @click="store.showAddMomentDialog = true" class="add-btn">
        新增回忆
      </el-button>
    </div>

    <UserProfileDialog v-model="showProfile" />
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useLoveStore } from "../stores/useLoveStore";
import { useAuthStore } from "../stores/useAuthStore";
import { useThemeStore, type ThemeMode } from "../stores/useThemeStore";
import UserProfileDialog from "./profile/UserProfileDialog.vue";
import { ArrowDown, User, SwitchButton } from "@element-plus/icons-vue";

const store = useLoveStore();
const authStore = useAuthStore();
const themeStore = useThemeStore();
const router = useRouter();

const showProfile = ref(false);
const defaultAvatar = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";

/* ---- 主题切换 ---- */
const themeOrder: ThemeMode[] = ["warm", "glass", "glass-dark"];
const themeLabels: Record<ThemeMode, string> = {
  warm: "暖阳",
  glass: "冰璃",
  "glass-dark": "暗璃",
};

const themeIcon = computed(() => {
  if (themeStore.mode === "glass") return "🧊";
  if (themeStore.mode === "glass-dark") return "🌙";
  return "☀";
});

const themeHint = computed(() => {
  const next = themeOrder[(themeOrder.indexOf(themeStore.mode) + 1) % themeOrder.length];
  return `当前: ${themeLabels[themeStore.mode]} · 点击切换为 ${themeLabels[next]}`;
});

function cycleTheme() {
  const idx = themeOrder.indexOf(themeStore.mode);
  const next = themeOrder[(idx + 1) % themeOrder.length];
  themeStore.setTheme(next);
}

function handleCommand(command: string) {
  if (command === "profile") {
    showProfile.value = true;
  } else if (command === "logout") {
    logout();
  }
}

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

.user-dropdown {
  flex-shrink: 0;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 20px;
  transition: all 0.3s;
  flex-shrink: 0;
  border: 1px solid transparent;
}

.user-entry:hover {
  background: rgba(255, 192, 203, 0.15);
  border-color: rgba(255, 192, 203, 0.4);
}

.user-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.user-name {
  font-size: 14px;
  color: var(--text-main);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 主题切换按钮 */
.theme-toggle {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid var(--line-soft);
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
  line-height: 1;
}

.theme-toggle:hover {
  background: var(--accent-light, rgba(255, 140, 160, 0.15));
  border-color: var(--accent, #ff8ca0);
  transform: scale(1.08);
}

[data-theme="glass"] .theme-toggle,
[data-theme="glass-dark"] .theme-toggle {
  background: var(--glass-bg-subtle);
  border-color: var(--glass-border);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

[data-theme="glass"] .theme-toggle:hover,
[data-theme="glass-dark"] .theme-toggle:hover {
  background: var(--glass-bg);
  border-color: var(--glass-border-hover);
}

/* Glass 主题下的导航链接适配 */
[data-theme="glass"] .link:hover,
[data-theme="glass-dark"] .link:hover {
  color: var(--text-main);
  background: var(--glass-bg-subtle);
}

[data-theme="glass"] .active,
[data-theme="glass-dark"] .active {
  color: var(--text-main);
  background: var(--accent-light);
  font-weight: 500;
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
