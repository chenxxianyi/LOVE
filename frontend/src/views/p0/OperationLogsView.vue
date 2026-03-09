<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">操作日志</h2>
      <p>查看登录、导出、恢复、解绑等敏感操作</p>
    </div>

    <div class="filter soft-card">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
      />
      <el-select v-model="actionTypes" multiple collapse-tags placeholder="操作类型">
        <el-option label="登录" value="login" />
        <el-option label="删除" value="delete" />
        <el-option label="导出" value="export" />
        <el-option label="恢复" value="restore" />
        <el-option label="解绑" value="unbind" />
      </el-select>
      <el-button @click="resetFilter">重置</el-button>
      <el-button @click="loadLogs">查询</el-button>
      <el-button type="primary" @click="exportLogs">导出 CSV</el-button>
    </div>

    <RequestStatePanel
      :loading="securityStore.loading"
      :error="securityStore.error"
      :empty="!securityStore.logs.length"
      empty-text="当前筛选条件下暂无记录"
      @retry="loadLogs"
    >
      <el-table :data="securityStore.logs" stripe class="soft-card table-wrap">
        <el-table-column prop="created_at" label="时间" min-width="170" />
        <el-table-column prop="action_label" label="操作" min-width="150" />
        <el-table-column prop="actor_name" label="操作者" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === "success" ? "成功" : "失败" }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </RequestStatePanel>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import RequestStatePanel from "../../components/p0/RequestStatePanel.vue";
import { useSecurityStore } from "../../stores/useSecurityStore";
import type { SecurityActionType } from "../../types/security";

const securityStore = useSecurityStore();

const dateRange = ref<[string, string] | null>(null);
const actionTypes = ref<SecurityActionType[]>([]);

function buildQuery() {
  return {
    date_from: dateRange.value?.[0],
    date_to: dateRange.value?.[1],
    action_types: actionTypes.value.length ? actionTypes.value : undefined,
  };
}

async function loadLogs() {
  try {
    await securityStore.fetchLogs(buildQuery());
  } catch {
    ElMessage.error("日志加载失败");
  }
}

function resetFilter() {
  dateRange.value = null;
  actionTypes.value = [];
  loadLogs();
}

async function exportLogs() {
  try {
    const blob = await securityStore.exportLogs(buildQuery());
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "operation-logs.csv";
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  }
}

onMounted(loadLogs);
</script>

<style scoped>
.p0-wrap {
  display: grid;
  gap: 14px;
}

.header,
.filter {
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

.filter {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.table-wrap {
  padding: 10px;
}
</style>
