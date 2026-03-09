<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">设备管理</h2>
      <p>管理当前账号的登录设备</p>
    </div>

    <RequestStatePanel
      :loading="securityStore.loading"
      :error="securityStore.error"
      :empty="!securityStore.sessions.length"
      empty-text="暂无设备记录"
      @retry="loadSessions"
    >
      <el-table :data="securityStore.sessions" stripe class="soft-card table-wrap">
        <el-table-column prop="device_name" label="设备" min-width="180" />
        <el-table-column prop="location" label="位置" min-width="120" />
        <el-table-column prop="last_seen_at" label="最近活跃" min-width="170" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_current ? 'success' : 'info'">
              {{ row.is_current ? "当前设备" : "已登录" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="danger"
              text
              :disabled="row.is_current"
              @click="removeSession(row.id)"
            >
              下线
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </RequestStatePanel>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { ElMessage } from "element-plus";
import RequestStatePanel from "../../components/p0/RequestStatePanel.vue";
import { useSecurityStore } from "../../stores/useSecurityStore";

const securityStore = useSecurityStore();

async function loadSessions() {
  try {
    await securityStore.fetchSessions();
  } catch {
    ElMessage.error("加载设备失败");
  }
}

async function removeSession(id: number | string) {
  try {
    await securityStore.removeSession(id);
    ElMessage.success("设备已下线");
  } catch {
    ElMessage.error("下线失败");
  }
}

onMounted(loadSessions);
</script>

<style scoped>
.p0-wrap {
  display: grid;
  gap: 14px;
}

.header {
  padding: 18px;
}

.header h2 {
  margin: 0;
  font-size: 34px;
}

.header p {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.table-wrap {
  padding: 10px;
}
</style>
