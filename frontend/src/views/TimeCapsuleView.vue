<template>
  <div class="capsule-page">
    <header class="capsule-head soft-card fade-up">
      <div class="head-content">
        <div>
          <h1 class="title-font">时光胶囊</h1>
          <p>给未来的我们写一封信，封存此刻的心意。</p>
        </div>
        <el-button type="primary" round size="large" @click="showAddDialog = true">
          埋下胶囊
        </el-button>
      </div>
    </header>

    <div class="capsule-grid">
      <div
        v-for="(item, index) in store.capsules"
        :key="item.id"
        class="capsule-card soft-card fade-up"
        :class="{ locked: !item.is_opened }"
        :style="{ animationDelay: `${index * 50}ms` }"
        @click="openCapsule(item)"
      >
        <!-- Status Badge -->
        <div class="status-badge">
          <span class="icon">{{ item.is_opened ? '🔓' : '🔒' }}</span>
          <span class="label">{{ item.is_opened ? '已开启' : '封印中' }}</span>
        </div>
        
        <!-- Decorative elements for glass/card effect -->
        <div class="card-glow"></div>
        <div class="card-noise"></div>

        <div class="card-content">
          <p class="to">To: {{ item.receiver }}</p>
          <div class="preview">
             <p v-if="item.is_opened" class="unlocked-text">{{ item.content }}</p>
             <p v-else class="locked-text">
               此信件将于<br/>
               <span class="highlight date-chip">{{ item.open_at.split(' ')[0] }}</span><br/>
               开启
             </p>
          </div>
          <p class="from">From: {{ item.sender }}</p>
        </div>

        <div class="card-footer">
          <small>埋藏于 {{ item.created_at.split(' ')[0] }}</small>
        </div>
      </div>
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="showAddDialog" title="埋藏时光胶囊" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="收信人">
          <el-input v-model="form.receiver" placeholder="写给谁？" />
        </el-form-item>
        <el-form-item label="寄信人">
          <el-input v-model="form.sender" placeholder="你是谁？" />
        </el-form-item>
        <el-form-item label="开启时间">
          <el-date-picker
            v-model="form.open_at"
            type="datetime"
            placeholder="选择未来的开启时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="信件内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="写下你想对未来传达的话..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="submit" :loading="loading">封存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Read Dialog -->
    <el-dialog v-model="showReadDialog" title="时光胶囊" width="500px">
      <div class="letter-content" v-if="currentCapsule">
        <div class="letter-head">
          <p><strong>To: {{ currentCapsule.receiver }}</strong></p>
          <p class="date">{{ currentCapsule.open_at }}</p>
        </div>
        <div class="letter-body">
          {{ currentCapsule.content }}
        </div>
        <div class="letter-foot">
          <p><strong>From: {{ currentCapsule.sender }}</strong></p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import type { TimeCapsule } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const store = useLoveStore();
const showAddDialog = ref(false);
const showReadDialog = ref(false);
const loading = ref(false);
const currentCapsule = ref<TimeCapsule | null>(null);

const form = reactive({
  sender: "",
  receiver: "",
  content: "",
  open_at: "",
});

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now();
};

onMounted(() => {
  store.fetchCapsules();
});

const openCapsule = (item: TimeCapsule) => {
  if (item.is_opened) {
    currentCapsule.value = item;
    showReadDialog.value = true;
  } else {
    ElMessage.warning(`这封信还没到开启时间哦，请耐心等待至 ${item.open_at}`);
  }
};

const submit = async () => {
  if (!form.sender || !form.receiver || !form.content || !form.open_at) {
    ElMessage.warning("请填写完整信件信息");
    return;
  }
  
  loading.value = true;
  try {
    await store.createCapsule(form);
    ElMessage.success("胶囊已成功埋藏！");
    showAddDialog.value = false;
    // Reset form
    form.sender = "";
    form.receiver = "";
    form.content = "";
    form.open_at = "";
  } catch (error) {
    ElMessage.error("埋藏失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.capsule-page {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.capsule-head {
  padding: 24px;
  margin-bottom: 20px;
}

.head-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.capsule-head h1 {
  margin: 0 0 8px;
  font-size: 32px;
}

.capsule-head p {
  margin: 0;
  color: var(--text-sub);
}

.capsule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.capsule-card {
  padding: 24px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bouncy transition */
  display: flex;
  flex-direction: column;
  height: 220px;
  border-radius: 20px;
  color: var(--capsule-ink);
  --capsule-ink: #2a1714;
  --capsule-ink-strong: #1a0d0b;
  --capsule-ink-muted: #4a2f2b;
  --capsule-divider: rgba(26, 13, 11, 0.18);
  
  /* Unlocked defaults (warm / light) */
  background: linear-gradient(135deg, rgba(255, 240, 240, 0.9) 0%, rgba(255, 255, 255, 0.6) 100%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 32px rgba(228, 155, 171, 0.15);
  backdrop-filter: blur(12px);
}

/* Glassmorphism Shine */
.capsule-card::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%);
  transform: skewX(-25deg);
  transition: all 0.6s ease;
  z-index: 1;
}

.capsule-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 15px 35px rgba(228, 155, 171, 0.25);
}

.capsule-card:hover::before {
  left: 200%;
}

/* Locked variations */
.capsule-card.locked {
  background: linear-gradient(135deg, rgba(235, 238, 245, 0.85) 0%, rgba(248, 250, 252, 0.6) 100%);
  box-shadow: 0 8px 32px rgba(144, 147, 153, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.6);
  --capsule-ink: #262b36;
  --capsule-ink-strong: #1a1f2b;
  --capsule-ink-muted: #4b5563;
  --capsule-divider: rgba(26, 31, 43, 0.18);
}

.capsule-card.locked:hover {
  box-shadow: 0 15px 35px rgba(144, 147, 153, 0.2);
}

/* Status Badge Ribbon */
.status-badge {
  position: absolute;
  top: 16px;
  right: -8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px 6px 12px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px 0 0 20px;
  box-shadow: -2px 4px 10px rgba(0,0,0,0.05);
  z-index: 2;
  /* Unlocked style */
  background: linear-gradient(90deg, var(--pink-deep) 0%, #ff6f82 100%);
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.35);
}

.capsule-card.locked .status-badge {
  /* Locked style */
  background: linear-gradient(90deg, #909399 0%, #c0c4cc 100%);
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Content Layout */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  z-index: 2;
  position: relative;
}

.to, .from {
  font-family: "Cormorant Garamond", "Noto Serif SC", serif;
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  color: var(--capsule-ink-strong);
}

.from {
  text-align: right;
}

.preview {
  flex: 1;
  margin: 16px 0;
  font-size: 15px;
  line-height: 1.6;
  overflow: hidden;
  position: relative;
  color: var(--capsule-ink);
}

.unlocked-text {
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--capsule-ink-strong);
  letter-spacing: 0.2px;
  text-shadow: none;
}

.locked-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  font-size: 14px;
  color: var(--capsule-ink-muted);
  letter-spacing: 1px;
}

.date-chip {
  display: inline-block;
  margin: 8px 0;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  color: #606266;
  font-family: monospace;
  font-size: 16px;
  font-weight: bold;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #ebeef5;
}

.card-footer {
  margin-top: auto;
  font-size: 12px;
  color: var(--capsule-ink);
  font-weight: 600;
  text-align: left;
  border-top: 1px dashed var(--capsule-divider);
  padding-top: 12px;
  z-index: 2;
}

.capsule-card.locked .card-footer {
  border-top-color: var(--capsule-divider);
}

 

.letter-content {
  padding: 10px;
  font-family: "KaiTi", "STKaiti", serif; /* 楷体更有书信感 */
  font-size: 18px;
  line-height: 1.8;
  background: #fff9f0;
  border-radius: 8px;
  padding: 20px;
  color: #5c3a2e;
}

.letter-head {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed #dcdfe6;
  padding-bottom: 10px;
  margin-bottom: 16px;
}

.letter-body {
  white-space: pre-wrap;
  min-height: 200px;
}

.letter-foot {
  text-align: right;
  margin-top: 20px;
}
</style>
