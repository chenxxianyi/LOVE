<template>
  <el-dialog
    v-model="visible"
    width="min(420px, 94vw)"
    :show-close="false"
    class="profile-dialog custom-dialog"
    :close-on-click-modal="true"
    append-to-body
  >
    <div class="profile-container" v-loading="loading">
      <!-- 顶部渐变封面 -->
      <div class="profile-cover">
        <div class="close-btn" @click="visible = false">
          <el-icon><Close /></el-icon>
        </div>
      </div>

      <!-- 头像区域（悬浮在封面上方） -->
      <div class="avatar-section">
        <el-upload
          class="avatar-uploader"
          action="http://localhost:8000/api/upload"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
        >
          <div class="avatar-wrapper">
            <el-avatar :size="90" :src="form.avatar || defaultAvatar" class="avatar-img" />
            <div class="avatar-mask">
              <el-icon><Camera /></el-icon>
            </div>
          </div>
        </el-upload>
      </div>

      <!-- 表单区域 -->
      <div class="profile-content-inner">
        <h2 class="title-font text-center" style="margin-top: 10px; margin-bottom: 24px; font-size: 22px;">个人资料</h2>
        
        <el-form :model="form" label-position="top">
          <el-form-item label="我的昵称">
            <el-input 
              v-model="form.nickname" 
              placeholder="给自己取个好听的名字" 
              maxlength="12" 
              size="large"
            />
          </el-form-item>
          <el-form-item label="登录账号">
            <el-input 
              :model-value="authStore.user?.account" 
              disabled 
              size="large"
            />
          </el-form-item>
        </el-form>

        <div class="security-card">
          <div class="sec-info">
            <h4>账号安全</h4>
            <p>修改你的登录密码</p>
          </div>
          <el-button round @click="showPassDialog = true">修改密码</el-button>
        </div>
      </div>

      <div class="dialog-footer">
        <el-button @click="visible = false" round>取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave" round>
          保存修改
        </el-button>
      </div>
    </div>

    <!-- 嵌套的修改密码弹窗 -->
    <el-dialog
      v-model="showPassDialog"
      title="修改密码"
      width="min(360px, 90vw)"
      append-to-body
      class="password-dialog"
    >
      <el-form :model="passForm" label-position="top">
        <el-form-item label="当前密码">
          <el-input v-model="passForm.old_password" type="password" show-password size="large" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passForm.new_password" type="password" show-password size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPassDialog = false" round>取消</el-button>
        <el-button type="primary" :loading="passLoading" @click="handleUpdatePass" round>
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from "vue";
import { ElMessage, type UploadProps } from "element-plus";
import { Camera, Close } from "@element-plus/icons-vue";
import { useAuthStore } from "../../stores/useAuthStore";
import { authApi } from "../../api/auth";

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits<{ (e: "update:modelValue", val: boolean): void }>();

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

const authStore = useAuthStore();
const loading = ref(false);
const saving = ref(false);
const defaultAvatar = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";

const form = reactive({
  nickname: authStore.user?.nickname || "",
  avatar: authStore.user?.avatar || "",
});

// 监听 store 数据变化同步到表单
watch(() => authStore.user, (u) => {
  if (u) {
    form.nickname = u.nickname || "";
    form.avatar = u.avatar || "";
  }
}, { immediate: true });

// 修改密码相关
const showPassDialog = ref(false);
const passLoading = ref(false);
const passForm = reactive({
  old_password: "",
  new_password: "",
});

const handleAvatarSuccess: UploadProps["onSuccess"] = (response) => {
  form.avatar = response.url;
  ElMessage.success("上传成功，千万别忘了点击底部的保存生效哦！");
};

const beforeAvatarUpload: UploadProps["beforeUpload"] = (rawFile) => {
  if (rawFile.type !== "image/jpeg" && rawFile.type !== "image/png" && rawFile.type !== "image/webp") {
    ElMessage.error("头像必须是 JPG/PNG/WEBP 格式");
    return false;
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error("图片大小不能超过 2MB");
    return false;
  }
  return true;
};

async function handleSave() {
  if (!form.nickname.trim()) {
    ElMessage.warning("昵称不能为空哦");
    return;
  }
  saving.value = true;
  try {
    const updatedUser = await authApi.updateMe({
      nickname: form.nickname.trim(),
      avatar: form.avatar,
    });
    // 更新本地 store
    authStore.user = updatedUser;
    // 同步到本地存储
    localStorage.setItem("love_user", JSON.stringify(updatedUser));
    ElMessage.success("个人资料已更新 ✨");
    visible.value = false;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "更新失败");
  } finally {
    saving.value = false;
  }
}

async function handleUpdatePass() {
  if (!passForm.old_password || !passForm.new_password) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  if (passForm.new_password.length < 6) {
    ElMessage.warning("新密码至少 6 位");
    return;
  }
  passLoading.value = true;
  try {
    await authApi.changePassword(passForm);
    ElMessage.success("密码修改成功，请重新登录");
    showPassDialog.value = false;
    authStore.logout(); 
    window.location.reload();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "修改失败");
  } finally {
    passLoading.value = false;
  }
}
</script>

<style scoped>
/* Reset el-dialog default paddings */
:global(.profile-dialog .el-dialog__header) {
  display: none !important;
}
:global(.profile-dialog .el-dialog__body) {
  padding: 0 !important;
}

.profile-container {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
}

.profile-cover {
  height: 120px;
  background: linear-gradient(135deg, #ffdde5 0%, #fbd1e0 100%);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c9516c;
  font-size: 16px;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: rotate(90deg);
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-top: -45px;
  position: relative;
  z-index: 2;
}

.avatar-wrapper {
  position: relative;
  border-radius: 50%;
  border: 4px solid #fff;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-wrapper:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}

.avatar-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-mask .el-icon {
  font-size: 24px;
}

.avatar-wrapper:hover .avatar-mask {
  opacity: 1;
}

.profile-content-inner {
  padding: 0 32px;
}

.text-center {
  text-align: center;
}

.security-card {
  margin-top: 28px;
  background: var(--bg-soft);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--line-soft);
}

.sec-info h4 {
  margin: 0 0 4px;
  font-size: 15px;
  color: var(--text-main);
}

.sec-info p {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub);
}

.dialog-footer {
  padding: 24px 32px 32px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.dialog-footer .el-button {
  flex: 1;
}
</style>
