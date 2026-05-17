<template>
  <main class="page-frame">
    <!-- PageHeader -->
    <header class="page-header fade-up">
      <div>
        <h1>愿望清单</h1>
        <p>一起去完成的100件小事，记录每一个实现的梦想。</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" round @click="showAddDialog = true">许个愿望</el-button>
      </div>
    </header>

    <!-- MetricStrip -->
    <section class="metric-strip soft-card fade-up">
      <div class="metric-item">
        <div class="metric-value title-font">{{ pendingCount }}</div>
        <div class="metric-label">未完成</div>
      </div>
      <div class="metric-item">
        <div class="metric-value title-font">{{ plannedCount }}</div>
        <div class="metric-label">计划中</div>
      </div>
      <div class="metric-item">
        <div class="metric-value title-font" style="color:var(--accent)">{{ completedCount }}</div>
        <div class="metric-label">已实现</div>
      </div>
    </section>

    <!-- CompactItemCard Grid -->
    <div class="item-grid">
      <div
        v-for="(item, index) in store.bucketList"
        :key="item.id"
        class="compact-item soft-card fade-up"
        :class="{ 'is-completed': item.status === 'completed' }"
        :style="{ animationDelay: `${index * 40}ms` }"
      >
        <div class="compact-icon">{{ item.icon }}</div>
        <div class="compact-body">
          <h3 class="compact-title">{{ item.title }}</h3>
          <p v-if="item.description" class="compact-desc">{{ item.description }}</p>
          <div class="card-meta">
            <el-tag size="small" :type="getStatusType(item.status)">
              {{ getStatusText(item.status) }}
            </el-tag>
            <span v-if="item.completed_at" class="meta-date">
              {{ item.completed_at.split(" ")[0] }} 达成
            </span>
          </div>
        </div>
        <div class="compact-action">
          <el-dropdown trigger="click" @command="(cmd: string) => handleCommand(cmd, item.id)">
            <el-button size="small" circle>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
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
  </main>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";
import { MoreFilled } from "@element-plus/icons-vue";

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
/* ── 卡片元数据微调 ── */
.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.meta-date {
  font-size: 12px;
  color: var(--text-sub);
}

/* ── 已完成状态 ── */
.compact-item.is-completed {
  opacity: 0.7;
  border-color: var(--accent-light, rgba(255, 179, 198, 0.2));
}
</style>
