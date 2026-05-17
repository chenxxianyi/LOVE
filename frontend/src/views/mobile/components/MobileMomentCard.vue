<template>
    <div class="mobile-moment-card">
        <!-- Dynamic Mosaic Gallery -->
        <div class="cover-wrap mosaic-gallery" :class="layoutClass" v-if="item.images && item.images.length > 0">
            <div v-for="(imgUrl, i) in displayImages" :key="i" class="mosaic-item" :class="`item-${i}`"
                @click="openGallery(i)">
                <!-- Native img is much more reliable in CSS grids than wrapped components like van-image -->
                <img :src="imgUrl" class="full-image" :class="{ 'img-blur': i === 3 && item.images.length > 4 }"
                    alt="Memory Image" />
                <div v-if="i === 3 && item.images.length > 4" class="more-overlay">
                    +{{ item.images.length - 4 }}
                </div>
            </div>

            <span v-if="item.hasVideo" class="video-tag">
                <van-icon name="play-circle-o" />
            </span>
        </div>

        <div class="card-content">
            <div class="tags-row">
                <span class="van-tag-custom">{{ item.location }}</span>
                <span class="van-tag-custom mood">· {{ item.mood }} ·</span>
            </div>

            <h3 class="title">{{ item.title }}</h3>
            <p class="summary">{{ item.summary }}</p>

            <div class="card-footer">
                <!-- Optional footer actions like edit/delete icon -->
                <span class="delete-icon" @click="$emit('delete', item.id)">
                    <van-icon name="delete-o" />
                </span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { MomentItem } from "../../../stores/useLoveStore";
import { showImagePreview } from "vant";

const props = defineProps<{
    item: MomentItem;
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
            resolve(img.height > img.width);
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
        if (!isFirstPortrait.value && !isSecondPortrait.value) return "layout-2-landscape";
        if (isFirstPortrait.value && isSecondPortrait.value) return "layout-2-portrait";
        return "layout-2-mixed";
    }
    if (len === 3) return isFirstPortrait.value ? "layout-3-portrait" : "layout-3-landscape";
    if (len === 0) return "layout-none";
    return "layout-4-plus";
});

// ---- Lightbox Viewer Logic ----
const openGallery = (index: number) => {
    showImagePreview({
        images: props.item.images,
        startPosition: index,
    });
};
</script>

<style scoped>
.mobile-moment-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    margin-bottom: 8px;
    /* Extra bottom margin inside timeline */
    border: 1px solid rgba(255, 94, 98, 0.05);
}

.cover-wrap {
    position: relative;
    width: 100%;
    background: #fcfcfc;
}

.card-content {
    padding: 14px 16px;
}

/* Tags */
.tags-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}

.van-tag-custom {
    font-size: 11px;
    padding: 2px 8px;
    background-color: #f7f8fa;
    color: #666;
    border-radius: 10px;
}

.van-tag-custom.mood {
    background-color: rgba(255, 94, 98, 0.05);
    color: #ff5e62;
}

/* Text */
.title {
    margin: 0 0 6px 0;
    font-size: 16px;
    color: #333;
    font-weight: 600;
    line-height: 1.4;
}

.summary {
    margin: 0;
    font-size: 13px;
    color: #666;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
}

.delete-icon {
    color: #ccc;
    font-size: 16px;
    padding: 4px;
}

.delete-icon:active {
    color: #ee0a24;
}

/* Video Tag */
.video-tag {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    padding: 2px 6px;
    border-radius: 12px;
    font-size: 12px;
    display: flex;
    align-items: center;
    backdrop-filter: blur(4px);
    z-index: 2;
}

/* Base Mosaic Gallery Styles */
.mosaic-gallery {
    display: grid;
    gap: 2px;
}

.mosaic-item {
    position: relative;
    overflow: hidden;
}

.img-blur {
    filter: blur(3px) brightness(0.7);
}

.full-image {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
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
    font-size: 20px;
    font-weight: bold;
    background: rgba(0, 0, 0, 0.2);
    pointer-events: none;
}

/* ---- Layout Specifics ---- */
.layout-none {
    display: none;
}

/* 1 Image */
.layout-1-landscape {
    display: block;
    aspect-ratio: 16 / 9;
}

.layout-1-portrait {
    display: block;
    height: clamp(220px, 55vh, 420px);
}

.layout-1-portrait .mosaic-item {
    height: 100%;
    background: #f8f2f0;
}

.layout-1-portrait .full-image {
    height: 100%;
    object-fit: contain;
    background: #f8f2f0;
}

/* 2 Images */
.layout-2-landscape {
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr;
    aspect-ratio: 4 / 3;
}

.layout-2-portrait {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr;
    aspect-ratio: 4 / 3;
}

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

.layout-3-landscape .item-0 {
    grid-column: 1 / 3;
}

.layout-3-portrait {
    grid-template-columns: 2fr 1fr;
    grid-template-rows: 1fr 1fr;
    aspect-ratio: 16 / 9;
}

.layout-3-portrait .item-0 {
    grid-row: 1 / 3;
}

/* 4+ Images */
.layout-4-plus {
    grid-template-columns: 3fr 1fr;
    grid-template-rows: 1fr 1fr 1fr;
    aspect-ratio: 16 / 9;
}

.layout-4-plus .item-0 {
    grid-row: 1 / 4;
}
</style>
