<template>
  <!-- 桌面端：左侧图标栏 -->
  <aside
    class="side-nav"
    aria-label="主导航侧边栏"
  >
    <!-- 顶部品牌 -->
    <RouterLink to="/" class="brand-block" aria-label="首页">
      <svg
        class="brand-icon-svg"
        width="22" height="22"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
      </svg>
      <span class="brand-text title-font">LOVE</span>
    </RouterLink>

    <!-- 主导航 -->
    <nav class="nav-items" aria-label="主导航">
      <RouterLink
        v-for="item in mainNav"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: isActive(item.to) }"
        :aria-label="item.label"
        :title="item.label"
      >
        <el-icon :size="20" class="nav-icon"><component :is="item.icon" /></el-icon>
        <span class="nav-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="spacer" />

    <!-- 辅助导航 -->
    <nav class="nav-items sub" aria-label="辅助导航">
      <RouterLink
        v-for="item in subNav"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: isActive(item.to) }"
        :aria-label="item.label"
        :title="item.label"
      >
        <el-icon :size="18" class="nav-icon"><component :is="item.icon" /></el-icon>
        <span class="nav-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <!-- 底部操作区 -->
    <div class="bottom-actions">
      <!-- 新建回忆 -->
      <button
        class="action-btn add-btn"
        aria-label="新增回忆"
        title="新增回忆"
        @click="store.showAddMomentDialog = true"
      >
        <el-icon :size="20" class="btn-icon"><CirclePlusFilled /></el-icon>
        <span class="btn-label">新增回忆</span>
      </button>

      <!-- 主题切换 -->
      <button
        class="action-btn theme-btn"
        :aria-label="themeHint"
        :title="themeHint"
        @click="cycleTheme"
      >
        <el-icon :size="20" class="btn-icon"><component :is="themeIconComponent" /></el-icon>
        <span v-show="isExpanded" class="btn-label">{{ themeLabel }}</span>
      </button>

      <!-- 用户头像 -->
      <el-dropdown trigger="click" @command="handleCommand" class="user-dropdown">
        <div class="action-btn user-btn" title="账号管理" aria-label="账号管理">
          <el-avatar
            :size="28"
            :src="authStore.user?.avatar || defaultAvatar"
            class="user-avatar"
          />
          <span class="btn-label user-name">
            {{ authStore.user?.nickname || '我' }}
          </span>
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
    </div>

    <UserProfileDialog v-model="showProfile" />
  </aside>

  <el-drawer
    v-model="showMobileMore"
    direction="btt"
    size="72%"
    :with-header="false"
    class="mobile-more-drawer"
  >
    <div class="mobile-more-panel">
      <div class="mobile-more-head">
        <div>
          <h3>更多功能</h3>
          <p>完整入口与账户操作</p>
        </div>
        <button class="mobile-more-close" type="button" @click="showMobileMore = false">
          关闭
        </button>
      </div>

      <div class="mobile-more-links">
        <RouterLink
          v-for="item in mobileMoreNav"
          :key="item.to"
          :to="item.to"
          class="mobile-more-link"
          @click="showMobileMore = false"
        >
          <el-icon :size="18" class="mobile-more-icon"><component :is="item.icon" /></el-icon>
          <div class="mobile-more-text">
            <span>{{ item.label }}</span>
            <small>{{ item.hint }}</small>
          </div>
        </RouterLink>
      </div>

      <div class="mobile-more-actions">
        <button class="mobile-more-action" type="button" @click="cycleTheme">
          切换主题
        </button>
        <button class="mobile-more-action" type="button" @click="openProfile">
          个人中心
        </button>
        <button class="mobile-more-action danger" type="button" @click="handleLogout">
          退出登录
        </button>
      </div>
    </div>
  </el-drawer>

  <!-- 移动端：底部 Tab Bar -->
  <nav class="mobile-tabs" aria-label="移动端导航">
    <RouterLink
      v-for="item in mobileTabsTop"
      :key="item.to"
      :to="item.to"
      class="tab-item"
      :class="{ active: isActive(item.to) }"
      :aria-label="item.label"
    >
      <el-icon :size="22" class="tab-icon"><component :is="item.icon" /></el-icon>
      <span class="tab-label">{{ item.label }}</span>
    </RouterLink>
    <button
      class="tab-item tab-add"
      aria-label="新增回忆"
      @click="store.showAddMomentDialog = true"
    >
      <el-icon :size="24" class="add-icon"><Plus /></el-icon>
    </button>
    <RouterLink
      v-for="item in mobileTabsBottom"
      :key="item.to"
      :to="item.to"
      class="tab-item"
      :class="{ active: isActive(item.to) }"
      :aria-label="item.label"
    >
      <el-icon :size="22" class="tab-icon"><component :is="item.icon" /></el-icon>
      <span class="tab-label">{{ item.label }}</span>
    </RouterLink>
    <button
      class="tab-item tab-more"
      type="button"
      aria-label="更多功能"
      @click="showMobileMore = true"
    >
      <el-icon :size="22" class="tab-icon"><MoreFilled /></el-icon>
      <span class="tab-label">更多</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, type Component } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useLoveStore } from "../stores/useLoveStore";
import { useAuthStore } from "../stores/useAuthStore";
import { useThemeStore, type ThemeMode } from "../stores/useThemeStore";
import UserProfileDialog from "./profile/UserProfileDialog.vue";
import {
  User,
  SwitchButton,
  HomeFilled,
  Clock,
  MapLocation,
  Star,
  Box,
  Present,
  DataAnalysis,
  SetUp,
  QuestionFilled,
  AlarmClock,
  Bell,
  Setting,
  CirclePlusFilled,
  MoreFilled,
  Sunny,
  Moon,
  MagicStick,
  Plus,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const store = useLoveStore();
const authStore = useAuthStore();
const themeStore = useThemeStore();

const showProfile = ref(false);
const showMobileMore = ref(false);
const defaultAvatar =
  "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";

/* ---- 导航项 (图标组件替代 emoji) ---- */
type NavItem = { icon: Component; label: string; to: string };

const mainNav: NavItem[] = [
  { icon: HomeFilled,    label: "首页",   to: "/" },
  { icon: Clock,         label: "时间线", to: "/timeline" },
  { icon: MapLocation,   label: "地图",   to: "/map" },
  { icon: Star,          label: "愿望",   to: "/bucket" },
  { icon: Box,           label: "胶囊",   to: "/capsule" },
  { icon: Present,       label: "纪念日", to: "/anniversary" },
  { icon: DataAnalysis,  label: "报告",   to: "/report" },
  { icon: SetUp,         label: "转盘",   to: "/wheel" },
  { icon: QuestionFilled,label: "问答",   to: "/question" },
];

const subNav: NavItem[] = [
  { icon: AlarmClock, label: "提醒", to: "/reminders" },
  { icon: Bell,       label: "消息", to: "/notifications" },
  { icon: Setting,    label: "安全", to: "/settings/security" },
];

const mobileTabsTop: NavItem[] = [
  { icon: HomeFilled, label: "首页", to: "/" },
  { icon: Clock,      label: "时间", to: "/timeline" },
];

const mobileTabsBottom: NavItem[] = [
  { icon: Star,       label: "愿望", to: "/bucket" },
];

const mobileMoreNav: Array<NavItem & { hint: string }> = [
  { icon: MapLocation,   label: "地图",   to: "/map", hint: "足迹与地点" },
  { icon: Box,           label: "胶囊",   to: "/capsule", hint: "时光封存" },
  { icon: Present,       label: "纪念日", to: "/anniversary", hint: "特别日期" },
  { icon: DataAnalysis,  label: "报告",   to: "/report", hint: "年度回顾" },
  { icon: SetUp,         label: "转盘",   to: "/wheel", hint: "随机决定" },
  { icon: QuestionFilled,label: "问答",   to: "/question", hint: "每日一问" },
  { icon: AlarmClock,    label: "提醒",   to: "/reminders", hint: "待办提醒" },
  { icon: Bell,          label: "消息",   to: "/notifications", hint: "消息中心" },
  { icon: Setting,       label: "安全",   to: "/settings/security", hint: "账号与隐私" },
];

function isActive(path: string): boolean {
  if (path === "/") return route.path === "/";
  return route.path.startsWith(path);
}

/* ---- 主题切换 (SVG 图标替代 emoji) ---- */
const themeOrder: ThemeMode[] = ["warm", "glass", "glass-dark"];
const themeLabels: Record<ThemeMode, string> = {
  warm: "暖阳",
  glass: "冰璃",
  "glass-dark": "暗璃",
};

const themeIconComponent = computed(() => {
  if (themeStore.mode === "glass") return MagicStick;
  if (themeStore.mode === "glass-dark") return Moon;
  return Sunny;
});

const themeLabel = computed(() => themeLabels[themeStore.mode]);

const themeHint = computed(() => {
  const next =
    themeOrder[(themeOrder.indexOf(themeStore.mode) + 1) % themeOrder.length];
  return `当前: ${themeLabels[themeStore.mode]} · 切换 ${themeLabels[next]}`;
});

function cycleTheme() {
  const idx = themeOrder.indexOf(themeStore.mode);
  const next = themeOrder[(idx + 1) % themeOrder.length];
  themeStore.setTheme(next);
}

function openProfile() {
  showMobileMore.value = false;
  showProfile.value = true;
}

function handleLogout() {
  authStore.logout();
  router.push("/auth");
}

/* ---- 用户操作 ---- */
function handleCommand(command: string) {
  if (command === "profile") {
    openProfile();
  } else if (command === "logout") {
    handleLogout();
  }
}
</script>

<style scoped>
/* ============================================
   SideNav — 桌面端左侧图标栏
   ============================================ */
.side-nav {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 40;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 200px;
  height: 100vh;
  padding: 16px 8px;
  background: var(--glass-bg-strong, rgba(255, 255, 255, 0.35));
  border-right: 1px solid var(--glass-border, rgba(255, 255, 255, 0.14));
  backdrop-filter: blur(var(--glass-blur-nav, 32px));
  -webkit-backdrop-filter: blur(var(--glass-blur-nav, 32px));
  box-shadow: var(--glass-shadow-sm);
  overflow: hidden;
  user-select: none;
}

/* ── 品牌 ── */
.brand-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  margin-bottom: 12px;
  text-decoration: none;
  color: var(--text-main);
  width: 100%;
  flex-shrink: 0;
}

.brand-icon-svg {
  flex-shrink: 0;
  color: var(--accent, #FFB3C6);
}

.brand-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  opacity: 1;
}

/* ── 导航列表 ── */
.nav-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  flex-shrink: 0;
}

.nav-items.sub {
  margin-top: 6px;
  opacity: 0.7;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-sub);
  transition: all 0.2s ease;
  width: 100%;
  position: relative;
}

.nav-item:hover {
  color: var(--text-main);
  background: var(--accent-light, rgba(255, 179, 198, 0.15));
}

.nav-item.active {
  color: var(--text-main);
  background: var(--accent-light, rgba(255, 179, 198, 0.25));
  font-weight: 500;
}

.nav-item.active::before {
  content: "";
  position: absolute;
  left: 2px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  border-radius: 3px;
  background: var(--accent, #FFB3C6);
}

.nav-icon {
  flex-shrink: 0;
  width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  font-size: 14px;
  white-space: nowrap;
  opacity: 1;
}

/* ── 弹性间隔 ── */
.spacer {
  flex: 1;
  min-height: 12px;
}

/* ── 底部操作 ── */
.bottom-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  flex-shrink: 0;
  padding-top: 8px;
  border-top: 1px solid var(--glass-border, rgba(255, 255, 255, 0.10));
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--text-sub);
  cursor: pointer;
  width: 100%;
  transition: all 0.2s ease;
  font-size: 14px;
}

.action-btn:hover {
  background: var(--accent-light, rgba(255, 179, 198, 0.15));
  color: var(--text-main);
}

.btn-icon {
  flex-shrink: 0;
  width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-label {
  font-size: 13px;
  white-space: nowrap;
  opacity: 1;
}

.add-btn .btn-icon {
  color: var(--accent, #FFB3C6);
}

/* ── 用户按钮 ── */
.user-btn {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  border: 2px solid var(--accent-light, rgba(255, 179, 198, 0.3));
  flex-shrink: 0;
}

.user-name {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ============================================
   Mobile — 底部 Tab Bar
   ============================================ */
.mobile-tabs {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: var(--glass-bg-strong, rgba(255, 255, 255, 0.85));
  border-top: 1px solid var(--glass-border, rgba(0, 0, 0, 0.06));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 6px 8px env(safe-area-inset-bottom, 8px);
  justify-content: space-around;
  align-items: center;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 10px;
  border-radius: 10px;
  text-decoration: none;
  color: var(--text-muted);
  transition: all 0.2s ease;
  min-width: 48px;
}

.tab-item.active {
  color: var(--accent, #FFB3C6);
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-label {
  font-size: 10px;
}

.tab-add {
  background: var(--accent, #FFB3C6);
  color: #fff;
  border: none;
  cursor: pointer;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -18px;
  box-shadow: 0 4px 16px rgba(255, 179, 198, 0.4);
}

.tab-add .add-icon {
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-more {
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
}

/* ============================================
   Mobile More Drawer
   ============================================ */
.mobile-more-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px 16px 20px;
}

.mobile-more-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mobile-more-head h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-main);
}

.mobile-more-head p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-sub);
}

.mobile-more-close {
  border: none;
  background: transparent;
  color: var(--text-sub);
  cursor: pointer;
  padding: 4px 0;
}

.mobile-more-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 48vh;
  overflow: auto;
}

.mobile-more-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  text-decoration: none;
  color: var(--text-main);
  background: var(--glass-bg-subtle, rgba(255, 255, 255, 0.12));
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.14));
}

.mobile-more-icon {
  flex-shrink: 0;
  color: var(--accent, #FFB3C6);
}

.mobile-more-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mobile-more-text span {
  font-size: 14px;
  font-weight: 500;
}

.mobile-more-text small {
  font-size: 12px;
  color: var(--text-sub);
}

.mobile-more-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mobile-more-action {
  flex: 1;
  min-width: 100px;
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.14));
  background: var(--glass-bg-subtle, rgba(255, 255, 255, 0.12));
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
}

.mobile-more-action.danger {
  color: #c6455f;
}

/* ── 键盘焦点 (Accessibility) ── */
.nav-item:focus-visible,
.action-btn:focus-visible,
.tab-item:focus-visible {
  outline: 2px solid var(--accent, #FFB3C6);
  outline-offset: 2px;
}

@media (max-width: 768px) {
  .side-nav {
    display: none;
  }

  .mobile-tabs {
    display: flex;
  }
}
</style>
