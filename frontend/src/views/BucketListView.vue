<template>
  <div class="bucket-page">
    <header class="bucket-head soft-card fade-up">
      <div class="head-content">
        <div>
          <h1 class="title-font">愿望清单</h1>
          <p>一起去完成的100件小事，记录每一个实现的梦想。</p>
        </div>
        <el-button type="primary" round size="large" @click="showAddDialog = true">
          许个愿望
        </el-button>
      </div>
    </header>

    <div class="bucket-stats soft-card fade-up">
      <div class="stat-item">
        <h3>{{ pendingCount }}</h3>
        <p>未完成</p>
      </div>
      <div class="stat-item">
        <h3>{{ plannedCount }}</h3>
        <p>计划中</p>
      </div>
      <div class="stat-item completed">
        <h3>{{ completedCount }}</h3>
        <p>已实现</p>
      </div>
    </div>

    <div class="bucket-grid">
      <div
        v-for="(item, index) in store.bucketList"
        :key="item.id"
        class="bucket-card soft-card fade-up"
        :class="{ completed: item.status === 'completed' }"
        :style="{ animationDelay: `${index * 50}ms` }"
      >
        <div class="card-icon">{{ item.icon }}</div>
        <div class="card-content">
          <h3>{{ item.title }}</h3>
          <p v-if="item.description">{{ item.description }}</p>
          <div class="card-meta">
            <el-tag size="small" :type="getStatusType(item.status)">
              {{ getStatusText(item.status) }}
            </el-tag>
            <span v-if="item.completed_at" class="date">
              {{ item.completed_at.split(" ")[0] }} 达成
            </span>
          </div>
        </div>
        <div class="card-actions">
          <el-dropdown trigger="click" @command="(cmd: string) => handleCommand(cmd, item.id)">
            <span class="more-btn">⋮</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="planned" v-if="item.status === 'pending'">
                  标记为计划中
                </el-dropdown-item>
                <el-dropdown-item command="completed" v-if="item.status !== 'completed'">
                  标记为已完成
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- Add Dialog -->
    <el-dialog v-model="showAddDialog" title="许个新愿望" width="400px">
      <el-form :model="form" label-width="60px">
        <el-form-item label="愿望">
          <el-input v-model="form.title" placeholder="例如：一起去迪士尼" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.description" type="textarea" placeholder="写点什么..." />
        </el-form-item>
        <el-form-item label="图标">
          <el-radio-group v-model="form.icon">
            <el-radio-button label="✨" />
            <el-radio-button label="🎡" />
            <el-radio-button label="✈️" />
            <el-radio-button label="🏠" />
            <el-radio-button label="🎁" />
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="submit" :loading="loading">许愿</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const store = useLoveStore();
const showAddDialog = ref(false);
const loading = ref(false);

const form = reactive({
  title: "",
  description: "",
  icon: "✨",
  status: "pending" as const,
  images: [] as string[],
});

const pendingCount = computed(() => store.bucketList.filter(i => i.status === 'pending').length);
const plannedCount = computed(() => store.bucketList.filter(i => i.status === 'planned').length);
const completedCount = computed(() => store.bucketList.filter(i => i.status === 'completed').length);

onMounted(() => {
  store.fetchBucketList();
});

const getStatusType = (status: string) => {
  const map: any = { pending: 'info', planned: 'warning', completed: 'success' };
  return map[status];
};

const getStatusText = (status: string) => {
  const map: any = { pending: '未开始', planned: '计划中', completed: '已实现' };
  return map[status];
};

const handleCommand = async (status: string, id: number) => {
  try {
    await store.updateBucketItem(id, { status: status as any });
    ElMessage.success("状态更新成功");
  } catch (error) {
    ElMessage.error("更新失败");
  }
};

const submit = async () => {
  if (!form.title) {
    ElMessage.warning("请填写愿望内容");
    return;
  }
  
  loading.value = true;
  try {
    await store.createBucketItem(form);
    ElMessage.success("许愿成功！");
    showAddDialog.value = false;
    form.title = "";
    form.description = "";
    form.icon = "✨";
  } catch (error) {
    ElMessage.error("保存失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.bucket-page {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.bucket-head {
  padding: 24px;
  margin-bottom: 20px;
}

.head-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bucket-head h1 {
  margin: 0 0 8px;
  font-size: 32px;
}

.bucket-head p {
  margin: 0;
  color: var(--text-sub);
}

.bucket-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px;
  margin-bottom: 24px;
  text-align: center;
}

.stat-item h3 {
  font-size: 32px;
  margin: 0;
  color: var(--text-main);
}

.stat-item p {
  margin: 4px 0 0;
  color: var(--text-sub);
  font-size: 14px;
}

.stat-item.completed h3 {
  color: var(--primary-color);
}

.bucket-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.bucket-card {
  padding: 16px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.bucket-card.completed {
  background: #fdf6f8;
  border-color: #ffeef2;
}

.bucket-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.05);
}

.card-icon {
  font-size: 32px;
  background: #fff;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.03);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 6px;
  font-size: 18px;
}

.card-content p {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--text-sub);
  line-height: 1.5;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date {
  font-size: 12px;
  color: var(--text-sub);
}

.more-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-sub);
  padding: 0 8px;
}
</style>
