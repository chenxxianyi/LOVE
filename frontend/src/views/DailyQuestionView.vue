<template>
  <div class="question-page">
    <header class="page-head soft-card fade-up">
      <div class="head-content">
        <div>
          <h1 class="title-font">每日一问</h1>
          <p>每天一个问题，更懂彼此一点。</p>
        </div>
        <el-button type="primary" round size="large" @click="showHistory = true">
          问答档案馆
        </el-button>
      </div>
    </header>

    <div class="question-container soft-card fade-up" v-if="store.dailyQuestion">
      <div class="date-tag">{{ store.dailyQuestion.date }}</div>
      <h2 class="question-text">{{ store.dailyQuestion.content }}</h2>
      
      <div class="answers-section">
        <!-- Answer A -->
        <div class="answer-box">
          <div class="avatar">A</div>
          <div v-if="store.dailyQuestion.answer_a" class="answer-content">
            {{ store.dailyQuestion.answer_a }}
          </div>
          <div v-else class="input-area">
            <el-input
              v-model="myAnswer"
              type="textarea"
              :rows="3"
              placeholder="写下你的回答..."
              v-if="!hasAnswered"
            />
            <el-button 
              type="primary" 
              size="small" 
              class="submit-btn" 
              @click="submitAnswer('answer_a')"
              v-if="!hasAnswered"
              :loading="loading"
            >
              提交
            </el-button>
            <p v-else class="waiting-text">等待对方回答后解锁...</p>
          </div>
        </div>

        <!-- Answer B -->
        <div class="answer-box">
          <div class="avatar" style="background: #a18cd1">B</div>
          <div v-if="store.dailyQuestion.answer_b" class="answer-content">
            {{ store.dailyQuestion.answer_b }}
          </div>
          <div v-else class="input-area">
            <el-input
              v-model="myAnswer"
              type="textarea"
              :rows="3"
              placeholder="写下你的回答..."
              v-if="!hasAnswered"
            />
            <el-button 
              type="primary" 
              size="small" 
              class="submit-btn" 
              @click="submitAnswer('answer_b')"
              v-if="!hasAnswered"
              :loading="loading"
            >
              提交
            </el-button>
            <p v-else class="waiting-text">等待对方回答后解锁...</p>
          </div>
        </div>
      </div>
      
      <div class="lock-mask" v-if="!isFullyAnswered">
        <div class="lock-content">
          <span class="icon">🔒</span>
          <p>双方都回答后，答案将自动公开</p>
        </div>
      </div>
    </div>

    <!-- History Drawer -->
    <el-drawer v-model="showHistory" title="问答档案馆" size="50%">
      <div class="history-list">
        <div v-for="q in store.questionHistory" :key="q.id" class="history-item soft-card">
          <div class="q-date">{{ q.date }}</div>
          <div class="q-content">{{ q.content }}</div>
          <div class="q-answers" v-if="q.answer_a && q.answer_b">
            <p><strong>A:</strong> {{ q.answer_a }}</p>
            <p><strong>B:</strong> {{ q.answer_b }}</p>
          </div>
          <div class="q-pending" v-else>
            未完成
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const store = useLoveStore();
const myAnswer = ref("");
const loading = ref(false);
const showHistory = ref(false);
const hasAnswered = ref(false);

// Ideally we should know which user is logged in (A or B)
// For simplicity, we'll let user choose which slot to fill
// Or simply: slot A is for user A, slot B for user B.
// Here we simulate simple logic: if slot is empty, show input.

onMounted(async () => {
  await store.fetchDailyQuestion();
  await store.fetchQuestionHistory();
});

const isFullyAnswered = computed(() => {
  return store.dailyQuestion?.answer_a && store.dailyQuestion?.answer_b;
});

const submitAnswer = async (slot: 'answer_a' | 'answer_b') => {
  if (!myAnswer.value) {
    ElMessage.warning("请填写回答");
    return;
  }
  
  loading.value = true;
  try {
    await store.answerQuestion(store.dailyQuestion!.id, { [slot]: myAnswer.value });
    ElMessage.success("回答已提交");
    hasAnswered.value = true;
    myAnswer.value = "";
  } catch (error) {
    ElMessage.error("提交失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.question-page {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.page-head {
  padding: 24px;
  margin-bottom: 20px;
}

.head-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-head h1 {
  margin: 0 0 8px;
  font-size: 32px;
}

.page-head p {
  margin: 0;
  color: var(--text-sub);
}

.question-container {
  padding: 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
  min-height: 400px;
}

.date-tag {
  display: inline-block;
  padding: 4px 12px;
  background: #fff0f3;
  color: var(--primary-color);
  border-radius: 20px;
  font-size: 14px;
  margin-bottom: 20px;
}

.question-text {
  font-size: 28px;
  margin-bottom: 40px;
  color: var(--text-main);
  line-height: 1.4;
}

.answers-section {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.answer-box {
  flex: 1;
  background: #f9f9f9;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  background: #ff9a9e;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.answer-content {
  margin-top: 20px;
  font-size: 16px;
  color: var(--text-main);
  text-align: left;
  width: 100%;
  white-space: pre-wrap;
  filter: blur(5px); /* Initially blurred */
  transition: filter 0.5s;
}

/* If fully answered, remove blur */
.question-container:not(:has(.lock-mask)) .answer-content {
  filter: none;
}

.input-area {
  width: 100%;
  margin-top: 20px;
}

.submit-btn {
  margin-top: 10px;
  width: 100%;
}

.waiting-text {
  color: var(--text-sub);
  font-size: 14px;
  margin-top: 30px;
}

.lock-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  pointer-events: none; /* Allow typing in inputs */
}

/* Make inputs clickable */
.input-area {
  position: relative;
  z-index: 20;
}

.lock-content {
  background: rgba(255, 255, 255, 0.9);
  padding: 20px 40px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.lock-content .icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.lock-content p {
  margin: 0;
  color: var(--text-sub);
}

/* History Styles */
.history-list {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  padding: 16px;
  border-left: 4px solid var(--primary-color);
}

.q-date {
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 4px;
}

.q-content {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 12px;
}

.q-answers p {
  margin: 4px 0;
  font-size: 14px;
  color: var(--text-main);
}

.q-pending {
  color: #e6a23c;
  font-size: 13px;
}
</style>
