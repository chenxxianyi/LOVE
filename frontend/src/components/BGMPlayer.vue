<template>
  <div class="bgm-player" :class="{ collapsed: isCollapsed }">
    <!-- Collapsed View -->
    <div v-if="isCollapsed" class="mini-player" @click="isCollapsed = false">
      <div class="music-icon" :class="{ spinning: isPlaying }">🎵</div>
    </div>

    <!-- Expanded View -->
    <div v-else class="full-player soft-card">
      <div class="player-header">
        <span class="title">BGM</span>
        <span class="close-btn" @click="isCollapsed = true">×</span>
      </div>

      <div class="current-info">
        <div class="cover-wrapper" :class="{ spinning: isPlaying }">
          <img :src="currentMusic?.cover || defaultCover" alt="cover" />
        </div>
        <div class="info-text">
          <p class="song-title">{{ currentMusic?.title || "未播放" }}</p>
          <p class="artist">{{ currentMusic?.artist || "请选择音乐" }}</p>
        </div>
      </div>

      <div class="controls">
        <el-button circle size="small" @click="prevSong">⏮</el-button>
        <el-button circle type="primary" @click="togglePlay">
          {{ isPlaying ? "⏸" : "▶" }}
        </el-button>
        <el-button circle size="small" @click="nextSong">⏭</el-button>
        <el-button circle size="small" @click="showPlaylist = !showPlaylist">≣</el-button>
      </div>

      <!-- Audio Element -->
      <audio
        ref="audioRef"
        :src="currentMusic?.url"
        @ended="nextSong"
        @error="handleError"
      ></audio>

      <!-- Playlist Drawer -->
      <div v-if="showPlaylist" class="playlist">
        <div class="playlist-header">
          <span>播放列表</span>
          <el-button type="text" size="small" @click="showAddDialog = true">添加</el-button>
        </div>
        <ul class="list">
          <li
            v-for="item in store.musicList"
            :key="item.id"
            :class="{ active: currentMusic?.id === item.id }"
            @click="playMusic(item)"
          >
            <div class="list-info">
              <span class="name">{{ item.title }}</span>
              <span class="singer">- {{ item.artist }}</span>
            </div>
            <span class="delete-btn" @click.stop="deleteMusic(item.id)">×</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Add Music Dialog -->
    <el-dialog v-model="showAddDialog" title="添加背景音乐" width="400px" append-to-body>
      <el-form :model="form" label-width="60px">
        <el-form-item label="歌名">
          <el-input v-model="form.title" placeholder="例如：告白气球" />
        </el-form-item>
        <el-form-item label="歌手">
          <el-input v-model="form.artist" placeholder="例如：周杰伦" />
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="form.url" placeholder="MP3 链接地址" />
        </el-form-item>
        <el-form-item label="封面">
          <el-input v-model="form.cover" placeholder="图片链接（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="submit" :loading="loading">添加</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useLoveStore, type MusicItem } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

const store = useLoveStore();
const audioRef = ref<HTMLAudioElement | null>(null);
const isCollapsed = ref(true);
const isPlaying = ref(false);
const showPlaylist = ref(false);
const showAddDialog = ref(false);
const loading = ref(false);
const currentMusic = ref<MusicItem | null>(null);
const defaultCover = "https://cdn-icons-png.flaticon.com/512/461/461238.png";

const form = reactive({
  title: "",
  artist: "",
  url: "",
  cover: "",
});

onMounted(async () => {
  await store.fetchMusicList();
  if (store.musicList.length > 0) {
    currentMusic.value = store.musicList[0];
  }
});

const togglePlay = () => {
  if (!audioRef.value || !currentMusic.value) return;
  if (isPlaying.value) {
    audioRef.value.pause();
  } else {
    audioRef.value.play();
  }
  isPlaying.value = !isPlaying.value;
};

const playMusic = (item: MusicItem) => {
  currentMusic.value = item;
  isPlaying.value = true;
  // Wait for DOM update
  setTimeout(() => {
    audioRef.value?.play();
  }, 100);
};

const nextSong = () => {
  if (store.musicList.length === 0) return;
  const currentIndex = store.musicList.findIndex(i => i.id === currentMusic.value?.id);
  const nextIndex = (currentIndex + 1) % store.musicList.length;
  playMusic(store.musicList[nextIndex]);
};

const prevSong = () => {
  if (store.musicList.length === 0) return;
  const currentIndex = store.musicList.findIndex(i => i.id === currentMusic.value?.id);
  const prevIndex = (currentIndex - 1 + store.musicList.length) % store.musicList.length;
  playMusic(store.musicList[prevIndex]);
};

const handleError = () => {
  ElMessage.error("播放失败，可能是链接无效");
  isPlaying.value = false;
};

const submit = async () => {
  if (!form.title || !form.url) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  
  loading.value = true;
  try {
    await store.addMusic(form);
    ElMessage.success("添加成功");
    showAddDialog.value = false;
    form.title = "";
    form.artist = "";
    form.url = "";
    form.cover = "";
    
    // If it's the first song, auto select it
    if (store.musicList.length === 1) {
      currentMusic.value = store.musicList[0];
    }
  } catch (error) {
    ElMessage.error("添加失败");
  } finally {
    loading.value = false;
  }
};

const deleteMusic = async (id: number) => {
  try {
    await store.deleteMusic(id);
    ElMessage.success("删除成功");
    if (currentMusic.value?.id === id) {
      isPlaying.value = false;
      audioRef.value?.pause();
      currentMusic.value = store.musicList[0] || null;
    }
  } catch (error) {
    ElMessage.error("删除失败");
  }
};
</script>

<style scoped>
.bgm-player {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.mini-player {
  width: 50px;
  height: 50px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.mini-player:hover {
  transform: scale(1.1);
}

.music-icon {
  font-size: 24px;
}

.spinning {
  animation: spin 4s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.full-player {
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.player-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: var(--text-sub);
  font-size: 12px;
}

.close-btn {
  cursor: pointer;
  font-size: 16px;
}

.current-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.cover-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #ffeef2;
}

.cover-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-text {
  flex: 1;
  overflow: hidden;
}

.song-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.artist {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-sub);
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.playlist {
  margin-top: 16px;
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.playlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 8px;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.list li:hover {
  background: #f5f7fa;
}

.list li.active {
  color: var(--primary-color);
  background: #fff2f6;
}

.list-info {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-btn {
  color: #c0c4cc;
  margin-left: 8px;
  padding: 0 4px;
}

.delete-btn:hover {
  color: #f56c6c;
}
</style>
