/**
 * useAsync composable - Handle async operations with loading/error state.
 */
import { ref } from "vue";
import { useLoading } from "./useLoading";

export function useAsync<T>(asyncFn: () => Promise<T>) {
  const { loading, isLoading, error, hasError, startLoading, stopLoading, setError } = useLoading();
  const data = ref<T | null>(null);

  async function execute(...args: unknown[]) {
    startLoading();
    data.value = null;

    try {
      const result = await asyncFn.apply(null, args as Parameters<typeof asyncFn>);
      data.value = result;
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "操作失败";
      setError(message);
      throw err;
    } finally {
      stopLoading();
    }
  }

  async function executeSafe(...args: unknown[]) {
    try {
      return await execute(...args);
    } catch {
      // Error already handled
    }
  }

  return {
    data,
    loading,
    isLoading,
    error,
    hasError,
    execute,
    executeSafe,
  };
}