<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">{{ isEdit ? "编辑提醒" : "新建提醒" }}</h2>
      <p>配置提醒触发时间、重复规则和通知渠道</p>
    </div>

    <div class="panel soft-card">
      <ReminderRuleForm v-model="form" />
      <div class="actions">
        <el-button @click="router.push('/reminders')">取消</el-button>
        <el-button :loading="loading" @click="save(false)">保存</el-button>
        <el-button type="primary" :loading="loading" @click="save(true)">
          保存并测试提醒
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import ReminderRuleForm from "../../components/p0/ReminderRuleForm.vue";
import { useReminderStore } from "../../stores/useReminderStore";
import type { ReminderPayload } from "../../types/reminder";

const route = useRoute();
const router = useRouter();
const reminderStore = useReminderStore();
const loading = ref(false);

const reminderId = computed(() => route.params.id as string | undefined);
const isEdit = computed(() => Boolean(reminderId.value));

const form = ref<ReminderPayload>({
  title: "",
  type: "anniversary",
  trigger_at: "",
  advance: "same_day",
  repeat_rule: "none",
  channels: ["in_app"],
  quiet_hours_start: "",
  quiet_hours_end: "",
  enabled: true,
});

async function loadDetail() {
  if (!isEdit.value) return;
  try {
    if (!reminderStore.reminders.length) {
      await reminderStore.fetchReminders();
    }
    const target = reminderStore.reminders.find((item) => String(item.id) === reminderId.value);
    if (target) {
      form.value = {
        title: target.title,
        type: target.type,
        trigger_at: target.trigger_at,
        advance: target.advance,
        repeat_rule: target.repeat_rule,
        channels: [...target.channels],
        quiet_hours_start: target.quiet_hours_start,
        quiet_hours_end: target.quiet_hours_end,
        enabled: target.enabled,
      };
    }
  } catch {
    ElMessage.error("加载提醒详情失败");
  }
}

async function save(runTest: boolean) {
  if (!form.value.title || !form.value.trigger_at || !form.value.channels.length) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  loading.value = true;
  try {
    let id: string | number | undefined = reminderId.value;
    if (isEdit.value && reminderId.value) {
      await reminderStore.updateReminder(reminderId.value, form.value);
    } else {
      const created = await reminderStore.createReminder(form.value);
      id = created.id;
    }

    if (runTest && id) {
      await reminderStore.testReminder(id);
      ElMessage.success("测试提醒已发送");
    } else {
      ElMessage.success("提醒已保存");
    }
    router.push("/reminders");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadDetail);
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

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
