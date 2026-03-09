# LOVE P0 前端开发设计

## 1. 目标与范围

本设计用于指导 P0 前端落地，覆盖以下模块：

- 账号体系：登录、注册、忘记密码、刷新会话
- 双人配对：创建空间、邀请码邀请、加入空间、配对完成
- 安全中心：安全设置、设备管理、操作日志
- 备份中心：手动备份、快照列表、恢复确认、导出数据
- 提醒系统：提醒中心、提醒编辑、消息中心

P0 不做：第三方登录、多空间切换、复杂运营系统。

---

## 2. 技术与架构

### 2.1 技术栈

- Vue 3 + TypeScript + Vite
- Pinia（状态管理）
- Vue Router（权限路由）
- Axios（HTTP）
- Element Plus（UI）

### 2.2 新目录建议

```text
frontend/src/
├─ api/
│  ├─ client.ts
│  ├─ auth.ts
│  ├─ couple.ts
│  ├─ security.ts
│  ├─ backup.ts
│  └─ reminder.ts
├─ stores/
│  ├─ useAuthStore.ts
│  ├─ useCoupleStore.ts
│  ├─ useSecurityStore.ts
│  ├─ useBackupStore.ts
│  ├─ useReminderStore.ts
│  └─ useNotificationStore.ts
├─ types/
│  ├─ auth.ts
│  ├─ couple.ts
│  ├─ security.ts
│  ├─ backup.ts
│  └─ reminder.ts
├─ views/p0/
│  ├─ AuthView.vue
│  ├─ ForgotPasswordView.vue
│  ├─ CoupleCreateView.vue
│  ├─ CoupleInviteView.vue
│  ├─ CoupleJoinView.vue
│  ├─ CoupleSuccessView.vue
│  ├─ SecuritySettingsView.vue
│  ├─ DeviceManagementView.vue
│  ├─ OperationLogsView.vue
│  ├─ BackupCenterView.vue
│  ├─ BackupRestoreView.vue
│  ├─ ExportCenterView.vue
│  ├─ ReminderCenterView.vue
│  ├─ ReminderEditView.vue
│  └─ NotificationsView.vue
└─ components/p0/
   ├─ SensitiveActionDialog.vue
   ├─ RequestStatePanel.vue
   ├─ InviteCodeCard.vue
   ├─ BackupSnapshotTable.vue
   └─ ReminderRuleForm.vue
```

### 2.3 API 统一规则

1. 统一通过 `api/client.ts` 发请求。
2. `401` 自动刷新 token；刷新失败后清理登录态并跳转 `/auth`。
3. API 基础地址来自 `VITE_API_BASE_URL`，禁止硬编码。
4. 统一错误提示：
   - 4xx：直接提示业务原因
   - 5xx：提示“系统繁忙，请稍后重试”

---

## 3. 路由与权限

### 3.1 路由清单

| 路由 | 页面 | 权限 |
|---|---|---|
| `/auth` | 登录/注册 | 公开 |
| `/auth/forgot` | 忘记密码 | 公开 |
| `/couple/create` | 创建空间 | 已登录、未配对 |
| `/couple/invite` | 邀请对方 | 已登录、未配对 |
| `/couple/join` | 输入邀请码 | 已登录、未配对 |
| `/couple/success` | 配对成功 | 已登录 |
| `/settings/security` | 安全设置 | 已登录、已配对 |
| `/settings/security/devices` | 设备管理 | 已登录、已配对 |
| `/settings/security/logs` | 操作日志 | 已登录、已配对 |
| `/settings/backup` | 备份中心 | 已登录、已配对 |
| `/settings/backup/restore` | 恢复确认 | 已登录、已配对 |
| `/settings/export` | 导出中心 | 已登录、已配对 |
| `/reminders` | 提醒中心 | 已登录、已配对 |
| `/reminders/edit/:id?` | 新建/编辑提醒 | 已登录、已配对 |
| `/notifications` | 消息中心 | 已登录、已配对 |

### 3.2 守卫规则

1. 未登录访问私有页：重定向 `/auth`。
2. 已登录未配对访问业务页：重定向 `/couple/create`。
3. 已登录且已配对访问 `/auth`：重定向首页。
4. 敏感操作（恢复/导出/解绑）必须二次确认。

---

## 4. 页面开发规格（可交互原型级）

以下每页定义字段、按钮、状态文案、接口。

### 4.1 AuthView (`/auth`)

字段：
- 账号 `account`（手机号/邮箱）
- 密码 `password`（8-20 位）
- 协议勾选 `agreePolicy`

按钮：
- `登录`
- `注册`
- `忘记密码`
- `使用邀请码加入`

状态文案：
- 加载：`正在验证账号信息...`
- 成功：`欢迎回来`
- 错误：`账号或密码错误`

接口：
- `POST /auth/login`
- `POST /auth/register`

### 4.2 ForgotPasswordView (`/auth/forgot`)

字段：
- 账号
- 验证码
- 新密码

按钮：
- `发送验证码`
- `重置密码`

状态文案：
- `验证码已发送`
- `验证码错误或已过期`

接口：
- `POST /auth/forgot/send-code`
- `POST /auth/forgot/reset`

### 4.3 CoupleCreateView (`/couple/create`)

字段：
- 空间名 `space_name`
- 我的昵称 `my_nickname`
- 在一起日期 `start_date`
- 隐私级别 `privacy_level`

按钮：
- `创建并继续`
- `稍后设置`

状态文案：
- `创建失败，请重试`

接口：
- `POST /couple-space/create`

### 4.4 CoupleInviteView (`/couple/invite`)

字段：
- 邀请码（只读）
- 邀请链接（只读）
- 失效时间（只读）

按钮：
- `复制邀请码`
- `复制邀请链接`
- `重新生成`
- `我已发送，下一步`

状态文案：
- `等待对方输入邀请码...`
- `邀请码已过期，请重新生成`

接口：
- `POST /couple-space/invite`

### 4.5 CoupleJoinView (`/couple/join`)

字段：
- 邀请码 `invite_code`
- 我的昵称 `my_nickname`

按钮：
- `加入空间`

状态文案：
- `正在校验邀请码...`
- `邀请码无效或已过期`

接口：
- `POST /couple-space/join`

### 4.6 CoupleSuccessView (`/couple/success`)

字段：
- 双方昵称
- 空间名称
- 在一起天数

按钮：
- `进入纪念馆`
- `去设置提醒`

状态文案：
- `配对完成，开始记录你们的故事吧`

接口：
- `GET /couple-space/me`

### 4.7 SecuritySettingsView (`/settings/security`)

字段：
- 二次锁开关
- 异地登录提醒开关
- 敏感操作验证开关
- 回收站保留期（7/15/30天）

按钮：
- `保存设置`
- `修改密码`
- `申请解绑`

状态文案：
- `安全设置已更新`

接口：
- `GET /security/settings`
- `PATCH /security/settings`
- `POST /auth/change-password`
- `POST /couple-space/unbind/request`

### 4.8 DeviceManagementView (`/settings/security/devices`)

字段：
- 当前设备卡片
- 其他设备列表

按钮：
- `下线该设备`
- `下线全部其他设备`

状态文案：
- `暂无其他登录设备`

接口：
- `GET /security/sessions`
- `DELETE /security/sessions/{id}`

### 4.9 OperationLogsView (`/settings/security/logs`)

字段：
- 时间筛选
- 类型筛选
- 日志列表

按钮：
- `导出日志CSV`
- `重置筛选`

状态文案：
- `当前筛选条件下暂无记录`

接口：
- `GET /security/logs`
- `POST /security/logs/export`

### 4.10 BackupCenterView (`/settings/backup`)

字段：
- 自动备份状态
- 最近备份信息
- 快照列表

按钮：
- `立即备份`
- `查看失败原因`
- `去恢复`

状态文案：
- `备份中，请勿关闭页面`
- `本次备份失败，可重试或查看原因`

接口：
- `GET /backup/snapshots`
- `POST /backup/manual`
- `GET /backup/jobs/{id}`

### 4.11 BackupRestoreView (`/settings/backup/restore`)

字段：
- 快照选择
- 恢复模式（全量/合并）
- 二次验证

按钮：
- `开始恢复`
- `取消`

状态文案：
- `恢复完成，已为你创建恢复前快照`
- `恢复失败，当前数据未被修改`

接口：
- `POST /backup/restore`

### 4.12 ExportCenterView (`/settings/export`)

字段：
- 导出范围
- 时间范围
- 导出格式（ZIP）

按钮：
- `创建导出`
- `下载`
- `复制下载链接`

状态文案：
- `正在打包数据，请稍候`
- `下载链接已过期，请重新导出`

接口：
- `POST /backup/export`
- `GET /backup/export/{job_id}`

### 4.13 ReminderCenterView (`/reminders`)

字段：
- 分类筛选
- 提醒列表
- 开关状态

按钮：
- `新建提醒`
- `标记完成`
- `稍后提醒`
- `删除`

状态文案：
- `还没有提醒，先创建一个吧`

接口：
- `GET /reminders`
- `PATCH /reminders/{id}`
- `POST /reminders/{id}/done`
- `DELETE /reminders/{id}`

### 4.14 ReminderEditView (`/reminders/edit/:id?`)

字段：
- 标题
- 类型
- 触发时间
- 提前提醒
- 重复规则
- 通知方式
- 免打扰时段

按钮：
- `保存`
- `保存并测试提醒`
- `取消`

状态文案：
- `提醒已保存`
- `测试提醒已发送`

接口：
- `POST /reminders`
- `PUT /reminders/{id}`
- `POST /reminders/{id}/test`

### 4.15 NotificationsView (`/notifications`)

字段：
- 分类 tab
- 消息列表

按钮：
- `全部标记已读`
- `清空已读`
- `删除`

状态文案：
- `暂无消息`

接口：
- `GET /notifications`
- `POST /notifications/read-all`
- `DELETE /notifications/read`
- `DELETE /notifications/{id}`

---

## 5. Pinia 状态拆分

### useAuthStore

- state: `accessToken`, `user`, `isAuthenticated`, `loading`
- actions: `login`, `register`, `refreshToken`, `logout`, `fetchMe`

### useCoupleStore

- state: `space`, `members`, `pairStatus`
- actions: `createSpace`, `createInvite`, `joinByInvite`, `requestUnbind`, `confirmUnbind`

### useSecurityStore

- state: `settings`, `sessions`, `logs`
- actions: `fetchSettings`, `updateSettings`, `fetchSessions`, `kickSession`, `fetchLogs`

### useBackupStore

- state: `snapshots`, `backupJobs`, `restoreJobs`, `exportJobs`
- actions: `manualBackup`, `fetchSnapshots`, `restoreSnapshot`, `createExport`, `pollJob`

### useReminderStore

- state: `items`, `filters`, `draft`
- actions: `fetchReminders`, `createReminder`, `updateReminder`, `completeReminder`, `deleteReminder`

### useNotificationStore

- state: `items`, `unreadCount`
- actions: `fetchNotifications`, `readAll`, `removeRead`, `deleteOne`

---

## 6. 通用交互与异常处理

1. 每页必须支持 `loading/empty/error` 三态。
2. 表单统一在 `blur + submit` 时校验。
3. 全局 toast 文案统一：
   - 成功：`操作成功`
   - 失败：`操作失败，请稍后重试`
   - 网络异常：`网络异常，请检查后重试`
4. 敏感操作统一弹窗：`执行后不可直接撤销`。

---

## 7. 验收标准

### 功能验收

1. 未登录访问私有页会被拦截。
2. 未配对账号无法访问提醒、备份、安全等页。
3. 备份/恢复/导出/解绑均需二次确认。
4. 提醒创建后可编辑、可完成、可删除。

### 异常验收

1. token 过期后可自动刷新并重放请求。
2. 邀请码失效有明确提示和回退路径。
3. 网络中断后页面可重试。

### 兼容验收

1. 桌面端与移动端（<=768px）关键按钮不遮挡。
2. 主要页面首屏可用时间满足现有性能基线。

---

## 8. 开发节奏（前端）

### 第 1 周

- API 基础层与鉴权拦截器
- A01-A06（登录注册与配对流程）
- 路由守卫改造

### 第 2 周

- S01-S03（安全设置、设备、日志）
- SensitiveActionDialog 组件

### 第 3 周

- B01-B03（备份、恢复、导出）
- 任务轮询与失败重试

### 第 4 周

- R01-R03（提醒与消息）
- 全链路联调、回归测试、上线准备

---

## 9. 对现有代码的改造约束

1. 保留现有业务页（首页、时间线等），P0 页面独立放在 `views/p0`。
2. 将现有 store 拆分为模块化 store，避免单 store 继续膨胀。
3. 将所有硬编码 API 地址迁移到环境变量。
4. 新增 P0 后，不破坏现有 `npm run build`。
