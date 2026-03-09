<template>
  <section class="p0-page">
    <div class="card soft-card">
      <h2 class="title-font">输入邀请码加入</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="邀请码">
          <el-input v-model="form.invite_code" maxlength="6" placeholder="请输入6位邀请码" />
        </el-form-item>
        <el-form-item label="我的昵称">
          <el-input v-model="form.my_nickname" maxlength="12" placeholder="请输入昵称" />
        </el-form-item>
      </el-form>
      <div class="actions">
        <el-button @click="router.push('/auth')">返回</el-button>
        <el-button type="primary" :loading="coupleStore.loading" @click="submit">
          加入空间
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { useCoupleStore } from "../../stores/useCoupleStore";

const router = useRouter();
const route = useRoute();
const coupleStore = useCoupleStore();

const form = reactive({
  invite_code: "",
  my_nickname: "",
});

onMounted(() => {
  // 自动从 URL ?code= 参数填充邀请码
  const codeFromUrl = route.query.code as string;
  if (codeFromUrl) {
    form.invite_code = codeFromUrl.trim().toUpperCase();
  }
});

async function submit() {
  if (!form.invite_code || !form.my_nickname) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  try {
    await coupleStore.joinByInvite({
      invite_code: form.invite_code.trim(),
      my_nickname: form.my_nickname.trim(),
    });
    ElMessage.success("加入成功");
    router.push("/couple/success");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "邀请码无效或已过期");
  }
}
</script>

<style scoped>
.p0-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  width: min(520px, 94vw);
  padding: 24px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
