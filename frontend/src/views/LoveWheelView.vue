<template>
  <div class="wheel-page">
    <header class="page-head soft-card fade-up">
      <div class="head-content">
        <div>
          <h1 class="title-font">恋爱大转盘</h1>
          <p>不知道做什么？让命运来决定吧！</p>
        </div>
        <el-button type="primary" round size="large" @click="showEditDialog = true">
          编辑选项
        </el-button>
      </div>
    </header>

    <div class="wheel-container soft-card fade-up">
      <div class="wheel-wrapper">
        <canvas ref="canvasRef" width="400" height="400" class="wheel-canvas"></canvas>
        <div class="pointer">▼</div>
        <div class="spin-btn" @click="spinWheel" :class="{ disabled: isSpinning }">
          {{ isSpinning ? '...' : 'GO' }}
        </div>
      </div>
      
      <div class="result-display" v-if="result">
        <h3>命运的安排是：</h3>
        <div class="result-text title-font">{{ result }}</div>
      </div>
    </div>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="编辑转盘选项" width="500px">
      <div class="options-list">
        <div v-for="(opt, index) in editOptions" :key="index" class="option-item">
          <el-color-picker v-model="opt.color" size="small" />
          <el-input v-model="opt.text" placeholder="选项内容" />
          <el-button type="danger" icon="Delete" circle size="small" @click="removeOption(index)" :disabled="editOptions.length <= 2" />
        </div>
        <el-button class="add-btn" type="dashed" @click="addOption" style="width: 100%">+ 添加选项</el-button>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveOptions">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";
import { Delete } from "@element-plus/icons-vue";

const store = useLoveStore();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const isSpinning = ref(false);
const result = ref<string | null>(null);
const showEditDialog = ref(false);
const currentRotation = ref(0);

// Local copy for editing
const editOptions = reactive([...store.wheelOptions]);

onMounted(() => {
  drawWheel();
});

watch(() => store.wheelOptions, () => {
  drawWheel();
  // Update edit copy
  editOptions.splice(0, editOptions.length, ...store.wheelOptions);
}, { deep: true });

const drawWheel = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const options = store.wheelOptions;
  const numOptions = options.length;
  const arc = Math.PI * 2 / numOptions;
  const radius = canvas.width / 2;
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Rotate based on current state
  ctx.save();
  ctx.translate(centerX, centerY);
  ctx.rotate(currentRotation.value);
  ctx.translate(-centerX, -centerY);

  for (let i = 0; i < numOptions; i++) {
    const angle = i * arc;
    ctx.fillStyle = options[i].color;
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius - 10, angle, angle + arc);
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#fff";
    ctx.stroke();

    // Text
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(angle + arc / 2);
    ctx.textAlign = "right";
    ctx.fillStyle = "#fff";
    ctx.font = "bold 16px 'PingFang SC', 'Microsoft YaHei', sans-serif";
    ctx.shadowColor = "rgba(0,0,0,0.2)";
    ctx.shadowBlur = 4;
    ctx.fillText(options[i].text, radius - 40, 6);
    
    // Add decorative heart icon
    ctx.font = "14px Arial";
    ctx.fillText("♥", radius - 20, 5);
    
    ctx.restore();
  }
  ctx.restore();
  
  // Center White Circle (Hub)
  ctx.beginPath();
  ctx.arc(centerX, centerY, 50, 0, Math.PI * 2);
  ctx.fillStyle = "#fff";
  ctx.fill();
  ctx.shadowColor = "rgba(0,0,0,0.1)";
  ctx.shadowBlur = 10;
  ctx.stroke();

  // Outer Border
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius - 5, 0, Math.PI * 2);
  ctx.lineWidth = 8;
  ctx.strokeStyle = "rgba(255,255,255,0.8)";
  ctx.stroke();
  
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius - 5, 0, Math.PI * 2);
  ctx.lineWidth = 2;
  ctx.strokeStyle = "rgba(0,0,0,0.05)";
  ctx.stroke();
};

const spinWheel = () => {
  if (isSpinning.value) return;
  
  isSpinning.value = true;
  result.value = null;
  
  const options = store.wheelOptions;
  // Random spins (5-10 full rotations) + random offset
  const spinAngle = (Math.random() * 5 + 5) * Math.PI * 2 + Math.random() * Math.PI * 2;
  
  const startRotation = currentRotation.value;
  const targetRotation = startRotation + spinAngle;
  const duration = 3000; // 3 seconds
  const startTime = performance.now();

  const animate = (time: number) => {
    const elapsed = time - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Ease out cubic function
    const easeOut = 1 - Math.pow(1 - progress, 3);
    
    currentRotation.value = startRotation + spinAngle * easeOut;
    drawWheel();

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      isSpinning.value = false;
      calculateResult();
    }
  };

  requestAnimationFrame(animate);
};

const calculateResult = () => {
  const options = store.wheelOptions;
  const numOptions = options.length;
  const arc = Math.PI * 2 / numOptions;
  
  // Normalize rotation to 0-2PI
  const normalizedRotation = currentRotation.value % (Math.PI * 2);
  
  // The pointer is at -PI/2 (top), so we need to find which segment is there
  // Effectively, we are looking at the angle 2PI - normalizedRotation - PI/2
  // But easier logic: Pointer is static at top.
  // The wheel rotated clockwise by `normalizedRotation`.
  // So the segment at top is determined by how much we rotated.
  
  // Correct logic:
  // Angle 0 is at 3 o'clock in canvas arc.
  // Pointer is at 12 o'clock (3/2 PI or -PI/2).
  // We need to transform the pointer angle to the wheel's coordinate system
  
  // Simple approximation that works:
  // Index = floor((2PI - (rotation % 2PI) + PI/2) / arc) % N
  
  // Let's rely on visual for now, or refine math:
  // Pointer is fixed at TOP.
  // Angle 0 of slice 0 starts at 3 o'clock.
  // So slice 0 covers [0, arc].
  // Slice 1 covers [arc, 2*arc], etc.
  // When rotated by R, slice 0 covers [0+R, arc+R].
  // We want to know which slice covers angle = 3/2 PI (270 deg / Top).
  
  let angleAtPointer = (Math.PI * 1.5 - normalizedRotation) % (Math.PI * 2);
  if (angleAtPointer < 0) angleAtPointer += Math.PI * 2;
  
  const index = Math.floor(angleAtPointer / arc);
  result.value = options[index].text;
  ElMessage.success(`结果是：${options[index].text}！`);
};

const addOption = () => {
  const id = Date.now();
  editOptions.push({
    id,
    text: `选项 ${editOptions.length + 1}`,
    color: '#' + Math.floor(Math.random()*16777215).toString(16)
  });
};

const removeOption = (index: number) => {
  editOptions.splice(index, 1);
};

const saveOptions = () => {
  store.updateWheelOptions([...editOptions]);
  showEditDialog.value = false;
  ElMessage.success("选项已更新");
};
</script>

<style scoped>
.wheel-page {
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

.wheel-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  min-height: 500px;
  background: radial-gradient(circle at center, #fff 0%, #fff9f9 100%);
}

.wheel-wrapper {
  position: relative;
  width: 400px;
  height: 400px;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1));
}

.wheel-canvas {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.pointer {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0;
  z-index: 10;
  width: 40px;
  height: 50px;
  background: #ff5e62;
  clip-path: polygon(0 0, 100% 0, 50% 100%);
  filter: drop-shadow(0 4px 4px rgba(0,0,0,0.2));
}

.spin-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 22px;
  color: var(--primary-color);
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  cursor: pointer;
  z-index: 10;
  border: none;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.spin-btn:hover {
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 8px 25px rgba(255, 94, 98, 0.3);
}

.spin-btn:active {
  transform: translate(-50%, -50%) scale(0.95);
}

.spin-btn.disabled {
  background: #f5f5f5;
  color: #ccc;
  border-color: #ddd;
  cursor: not-allowed;
}

.result-display {
  margin-top: 40px;
  text-align: center;
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.result-display h3 {
  color: var(--text-sub);
  margin-bottom: 10px;
}

.result-text {
  font-size: 48px;
  color: var(--primary-color);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.5); }
  to { opacity: 1; transform: scale(1); }
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.add-btn {
  margin-top: 10px;
}
</style>
