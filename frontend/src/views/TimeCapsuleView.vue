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
        <div class="card-status">
          <span class="icon">{{ item.is_opened ? '🔓' : '🔒' }}</span>
          <span class="label">{{ item.is_opened ? '已开启' : '封印中' }}</span>
        </div>
        
        <div class="card-content">
          <p class="to">To: {{ item.receiver }}</p>
          <div class="preview">
             <p v-if="item.is_opened">{{ item.content }}</p>
             <p v-else class="locked-text">
               此信件将于 <span class="highlight">{{ item.open_at.split(' ')[0] }}</span> 开启
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
  padding: 20px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  display: flex;
  flex-direction: column;
  height: 200px;
}

.capsule-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08);
}

.capsule-card.locked {
  background: #f4f4f5;
  color: #909399;
}

.capsule-card.locked:hover {
  border-color: #dcdfe6;
}

.card-status {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: bold;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.to, .from {
  font-weight: 600;
  margin: 0;
}

.preview {
  flex: 1;
  margin: 10px 0;
  font-size: 14px;
  line-height: 1.6;
  overflow: hidden;
  color: var(--text-sub);
}

.locked-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  font-size: 13px;
}

.highlight {
  color: var(--primary-color);
  font-weight: bold;
  margin: 4px 0;
}

.card-footer {
  margin-top: auto;
  font-size: 12px;
  color: #c0c4cc;
  text-align: right;
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
