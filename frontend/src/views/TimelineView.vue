<template>
  <section class="timeline-page">
    <header class="timeline-head soft-card fade-up">
      <h1 class="title-font">时光时间线</h1>
      <p>把每次约会、旅行、深夜小事都串成一条长长的温柔轨迹。</p>
    </header>

    <section class="filters soft-card fade-up">
      <el-input v-model="keyword" clearable placeholder="搜索关键字（如：海边、做饭）">
        <template #prefix>🔎</template>
      </el-input>
      <el-select v-model="mood" clearable placeholder="按心情筛选">
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

    <el-timeline class="timeline-list">
      <el-timeline-item
        v-for="(item, index) in filteredMoments"
        :key="item.id"
        placement="top"
        :timestamp="item.date"
        color="#e49bab"
      >
        <MomentCard :item="item" :index="index" />
      </el-timeline-item>
    </el-timeline>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import MomentCard from "../components/MomentCard.vue";
import { useLoveStore } from "../stores/useLoveStore";

const store = useLoveStore();
const keyword = ref("");
const mood = ref("");
const onlyVideo = ref(false);

onMounted(() => {
  store.fetchMoments();
});

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
.timeline-page {
  padding-bottom: 20px;
}

.timeline-head {
  padding: 20px;
}

.timeline-head h1 {
  margin: 0 0 6px;
  font-size: clamp(32px, 5vw, 48px);
}

.timeline-head p {
  margin: 0;
  color: var(--text-sub);
}

.filters {
  margin-top: 14px;
  padding: 14px;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 180px 120px;
  gap: 10px;
  align-items: center;
}

.timeline-list {
  margin-top: 18px;
}

:deep(.el-timeline-item__timestamp) {
  color: #9a7a72;
}

@media (max-width: 900px) {
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>
