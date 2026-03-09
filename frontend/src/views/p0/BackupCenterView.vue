<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">备份中心</h2>
      <p>管理自动/手动备份快照</p>
    </div>

    <div class="toolbar soft-card">
      <div class="left">
        <p>最近任务：{{ latestStatus }}</p>
      </div>
      <div class="right">
        <el-button type="primary" @click="manualBackup">立即备份</el-button>
      </div>
    </div>

    <RequestStatePanel
      :loading="backupStore.loading"
      :error="backupStore.error"
      :empty="!backupStore.snapshots.length"
      empty-text="暂无备份记录"
      @retry="loadSnapshots"
    >
      <div class="soft-card panel">
        <BackupSnapshotTable :snapshots="backupStore.snapshots" @restore="goRestore" />
      </div>
    </RequestStatePanel>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import BackupSnapshotTable from "../../components/p0/BackupSnapshotTable.vue";
import RequestStatePanel from "../../components/p0/RequestStatePanel.vue";
import { useBackupStore } from "../../stores/useBackupStore";

const router = useRouter();
const backupStore = useBackupStore();

const latestStatus = computed(
  () =>
    backupStore.latestBackupJob?.status ||
    backupStore.latestRestoreJob?.status ||
    backupStore.latestExportJob?.status ||
    "暂无"
);

async function loadSnapshots() {
  try {
    await backupStore.fetchSnapshots();
  } catch {
    ElMessage.error("加载备份失败");
  }
}

async function manualBackup() {
  try {
    const job = await backupStore.createManualBackup();
    ElMessage.success("备份任务已创建");
    if (job.id) {
      await backupStore.pollBackupJob(job.id);
    }
    await loadSnapshots();
  } catch {
    ElMessage.error("创建备份失败");
  }
}

function goRestore(snapshotId: number | string) {
  router.push({
    path: "/settings/backup/restore",
    query: { snapshot_id: String(snapshotId) },
  });
}

onMounted(loadSnapshots);
</script>

<style scoped>
.p0-wrap {
  display: grid;
  gap: 14px;
}

.header,
.toolbar {
  padding: 18px;
}

.header h2 {
  margin: 0;
  font-size: 34px;
}

.header p,
.toolbar p {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel {
  padding: 10px;
}
</style>
