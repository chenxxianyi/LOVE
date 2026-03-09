<template>
  <section class="p0-page">
    <div class="card soft-card">
      <h1 class="title-font">配对成功</h1>
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

      <div class="actions">
        <el-button @click="router.push('/reminders/edit')">去设置提醒</el-button>
        <el-button type="primary" @click="router.push('/')">进入纪念馆</el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useCoupleStore } from "../../stores/useCoupleStore";

const router = useRouter();
const coupleStore = useCoupleStore();

const memberText = computed(() =>
  (coupleStore.space?.members || []).map((member) => member.nickname).join(" / ") || "--"
);

onMounted(async () => {
  if (!coupleStore.space) {
    try {
      await coupleStore.fetchSpace();
    } catch {
      // ignore and keep fallback values
    }
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
