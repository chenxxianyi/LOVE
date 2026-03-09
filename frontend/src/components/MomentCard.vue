<template>
  <article class="moment-card soft-card fade-up">
    <div class="cover-wrap" :style="{ animationDelay: `${(index || 0) * 60}ms` }">
      <img :src="item.images[0]" :alt="item.title" />
      <span v-if="item.hasVideo" class="video-tag">VIDEO</span>
    </div>

    <div class="content">
      <div class="meta">
        <span class="glow-chip">{{ item.date }}</span>
        <span class="glow-chip">{{ item.location }}</span>
        <span class="glow-chip">心情 · {{ item.mood }}</span>
      </div>
      <h3 class="title-font">{{ item.title }}</h3>
      <p>{{ item.summary }}</p>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { MomentItem } from "../stores/useLoveStore";

defineProps<{
  item: MomentItem;
  index?: number;
}>();
</script>

<style scoped>
.moment-card {
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.moment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 26px rgba(212, 155, 142, 0.25);
}

.cover-wrap {
  position: relative;
  aspect-ratio: 16 / 9;
}

.cover-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-tag {
  position: absolute;
  right: 10px;
  top: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(71, 42, 46, 0.75);
  color: #fff;
  font-size: 11px;
}

.content {
  padding: 14px 16px 16px;
}

.meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

h3 {
  margin: 10px 0 8px;
  font-size: 26px;
  line-height: 1.1;
}

p {
  margin: 0;
  color: var(--text-sub);
  font-size: 14px;
  line-height: 1.7;
}
</style>
