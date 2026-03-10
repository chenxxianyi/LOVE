<template>
  <div class="wheel-page">
    <header class="page-head soft-card fade-up">
      <div class="head-content">
        <div class="header-text">
          <h1 class="title-font">恋爱大转盘</h1>
          <p>不知道做什么？让命运来决定吧！</p>
        </div>
        <button class="custom-edit-btn" @click="showEditDialog = true">
          编辑选项
        </button>
      </div>
    </header>

    <div class="wheel-container soft-card fade-up">
      <div class="wheel-wrapper">
        <div class="wheel-outer-ring">
          <canvas ref="canvasRef" width="440" height="440" class="wheel-canvas"></canvas>
        </div>
        <div class="pointer-container">
          <div class="pointer"></div>
          <div class="pointer-shadow"></div>
        </div>
        <button class="spin-btn" @click="spinWheel" :class="{ disabled: isSpinning }">
          <span class="spin-text">{{ isSpinning ? '...' : 'GO' }}</span>
        </button>
      </div>

      <div class="result-display" :class="{ 'show': result }">
        <h3 class="result-subtitle">命运的安排是</h3>
        <div class="result-text title-font">{{ result || '...' }}</div>
      </div>
    </div>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="编辑转盘选项" width="480px" class="premium-dialog">
      <div class="options-list">
        <div v-for="(opt, index) in editOptions" :key="index" class="option-item fade-up"
          :style="{ animationDelay: `${index * 0.05}s` }">
          <el-color-picker v-model="opt.color" size="default" />
          <el-input v-model="opt.text" placeholder="选项内容" size="large" />
          <el-button type="danger" icon="Delete" circle plain size="default" @click="removeOption(index)"
            :disabled="editOptions.length <= 2" />
        </div>
        <el-button class="add-btn" type="primary" plain @click="addOption" style="width: 100%" size="large"
          icon="Plus">添加新选项</el-button>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false" size="large" round>取消</el-button>
          <el-button type="primary" @click="saveOptions" size="large" round>保存更改</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from "vue";
import { useLoveStore } from "../stores/useLoveStore";
import { ElMessage } from "element-plus";

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
  const width = canvas.width;
  const height = canvas.height;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(centerX, centerY) - 10; // slightly smaller to avoid clipping borders

  ctx.clearRect(0, 0, width, height);

  // Rotate based on current state
  ctx.save();
  ctx.translate(centerX, centerY);
  ctx.rotate(currentRotation.value);
  ctx.translate(-centerX, -centerY);

  for (let i = 0; i < numOptions; i++) {
    const angle = i * arc;

    // Draw slice
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, angle, angle + arc);
    ctx.closePath();

    // Fill slice
    ctx.fillStyle = options[i].color;
    ctx.fill();

    // Draw lines between slices (border)
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#ffffff";
    ctx.stroke();

    // Text & formatting
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(angle + arc / 2);
    ctx.textAlign = "right";

    // Shadow for text to stand out nicely
    ctx.shadowColor = "rgba(0,0,0,0.2)";
    ctx.shadowBlur = 4;
    ctx.shadowOffsetY = 2;

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 22px 'PingFang SC', 'Microsoft YaHei', sans-serif";
    ctx.fillText(options[i].text, radius - 45, 8);

    // Add decorative element far right
    ctx.font = "14px Arial";
    ctx.fillText("✨", radius - 20, 5);

    ctx.restore();
  }

  // Draw a glossy overlay on the whole wheel
  const gloss = ctx.createRadialGradient(
    centerX - radius * 0.3, centerY - radius * 0.3, 0,
    centerX, centerY, radius
  );
  gloss.addColorStop(0, "rgba(255,255,255,0.3)");
  gloss.addColorStop(1, "rgba(255,255,255,0)");
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
  ctx.fillStyle = gloss;
  ctx.fill();

  ctx.restore();
};

const spinWheel = () => {
  if (isSpinning.value) return;

  isSpinning.value = true;
  result.value = null;

  const options = store.wheelOptions;
  // Random spins (6-10 full rotations) + random offset to guarantee randomness
  const spinAngle = (Math.random() * 4 + 6) * Math.PI * 2 + Math.random() * Math.PI * 2;

  const startRotation = currentRotation.value;
  const targetRotation = startRotation + spinAngle;
  const duration = 4000; // 4 seconds for a more dramatic spin
  const startTime = performance.now();

  const animate = (time: number) => {
    const elapsed = time - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Custom cubic-bezier like ease-out function
    const easeOut = 1 - Math.pow(1 - progress, 3.5);

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

  const normalizedRotation = currentRotation.value % (Math.PI * 2);

  let angleAtPointer = (Math.PI * 1.5 - normalizedRotation) % (Math.PI * 2);
  if (angleAtPointer < 0) angleAtPointer += Math.PI * 2;

  const index = Math.floor(angleAtPointer / arc);
  result.value = options[index].text;
  ElMessage.success(`命运选择了：${options[index].text}！`);
};

const addOption = () => {
  const id = Date.now();
  editOptions.push({
    id,
    text: `选项 ${editOptions.length + 1}`,
    color: '#' + Math.floor(Math.random() * 16777215).toString(16)
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
  padding: 30px;
  margin-bottom: 30px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(255, 94, 98, 0.05);
}

.head-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  margin: 0 0 10px;
  font-size: 36px;
  color: var(--primary-color);
}

.header-text p {
  margin: 0;
  color: var(--text-sub);
  font-size: 16px;
}

.custom-edit-btn {
  background: linear-gradient(135deg, var(--primary-color, #e49bab) 0%, #ff7f8e 100%);
  color: #fff;
  border: 1px solid rgba(255, 120, 140, 0.55);
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 30px;
  cursor: pointer;
  box-shadow:
    0 10px 22px rgba(228, 155, 171, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: all 0.25s ease;
  text-shadow: 0 1px 2px rgba(120, 40, 55, 0.35);
}

.custom-edit-btn:hover {
  transform: translateY(-2px);
  box-shadow:
    0 14px 26px rgba(228, 155, 171, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.custom-edit-btn:active {
  transform: translateY(0);
  box-shadow: 0 6px 14px rgba(228, 155, 171, 0.3);
}

.custom-edit-btn:focus-visible {
  outline: 3px solid rgba(255, 146, 158, 0.55);
  outline-offset: 3px;
}

.wheel-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 20px 100px;
  min-height: 550px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.03);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 94, 98, 0.05);
}

/* Add a very subtle gradient background to the container */
.wheel-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top right, rgba(255, 94, 98, 0.05) 0%, transparent 40%),
    radial-gradient(circle at bottom left, rgba(255, 153, 102, 0.05) 0%, transparent 40%);
  pointer-events: none;
}

.wheel-wrapper {
  position: relative;
  width: 460px;
  height: 460px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  margin-bottom: 20px;
}

.wheel-outer-ring {
  position: relative;
  width: 440px;
  height: 440px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fff3f3 0%, #ffd1d1 100%);
  padding: 10px;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.1),
    inset 0 4px 10px rgba(255, 255, 255, 0.8),
    inset 0 -4px 10px rgba(0, 0, 0, 0.05),
    0 0 0 12px rgba(255, 255, 255, 0.4);
}

.wheel-canvas {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.2);
  display: block;
}

.pointer-container {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.pointer {
  width: 38px;
  height: 52px;
  background: linear-gradient(135deg, #ff5e62 0%, #ff9966 100%);
  clip-path: polygon(50% 100%, 0 0, 100% 0);
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2));
  position: relative;
  z-index: 2;
}

.pointer::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
}

.pointer-shadow {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 38px;
  height: 52px;
  background: rgba(0, 0, 0, 0.2);
  clip-path: polygon(50% 100%, 0 0, 100% 0);
  filter: blur(4px);
  z-index: 1;
}

.spin-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
  border: 6px solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 10px 25px rgba(0, 0, 0, 0.1),
    inset 0 -4px 8px rgba(0, 0, 0, 0.05),
    inset 0 4px 8px rgba(255, 255, 255, 1);
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  padding: 0;
  outline: none;
}

.spin-text {
  font-weight: 900;
  font-size: 26px;
  background: linear-gradient(135deg, #ff5e62 0%, #ff9966 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

.spin-btn:hover:not(.disabled) {
  transform: translate(-50%, -50%) scale(1.08);
  box-shadow:
    0 15px 35px rgba(255, 94, 98, 0.25),
    inset 0 -4px 8px rgba(0, 0, 0, 0.05),
    inset 0 4px 8px rgba(255, 255, 255, 1);
}

.spin-btn:active:not(.disabled) {
  transform: translate(-50%, -50%) scale(0.95);
  transition: all 0.1s;
}

.spin-btn.disabled {
  background: #f0f0f0;
  border-color: #f5f5f5;
  cursor: not-allowed;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.spin-btn.disabled .spin-text {
  background: #999;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.result-display {
  margin-top: 30px;
  text-align: center;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: absolute;
  bottom: 25px;
  left: 0;
  right: 0;
}

.result-display.show {
  opacity: 1;
  transform: translateY(0);
}

.result-subtitle {
  color: #888;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.result-text {
  font-size: 56px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary-color) 0%, #ff9966 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 10px 30px rgba(255, 94, 98, 0.15);
  animation: pulseResult 2s infinite ease-in-out;
}

@keyframes pulseResult {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.02);
  }

  100% {
    transform: scale(1);
  }
}

/* Edit Dialog Styling */
.options-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 16px;
  background: #fdfdfd;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.option-item:hover {
  border-color: rgba(255, 94, 98, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Custom fade up animation */
.fade-up {
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
