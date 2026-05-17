<template>
  <main class="page-frame">
    <!-- PageHeader: 轻量 -->
    <header class="page-header fade-up">
      <div>
        <h1>时光时间线</h1>
        <p>把每次约会、旅行、深夜小事都串成一条长长的温柔轨迹。</p>
      </div>
    </header>

    <!-- FilterBar: 轻量筛选 -->
    <section class="filter-bar soft-card fade-up">
      <el-input v-model="keyword" clearable placeholder="搜索关键字（如：海边、做饭）" style="flex:1; min-width:180px">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="mood" clearable placeholder="按心情筛选" style="width:150px">
        <el-option label="心动" value="心动" />
        <el-option label="治愈" value="治愈" />
        <el-option label="浪漫" value="浪漫" />
      </el-select>
      <el-switch
        v-model="onlyVideo"
        inline-prompt
        active-text="仅视频"
        inactive-text="全部"
      />
    </section>

    <!-- Timeline content -->
    <el-timeline class="timeline-list">
      <el-timeline-item
        v-for="(item, index) in filteredMoments"
        :key="item.id"
        placement="top"
        :timestamp="item.date"
        color="#e49bab"
      >
        <MomentCard 
          :item="item" 
          :index="index" 
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </el-timeline-item>
    </el-timeline>

    <!-- Edit Dialog -->
    <AddMomentForm 
      v-model="editDialogVisible" 
      :edit-data="currentEditItem"
      @success="store.fetchMoments"
    />
  </main>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import MomentCard from "../components/MomentCard.vue";
import AddMomentForm from "../components/AddMomentForm.vue";
import { useLoveStore, type MomentItem } from "../stores/useLoveStore";
import { ElMessageBox, ElMessage } from "element-plus";
import { Search } from "@element-plus/icons-vue";

const store = useLoveStore();
const keyword = ref("");
const mood = ref("");
const onlyVideo = ref(false);

const editDialogVisible = ref(false);
const currentEditItem = ref<MomentItem | null>(null);

onMounted(() => {
  store.fetchMoments();
});

const handleEdit = (item: MomentItem) => {
  currentEditItem.value = item;
  editDialogVisible.value = true;
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条珍贵的回忆吗？删除后无法恢复哦。',
      '删除提醒',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '留着',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    await store.deleteMoment(id);
    ElMessage.success("回忆已删除");
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error("删除失败");
    }
  }
};

const filteredMoments = computed(() => {
  return store.moments.filter((item) => {
    const matchedKeyword = keyword.value
      ? item.title.includes(keyword.value) || item.summary.includes(keyword.value)
      : true;
    const matchedMood = mood.value ? item.mood === mood.value : true;
    const matchedVideo = onlyVideo.value ? item.hasVideo : true;
    return matchedKeyword && matchedMood && matchedVideo;
  });
});
</script>

<style scoped>
.timeline-list {
  margin-top: 4px;
}

:deep(.el-timeline-item__timestamp) {
  color: #9a7a72;
}
</style>
