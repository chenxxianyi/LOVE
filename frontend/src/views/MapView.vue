<template>
  <div class="map-page">
    <header class="map-head soft-card fade-up">
      <h1 class="title-font">恋爱足迹地图</h1>
      <p>记录我们一起走过的每一个角落，点亮属于我们的世界。</p>
    </header>

    <div class="map-container soft-card fade-up">
      <l-map
        ref="map"
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
          <l-popup>
            <div class="map-popup">
              <img v-if="moment.images.length > 0" :src="moment.images[0]" class="popup-img" />
              <h4>{{ moment.title }}</h4>
              <p class="popup-meta">{{ moment.date }} @ {{ moment.location }}</p>
              <p class="popup-desc">{{ moment.summary.slice(0, 40) }}...</p>
            </div>
          </l-popup>
        </l-marker>
      </l-map>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import { useLoveStore } from "../stores/useLoveStore";

const store = useLoveStore();
const zoom = ref(5);
const center = ref<[number, number]>([35, 105]); // Default center for China

const momentsWithCoords = computed(() => {
  return store.moments.filter(m => m.latitude && m.longitude);
});

onMounted(async () => {
  // Always fetch fresh moments to ensure we have coordinates
  await store.fetchMoments();
  
  // If we have moments with coords, center map on the first one
  if (momentsWithCoords.value.length > 0) {
    const first = momentsWithCoords.value[0];
    center.value = [parseFloat(first.latitude!), parseFloat(first.longitude!)];
    zoom.value = 10;
  }
});
</script>

<style scoped>
.map-page {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.map-head {
  padding: 20px;
}

.map-head h1 {
  margin: 0 0 6px;
  font-size: clamp(32px, 5vw, 48px);
}

.map-head p {
  margin: 0;
  color: var(--text-sub);
}

.map-container {
  flex: 1;
  overflow: hidden;
  padding: 0;
  border-radius: 14px;
}

.map-popup {
  width: 200px;
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
  color: var(--primary-color);
}

.popup-meta {
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 4px;
}

.popup-desc {
  font-size: 13px;
  margin: 0;
}
</style>
