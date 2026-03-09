<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">导出中心</h2>
      <p>可导出纪念数据包（ZIP）</p>
    </div>

    <div class="panel soft-card">
      <el-form :model="form" label-width="110px">
        <el-form-item label="导出范围">
          <el-checkbox-group v-model="form.scope">
            <el-checkbox label="moments">回忆</el-checkbox>
            <el-checkbox label="images">图片</el-checkbox>
            <el-checkbox label="questions">问答</el-checkbox>
            <el-checkbox label="reminders">提醒</el-checkbox>
            <el-checkbox label="logs">日志</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>

      <div class="actions">
        <el-button @click="router.push('/settings/security')">去安全设置</el-button>
        <el-button type="primary" @click="dialogOpen = true">创建导出</el-button>
      </div>
      <p class="hint">状态：{{ backupStore.latestExportJob?.status || "暂无任务" }}</p>
      <p class="hint" v-if="backupStore.latestExportJob?.download_url">
        下载链接：{{ backupStore.latestExportJob?.download_url }}
      </p>
    </div>

    <SensitiveActionDialog
      v-model="dialogOpen"
      title="确认导出"
      content="导出包包含敏感数据，请确认后继续。"
      confirm-text="确认导出"
      :loading="loading"
      @confirm="runExport"
    />
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import SensitiveActionDialog from "../../components/p0/SensitiveActionDialog.vue";
import { useBackupStore } from "../../stores/useBackupStore";
import { useCoupleStore } from "../../stores/useCoupleStore";

const router = useRouter();
const coupleStore = useCoupleStore();
const backupStore = useBackupStore();
const loading = ref(false);
const dialogOpen = ref(false);

const dateRange = ref<[string, string] | null>(null);
const form = reactive({
  scope: ["moments", "images", "questions", "reminders", "logs"],
});

async function runExport() {
  if (!coupleStore.hasSensitiveAccess) {
    ElMessage.warning("请先完成敏感操作验证");
    dialogOpen.value = false;
    return;
  }
  loading.value = true;
  try {
    const job = await backupStore.createExport({
      scope: [...form.scope],
      date_from: dateRange.value?.[0],
      date_to: dateRange.value?.[1],
      format: "zip",
    });
    ElMessage.success("导出任务已创建");
    if (job.id) {
      await backupStore.pollExportJob(job.id);
    }
    dialogOpen.value = false;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "导出失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.p0-wrap {
  display: grid;
  gap: 14px;
}

.header,
.panel {
  padding: 18px;
}

.header h2 {
  margin: 0;
  font-size: 34px;
}

.header p,
.hint {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
