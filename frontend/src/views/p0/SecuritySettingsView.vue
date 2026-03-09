<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">安全设置</h2>
      <p>管理登录与隐私安全策略</p>
    </div>

    <div class="panel soft-card">
      <el-form :model="settings" label-width="140px">
        <el-form-item label="应用二次锁">
          <el-switch v-model="settings.secondary_lock_enabled" />
        </el-form-item>
        <el-form-item label="异地登录提醒">
          <el-switch v-model="settings.new_device_alert_enabled" />
        </el-form-item>
        <el-form-item label="敏感操作验证">
          <el-switch v-model="settings.sensitive_action_verify_enabled" />
        </el-form-item>
        <el-form-item label="回收站保留期">
          <el-select v-model="settings.recycle_retention_days" style="width: 200px">
            <el-option :value="7" label="7 天" />
            <el-option :value="15" label="15 天" />
            <el-option :value="30" label="30 天" />
          </el-select>
        </el-form-item>
      </el-form>
      <div class="actions">
        <el-button @click="openPasswordDialog = true">修改密码</el-button>
        <el-button @click="verifySensitive">验证敏感操作（10分钟）</el-button>
        <el-button type="danger" @click="requestUnbind">申请解绑</el-button>
        <el-button type="primary" :loading="securityStore.loading" @click="saveSettings">
          保存设置
        </el-button>
      </div>
    </div>

    <el-dialog v-model="openPasswordDialog" title="修改密码" width="420px">
      <el-form :model="passwordForm" label-position="top">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="openPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingPassword" @click="changePassword">提交</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { authApi } from "../../api/auth";
import { useCoupleStore } from "../../stores/useCoupleStore";
import { useSecurityStore } from "../../stores/useSecurityStore";
import type { SecuritySettings } from "../../types/security";

const securityStore = useSecurityStore();
const coupleStore = useCoupleStore();

const settings = reactive<SecuritySettings>({
  secondary_lock_enabled: false,
  new_device_alert_enabled: true,
  sensitive_action_verify_enabled: true,
  recycle_retention_days: 30,
});

const openPasswordDialog = ref(false);
const savingPassword = ref(false);
const passwordForm = reactive({
  old_password: "",
  new_password: "",
});

onMounted(async () => {
  try {
    await securityStore.fetchSettings();
    Object.assign(settings, securityStore.settings);
  } catch {
    ElMessage.warning("未获取到远端配置，使用默认值");
  }
});

async function saveSettings() {
  try {
    await securityStore.updateSettings({ ...settings });
    ElMessage.success("安全设置已更新");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  }
}

function verifySensitive() {
  coupleStore.grantSensitiveAccess(10);
  ElMessage.success("已获得 10 分钟敏感操作权限");
}

async function requestUnbind() {
  try {
    await coupleStore.requestUnbind();
    ElMessage.success("解绑申请已提交");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "申请失败");
  }
}

async function changePassword() {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    ElMessage.warning("请填写完整密码");
    return;
  }
  savingPassword.value = true;
  try {
    await authApi.changePassword({ ...passwordForm });
    ElMessage.success("密码已修改");
    openPasswordDialog.value = false;
    passwordForm.old_password = "";
    passwordForm.new_password = "";
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "修改失败");
  } finally {
    savingPassword.value = false;
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
  font-size: 36px;
}

.header p {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}
</style>
