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
        <div style="display: flex; gap: 8px; width: 100%;">
          <el-input
            v-model="form.location"
            placeholder="例如：武汉、青岛石老人海水浴场"
            @blur="autoGeocode"
            style="flex: 1"
          />
          <button
            class="premium-btn geo-btn"
            :class="{ 'is-loading': geocoding, 'is-active': geocoded }"
            @click.prevent="autoGeocode"
            type="button"
          >
            <span class="btn-content">
              <el-icon v-if="geocoding" class="is-spinning"><Loading /></el-icon>
              <el-icon v-else-if="geocoded"><LocationInformation /></el-icon>
              <el-icon v-else><Location /></el-icon>
              {{ geocoding ? '定位中...' : (geocoded ? '已定位' : '自动定位') }}
            </span>
            <div class="btn-glow"></div>
          </button>
        </div>
        <div v-if="geocoded" class="geo-hint">
          📍 {{ form.latitude }}, {{ form.longitude }}
        </div>
        <div v-if="geoError" class="geo-error">
          ⚠️ {{ geoError }}，可手动输入坐标
        </div>
      </el-form-item>

      <!-- 手动填坐标（折叠） -->
      <el-form-item label="">
        <el-collapse-transition>
          <div v-show="showManual" style="display: flex; gap: 10px; width: 100%;">
            <el-input v-model="form.latitude" placeholder="纬度 (如 30.59)" />
            <el-input v-model="form.longitude" placeholder="经度 (如 114.30)" />
          </div>
        </el-collapse-transition>
        <el-link type="info" :underline="false" @click="showManual = !showManual" style="font-size: 12px; margin-top: 4px;">
          {{ showManual ? '▲ 收起' : '▼ 手动输入坐标' }}
        </el-link>
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
import { Plus, Location, LocationInformation, Loading } from "@element-plus/icons-vue";
import { useLoveStore, type MomentItem } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const props = defineProps<{
  modelValue: boolean;
  editData?: MomentItem | null;
}>();

const emit = defineEmits(["update:modelValue", "success"]);

const store = useLoveStore();
const visible = ref(false);
const loading = ref(false);
const geocoding = ref(false);
const geocoded = ref(false);
const geoError = ref("");
const showManual = ref(false);
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
      if (props.editData) {
        // Edit mode
        form.title = props.editData.title;
        form.date = props.editData.date;
        form.location = props.editData.location;
        form.latitude = props.editData.latitude || "";
        form.longitude = props.editData.longitude || "";
        form.mood = props.editData.mood;
        form.summary = props.editData.summary;
        form.images = [...props.editData.images];
        form.hasVideo = props.editData.hasVideo;
        
        fileList.value = props.editData.images.map((url: string, index: number) => ({
          name: `image-${index}`,
          url: url
        }));
        
        geocoded.value = !!(form.latitude && form.longitude);
        geoError.value = "";
        showManual.value = false;
      } else {
        // Reset form for create mode
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
        geocoded.value = false;
        geoError.value = "";
        showManual.value = false;
      }
    }
  }
);

watch(visible, (val) => {
  emit("update:modelValue", val);
});

// 自动地理编码：通过 Nominatim 把地名转成经纬度
const autoGeocode = async () => {
  const location = form.location.trim();
  if (!location) return;

  geocoding.value = true;
  geocoded.value = false;
  geoError.value = "";

  try {
    // 使用 OpenStreetMap Nominatim（免费，无需 API Key）
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(location)}&format=json&limit=1&accept-language=zh-CN`;
    const res = await fetch(url, {
      headers: { "Accept-Language": "zh-CN,zh;q=0.9" }
    });
    const data = await res.json();

    if (data && data.length > 0) {
      form.latitude = parseFloat(data[0].lat).toFixed(6);
      form.longitude = parseFloat(data[0].lon).toFixed(6);
      geocoded.value = true;
    } else {
      geoError.value = `未找到"${location}"的坐标`;
      showManual.value = true;
    }
  } catch (e) {
    geoError.value = "定位服务暂时不可用";
    showManual.value = true;
  } finally {
    geocoding.value = false;
  }
};

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
    if (props.editData) {
      await store.updateMoment(props.editData.id, { ...form });
      ElMessage.success("回忆更新成功！");
    } else {
      await store.createMoment({ ...form });
      ElMessage.success("回忆保存成功！🗺️ 已在地图上留下足迹");
    }
    visible.value = false;
    emit("success");
  } catch (error) {
    ElMessage.error("保存失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.geo-hint {
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
}
.geo-error {
  font-size: 12px;
  color: #e6a23c;
  margin-top: 4px;
}

/* 高级定位按钮样式 */
.premium-btn {
  position: relative;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  outline: none;
  font-family: inherit;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  white-space: nowrap;
  flex-shrink: 0;
  height: 32px;
}

.premium-btn .btn-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
  height: 100%;
  font-size: 13px;
  font-weight: 500;
  color: var(--pink-deep);
  background: rgba(255, 233, 239, 0.4);
  border: 1px solid rgba(212, 155, 142, 0.3);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.premium-btn:hover .btn-content {
  background: rgba(255, 233, 239, 0.8);
  border-color: rgba(212, 155, 142, 0.6);
  transform: translateY(-1px);
}

.premium-btn:active .btn-content {
  transform: translateY(1px);
}

/* 定位中状态 */
.premium-btn.is-loading {
  pointer-events: none;
}
.premium-btn.is-loading .btn-content {
  color: #a77c85;
  background: rgba(245, 245, 245, 0.8);
  border-color: #ddd;
}
.is-spinning {
  animation: spin 1s linear infinite;
}

/* 已定位高亮状态 */
.premium-btn.is-active .btn-content {
  background: linear-gradient(135deg, #fbd1e0 0%, #ffdde5 100%);
  color: #c9516c;
  border-color: rgba(212, 155, 142, 0.5);
  box-shadow: 0 4px 12px rgba(212, 155, 142, 0.25);
}

/* 底部发光特效 */
.premium-btn .btn-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.8) 0%, transparent 70%);
  opacity: 0;
  z-index: 1;
  transition: opacity 0.3s ease;
  mix-blend-mode: overlay;
}

.premium-btn.is-active:hover .btn-glow {
  opacity: 1;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>
