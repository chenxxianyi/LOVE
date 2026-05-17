<template>
  <main class="page-frame-wide">
    <!-- 加载骨架 -->
    <template v-if="store.loading">
      <section class="hero-card soft-card skeleton-pulse">
        <div class="hero-text">
          <div class="skel-chip"></div>
          <div class="skel-line w-60"></div>
          <div class="skel-line w-80"></div>
          <div class="skel-btns">
            <div class="skel-btn"></div>
            <div class="skel-btn"></div>
          </div>
        </div>
        <div class="hero-visual">
          <div class="skel-img"></div>
        </div>
      </section>
      <section class="metric-strip soft-card skeleton-pulse">
        <div class="metric-item" v-for="i in 3" :key="i">
          <div class="skel-num"></div>
          <div class="skel-label"></div>
        </div>
      </section>
    </template>

    <!-- HeroCard: 唯一主视觉中心 -->
    <section v-else class="hero-card soft-card fade-up">
      <div class="hero-text">
        <p class="glow-chip">我们的私人恋爱档案馆</p>
        <h1 class="title-font" @click="showInfoDialog = true" style="cursor: pointer" title="点击修改信息">
          {{ store.coupleName }}
          <el-icon :size="18" class="edit-icon"><Edit /></el-icon>
        </h1>
        <p class="hero-desc">
          用照片、视频和文字，慢慢收藏每一段日常。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="store.showAddMomentDialog = true">写一条回忆</el-button>
          <el-button size="large" round plain @click="showCoverManager = true">更换封面</el-button>
        </div>
      </div>
      <div class="hero-visual">
        <img
          :src="store.currentCover"
          alt="couple"
          loading="lazy"
          @click="showCoverManager = true"
          title="点击更换封面"
          style="cursor: pointer; width: 100%; border-radius: 14px"
        />
      </div>
    </section>

    <!-- MetricStrip: 横向统计条 -->
    <section v-if="!store.loading" class="metric-strip soft-card fade-up">
      <div
        v-for="stat in store.dashboardStats"
        :key="stat.label"
        class="metric-item"
      >
        <div class="metric-value title-font">{{ stat.value }}</div>
        <div class="metric-label">{{ stat.label }}</div>
      </div>
    </section>

    <!-- 7:5 双栏 (loading 时隐藏内容区) -->
    <section v-if="!store.loading" class="home-grid">
      <div class="home-main">
        <div class="section-head">
          <h2 class="title-font">最近的甜蜜瞬间</h2>
          <RouterLink to="/timeline" class="section-link">查看全部 →</RouterLink>
        </div>
        <div class="content-grid">
          <MomentCard
            v-for="(item, index) in store.moments.slice(0, 4)"
            :key="item.id"
            :item="item"
            :index="index"
            @edit="handleEdit"
            @delete="handleDelete"
          />
        </div>
      </div>
      <aside class="home-aside">
        <div class="soft-card aside-card fade-up">
          <h3 class="aside-title">💬 今日问题</h3>
          <p class="aside-text">去看看今天的问题吧</p>
          <RouterLink to="/question" class="aside-link">去回答 →</RouterLink>
        </div>
        <div class="soft-card aside-card fade-up">
          <h3 class="aside-title">💝 纪念日</h3>
          <p class="aside-text">查看你们的特别日子</p>
          <RouterLink to="/anniversary" class="aside-link">去看看 →</RouterLink>
        </div>
        <div class="soft-card aside-card fade-up">
          <h3 class="aside-title">🗺️ 足迹地图</h3>
          <p class="aside-text">标记一起去过的地方</p>
          <RouterLink to="/map" class="aside-link">去看看 →</RouterLink>
        </div>
      </aside>
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
  </main>
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
/* ── Dialog 样式 (保留) ── */
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
  border-color: var(--accent, #FFB3C6);
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

/* ── Hero 卡片细调 ── */
.hero-desc {
  color: var(--text-sub);
  line-height: 1.7;
  margin: 10px 0 18px;
  max-width: 440px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* ── Section 标题 ── */
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 4px;
}

.section-head h2 {
  margin: 0;
  font-size: 26px;
}

.section-link {
  color: var(--accent-text, #D47080);
  text-decoration: none;
  font-size: 14px;
}

/* ── 右侧快捷卡片 ── */
.aside-card {
  padding: 20px;
  border-radius: 18px;
  transition: transform 0.3s ease;
}

.aside-card:hover {
  transform: translateY(-2px);
}

.aside-title {
  margin: 0 0 6px;
  font-size: 16px;
  color: var(--text-main);
}

.aside-text {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--text-sub);
}

.aside-link {
  font-size: 13px;
  color: var(--accent-text, #D47080);
  text-decoration: none;
}
</style>
