<template>
  <article class="moment-card soft-card fade-up">
    <!-- Dynamic Mosaic Gallery -->
    <div 
      class="cover-wrap mosaic-gallery" 
      :class="layoutClass"
      :style="{ animationDelay: `${(index || 0) * 60}ms` }"
    >
      <div 
        v-for="(imgUrl, i) in displayImages" 
        :key="i"
        class="mosaic-item"
        :class="`item-${i}`"
        @click="openGallery(i)"
      >
        <img :src="imgUrl" :alt="`${item.title} - ${i}`" loading="lazy" :class="{ 'img-blur': i === 3 && item.images.length > 4 }" />
        <div v-if="i === 3 && item.images.length > 4" class="more-overlay">
          +{{ item.images.length - 4 }}
        </div>
      </div>

      <span v-if="item.hasVideo" class="video-tag">VIDEO</span>
      
      <div class="card-actions">
        <button class="action-btn edit" @click.stop="$emit('edit', item)">
          <el-icon><Edit /></el-icon>
        </button>
        <button class="action-btn delete" @click.stop="$emit('delete', item.id)">
          <el-icon><Delete /></el-icon>
        </button>
      </div>
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

    <!-- ImageViewer for Fullscreen Gallery -->
    <teleport to="body">
      <el-image-viewer
        v-if="showViewer"
        :url-list="item.images"
        :initial-index="viewerIndex"
        @close="closeGallery"
        :z-index="9999"
        :hide-on-click-modal="true"
      />
    </teleport>
  </article>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { MomentItem } from "../stores/useLoveStore";
import { Edit, Delete } from "@element-plus/icons-vue";

const props = defineProps<{
  item: MomentItem;
  index?: number;
}>();

defineEmits<{
  (e: "edit", item: MomentItem): void;
  (e: "delete", id: number): void;
}>();

// ---- Mosaic Layout Logic ----
const displayImages = computed(() => props.item.images.slice(0, 4));

const isFirstPortrait = ref(false);
const isSecondPortrait = ref(false);

const checkImageAspect = (url: string): Promise<boolean> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      resolve(img.height > img.width); // true if portrait
    };
    img.onerror = () => resolve(false);
    img.src = url;
  });
};

onMounted(async () => {
  if (props.item.images.length > 0) {
    isFirstPortrait.value = await checkImageAspect(props.item.images[0]);
  }
  if (props.item.images.length > 1) {
    isSecondPortrait.value = await checkImageAspect(props.item.images[1]);
  }
});

const layoutClass = computed(() => {
  const len = props.item.images.length;
  if (len === 1) return isFirstPortrait.value ? "layout-1-portrait" : "layout-1-landscape";
  if (len === 2) {
    if (!isFirstPortrait.value && !isSecondPortrait.value) return "layout-2-landscape"; // Both horizontal -> stack vertically
    if (isFirstPortrait.value && isSecondPortrait.value) return "layout-2-portrait";   // Both vertical -> stack horizontally
    return "layout-2-mixed"; // One each -> asymmetrical
  }
  if (len === 3) return isFirstPortrait.value ? "layout-3-portrait" : "layout-3-landscape";
  return "layout-4-plus"; // 4 or more
});

// ---- Lightbox Viewer Logic ----
const showViewer = ref(false);
const viewerIndex = ref(0);

const openGallery = (index: number) => {
  viewerIndex.value = index;
  showViewer.value = true;
};

const closeGallery = () => {
  showViewer.value = false;
};
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
  width: 100%;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  background: var(--bg-soft);
}

.content {
  padding: 20px 24px 24px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

/* Base Mosaic Gallery Styles */
.mosaic-gallery {
  display: grid;
  gap: 3px;
}

.mosaic-item {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  background: var(--bg-soft);
}

/* 防止 hover 放大的图片逸出导致外围白边或圆角丢失 */
.mosaic-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  will-change: transform;
  display: block;
}

.mosaic-item:hover img {
  transform: scale(1.03); /* 降低放大倍率防止显得过于拥挤 */
}

.img-blur {
  filter: blur(4px) brightness(0.8);
}

.more-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
  font-family: var(--font-title);
  background: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.card-actions {
  position: absolute;
  right: 12px;
  bottom: 12px;
  display: flex;
  gap: 10px;
  opacity: 0;
  transform: translateY(5px);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 10;
  pointer-events: auto;
}

.moment-card:hover .card-actions {
  opacity: 1;
  transform: translateY(0);
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.15); /* 微弱的玻璃内发光边缘 */
  background: rgba(0, 0, 0, 0.45); /* 深色半透底，保证在白色白云背景下清晰可见 */
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 11;
  font-size: 16px;
}

.action-btn:hover {
  transform: scale(1.15) translateY(-2px);
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
  border-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.action-btn.delete:hover {
  color: #f56c6c;
}

/* ---- Layout Specifics ---- */

/* 1 Image */
.layout-1-landscape {
  display: block;
  aspect-ratio: 16 / 9;
}
.layout-1-portrait {
  display: block;
  height: clamp(280px, 60vh, 640px);
}

.layout-1-portrait .mosaic-item {
  height: 100%;
  background: #f8f2f0;
}

.layout-1-portrait .mosaic-item img {
  height: 100%;
  object-fit: contain;
  background: #f8f2f0;
}

/* 2 Images */
/* 横图上下等分：改用长宽比锁定而不要定死高度 */
.layout-2-landscape {
  grid-template-rows: 1fr 1fr;
  grid-template-columns: 1fr;
  aspect-ratio: 4 / 3; 
}
/* 竖图左右等分 */
.layout-2-portrait {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr;
  aspect-ratio: 4 / 3;
}
/* 一横一竖 */
.layout-2-mixed {
  grid-template-columns: 2fr 1fr;
  grid-template-rows: 1fr;
  aspect-ratio: 16 / 9;
}

/* 3 Images */
.layout-3-landscape {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 2fr 1fr;
  aspect-ratio: 4 / 3;
}
.layout-3-landscape .item-0 { grid-column: 1 / 3; }

.layout-3-portrait {
  grid-template-columns: 2fr 1fr;
  grid-template-rows: 1fr 1fr;
  aspect-ratio: 16 / 9; 
}
.layout-3-portrait .item-0 { grid-row: 1 / 3; }

/* 4+ Images */
.layout-4-plus {
  grid-template-columns: 3fr 1fr;
  grid-template-rows: 1fr 1fr 1fr;
  aspect-ratio: 16 / 9;
}
.layout-4-plus .item-0 { grid-row: 1 / 4; }
</style>
