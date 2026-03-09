import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { authApi } from "../api/auth";
import { tokenStorage } from "../api/client";
import { useCoupleStore } from "./useCoupleStore";
import type {
  AuthSession,
  ForgotResetPayload,
  ForgotSendCodePayload,
  LoginPayload,
  RegisterPayload,
  UserProfile,
} from "../types/auth";

const USER_KEY = "love_user";
const LEGACY_LOGIN_KEY = "isLoggedIn";

function parseUser(raw: string | null): UserProfile | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
}

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserProfile | null>(parseUser(localStorage.getItem(USER_KEY)));
  const accessToken = ref<string | null>(tokenStorage.getAccessToken());
  const loading = ref(false);

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value));

  function persistUser() {
    if (user.value) {
      localStorage.setItem(USER_KEY, JSON.stringify(user.value));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }

  function syncLegacyLoginState() {
    if (isAuthenticated.value) {
      localStorage.setItem(LEGACY_LOGIN_KEY, "true");
    } else {
      localStorage.removeItem(LEGACY_LOGIN_KEY);
    }
  }

  function applySession(session: AuthSession) {
    user.value = session.user;
    accessToken.value = session.access_token;
    tokenStorage.setTokens(session.access_token, session.refresh_token);
    persistUser();
    syncLegacyLoginState();

    if (session.pair_status) {
      const coupleStore = useCoupleStore();
      coupleStore.setPairState(session.pair_status);
    }
  }

  function setSession(session: AuthSession) {
    applySession(session);
  }

  async function login(payload: LoginPayload) {
    loading.value = true;
    try {
      const session = await authApi.login(payload);
      applySession(session);
      return session;
    } finally {
      loading.value = false;
    }
  }

  async function register(payload: RegisterPayload) {
    loading.value = true;
    try {
      const session = await authApi.register(payload);
      applySession(session);
      return session;
    } finally {
      loading.value = false;
    }
  }

  async function fetchMe() {
    if (!tokenStorage.getAccessToken()) return null;
    const me = await authApi.fetchMe();
    user.value = me;
    persistUser();
    syncLegacyLoginState();
    return me;
  }

  async function sendResetCode(payload: ForgotSendCodePayload) {
    return authApi.sendResetCode(payload);
  }

  async function resetPassword(payload: ForgotResetPayload) {
    return authApi.resetPassword(payload);
  }

  function logout() {
    user.value = null;
    accessToken.value = null;
    tokenStorage.clearTokens();
    persistUser();
    syncLegacyLoginState();
    const coupleStore = useCoupleStore();
    coupleStore.reset();
  }

  function hydrateFromStorage() {
    accessToken.value = tokenStorage.getAccessToken();
    user.value = parseUser(localStorage.getItem(USER_KEY));
    syncLegacyLoginState();
  }

  return {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    setSession,
    fetchMe,
    sendResetCode,
    resetPassword,
    logout,
    hydrateFromStorage,
  };
});
