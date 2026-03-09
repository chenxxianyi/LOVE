<template>
  <div class="report-page">
    <div class="report-container soft-card fade-up" v-if="store.reportData">
      <div class="slides" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
        
        <!-- Slide 1: Intro -->
        <div class="slide intro">
          <h1>💖</h1>
          <h2>我们的恋爱报告</h2>
          <p>这一年，我们一起走过的点点滴滴</p>
          <el-button round @click="nextSlide">开始回顾</el-button>
        </div>

        <!-- Slide 2: Moments -->
        <div class="slide">
          <div class="stat-big">{{ store.reportData.total_moments }}</div>
          <h3>个心动瞬间</h3>
          <p>每一次记录，都是爱的证明</p>
        </div>

        <!-- Slide 3: Mood -->
        <div class="slide">
          <h3>这一年，我们的关键词是</h3>
          <div class="stat-big highlight">{{ store.reportData.top_mood || '爱' }}</div>
          <p>无论开心还是难过，都有你在身边</p>
        </div>

        <!-- Slide 4: Locations -->
        <div class="slide">
          <h3>我们的足迹遍布</h3>
          <div class="stat-big">{{ store.reportData.total_locations }}</div>
          <h3>个地方</h3>
          <p>世界很大，想和你一起去看看</p>
        </div>

        <!-- Slide 5: Images -->
        <div class="slide">
          <h3>我们一共拍了</h3>
          <div class="stat-big">{{ store.reportData.total_images }}</div>
          <h3>张照片</h3>
          <p>定格的瞬间，是永恒的回忆</p>
        </div>

        <!-- Slide 6: Days -->
        <div class="slide">
          <h3>我们已经相爱了</h3>
          <div class="stat-big highlight">{{ store.reportData.days_together }}</div>
          <h3>天</h3>
          <p>从 {{ store.reportData.latest_moment_date?.split(' ')[0] }} 到永远</p>
        </div>

        <!-- Slide 7: End -->
        <div class="slide end">
          <h2>未来的路，也要一起走</h2>
          <p>To be continued...</p>
          <div class="actions">
            <el-button round @click="currentSlide = 0">再看一遍</el-button>
            <RouterLink to="/">
              <el-button type="primary" round>回到首页</el-button>
            </RouterLink>
          </div>
        </div>

      </div>

      <!-- Navigation Dots -->
      <div class="dots">
        <span 
          v-for="i in 7" 
          :key="i" 
          class="dot" 
          :class="{ active: currentSlide === i - 1 }"
          @click="currentSlide = i - 1"
        ></span>
      </div>
      
      <!-- Arrows -->
      <div class="arrow left" @click="prevSlide" v-if="currentSlide > 0">❮</div>
      <div class="arrow right" @click="nextSlide" v-if="currentSlide < 6">❯</div>
    </div>
    
    <div v-else class="loading">
      <el-skeleton animated />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";

const store = useLoveStore();
const currentSlide = ref(0);

onMounted(() => {
  store.fetchReport();
});

const nextSlide = () => {
  if (currentSlide.value < 6) {
    currentSlide.value++;
  }
};

const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--;
  }
};
</script>

<style scoped>
.report-page {
  height: calc(100vh - 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.report-container {
  width: 100%;
  max-width: 600px;
  height: 80vh;
  max-height: 800px;
  background: #fff;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.slides {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease-in-out;
}

.slide {
  min-width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  background: linear-gradient(180deg, #fff0f3 0%, #fff 100%);
}

.slide.intro h1 {
  font-size: 80px;
  margin: 0 0 20px;
}

.slide.end h2 {
  color: var(--primary-color);
  margin-bottom: 20px;
}

.stat-big {
  font-size: 80px;
  font-weight: 800;
  color: var(--text-main);
  margin: 20px 0;
  font-family: 'Times New Roman', serif;
}

.stat-big.highlight {
  color: var(--primary-color);
}

h2 {
  font-size: 32px;
  margin: 0 0 10px;
}

h3 {
  font-size: 24px;
  margin: 0;
  font-weight: normal;
  color: var(--text-sub);
}

p {
  color: var(--text-sub);
  margin-top: 10px;
  font-size: 16px;
}

.dots {
  position: absolute;
  bottom: 20px;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.dot.active {
  background: var(--primary-color);
  transform: scale(1.2);
}

.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  color: var(--text-sub);
  cursor: pointer;
  padding: 20px;
  user-select: none;
}

.arrow:hover {
  color: var(--primary-color);
}

.arrow.left { left: 0; }
.arrow.right { right: 0; }

.actions {
  display: flex;
  gap: 16px;
  margin-top: 40px;
}

.loading {
  width: 100%;
  max-width: 600px;
  padding: 20px;
}
</style>
