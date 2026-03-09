<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">提醒中心</h2>
      <p>统一管理纪念日、胶囊、问答、愿望提醒</p>
    </div>

    <div class="toolbar soft-card">
      <el-radio-group v-model="activeType" @change="changeType">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="anniversary">纪念日</el-radio-button>
        <el-radio-button label="capsule">胶囊</el-radio-button>
        <el-radio-button label="question">问答</el-radio-button>
        <el-radio-button label="bucket">愿望</el-radio-button>
      </el-radio-group>
      <el-button type="primary" @click="router.push('/reminders/edit')">新建提醒</el-button>
    </div>

    <RequestStatePanel
      :loading="reminderStore.loading"
      :error="reminderStore.error"
      :empty="!reminderStore.reminders.length"
      empty-text="还没有提醒，先创建一个吧"
      @retry="loadReminders"
    >
      <div class="list">
        <article v-for="item in reminderStore.reminders" :key="item.id" class="item soft-card">
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.type }} · {{ item.trigger_at }} · {{ item.repeat_rule }}</p>
          </div>
          <div class="ops">
            <el-switch
              :model-value="item.enabled"
              @change="(val: string | number | boolean) => toggleEnabled(item.id, !!val)"
            />
            <el-button text @click="router.push(`/reminders/edit/${item.id}`)">编辑</el-button>
            <el-button text @click="complete(item.id)">完成</el-button>
            <el-button type="danger" text @click="remove(item.id)">删除</el-button>
          </div>
        </article>
      </div>
    </RequestStatePanel>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import RequestStatePanel from "../../components/p0/RequestStatePanel.vue";
import { useReminderStore } from "../../stores/useReminderStore";
import type { ReminderType } from "../../types/reminder";

const router = useRouter();
const reminderStore = useReminderStore();
const activeType = ref<ReminderType | "all">("all");

async function loadReminders() {
  try {
    const type = activeType.value === "all" ? undefined : activeType.value;
    await reminderStore.fetchReminders(type);
  } catch {
    ElMessage.error("加载提醒失败");
  }
}

function changeType() {
  loadReminders();
}

async function toggleEnabled(id: string | number, enabled: boolean) {
  try {
    await reminderStore.updateReminder(id, { enabled });
    ElMessage.success("状态已更新");
  } catch {
    ElMessage.error("更新失败");
  }
}

async function complete(id: string | number) {
  try {
    await reminderStore.completeReminder(id);
    ElMessage.success("已标记完成");
  } catch {
    ElMessage.error("操作失败");
  }
}

async function remove(id: string | number) {
  try {
    await reminderStore.deleteReminder(id);
    ElMessage.success("已删除");
  } catch {
    ElMessage.error("删除失败");
  }
}

onMounted(loadReminders);
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

.header p {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.list {
  display: grid;
  gap: 10px;
}

.item {
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.item h3 {
  margin: 0;
}

.item p {
  margin: 4px 0 0;
  color: var(--text-sub);
}

.ops {
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
