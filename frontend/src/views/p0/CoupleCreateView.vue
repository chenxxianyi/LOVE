<template>
  <section class="p0-page">
    <div class="card soft-card">
      <h2 class="title-font">创建情侣空间</h2>
      <p class="sub">创建后即可邀请对方加入</p>

      <el-form :model="form" label-position="top">
        <el-form-item label="空间名称">
          <el-input v-model="form.space_name" maxlength="20" placeholder="例如：我们的纪念馆" />
        </el-form-item>
        <el-form-item label="我的昵称">
          <el-input v-model="form.my_nickname" maxlength="12" placeholder="例如：小鹿" />
        </el-form-item>
        <el-form-item label="在一起日期">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <div class="actions">
        <el-button @click="handleLaterSetup">稍后设置</el-button>
        <el-button type="primary" :loading="coupleStore.loading" @click="submit">
          创建并继续
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useCoupleStore } from "../../stores/useCoupleStore";

const router = useRouter();
const coupleStore = useCoupleStore();

const today = new Date().toISOString().slice(0, 10);
const form = reactive({
  space_name: "",
  my_nickname: "",
  start_date: today,
});

function handleLaterSetup() {
  ElMessage.info("可以稍后创建，先去输入邀请码加入");
  router.push("/couple/join");
}

async function submit() {
  if (!form.space_name || !form.my_nickname || !form.start_date) {
    ElMessage.warning("请填写完整信息");
    return;
  }

  try {
    await coupleStore.createSpace({
      space_name: form.space_name.trim(),
      my_nickname: form.my_nickname.trim(),
      start_date: form.start_date,
      privacy_level: "couple_only",
    });
    ElMessage.success("创建成功");
    router.push("/couple/invite");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建失败，请重试");
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
  width: min(560px, 94vw);
  padding: 24px;
}

.sub {
  color: var(--text-sub);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
