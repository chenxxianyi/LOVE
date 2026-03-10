import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/useAuthStore";
import { useCoupleStore } from "../stores/useCoupleStore";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/auth",
      name: "auth",
      component: () => import("../views/p0/AuthView.vue"),
      meta: { public: true, hideLegacyShell: true },
    },
    {
      path: "/auth/forgot",
      name: "forgot-password",
      component: () => import("../views/p0/ForgotPasswordView.vue"),
      meta: { public: true, hideLegacyShell: true },
    },
    {
      path: "/login",
      redirect: "/auth",
    },
    {
      path: "/couple/create",
      name: "couple-create",
      component: () => import("../views/p0/CoupleCreateView.vue"),
      meta: { prePairOnly: true, hideLegacyShell: true },
    },
    {
      path: "/couple/invite",
      name: "couple-invite",
      component: () => import("../views/p0/CoupleInviteView.vue"),
      meta: { prePairOnly: true, hideLegacyShell: true },
    },
    {
      path: "/couple/join",
      name: "couple-join",
      component: () => import("../views/p0/CoupleJoinView.vue"),
      meta: { prePairOnly: true, hideLegacyShell: true },
    },
    {
      path: "/couple/success",
      name: "couple-success",
      component: () => import("../views/p0/CoupleSuccessView.vue"),
      meta: { public: true, hideLegacyShell: true },
    },
    {
      path: "/",
      name: "home",
      component: HomeView,
      meta: { requiresPair: true },
    },
    {
      path: "/timeline",
      name: "timeline",
      component: () => import("../utils/device").then(m => m.isMobile() ? import("../views/mobile/TimelineView.vue") : import("../views/TimelineView.vue")),
      meta: { requiresPair: true },
    },
    {
      path: "/map",
      name: "map",
      component: () => import("../views/MapView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/bucket",
      name: "bucket",
      component: () => import("../views/BucketListView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/capsule",
      name: "capsule",
      component: () => import("../views/TimeCapsuleView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/anniversary",
      name: "anniversary",
      component: () => import("../views/AnniversaryView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/report",
      name: "report",
      component: () => import("../views/ReportView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/wheel",
      name: "wheel",
      component: () => import("../utils/device").then(m => m.isMobile() ? import("../views/mobile/LoveWheelView.vue") : import("../views/LoveWheelView.vue")),
      meta: { requiresPair: true },
    },
    {
      path: "/question",
      name: "question",
      component: () => import("../views/DailyQuestionView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/settings/security",
      name: "security-settings",
      component: () => import("../views/p0/SecuritySettingsView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/settings/security/devices",
      name: "device-management",
      component: () => import("../views/p0/DeviceManagementView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/settings/security/logs",
      name: "operation-logs",
      component: () => import("../views/p0/OperationLogsView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/settings/backup",
      name: "backup-center",
      component: () => import("../views/p0/BackupCenterView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/settings/backup/restore",
      name: "backup-restore",
      component: () => import("../views/p0/BackupRestoreView.vue"),
      meta: { requiresPair: true, sensitive: true },
    },
    {
      path: "/settings/export",
      name: "export-center",
      component: () => import("../views/p0/ExportCenterView.vue"),
      meta: { requiresPair: true, sensitive: true },
    },
    {
      path: "/reminders",
      name: "reminders",
      component: () => import("../views/p0/ReminderCenterView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/reminders/edit/:id?",
      name: "reminder-edit",
      component: () => import("../views/p0/ReminderEditView.vue"),
      meta: { requiresPair: true },
    },
    {
      path: "/notifications",
      name: "notifications",
      component: () => import("../views/p0/NotificationsView.vue"),
      meta: { requiresPair: true },
    },
  ],
});

export default router;

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const coupleStore = useCoupleStore();

  authStore.hydrateFromStorage();

  const isPublic = Boolean(to.meta.public);
  const requiresPair = Boolean(to.meta.requiresPair);
  const prePairOnly = Boolean(to.meta.prePairOnly);
  const isSensitive = Boolean(to.meta.sensitive);

  // 兼容旧版暗号密码登录（useLoveStore.login() 会设置 localStorage.isLoggedIn）
  const legacyLoggedIn = localStorage.getItem("isLoggedIn") === "true";
  // 未登录状态：既没有 JWT token，也没有旧版暗号登录
  const isAuthenticated = authStore.isAuthenticated || legacyLoggedIn;

  if (!isAuthenticated && !isPublic) {
    // 如果是预配对页（couple/join, couple/create），允许通过（邀请码就是认证）
    if (prePairOnly) {
      next();
      return;
    }
    next("/auth");
    return;
  }

  if (isAuthenticated && (to.path === "/auth" || to.path === "/auth/forgot")) {
    next(coupleStore.isPaired ? "/" : "/");
    return;
  }

  if (isAuthenticated && prePairOnly && coupleStore.isPaired) {
    next("/");
    return;
  }

  if (isAuthenticated && !coupleStore.isPaired && requiresPair) {
    // 旧版暗号登录不走配对流程，直接放行
    if (legacyLoggedIn && !authStore.isAuthenticated) {
      next();
      return;
    }
    next("/couple/create");
    return;
  }

  if (isAuthenticated && isSensitive && !coupleStore.hasSensitiveAccess) {
    next("/settings/security");
    return;
  }

  next();
});

