<template>
  <section class="p0-wrap">
    <div class="header soft-card">
      <h2 class="title-font">消息中心</h2>
      <p>未读 {{ notificationStore.unreadCount }} 条</p>
    </div>

    <div class="toolbar soft-card">
      <el-radio-group v-model="activeCategory" @change="loadNotifications">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="system">系统</el-radio-button>
        <el-radio-button label="reminder">提醒</el-radio-button>
      </el-radio-group>
      <div class="ops">
        <el-button @click="readAll">全部标记已读</el-button>
        <el-button @click="clearRead">清空已读</el-button>
      </div>
    </div>

    <RequestStatePanel
      :loading="notificationStore.loading"
      :error="notificationStore.error"
      :empty="!notificationStore.notifications.length"
      empty-text="暂无消息"
      @retry="loadNotifications"
    >
      <div class="list">
        <article
          v-for="item in notificationStore.notifications"
          :key="item.id"
          class="item soft-card"
          :class="{ unread: !item.is_read }"
        >
          <div class="main">
            <h3>{{ item.title }}</h3>
            <p>{{ item.content }}</p>
            <small>{{ item.created_at }}</small>
          </div>
          <el-button type="danger" text @click="remove(item.id)">删除</el-button>
        </article>
      </div>
    </RequestStatePanel>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import RequestStatePanel from "../../components/p0/RequestStatePanel.vue";
import { useNotificationStore } from "../../stores/useNotificationStore";

const notificationStore = useNotificationStore();
const activeCategory = ref<"all" | "system" | "reminder">("all");

async function loadNotifications() {
  try {
    const category = activeCategory.value === "all" ? undefined : activeCategory.value;
    await notificationStore.fetchNotifications(category);
  } catch {
    ElMessage.error("加载消息失败");
  }
}

async function readAll() {
  try {
    await notificationStore.readAll();
    ElMessage.success("已全部标记已读");
  } catch {
    ElMessage.error("操作失败");
  }
}

async function clearRead() {
  try {
    await notificationStore.removeRead();
    ElMessage.success("已清空已读消息");
  } catch {
    ElMessage.error("操作失败");
  }
}

async function remove(id: string | number) {
  try {
    await notificationStore.deleteOne(id);
    ElMessage.success("已删除");
  } catch {
    ElMessage.error("删除失败");
  }
}

onMounted(loadNotifications);
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
  gap: 10px;
}

.ops {
  display: flex;
  gap: 8px;
}

.list {
  display: grid;
  gap: 10px;
}

.item {
  padding: 12px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.item.unread {
  border-color: #f4b8c4;
}

.main h3 {
  margin: 0;
}

.main p {
  margin: 6px 0;
}

.main small {
  color: var(--text-sub);
}
</style>
