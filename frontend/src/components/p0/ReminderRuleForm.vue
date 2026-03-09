<template>
  <el-form :model="model" label-width="90px">
    <el-form-item label="标题">
      <el-input v-model="model.title" />
    </el-form-item>

    <el-form-item label="类型">
      <el-select v-model="model.type" style="width: 100%">
        <el-option label="纪念日" value="anniversary" />
        <el-option label="胶囊" value="capsule" />
        <el-option label="每日问答" value="question" />
        <el-option label="愿望" value="bucket" />
      </el-select>
    </el-form-item>

    <el-form-item label="触发时间">
      <el-date-picker
        v-model="model.trigger_at"
        type="datetime"
        value-format="YYYY-MM-DD HH:mm:ss"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="重复规则">
      <el-select v-model="model.repeat_rule" style="width: 100%">
        <el-option label="不重复" value="none" />
        <el-option label="每天" value="daily" />
        <el-option label="每周" value="weekly" />
        <el-option label="每月" value="monthly" />
        <el-option label="每年" value="yearly" />
      </el-select>
    </el-form-item>

    <el-form-item label="通知方式">
      <el-checkbox-group v-model="model.channels">
        <el-checkbox label="in_app">站内</el-checkbox>
        <el-checkbox label="push">推送</el-checkbox>
        <el-checkbox label="email">邮件</el-checkbox>
      </el-checkbox-group>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import type { ReminderPayload } from "../../types/reminder";

const model = defineModel<ReminderPayload>({ required: true });
</script>
