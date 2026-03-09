<template>
  <section class="p0-page">
    <div class="wrap">
      <InviteCodeCard
        :code="inviteCode"
        :link="inviteLink"
        :expires-at="expiresAt"
        @copy-code="copyCode"
        @copy-link="copyLink"
        @refresh="refreshInvite"
      />
      <div class="actions">
        <el-button @click="router.push('/couple/create')">返回上一步</el-button>
        <el-button type="primary" @click="router.push('/couple/success')">
          我已发送，下一步
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import InviteCodeCard from "../../components/p0/InviteCodeCard.vue";
import { useCoupleStore } from "../../stores/useCoupleStore";

const router = useRouter();
const coupleStore = useCoupleStore();

const inviteCode = computed(() => coupleStore.lastInvite?.invite_code || "");
const inviteLink = computed(() => coupleStore.lastInvite?.invite_link || "");
const expiresAt = computed(() => coupleStore.lastInvite?.expires_at || "");

async function refreshInvite() {
  try {
    await coupleStore.createInvite();
    ElMessage.success("新邀请码已生成");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "生成失败");
  }
}

async function copyText(text: string, success: string) {
  if (!text) return;
  await navigator.clipboard.writeText(text);
  ElMessage.success(success);
}

function copyCode() {
  copyText(inviteCode.value, "已复制邀请码");
}

function copyLink() {
  copyText(inviteLink.value, "已复制邀请链接");
}

onMounted(async () => {
  if (!coupleStore.lastInvite) {
    await refreshInvite();
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

.wrap {
  width: min(620px, 94vw);
}

.actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
