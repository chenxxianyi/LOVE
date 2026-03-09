<template>
  <div class="anniversary-page">
    <header class="page-head soft-card fade-up">
      <div class="head-content">
        <div>
          <h1 class="title-font">纪念日</h1>
          <p>每一个特别的日子，都值得被铭记。</p>
        </div>
        <el-button type="primary" round size="large" @click="showAddDialog = true">
          添加纪念日
        </el-button>
      </div>
    </header>

    <div class="event-grid">
      <div
        v-for="(item, index) in store.anniversaries"
        :key="item.id"
        class="event-card soft-card fade-up"
        :class="{ urgent: item.days_left <= 7, today: item.days_left === 0 }"
        :style="{ animationDelay: `${index * 50}ms` }"
      >
        <div class="card-left">
          <div class="icon-wrapper">{{ item.icon }}</div>
          <div class="info">
            <h3>{{ item.title }}</h3>
            <p class="date">{{ item.date }} · {{ item.type === 'anniversary' ? '每年' : '一次性' }}</p>
          </div>
        </div>
        <div class="card-right">
          <div class="days-badge">
            <span class="label">{{ item.days_left === 0 ? '就是' : '还有' }}</span>
            <span class="number">{{ item.days_left === 0 ? '今天' : item.days_left }}</span>
            <span class="label" v-if="item.days_left > 0">天</span>
          </div>
          <el-button
            type="text"
            icon="Delete"
            class="delete-btn"
            @click="handleDelete(item.id)"
          ></el-button>
        </div>
      </div>
    </div>

    <!-- Add Dialog -->
    <el-dialog v-model="showAddDialog" title="添加纪念日" width="400px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称">
          <el-input v-model="form.title" placeholder="例如：对方生日" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.type">
            <el-radio-button label="anniversary">每年重复</el-radio-button>
            <el-radio-button label="event">一次性</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="例如：🎂" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="submit" :loading="loading">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete } from "@element-plus/icons-vue";

const store = useLoveStore();
const showAddDialog = ref(false);
const loading = ref(false);

const form = reactive({
  title: "",
  date: "",
  type: "anniversary",
  icon: "📅",
});

onMounted(() => {
  store.fetchAnniversaries();
});

const submit = async () => {
  if (!form.title || !form.date) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  
  loading.value = true;
  try {
    await store.createAnniversary({ ...form } as any);
    ElMessage.success("添加成功");
    showAddDialog.value = false;
    form.title = "";
    form.date = "";
    form.type = "anniversary";
    form.icon = "📅";
  } catch (error) {
    ElMessage.error("添加失败");
  } finally {
    loading.value = false;
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm("确定要删除这个纪念日吗？", "提示", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await store.deleteAnniversary(id);
    ElMessage.success("已删除");
  } catch (e) {
    // Cancelled
  }
};
</script>

<style scoped>
.anniversary-page {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.page-head {
  padding: 24px;
  margin-bottom: 20px;
}

.head-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-head h1 {
  margin: 0 0 8px;
  font-size: 32px;
}

.page-head p {
  margin: 0;
  color: var(--text-sub);
}

.event-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-left: 4px solid transparent;
  transition: all 0.3s ease;
}

.event-card:hover {
  transform: translateX(4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.05);
}

.event-card.urgent {
  border-left-color: #ff9a9e;
  background: linear-gradient(to right, #fff0f3, #fff);
}

.event-card.today {
  border-left-color: #ff5e62;
  background: linear-gradient(to right, #ffe6e6, #fff);
  box-shadow: 0 8px 20px rgba(255, 94, 98, 0.15);
}

.card-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-wrapper {
  font-size: 32px;
  width: 56px;
  height: 56px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.info h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: var(--text-main);
}

.info .date {
  margin: 0;
  font-size: 14px;
  color: var(--text-sub);
}

.card-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.days-badge {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.days-badge .label {
  font-size: 12px;
  color: var(--text-sub);
}

.days-badge .number {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary-color);
  line-height: 1;
  margin: 2px 0;
}

.event-card.urgent .days-badge .number {
  color: #ff5e62;
}

.delete-btn {
  color: #c0c4cc;
  font-size: 18px;
}

.delete-btn:hover {
  color: #f56c6c;
}
</style>
