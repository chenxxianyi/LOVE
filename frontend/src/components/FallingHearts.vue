<template>
  <div class="falling-hearts" aria-hidden="true">
    <span
      v-for="leaf in leaves"
      :key="leaf.id"
      class="heart-leaf"
      :style="leaf.style"
    >
      {{ leaf.char }}
    </span>
  </div>
</template>

<script setup lang="ts">
type LeafStyle = Record<string, string>;

interface HeartLeaf {
  id: number;
  char: string;
  style: LeafStyle;
}

const chars = ["❤", "♥", "❥"];
const colors = ["#f4b8c4", "#f9d7df", "#f7c9a8", "#f2a9b8"];
const count =
  typeof window !== "undefined" && window.innerWidth <= 768 ? 14 : 24;

const leaves: HeartLeaf[] = Array.from({ length: count }, (_, idx) => {
  const left = Math.random() * 100;
  const fontSize = 14 + Math.random() * 14;
  const fallDuration = 8 + Math.random() * 10;
  const swayDuration = 1.8 + Math.random() * 2.2;
  const delay = -(Math.random() * 12);
  const drift = `${Math.round(Math.random() * 120 - 60)}px`;
  const spin = `${Math.round(Math.random() * 340 + 80)}deg`;
  const opacity = (0.45 + Math.random() * 0.4).toFixed(2);

  return {
    id: idx + 1,
    char: chars[idx % chars.length],
    style: {
      left: `${left}%`,
      fontSize: `${fontSize}px`,
      color: colors[idx % colors.length],
      opacity,
      "--fall-duration": `${fallDuration}s`,
      "--sway-duration": `${swayDuration}s`,
      "--fall-delay": `${delay}s`,
      "--drift": drift,
      "--spin": spin,
    } as LeafStyle,
  };
});
</script>

<style scoped>
.falling-hearts {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  overflow: hidden;
}

.heart-leaf {
  position: absolute;
  top: -12vh;
  user-select: none;
  text-shadow: 0 2px 8px rgba(224, 140, 164, 0.3);
  animation-name: heart-fall, heart-sway;
  animation-duration: var(--fall-duration), var(--sway-duration);
  animation-timing-function: linear, ease-in-out;
  animation-delay: var(--fall-delay), var(--fall-delay);
  animation-iteration-count: infinite, infinite;
  animation-direction: normal, alternate;
  will-change: transform;
}

@keyframes heart-fall {
  0% {
    transform: translate3d(0, -12vh, 0) rotate(0deg);
  }

  100% {
    transform: translate3d(var(--drift), 112vh, 0) rotate(var(--spin));
  }
}

@keyframes heart-sway {
  0% {
    margin-left: -10px;
  }

  100% {
    margin-left: 10px;
  }
}

@media (max-width: 768px) {
  .falling-hearts {
    z-index: 10;
  }
}
</style>
