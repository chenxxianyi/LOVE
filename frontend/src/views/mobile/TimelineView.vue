<template>
    <div class="mobile-timeline-page">
        <van-nav-bar title="时光时间线" left-arrow @click-left="$router.back()" fixed placeholder class="nav-bg-blur" />

        <div class="page-header">
            <p class="subtitle">把每次约会、旅行、深夜小事都串成一条长长的温柔轨迹。</p>
        </div>

        <!-- Sticky Filters Area -->
        <van-sticky :offset-top="46">
            <div class="filters-wrap">
                <van-search v-model="keyword" placeholder="搜索关键字（如：海边、做饭）" shape="round" background="transparent"
                    class="custom-search" />

                <div class="filter-actions">
                    <van-dropdown-menu class="custom-dropdown" active-color="#ff5e62">
                        <van-dropdown-item v-model="mood" :options="moodOptions" />
                    </van-dropdown-menu>

                    <div class="switch-wrap" @click="onlyVideo = !onlyVideo">
                        <span :class="{ active: onlyVideo }">仅视频</span>
                        <van-switch v-model="onlyVideo" size="18px" active-color="#ff5e62" />
                    </div>
                </div>
            </div>
        </van-sticky>

        <!-- Custom Mobile Timeline (Left-aligned) -->
        <div class="timeline-container">
            <div v-if="filteredMoments.length === 0" class="empty-state">
                <van-empty description="没有找到回忆小结哦~" image="search" />
            </div>

            <div v-for="(item, index) in filteredMoments" :key="item.id" class="timeline-item-wrapper">
                <!-- Timeline Left Line & Dot -->
                <div class="timeline-axis">
                    <div class="timeline-dot"></div>
                    <div class="timeline-line" v-if="index !== filteredMoments.length - 1"></div>
                </div>

                <!-- Timeline Right Content (Moment Card) -->
                <div class="timeline-content">
                    <div class="timeline-date">{{ item.date }}</div>
                    <MobileMomentCard :item="item" @edit="handleEdit" @delete="handleDelete" />
                </div>
            </div>
        </div>

        <van-floating-panel v-model:height="panelHeight" :anchors="[0, 0]" v-if="false">
            <!-- Future placeholder for Add Moment Drawer if needed -->
        </van-floating-panel>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useLoveStore, type MomentItem } from "../../stores/useLoveStore";
import MobileMomentCard from "./components/MobileMomentCard.vue";
import { showConfirmDialog, showSuccessToast, showFailToast } from "vant";

const store = useLoveStore();
const keyword = ref("");
const mood = ref("");
const onlyVideo = ref(false);

const panelHeight = ref(0);

const moodOptions = [
    { text: '全部心情', value: '' },
    { text: '心动', value: '心动' },
    { text: '治愈', value: '治愈' },
    { text: '浪漫', value: '浪漫' },
];

onMounted(() => {
    store.fetchMoments();
});

const handleEdit = (item: MomentItem) => {
    showSuccessToast("手机端暂不支持编辑哦");
};

const handleDelete = async (id: number) => {
    showConfirmDialog({
        title: '删除提醒',
        message: '确定要删除这条珍贵的回忆吗？',
        confirmButtonColor: '#ee0a24'
    }).then(async () => {
        try {
            await store.deleteMoment(id);
            showSuccessToast("回忆已删除");
        } catch {
            showFailToast("删除失败");
        }
    }).catch(() => {
        // on cancel
    });
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
.mobile-timeline-page {
    min-height: 100vh;
    background-color: #fcf8f8;
    /* Soft pink-ish white */
    padding-bottom: 40px;
}

.nav-bg-blur {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
}

:deep(.van-nav-bar__title) {
    font-family: 'Playfair Display', "Noto Serif SC", serif;
    font-weight: bold;
}

.page-header {
    padding: 16px 20px 4px;
}

.subtitle {
    color: #888;
    font-size: 13px;
    line-height: 1.6;
    margin: 0;
}

/* Filters */
.filters-wrap {
    background: rgba(252, 248, 248, 0.95);
    backdrop-filter: blur(8px);
    padding: 8px 16px 16px;
    z-index: 10;
}

.custom-search {
    padding: 0 0 12px 0;
}

:deep(.van-search__content) {
    background-color: #fff;
    border: 1px solid rgba(255, 94, 98, 0.1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.filter-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.custom-dropdown {
    flex: 1;
    background: transparent;
    height: 32px;
}

:deep(.van-dropdown-menu__bar) {
    background: #fff;
    height: 36px;
    border-radius: 18px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    border: 1px solid rgba(255, 94, 98, 0.1);
}

.switch-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #fff;
    height: 36px;
    padding: 0 12px;
    border-radius: 18px;
    margin-left: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    border: 1px solid rgba(255, 94, 98, 0.1);
    font-size: 13px;
    color: #666;
}

.switch-wrap span.active {
    color: #ff5e62;
    font-weight: 500;
}

/* Timeline Layout */
.timeline-container {
    padding: 16px 16px 40px 16px;
}

.timeline-item-wrapper {
    display: flex;
    position: relative;
    margin-bottom: 24px;
}

.timeline-axis {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 24px;
    margin-right: 12px;
    flex-shrink: 0;
}

.timeline-dot {
    width: 12px;
    height: 12px;
    background-color: #e49bab;
    border-radius: 50%;
    border: 3px solid rgba(228, 155, 171, 0.3);
    background-clip: padding-box;
    margin-top: 4px;
    /* Align with date text text-top */
    z-index: 2;
}

.timeline-line {
    width: 2px;
    background: linear-gradient(to bottom, rgba(228, 155, 171, 0.5), rgba(228, 155, 171, 0.1));
    flex: 1;
    margin-top: 4px;
    margin-bottom: -28px;
    /* extend to next dot */
    border-radius: 1px;
}

.timeline-content {
    flex: 1;
    min-width: 0;
    /* Prevent overflow */
}

.timeline-date {
    font-size: 13px;
    color: #9a7a72;
    margin-bottom: 8px;
    font-weight: 500;
    letter-spacing: 0.5px;
}

.empty-state {
    padding: 60px 0;
}
</style>
