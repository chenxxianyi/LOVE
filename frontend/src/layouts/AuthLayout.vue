<script setup lang="ts">
/**
 * Auth Layout - Layout for authentication pages (login, register, etc.)
 */
</script>

<template>
  <div class="auth-layout">
    <div class="auth-layout__container">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
}

.auth-layout__container {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
}
</style>