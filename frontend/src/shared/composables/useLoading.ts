/**
 * useLoading composable - Manage loading state.
 */
import { ref, computed } from "vue";

export function useLoading(initial = false) {
  const loading = ref(initial);
  const error = ref<string | null>(null);

  const isLoading = computed(() => loading.value);
  const hasError = computed(() => error.value !== null);

  function startLoading() {
    loading.value = true;
    error.value = null;
  }

  function stopLoading() {
    loading.value = false;
  }

  function setError(message: string) {
    error.value = message;
    loading.value = false;
  }

  function clearError() {
    error.value = null;
  }

  return {
    loading,
    isLoading,
    error,
    hasError,
    startLoading,
    stopLoading,
    setError,
    clearError,
  };
}