<template>
  <el-table :data="snapshots" stripe>
    <el-table-column prop="created_at" label="时间" min-width="170" />
    <el-table-column prop="source" label="来源" width="120" />
    <el-table-column prop="status" label="状态" width="120" />
    <el-table-column label="大小" width="120">
      <template #default="{ row }">{{ prettySize(row.size_bytes) }}</template>
    </el-table-column>
    <el-table-column label="操作" width="120">
      <template #default="{ row }">
        <el-button type="primary" text @click="$emit('restore', row.id)">恢复</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import type { BackupSnapshot } from "../../types/backup";

defineProps<{
  snapshots: BackupSnapshot[];
}>();

defineEmits<{
  (e: "restore", snapshotId: string | number): void;
}>();

function prettySize(sizeBytes: number): string {
  if (sizeBytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = sizeBytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`;
}
</script>
