<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">恢复确认</h2>
      <p>执行后不可直接撤销，请先完成敏感操作验证</p>
    </div>

    <div class="panel soft-card">
      <el-alert
        v-if="!coupleStore.hasSensitiveAccess"
        type="warning"
        :closable="false"
        show-icon
        title="当前未获得敏感操作权限，请先在安全设置中验证。"
      />

      <el-form :model="form" label-width="110px" class="restore-form">
        <el-form-item label="快照 ID">
          <el-input v-model="form.snapshot_id" />
        </el-form-item>
        <el-form-item label="恢复模式">
          <el-radio-group v-model="form.mode">
            <el-radio label="full">全量恢复</el-radio>
            <el-radio label="merge">合并恢复</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="验证口令">
          <el-input v-model="form.verify_token" type="password" show-password />
        </el-form-item>
      </el-form>

      <div class="actions">
        <el-button @click="router.push('/settings/security')">去安全设置</el-button>
        <el-button type="danger" @click="dialogOpen = true">开始恢复</el-button>
      </div>
    </div>

    <SensitiveActionDialog
      v-model="dialogOpen"
      title="恢复确认"
      content="恢复将覆盖部分现有数据，执行后不可直接撤销。"
      confirm-text="确认恢复"
      :loading="loading"
      @confirm="runRestore"
    />
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import SensitiveActionDialog from "../../components/p0/SensitiveActionDialog.vue";
import { useBackupStore } from "../../stores/useBackupStore";
import { useCoupleStore } from "../../stores/useCoupleStore";

const router = useRouter();
const route = useRoute();
const backupStore = useBackupStore();
const coupleStore = useCoupleStore();
const loading = ref(false);
const dialogOpen = ref(false);

const form = reactive({
  snapshot_id: String(route.query.snapshot_id || ""),
  mode: "full" as "full" | "merge",
  verify_token: "",
});

async function runRestore() {
  if (!coupleStore.hasSensitiveAccess) {
    ElMessage.warning("请先完成敏感操作验证");
    dialogOpen.value = false;
    return;
  }
  if (!form.snapshot_id || !form.verify_token) {
    ElMessage.warning("请填写快照ID和验证口令");
    return;
  }
  loading.value = true;
  try {
    await backupStore.restoreSnapshot({
      snapshot_id: form.snapshot_id,
      mode: form.mode,
      verify_token: form.verify_token,
    });
    ElMessage.success("恢复任务已提交");
    dialogOpen.value = false;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "恢复失败");
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

.header p {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.restore-form {
  margin-top: 12px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
