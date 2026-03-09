<template>
  <div class="home-page">
    <section class="hero soft-card fade-up">
      <div class="hero-text">
        <p class="glow-chip">我们的私人恋爱档案馆</p>
        <h1 class="title-font" @click="showInfoDialog = true" style="cursor: pointer" title="点击修改信息">
          {{ store.coupleName }}
          <el-icon size="20" class="edit-icon"><Edit /></el-icon>
        </h1>
        <p class="desc">
          用照片、视频和文字，慢慢收藏每一段日常。这里不需要完美，只记录你们真实又温柔的片段。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="store.showAddMomentDialog = true">写一条回忆</el-button>
          <el-button size="large" round plain>上传照片/视频</el-button>
        </div>
      </div>
      <div class="hero-cover">
        <img
          :src="store.currentCover"
          alt="couple"
          @click="showCoverManager = true"
          title="点击更换封面"
          style="cursor: pointer"
        />
      </div>
    </section>

    <section class="stats">
      <article
        v-for="(stat, idx) in store.dashboardStats"
        :key="stat.label"
        class="stat-item soft-card fade-up"
        :style="{ animationDelay: `${idx * 60}ms` }"
      >
        <p>{{ stat.label }}</p>
        <h2 class="title-font">{{ stat.value }}</h2>
        <small>{{ stat.hint }}</small>
      </article>
    </section>

    <section class="featured">
      <div class="featured-head">
        <h2 class="title-font">最近的甜蜜瞬间</h2>
        <RouterLink to="/timeline">查看全部</RouterLink>
      </div>
      <div class="featured-grid">
        <MomentCard
          v-for="(item, index) in store.moments.slice(0, 2)"
          :key="item.id"
          :item="item"
          :index="index"
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </div>
    </section>

    <!-- Cover Manager Dialog -->
    <el-dialog v-model="showCoverManager" title="管理封面图" width="500px">
      <div class="cover-manager">
        <div class="upload-area">
          <el-upload
            action="#"
            :show-file-list="false"
            :http-request="handleUploadCover"
          >
            <el-button type="primary">上传新封面</el-button>
          </el-upload>
          <span class="tip">建议上传横版高清大图</span>
        </div>
        
        <div class="cover-list">
          <div 
            v-for="cover in store.covers" 
            :key="cover.id" 
            class="cover-item"
            :class="{ active: store.currentCover === cover.url }"
            @click="store.currentCover = cover.url"
          >
            <img :src="cover.url" />
            <span class="delete-btn" @click.stop="handleDeleteCover(cover.id)">×</span>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Info Edit Dialog -->
    <el-dialog v-model="showInfoDialog" title="设置基础信息" width="400px">
      <el-form :model="infoForm" label-width="80px">
        <el-form-item label="恋人昵称">
          <el-input v-model="infoForm.couple_names" placeholder="例如：小鹿 & 小棠" />
        </el-form-item>
        <el-form-item label="在一起">
          <el-date-picker
            v-model="infoForm.start_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInfoDialog = false">取消</el-button>
          <el-button type="primary" @click="saveInfo" :loading="loading">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <AddMomentForm 
      v-model="editDialogVisible" 
      :edit-data="currentEditItem"
      @success="store.fetchMoments"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import MomentCard from "../components/MomentCard.vue";
import AddMomentForm from "../components/AddMomentForm.vue";
import { useLoveStore, type MomentItem } from "../stores/useLoveStore";
import { ElMessage, ElMessageBox } from "element-plus";
import { Edit } from "@element-plus/icons-vue";

const store = useLoveStore();
const showCoverManager = ref(false);
const showInfoDialog = ref(false);
const loading = ref(false);

const editDialogVisible = ref(false);
const currentEditItem = ref<MomentItem | null>(null);

const infoForm = reactive({
  couple_names: "",
  start_date: "",
});

onMounted(async () => {
  await store.fetchAll();
  infoForm.couple_names = store.coupleName;
  infoForm.start_date = store.startDate;
});

// Update form when store changes (e.g. initial load)
watch(() => store.coupleName, (newVal) => {
  if (newVal) infoForm.couple_names = newVal;
});
watch(() => store.startDate, (newVal) => {
  if (newVal) infoForm.start_date = newVal;
});

const saveInfo = async () => {
  loading.value = true;
  try {
    await store.updateInfo(infoForm);
    ElMessage.success("信息已更新");
    showInfoDialog.value = false;
  } catch (error) {
    ElMessage.error("更新失败");
  } finally {
    loading.value = false;
  }
};

const handleUploadCover = async (options: any) => {
  try {
    const url = await store.uploadImage(options.file);
    await store.addCover(url);
    store.currentCover = url;
    ElMessage.success("封面上传成功");
  } catch (error) {
    ElMessage.error("上传失败");
  }
};

const handleDeleteCover = async (id: number) => {
  try {
    await store.deleteCover(id);
    ElMessage.success("删除成功");
    if (store.covers.length > 0) {
      store.setRandomCover();
    }
  } catch (error) {
    ElMessage.error("删除失败");
  }
};

const handleEdit = (item: MomentItem) => {
  currentEditItem.value = item;
  editDialogVisible.value = true;
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条珍贵的回忆吗？删除后无法恢复哦。',
      '删除提醒',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '留着',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    await store.deleteMoment(id);
    ElMessage.success("回忆已删除");
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error("删除失败");
    }
  }
};
</script>

<style scoped>
.home-page {
  position: relative;
}

/* ... existing styles ... */

.cover-manager {
  padding: 10px;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.tip {
  font-size: 12px;
  color: var(--text-sub);
}

.cover-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.cover-item {
  position: relative;
  aspect-ratio: 16/9;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
}

.cover-item.active {
  border-color: var(--primary-color);
}

.cover-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-item .delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0,0,0,0.5);
  color: #fff;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.cover-item:hover .delete-btn {
  opacity: 1;
}

.edit-icon {
  margin-left: 8px;
  color: var(--text-sub);
  opacity: 0.5;
  transition: opacity 0.2s;
  vertical-align: middle;
}

.title-font:hover .edit-icon {
  opacity: 1;
}

.hero,
.stats,
.featured {
  position: relative;
  z-index: 19;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 22px;
  padding: 22px;
}

.hero-text h1 {
  margin: 8px 0 8px;
  font-size: clamp(32px, 5vw, 52px);
  line-height: 1;
}

.desc {
  color: var(--text-sub);
  line-height: 1.8;
  margin-bottom: 18px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-cover {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--line-soft);
}

.hero-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stats {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.stat-item {
  padding: 14px 16px;
}

.stat-item p {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub);
}

.stat-item h2 {
  margin: 6px 0;
  font-size: 32px;
}

.stat-item small {
  color: var(--text-sub);
}

.featured {
  margin-top: 22px;
}

.featured-head {
  margin-bottom: 10px;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.featured-head h2 {
  margin: 0;
  font-size: 34px;
}

.featured-head a {
  color: var(--pink-deep);
  text-decoration: none;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .featured-grid {
    grid-template-columns: 1fr;
  }
}
</style>
