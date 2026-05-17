<template>
  <section class="p0-page">
    <div class="card soft-card">
      <h1 class="title-font">配对成功 🎉</h1>
      <p class="sub">你们的专属空间已建立，开始记录回忆吧</p>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="空间名称">
          {{ coupleStore.space?.space_name || "--" }}
        </el-descriptions-item>
        <el-descriptions-item label="成员">
          {{ memberText }}
        </el-descriptions-item>
        <el-descriptions-item label="在一起日期">
          {{ coupleStore.space?.start_date || "--" }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 临时账号提示 -->
      <el-alert
        v-if="isTempAccount"
        type="warning"
        :closable="false"
        show-icon
        style="margin-top: 16px;"
      >
        <template #title>
          你使用的是临时账号，换设备后将无法找回
        </template>
        <template #default>
          <el-button text type="primary" size="small" @click="showSetup = true">
            立即设置账号密码 →
          </el-button>
        </template>
      </el-alert>

      <div class="actions">
        <el-button @click="router.push('/reminders/edit')">去设置提醒</el-button>
        <el-button type="primary" @click="router.push('/')">进入纪念馆</el-button>
      </div>
    </div>

    <!-- 账号设置对话框 -->
    <AccountSetupDialog
      v-model="showSetup"
      @done="onSetupDone"
      @skip="showSetup = false"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useCoupleStore } from "../../stores/useCoupleStore";
import { useAuthStore } from "../../stores/useAuthStore";
import AccountSetupDialog from "../../components/p0/AccountSetupDialog.vue";

const router = useRouter();
const coupleStore = useCoupleStore();
const authStore = useAuthStore();

const showSetup = ref(false);

// 判断是否为通过邀请码自动创建的临时账号
const isTempAccount = computed(
  () => authStore.user?.account?.endsWith("@love.local") ?? false
);

const memberText = computed(() =>
  (coupleStore.space?.members || []).map((member) => member.nickname).join(" / ") || "--"
);

function onSetupDone() {
  showSetup.value = false;
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      await coupleStore.fetchSpace();
    } catch {
      // ignore
    }
  }

  // 自动弹出账号设置（临时账号且刚加入）
  if (isTempAccount.value) {
    setTimeout(() => {
      showSetup.value = true;
    }, 800);
  }
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
  width: min(680px, 94vw);
  padding: 24px;
}

h1 {
  margin: 0;
  font-size: 46px;
}

.sub {
  color: var(--text-sub);
}

.actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
