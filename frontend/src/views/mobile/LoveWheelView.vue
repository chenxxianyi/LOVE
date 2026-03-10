<template>
    <div class="wheel-page">
        <van-nav-bar title="恋爱大转盘" left-arrow @click-left="onClickLeft" />

        <div class="header-text">
            <p>不知道做什么？让命运来决定吧！</p>
        </div>

        <div class="wheel-container">
            <div class="wheel-wrapper">
                <div class="wheel-outer-ring">
                    <canvas ref="canvasRef" width="300" height="300" class="wheel-canvas"></canvas>
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
                <div class="result-text">{{ result || '...' }}</div>
            </div>
        </div>

        <div style="padding: 16px;">
            <van-button round block type="primary" color="linear-gradient(to right, #ff6034, #ee0a24)"
                @click="showEditDialog = true">
                编辑选项
            </van-button>
        </div>

        <!-- Edit Popup -->
        <van-popup v-model:show="showEditDialog" position="bottom" round :style="{ height: '70%' }">
            <div class="popup-header">
                <div class="popup-title">编辑转盘选项</div>
            </div>
            <div class="options-list">
                <div v-for="(opt, index) in editOptions" :key="index" class="option-item">
                    <!-- A simple color indicator instead of full color picker to keep mobile UI clean -->
                    <div class="color-dot" :style="{ backgroundColor: opt.color }"></div>
                    <van-field v-model="opt.text" placeholder="选项内容" class="option-input" clearable />
                    <van-icon name="delete-o" size="24" color="#ee0a24" @click="removeOption(index)"
                        v-if="editOptions.length > 2" />
                </div>
                <div class="add-btn-wrapper">
                    <van-button plain type="primary" block icon="plus" @click="addOption"
                        style="margin-top: 10px;">添加新选项</van-button>
                </div>
            </div>
            <div class="popup-footer">
                <van-button block round type="danger" @click="saveOptions">保存更改</van-button>
            </div>
        </van-popup>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from "vue";
import { useRouter } from "vue-router";
import { useLoveStore } from "../../stores/useLoveStore";
import { showSuccessToast } from "vant";

const router = useRouter();
const store = useLoveStore();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const isSpinning = ref(false);
const result = ref<string | null>(null);
const showEditDialog = ref(false);
const currentRotation = ref(0);

// Local copy for editing
const editOptions = reactive([...store.wheelOptions]);

const onClickLeft = () => {
    router.back();
};

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
    const radius = Math.min(centerX, centerY) - 8; // responsive radius

    ctx.clearRect(0, 0, width, height);

    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(currentRotation.value);
    ctx.translate(-centerX, -centerY);

    for (let i = 0; i < numOptions; i++) {
        const angle = i * arc;

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, angle, angle + arc);
        ctx.closePath();

        ctx.fillStyle = options[i].color;
        ctx.fill();

        ctx.lineWidth = 3;
        ctx.strokeStyle = "#ffffff";
        ctx.stroke();

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(angle + arc / 2);
        ctx.textAlign = "right";

        ctx.shadowColor = "rgba(0,0,0,0.2)";
        ctx.shadowBlur = 4;
        ctx.shadowOffsetY = 2;

        ctx.fillStyle = "#ffffff";
        // Smaller font for mobile
        ctx.font = "bold 16px 'PingFang SC', 'Microsoft YaHei', sans-serif";
        ctx.fillText(options[i].text, radius - 30, 6);

        ctx.font = "12px Arial";
        ctx.fillText("✨", radius - 10, 4);

        ctx.restore();
    }

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

    const spinAngle = (Math.random() * 4 + 6) * Math.PI * 2 + Math.random() * Math.PI * 2;
    const startRotation = currentRotation.value;
    const targetRotation = startRotation + spinAngle;
    const duration = 4000;
    const startTime = performance.now();

    const animate = (time: number) => {
        const elapsed = time - startTime;
        const progress = Math.min(elapsed / duration, 1);
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
    showSuccessToast(`命运选择了：${options[index].text}！`);
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
    showSuccessToast("选项已更新");
};
</script>

<style scoped>
.wheel-page {
    min-height: 100vh;
    background-color: #f7f8fa;
}

.header-text {
    text-align: center;
    padding: 20px 16px 10px;
}

.header-text p {
    margin: 0;
    color: #666;
    font-size: 14px;
}

.wheel-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 30px 16px 20px;
    position: relative;
}

.wheel-wrapper {
    position: relative;
    width: 320px;
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    margin-bottom: 20px;
}

.wheel-outer-ring {
    position: relative;
    width: 310px;
    height: 310px;
    border-radius: 50%;
    background: linear-gradient(135deg, #fff3f3 0%, #ffd1d1 100%);
    padding: 10px;
    box-shadow:
        0 15px 30px rgba(0, 0, 0, 0.1),
        inset 0 4px 10px rgba(255, 255, 255, 0.8),
        inset 0 -4px 10px rgba(0, 0, 0, 0.05);
}

.wheel-canvas {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    display: block;
}

.pointer-container {
    position: absolute;
    top: -16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
}

.pointer {
    width: 28px;
    height: 40px;
    background: linear-gradient(135deg, #ff5e62 0%, #ff9966 100%);
    clip-path: polygon(50% 100%, 0 0, 100% 0);
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    position: relative;
    z-index: 2;
}

.pointer::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 50%;
    transform: translateX(-50%);
    width: 8px;
    height: 8px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
}

.pointer-shadow {
    position: absolute;
    top: 6px;
    left: 50%;
    transform: translateX(-50%);
    width: 28px;
    height: 40px;
    background: rgba(0, 0, 0, 0.2);
    clip-path: polygon(50% 100%, 0 0, 100% 0);
    filter: blur(3px);
    z-index: 1;
}

.spin-btn {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
    border: 4px solid #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    z-index: 10;
    padding: 0;
    outline: none;
}

.spin-text {
    font-weight: 900;
    font-size: 18px;
    background: linear-gradient(135deg, #ff5e62 0%, #ff9966 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.spin-btn:active:not(.disabled) {
    transform: translate(-50%, -50%) scale(0.95);
}

.spin-btn.disabled {
    background: #f0f0f0;
    border-color: #f5f5f5;
    cursor: not-allowed;
}

.spin-btn.disabled .spin-text {
    background: #999;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.result-display {
    margin-top: 20px;
    text-align: center;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.4s ease;
    min-height: 80px;
}

.result-display.show {
    opacity: 1;
    transform: translateY(0);
}

.result-subtitle {
    color: #888;
    margin-bottom: 4px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.result-text {
    font-size: 32px;
    font-weight: bold;
    background: linear-gradient(135deg, #ff5e62 0%, #ff9966 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.popup-header {
    padding: 16px;
    text-align: center;
    border-bottom: 1px solid #f5f5f5;
}

.popup-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
}

.options-list {
    padding: 16px;
    max-height: calc(100% - 120px);
    overflow-y: auto;
}

.option-item {
    display: flex;
    align-items: center;
    background: #f9f9f9;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 12px;
}

.color-dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    margin-right: 12px;
    border: 1px solid #eee;
}

.option-input {
    flex: 1;
    background: transparent;
    padding: 4px 8px;
}

.popup-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px;
    background: #fff;
    border-top: 1px solid #f5f5f5;
}
</style>
