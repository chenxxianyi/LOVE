<template>
  <el-dialog
    v-model="visible"
    title="写一条回忆"
    width="500px"
    destroy-on-close
    :close-on-click-modal="false"
  >
    <el-form :model="form" label-width="80px">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="例如：海边日落" />
      </el-form-item>
      
      <el-form-item label="日期">
        <el-date-picker
          v-model="form.date"
          type="datetime"
          placeholder="选择日期时间"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="地点">
        <el-input v-model="form.location" placeholder="例如：青岛" />
      </el-form-item>
      
      <el-form-item label="坐标">
        <div style="display: flex; gap: 10px; width: 100%;">
          <el-input v-model="form.latitude" placeholder="纬度 (如 36.06)" />
          <el-input v-model="form.longitude" placeholder="经度 (如 120.38)" />
        </div>
      </el-form-item>

      <el-form-item label="心情">
        <el-select v-model="form.mood" placeholder="选择心情" style="width: 100%">
          <el-option label="心动" value="心动" />
          <el-option label="治愈" value="治愈" />
          <el-option label="浪漫" value="浪漫" />
          <el-option label="开心" value="开心" />
          <el-option label="难过" value="难过" />
        </el-select>
      </el-form-item>

      <el-form-item label="内容">
        <el-input
          v-model="form.summary"
          type="textarea"
          :rows="3"
          placeholder="记录这一刻的感受..."
        />
      </el-form-item>

      <el-form-item label="图片">
        <el-upload
          action="#"
          list-type="picture-card"
          :auto-upload="true"
          :http-request="handleUpload"
          :on-remove="handleRemove"
          :file-list="fileList"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      
       <el-form-item label="包含视频">
        <el-switch v-model="form.hasVideo" />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from "vue";
import { Plus } from "@element-plus/icons-vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits(["update:modelValue", "success"]);

const store = useLoveStore();
const visible = ref(false);
const loading = ref(false);
const fileList = ref<any[]>([]);

const form = reactive({
  title: "",
  date: "",
  location: "",
  latitude: "",
  longitude: "",
  mood: "",
  summary: "",
  images: [] as string[],
  hasVideo: false,
});

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val;
    if (val) {
      // Reset form
      form.title = "";
      form.date = new Date().toISOString().slice(0, 16).replace("T", " ");
      form.location = "";
      form.latitude = "";
      form.longitude = "";
      form.mood = "";
      form.summary = "";
      form.images = [];
      form.hasVideo = false;
      fileList.value = [];
    }
  }
);

watch(visible, (val) => {
  emit("update:modelValue", val);
});

const handleUpload = async (options: any) => {
  try {
    const url = await store.uploadImage(options.file);
    form.images.push(url);
    fileList.value.push({ name: options.file.name, url });
  } catch (error) {
    ElMessage.error("图片上传失败");
  }
};

const handleRemove = (file: any) => {
  const index = fileList.value.indexOf(file);
  if (index !== -1) {
    fileList.value.splice(index, 1);
    form.images.splice(index, 1);
  }
};

const submit = async () => {
  if (!form.title || !form.date) {
    ElMessage.warning("请填写完整信息");
    return;
  }

  loading.value = true;
  try {
    await store.createMoment({ ...form });
    ElMessage.success("回忆保存成功！");
    visible.value = false;
    emit("success");
  } catch (error) {
    ElMessage.error("保存失败");
  } finally {
    loading.value = false;
  }
};
</script>
