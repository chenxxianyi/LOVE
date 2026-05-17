<template>
  <main class="page-frame-wide">
    <!-- PageHeader: 轻量 -->
    <header class="page-header fade-up">
      <div>
        <h1>恋爱足迹地图</h1>
        <p>记录我们一起走过的每一个角落，点亮属于我们的世界。</p>
      </div>
      <div class="page-actions" v-if="momentsWithCoords.length > 0">
        <span class="stat-chip">📍 {{ momentsWithCoords.length }} 足迹</span>
        <span class="stat-chip">🗺️ {{ uniqueLocations }} 城市</span>
      </div>
    </header>

    <!-- 无数据状态 -->
    <div v-if="momentsWithCoords.length === 0 && !loading" class="empty-map soft-card fade-up">
      <div class="empty-icon">🗺️</div>
      <h3>地图上还没有你们的足迹</h3>
      <p>在新增回忆时填写地点，系统会自动定位，让足迹点亮地图～</p>
    </div>

    <div v-else class="map-container soft-card fade-up">
      <!-- 地理编码进行中提示 -->
      <div v-if="geocodingCount > 0" class="geocoding-bar">
        📡 正在自动定位历史记录... (剩余 {{ geocodingCount }} 条)
      </div>
      <l-map
        ref="mapRef"
        v-model:zoom="zoom"
        :center="center"
        :use-global-leaflet="false"
      >
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          layer-type="base"
          name="OpenStreetMap"
        ></l-tile-layer>

        <l-marker
          v-for="moment in momentsWithCoords"
          :key="moment.id"
          :lat-lng="[parseFloat(moment.latitude!), parseFloat(moment.longitude!)]"
        >
          <l-icon
            :icon-url="heartIconUrl"
            :icon-size="[36, 36]"
            :icon-anchor="[18, 36]"
            :popup-anchor="[0, -36]"
          />
          <l-popup>
            <div class="map-popup">
              <img v-if="moment.images.length > 0" :src="moment.images[0]" class="popup-img" />
              <h4>{{ moment.title }}</h4>
              <p class="popup-meta">{{ moment.date }} @ {{ moment.location }}</p>
              <p class="popup-mood">{{ moodEmoji(moment.mood) }} {{ moment.mood }}</p>
              <p class="popup-desc">{{ moment.summary.slice(0, 50) }}{{ moment.summary.length > 50 ? '...' : '' }}</p>
            </div>
          </l-popup>
        </l-marker>
      </l-map>
    </div>

    <!-- 足迹列表 -->
    <div v-if="momentsWithCoords.length > 0" class="footprint-list soft-card fade-up">
      <h3 class="footprint-title">📍 足迹列表</h3>
      <div class="footprint-grid">
        <div
          v-for="moment in momentsWithCoords"
          :key="moment.id"
          class="footprint-item"
          @click="flyTo(moment)"
        >
          <span class="fp-mood">{{ moodEmoji(moment.mood) }}</span>
          <div class="fp-info">
            <div class="fp-name">{{ moment.location }}</div>
            <div class="fp-date">{{ moment.date.slice(0, 10) }}</div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LMarker, LPopup, LIcon } from "@vue-leaflet/vue-leaflet";
import { useLoveStore } from "../stores/useLoveStore";
import type { MomentItem } from "../stores/useLoveStore";
import axios from "axios";

const store = useLoveStore();
const zoom = ref(5);
const center = ref<[number, number]>([35, 105]);
const loading = ref(true);
const geocodingCount = ref(0);
const mapRef = ref<any>(null);

// 使用 emoji 作为地图标记（转成 SVG Data URL）
const heartIconUrl = computed(() => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36">
    <circle cx="18" cy="18" r="18" fill="#e49bab" opacity="0.25"/>
    <circle cx="18" cy="18" r="13" fill="#e49bab" opacity="0.5"/>
    <circle cx="18" cy="18" r="8" fill="#e45b7a"/>
    <text x="18" y="23" font-size="12" text-anchor="middle">💗</text>
  </svg>`;
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`;
});

const momentsWithCoords = computed(() => {
  return store.moments.filter(
    m => m.latitude && m.longitude &&
    m.latitude.trim() !== "" && m.longitude.trim() !== "" &&
    !isNaN(parseFloat(m.latitude)) && !isNaN(parseFloat(m.longitude))
  );
});

const uniqueLocations = computed(() => {
  const locs = new Set(momentsWithCoords.value.map(m => m.location));
  return locs.size;
});

const moodEmoji = (mood: string) => {
  const map: Record<string, string> = {
    "心动": "💓", "治愈": "🌿", "浪漫": "🌹", "开心": "😊", "难过": "🌧️"
  };
  return map[mood] ?? "✨";
};

const flyTo = (moment: MomentItem) => {
  if (mapRef.value && mapRef.value.leafletObject) {
    mapRef.value.leafletObject.flyTo(
      [parseFloat(moment.latitude!), parseFloat(moment.longitude!)],
      12,
      { duration: 1.5 }
    );
  }
};

// 自动为历史记录补全坐标（串行避免触发速率限制）
const geocodeMissing = async () => {
  const missing = store.moments.filter(
    m => m.location && m.location.trim() !== "" &&
    (!m.latitude || m.latitude.trim() === "" || !m.longitude || m.longitude.trim() === "")
  );
  geocodingCount.value = missing.length;
  for (const m of missing) {
    try {
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(m.location)}&format=json&limit=1`;
      const res = await fetch(url, { headers: { "Accept-Language": "zh-CN,zh;q=0.9" } });
      const data = await res.json();
      if (data && data.length > 0) {
        const lat = parseFloat(data[0].lat).toFixed(6);
        const lng = parseFloat(data[0].lon).toFixed(6);
        await store.updateMoment(m.id, { latitude: lat, longitude: lng });
      }
      // 串行延迟 1s 避免 Nominatim 速率限制
      await new Promise(r => setTimeout(r, 1100));
    } catch (e) {
      // 静默失败，不影响地图展示
    }
    geocodingCount.value--;
  }
};

onMounted(async () => {
  await store.fetchMoments();
  loading.value = false;

  // 异步自动补全缺坐标的历史记录（不阻塞地图渲染）
  geocodeMissing();

  if (momentsWithCoords.value.length > 0) {
    const lats = momentsWithCoords.value.map(m => parseFloat(m.latitude!));
    const lngs = momentsWithCoords.value.map(m => parseFloat(m.longitude!));
    const centerLat = (Math.max(...lats) + Math.min(...lats)) / 2;
    const centerLng = (Math.max(...lngs) + Math.min(...lngs)) / 2;
    center.value = [centerLat, centerLng];
    zoom.value = momentsWithCoords.value.length === 1 ? 12 : 6;
  }
});
</script>

<style scoped>
/* ── 统计芯片 ── */
.stat-chip {
  background: var(--accent-light, rgba(255, 179, 198, 0.15));
  color: var(--accent-text, #D47080);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

/* ── 地图主卡片 (唯一视觉中心) ── */
.map-container {
  height: 560px;
  overflow: hidden;
  padding: 0;
  border-radius: 14px;
  position: relative;
}

.geocoding-bar {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #e49bab;
  color: #c87898;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(228, 155, 171, 0.2);
}

.empty-map {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-sub);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-map h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--text-main, #333);
}

.empty-map p {
  margin: 0;
  font-size: 14px;
}

/* Popup Style */
.map-popup {
  width: 210px;
}

.popup-img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 8px;
}

.map-popup h4 {
  margin: 0 0 4px;
  color: var(--primary-color, #e49bab);
  font-size: 15px;
}

.popup-meta {
  font-size: 12px;
  color: var(--text-sub);
  margin: 0 0 4px;
}

.popup-mood {
  font-size: 12px;
  margin: 0 0 4px;
}

.popup-desc {
  font-size: 13px;
  margin: 0;
  color: var(--text-main, #555);
}

/* Footprint List */
.footprint-list {
  padding: 16px 20px;
}

.footprint-title {
  font-size: 16px;
  margin: 0 0 12px;
  color: var(--text-main, #444);
}

.footprint-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.footprint-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-light, #fce4ec);
  border-radius: 10px;
  padding: 8px 14px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.footprint-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(228, 155, 171, 0.3);
}

.fp-mood {
  font-size: 20px;
}

.fp-info .fp-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main, #333);
}

.fp-info .fp-date {
  font-size: 11px;
  color: var(--text-sub);
}
</style>
