import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { coupleApi } from "../api/couple";
import type {
  CoupleCreatePayload,
  CoupleInviteResponse,
  CoupleJoinPayload,
  CoupleSpace,
  PairStatus,
  UnbindConfirmPayload,
  UnbindRequestPayload,
} from "../types/couple";

const SPACE_KEY = "love_space";
const PAIR_STATUS_KEY = "love_pair_status";
const SENSITIVE_UNTIL_KEY = "love_sensitive_until";

function parseJson<T>(raw: string | null): T | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export const useCoupleStore = defineStore("couple", () => {
  const space = ref<CoupleSpace | null>(parseJson<CoupleSpace>(localStorage.getItem(SPACE_KEY)));
  const pairStatus = ref<PairStatus>(
    (localStorage.getItem(PAIR_STATUS_KEY) as PairStatus | null) || "none"
  );
  const sensitiveConfirmedUntil = ref<number>(
    Number(localStorage.getItem(SENSITIVE_UNTIL_KEY) || "0")
  );
  const lastInvite = ref<CoupleInviteResponse | null>(null);
  const loading = ref(false);

  const isPaired = computed(() => pairStatus.value === "paired");
  const hasSensitiveAccess = computed(
    () => sensitiveConfirmedUntil.value > 0 && Date.now() < sensitiveConfirmedUntil.value
  );

  function persistSpace() {
    if (space.value) {
      localStorage.setItem(SPACE_KEY, JSON.stringify(space.value));
    } else {
      localStorage.removeItem(SPACE_KEY);
    }
  }

  function persistPairStatus() {
    localStorage.setItem(PAIR_STATUS_KEY, pairStatus.value);
  }

  function persistSensitiveWindow() {
    localStorage.setItem(SENSITIVE_UNTIL_KEY, String(sensitiveConfirmedUntil.value));
  }

  function setPairState(status: PairStatus, nextSpace?: CoupleSpace | null) {
    pairStatus.value = status;
    if (typeof nextSpace !== "undefined") {
      space.value = nextSpace;
      persistSpace();
    }
    persistPairStatus();
  }

  async function fetchSpace() {
    loading.value = true;
    try {
      const response = await coupleApi.fetchMySpace();
      space.value = response;
      pairStatus.value = response.pair_status || (response.members.length >= 2 ? "paired" : "pending");
      persistSpace();
      persistPairStatus();
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function createSpace(payload: CoupleCreatePayload) {
    loading.value = true;
    try {
      const response = await coupleApi.createSpace(payload);
      setPairState(response.pair_status || "pending", response.space);
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function createInvite() {
    const response = await coupleApi.createInvite();
    lastInvite.value = response;
    return response;
  }

  async function joinByInvite(payload: CoupleJoinPayload) {
    loading.value = true;
    try {
      const response = await coupleApi.joinSpace(payload);
      setPairState(response.pair_status || "paired", response.space);
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function requestUnbind(payload: UnbindRequestPayload = {}) {
    return coupleApi.requestUnbind(payload);
  }

  async function confirmUnbind(payload: UnbindConfirmPayload) {
    const response = await coupleApi.confirmUnbind(payload);
    reset();
    return response;
  }

  function grantSensitiveAccess(minutes = 10) {
    sensitiveConfirmedUntil.value = Date.now() + minutes * 60 * 1000;
    persistSensitiveWindow();
  }

  function clearSensitiveAccess() {
    sensitiveConfirmedUntil.value = 0;
    persistSensitiveWindow();
  }

  function reset() {
    space.value = null;
    pairStatus.value = "none";
    lastInvite.value = null;
    clearSensitiveAccess();
    localStorage.removeItem(SPACE_KEY);
    persistPairStatus();
  }

  return {
    space,
    pairStatus,
    lastInvite,
    loading,
    isPaired,
    hasSensitiveAccess,
    setPairState,
    fetchSpace,
    createSpace,
    createInvite,
    joinByInvite,
    requestUnbind,
    confirmUnbind,
    grantSensitiveAccess,
    clearSensitiveAccess,
    reset,
  };
});
