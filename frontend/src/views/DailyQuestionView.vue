<template>
  <div class="question-page">
    <header class="page-head soft-card fade-up">
      <div class="head-content">
        <div>
          <h1 class="title-font">每日一问</h1>
          <p>每天一个问题，更懂彼此一点。</p>
        </div>
        <div class="actions" style="display: flex; gap: 10px;">
          <el-button type="primary" round size="large" @click="showHistory = true">
            问答档案馆
          </el-button>
          <el-button round size="large" @click="showQuestionBank = true">
            ⚙️ 题库管理
          </el-button>
        </div>
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
              v-if="!hasAnswered && currentRole === 'A'"
            />
            <p v-else-if="currentRole !== 'A' && !store.dailyQuestion.answer_a" class="waiting-text">
              这是 A 的回答区域
            </p>
            <el-button 
              type="primary" 
              size="small" 
              class="submit-btn" 
              @click="submitAnswer('answer_a')"
              v-if="!hasAnswered && currentRole === 'A'"
              :loading="loading"
            >
              提交
            </el-button>
            <p v-else-if="hasAnswered && currentRole === 'A' && !store.dailyQuestion.answer_a" class="waiting-text">
              等待对方回答后解锁...
            </p>
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
              v-if="!hasAnswered && currentRole === 'B'"
            />
            <p v-else-if="currentRole !== 'B' && !store.dailyQuestion.answer_b" class="waiting-text">
              这是 B 的回答区域
            </p>
            <el-button 
              type="primary" 
              size="small" 
              class="submit-btn" 
              @click="submitAnswer('answer_b')"
              v-if="!hasAnswered && currentRole === 'B'"
              :loading="loading"
            >
              提交
            </el-button>
            <p v-else-if="hasAnswered && currentRole === 'B' && !store.dailyQuestion.answer_b" class="waiting-text">
              等待对方回答后解锁...
            </p>
          </div>
        </div>
      </div>
      
      <div class="lock-banner fade-up" v-if="!isFullyAnswered">
        <span class="icon">🔒</span>
        <p>双方都回答后，答案将自动公开</p>
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

    <!-- Question Bank Dialog -->
    <QuestionBankDialog v-model="showQuestionBank" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { useAuthStore } from "../stores/useAuthStore";
import { useCoupleStore } from "../stores/useCoupleStore";
import { ElMessage } from "element-plus";
import QuestionBankDialog from "../components/QuestionBankDialog.vue";

const store = useLoveStore();
const authStore = useAuthStore();
const coupleStore = useCoupleStore();
const myAnswer = ref("");
const loading = ref(false);
const showHistory = ref(false);
const showQuestionBank = ref(false);
const hasAnswered = ref(false);

// Ideally we should know which user is logged in (A or B)
// For simplicity, we'll let user choose which slot to fill
// Or simply: slot A is for user A, slot B for user B.
// Here we simulate simple logic: if slot is empty, show input.

onMounted(async () => {
  await store.fetchDailyQuestion();
  await store.fetchQuestionHistory();
  if (!coupleStore.space) {
    await coupleStore.fetchSpace();
  }
});

const currentRole = computed(() => {
  if (!authStore.user || !coupleStore.space) return null;
  const me = coupleStore.space.members.find(m => String(m.id) === String(authStore.user?.id));
  return me?.role || null;
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
  padding: 50px 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
  min-height: 440px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 245, 247, 0.7) 100%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 12px 36px rgba(228, 155, 171, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 24px;
}

.date-tag {
  display: inline-block;
  padding: 6px 16px;
  background: linear-gradient(90deg, #ffdde1 0%, #ee9ca7 100%);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 24px;
  box-shadow: 0 4px 10px rgba(238, 156, 167, 0.3);
  letter-spacing: 1px;
}

.question-text {
  font-family: "Georgia", "KaiTi", serif;
  font-size: 32px;
  margin-bottom: 50px;
  color: #4a3434;
  line-height: 1.5;
  font-weight: 700;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
}

.answers-section {
  display: flex;
  gap: 24px;
  justify-content: center;
  position: relative;
  z-index: 5;
}

.answer-box {
  flex: 1;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 30px 24px 24px;
  position: relative;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 20px rgba(0,0,0,0.03);
  backdrop-filter: blur(8px);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.answer-box:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.06);
}

.avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
  color: #fff;
  border-radius: 50%;
  border: 3px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 6px 12px rgba(255, 154, 158, 0.3);
}

.answer-content {
  margin-top: 16px;
  font-size: 16px;
  color: #5c3a2e;
  text-align: left;
  width: 100%;
  white-space: pre-wrap;
  filter: blur(5px);
  transition: filter 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  line-height: 1.8;
}

.question-container:not(:has(.lock-banner)) .answer-content {
  filter: blur(0);
}

.input-area {
  width: 100%;
  margin-top: 10px;
  position: relative;
  z-index: 20;
}

.submit-btn {
  margin-top: 16px;
  width: 100%;
  border-radius: 12px;
  font-weight: bold;
}

.waiting-text {
  color: #909399;
  font-size: 14px;
  margin-top: 40px;
  font-style: italic;
}

.lock-banner {
  margin: 40px auto 0;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px 32px;
  border-radius: 50px;
  box-shadow: 0 8px 24px rgba(228, 155, 171, 0.2);
  border: 1px solid rgba(228, 155, 171, 0.3);
  color: #5c3a2e;
  font-weight: 500;
  animation: float-banner 4s ease-in-out infinite;
  backdrop-filter: blur(10px);
}

.lock-banner .icon {
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.lock-banner p {
  margin: 0;
  font-size: 16px;
  letter-spacing: 0.5px;
}

@keyframes float-banner {
  0% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-6px) scale(1.02); }
  100% { transform: translateY(0px) scale(1); }
}

/* History Styles */
.history-list {
  padding: 10px 20px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-item {
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  border-top: 4px solid var(--primary-color);
  transition: transform 0.2s ease;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.q-date {
  display: inline-block;
  font-size: 13px;
  color: var(--primary-color);
  background: #fff0f3;
  padding: 4px 10px;
  border-radius: 12px;
  margin-bottom: 12px;
  font-weight: bold;
}

.q-content {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: #4a3434;
  line-height: 1.4;
}

.q-answers {
  background: #fcfcfc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #f2f2f2;
}

.q-answers p {
  margin: 8px 0;
  font-size: 15px;
  color: #5c3a2e;
  line-height: 1.6;
}

.q-answers strong {
  display: inline-block;
  width: 24px;
  color: var(--primary-color);
}

.q-pending {
  color: #909399;
  font-size: 14px;
  font-style: italic;
  padding: 10px 0;
}
</style>
