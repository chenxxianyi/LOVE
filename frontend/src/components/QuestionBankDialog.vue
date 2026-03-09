<template>
  <el-dialog v-model="visible" title="自定义专属题库" width="600px" @open="loadData">
    <div class="bank-container">
      <el-alert
        title="在这里可以添加你们专属的问题。如果选择了特定日期，那一天一定会刷出这道题！"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <!-- List Area -->
      <div v-loading="store.loading" class="question-list">
        <div v-if="store.questionBank.length === 0" class="empty-state">
          暂无自定义题目，快来添加第一道专属问题吧！
        </div>
        <div v-for="item in store.questionBank" :key="item.id" class="question-item soft-card">
          <div class="content">{{ item.content }}</div>
          <div class="meta">
            <el-tag v-if="item.target_date" type="success" size="small">
              专属日: {{ item.target_date }}
            </el-tag>
            <el-tag v-else type="info" size="small">随机题库</el-tag>
            <el-button type="danger" text @click="handleDelete(item.id)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- Add Area -->
      <div class="add-section">
        <h3>添加新问题</h3>
        <el-form :model="form" label-width="80px">
          <el-form-item label="题目内容">
            <el-input v-model="form.content" placeholder="例如：你最喜欢我穿哪件衣服？" />
          </el-form-item>
          <el-form-item label="专属日期">
            <el-date-picker
              v-model="form.target_date"
              type="date"
              placeholder="指定在哪一天出现（可选）"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleAdd" :loading="submitLoading" :disabled="!form.content.trim()">
              保存到题库
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useLoveStore } from '../stores/useLoveStore';
import { ElMessage, ElMessageBox } from 'element-plus';

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits(['update:modelValue']);

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const store = useLoveStore();
const submitLoading = ref(false);

const form = ref({
  content: '',
  target_date: null as string | null
});

const loadData = async () => {
  await store.fetchQuestionBank();
};

const handleAdd = async () => {
  if (!form.value.content.trim()) return;
  submitLoading.value = true;
  try {
    await store.addQuestionBank({
      content: form.value.content.trim(),
      target_date: form.value.target_date || null
    });
    ElMessage.success("添加成功");
    form.value.content = "";
    form.value.target_date = null;
  } catch (error) {
    ElMessage.error("添加失败");
  } finally {
    submitLoading.value = false;
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这道专属问题吗？', '提示', { type: 'warning' });
    await store.deleteQuestionBank(id);
    ElMessage.success("删除成功");
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error("删除失败");
    }
  }
};
</script>

<style scoped>
.bank-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.question-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 10px;
}
.empty-state {
  text-align: center;
  color: #999;
  padding: 30px 0;
}
.question-item {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}
.question-item .content {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}
.question-item .meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.add-section {
  border-top: 1px dashed #dcdfe6;
  padding-top: 20px;
  margin-top: 10px;
}
.add-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #606266;
}
</style>
