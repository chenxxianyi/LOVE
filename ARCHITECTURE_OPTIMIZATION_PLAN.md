# LOVE 项目架构优化完整方案

## 0. 结论先行

当前项目是一个 `FastAPI + SQLAlchemy + MySQL` 后端、`Vue 3 + Vite + TypeScript + Pinia + Element Plus` 前端的情侣纪念应用。项目已经具备较完整的业务雏形：回忆时间线、地图足迹、愿望清单、时光胶囊、纪念日、每日问答、报告、音乐、账号认证、情侣空间、提醒、通知、安全设置、备份导出。

最适合的优化方向不是拆微服务，也不是重写，而是演进为“模块化单体”：

- 后端按领域拆分为 `auth / couple / memories / bucket / capsules / anniversaries / questions / media / notifications / reminders / backup / report`。
- 每个领域内部保持 `router -> service -> repository -> model/schema` 的清晰边界。
- 前端按业务模块组织 `features`，统一 API Client、状态管理、布局组件和路由守卫。
- 数据库引入迁移、统一时间类型、统一命名规范，并逐步修复历史编码问题。
- 短期保持兼容旧接口，长期收敛到 `/api/v1` 和后端鉴权。

这个方案的核心原则：保留现有产品气质和功能，先把边界立起来，再逐步迁移。

---

## 1. 当前项目判断

### 1.1 后端现状

当前后端有两条并行演进线：

1. 旧主应用集中在 `main.py`
   - 应用启动、CORS、静态文件、建表、种子数据、Pydantic Schema、业务路由、上传逻辑都放在一个文件里。
   - `main.py` 目前承担了过多职责，后续维护会变得越来越吃力。

2. P0 能力已经开始模块化
   - `love_core/routers/auth.py`
   - `love_core/routers/couple.py`
   - `love_core/routers/reminders.py`
   - `love_core/routers/notifications.py`
   - `love_core/routers/security.py`
   - `love_core/routers/backup.py`

这说明项目已经有了正确方向，但还没有形成统一架构。

### 1.2 前端现状

前端结构已经有基础分层：

- `views/` 页面
- `components/` 通用组件
- `stores/` Pinia 状态
- `api/` P0 API 模块
- `types/` 类型定义
- `router/` 路由守卫
- `styles/` 主题和全局样式

但也存在混合状态：

- 旧业务数据大量集中在 `useLoveStore.ts`。
- 旧 Store 直接使用 `axios.get("http://localhost:8000/...")`，新 P0 API 使用 `apiClient`。
- 认证逻辑同时存在旧的 `localStorage.isLoggedIn` 和新的 token 鉴权。
- `App.vue` 同时承担主 Shell、legacy Shell、背景效果、播放器、弹窗挂载等职责。
- UI 优化计划已经存在，但架构层还需要补齐。

### 1.3 主要风险

- 单文件后端继续膨胀，功能越多越难改。
- 旧接口没有用户/情侣空间隔离，未来多用户数据会混在一起。
- 没有 Alembic 迁移，数据库结构升级风险高。
- 日期大量用字符串保存，统计、排序、时区、重复提醒都会变复杂。
- 存在历史乱码，文案和种子数据可维护性差。
- CORS `allow_origins=["*"]`、硬编码数据库账号、SHA256 密码哈希只适合演示环境。
- 前端 API 调用方式不统一，错误处理和 token 刷新无法覆盖旧业务。

---

## 2. 架构目标

### 2.1 产品目标

- 保持 LOVE 当前“私密、温柔、纪念馆式”的产品体验。
- 支持两个人共享一个情侣空间。
- 所有核心内容都归属到情侣空间，而不是全局数据。
- 支持未来扩展：多设备、提醒、导出、备份、回收站、权限校验。

### 2.2 技术目标

- 后端从“单文件脚本式应用”升级为“模块化单体应用”。
- 前端从“页面 + 大 Store”升级为“功能模块 + 组合式数据层”。
- API 契约稳定，前后端类型边界明确。
- 数据库结构可迁移、可回滚、可审计。
- 保持开发启动简单，不引入复杂基础设施。

### 2.3 不建议做的事

- 现在不拆微服务。
- 现在不换 Nuxt / React / Nest / Django。
- 现在不引入 Kubernetes、消息队列、分布式任务系统。
- 现在不一次性重写所有页面和接口。

原因很简单：这个项目的复杂度还没有到需要微服务的程度，真正的痛点是模块边界和数据归属。

---

## 3. 推荐总体架构

```text
LOVE
├─ backend/
│  └─ app/
│     ├─ main.py
│     ├─ api/
│     │  └─ v1/
│     │     ├─ router.py
│     │     └─ endpoints/
│     ├─ core/
│     │  ├─ config.py
│     │  ├─ security.py
│     │  ├─ time.py
│     │  └─ errors.py
│     ├─ db/
│     │  ├─ base.py
│     │  ├─ session.py
│     │  └─ migrations/
│     ├─ domains/
│     │  ├─ auth/
│     │  ├─ couple/
│     │  ├─ memories/
│     │  ├─ bucket/
│     │  ├─ capsules/
│     │  ├─ anniversaries/
│     │  ├─ questions/
│     │  ├─ media/
│     │  ├─ reminders/
│     │  ├─ notifications/
│     │  ├─ backup/
│     │  └─ reports/
│     ├─ services/
│     ├─ storage/
│     └─ tests/
│
├─ frontend/
│  └─ src/
│     ├─ app/
│     ├─ shared/
│     ├─ features/
│     ├─ layouts/
│     ├─ router/
│     ├─ styles/
│     └─ main.ts
│
├─ docs/
│  ├─ architecture.md
│  ├─ api-contract.md
│  └─ migration-plan.md
└─ uploads/
```

如果不想马上移动目录，也可以先保留当前根目录结构，按这个目标逐步迁移。

---

## 4. 后端架构设计

### 4.1 后端分层

每个业务模块采用统一结构：

```text
domains/memories/
├─ models.py        # SQLAlchemy ORM
├─ schemas.py       # Pydantic 入参/出参
├─ repository.py    # 数据库读写
├─ service.py       # 业务规则
└─ router.py        # FastAPI 路由
```

职责边界：

- `router.py`：只做 HTTP 参数接收、依赖注入、返回响应。
- `service.py`：处理业务规则，例如权限、状态流转、日期计算。
- `repository.py`：封装查询和持久化，不写业务判断。
- `models.py`：只定义数据库结构。
- `schemas.py`：只定义接口契约。

示例调用链：

```text
POST /api/v1/memories
  -> memories.router.create_memory()
  -> memories.service.create_memory_for_space()
  -> memories.repository.create()
  -> db.commit()
```

### 4.2 API 分组

推荐最终接口：

```text
/api/v1/auth
/api/v1/couple-space
/api/v1/memories
/api/v1/bucket-items
/api/v1/time-capsules
/api/v1/anniversaries
/api/v1/questions
/api/v1/question-bank
/api/v1/music
/api/v1/covers
/api/v1/media
/api/v1/dashboard
/api/v1/reports
/api/v1/reminders
/api/v1/notifications
/api/v1/security
/api/v1/backup
```

旧接口先保留：

```text
/api/moments
/api/bucket
/api/capsules
/api/info
...
```

迁移策略：

- 第一阶段：新旧接口同时可用。
- 第二阶段：前端全部改用 `/api/v1`。
- 第三阶段：旧接口只保留兼容层。
- 第四阶段：删除旧接口。

### 4.3 应用入口

目标 `main.py` 只保留应用组装：

```python
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.middleware import setup_cors
from app.storage.static import mount_static_files

def create_app() -> FastAPI:
    app = FastAPI(title="LOVE API")
    setup_cors(app, settings)
    mount_static_files(app)
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()
```

建表、种子数据、数据库创建不要放在主入口里，改为：

- `alembic upgrade head`
- `python -m app.scripts.seed`

### 4.4 数据库模型重组

当前模型分散在：

- `database.py`
- `love_core/models.py`

建议迁移后按领域拆分，并统一导出：

```text
app/db/base.py
app/domains/auth/models.py
app/domains/couple/models.py
app/domains/memories/models.py
...
```

数据库核心关系建议：

```text
User
  └─ Session
  └─ SecuritySettings

CoupleSpace
  └─ CoupleMember
  └─ Invite
  └─ Memory
  └─ BucketItem
  └─ TimeCapsule
  └─ Anniversary
  └─ DailyQuestion
  └─ QuestionBank
  └─ Reminder
  └─ BackupSnapshot
```

关键点：

- 所有情侣内容都应有 `space_id`。
- 所有用户私有内容都应有 `user_id`。
- 所有可审计内容建议有 `created_at / updated_at / deleted_at`。
- 删除建议优先软删除，尤其是回忆、愿望、胶囊、纪念日。

### 4.5 推荐核心表

#### users

```text
id
account
password_hash
nickname
avatar
created_at
updated_at
```

#### user_sessions

```text
id
user_id
access_token_hash
refresh_token_hash
access_expires_at
refresh_expires_at
device_name
os
ip
last_seen_at
revoked_at
created_at
```

注意：token 最好只存 hash，不直接存明文。

#### couple_spaces

```text
id
space_name
start_date
privacy_level
created_by
created_at
updated_at
```

#### couple_members

```text
id
space_id
user_id
nickname
role
joined_at
```

建议唯一约束：

```text
unique(space_id, user_id)
unique(user_id)
```

#### memories

```text
id
space_id
title
occurred_at
location_name
latitude
longitude
mood
summary
has_video
created_by
created_at
updated_at
deleted_at
```

#### memory_assets

```text
id
memory_id
asset_type       # image | video
url
sort_order
created_at
```

相比把图片数组放在 JSON 字段里，单独拆表更利于排序、删除、封面、视频扩展。

### 4.6 时间和日期

当前大量时间是字符串：

```text
"2026-02-14 18:20"
"2024-04-21"
```

建议：

- 数据库存 `Date` / `DateTime(timezone=True)`。
- API 对外统一 ISO 8601 字符串。
- 后端集中提供时间工具。
- 前端展示时再格式化。

迁移优先级：

1. 新表和新字段先用标准时间类型。
2. 旧字段保留。
3. 写迁移脚本将旧字符串转为新字段。
4. 前端切换后删除旧字段。

### 4.7 配置管理

新增：

```text
app/core/config.py
.env
.env.example
```

配置项：

```text
APP_ENV=development
API_PREFIX=/api/v1
DATABASE_URL=mysql+pymysql://...
CORS_ORIGINS=http://localhost:5174
UPLOAD_DIR=uploads
PUBLIC_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5174
PASSWORD_SALT=...
ACCESS_TOKEN_TTL_MINUTES=120
REFRESH_TOKEN_TTL_DAYS=30
```

不要在代码里硬编码数据库账号、前端地址、上传地址。

### 4.8 安全设计

短期改进：

- CORS 改为环境变量白名单。
- 密码哈希从 `sha256(salt + password)` 升级到 `passlib[bcrypt]`。
- 上传文件校验扩展名、MIME、大小。
- 上传文件名保留 UUID，禁止用户文件名进入路径。
- token 存数据库时改为 hash。
- 敏感操作增加二次校验。

中期改进：

- 加入接口限流。
- 登录失败次数限制。
- 备份/导出文件过期清理。
- 操作日志补齐 actor、target、metadata。

### 4.9 文件存储

当前上传保存在本地 `uploads/`，可以继续保留，但要抽象一层：

```text
storage/
├─ base.py
├─ local.py
└─ service.py
```

对业务暴露：

```python
storage.save_upload(file) -> MediaAsset
storage.delete_asset(asset_id)
```

未来如果换 OSS/S3，只改 storage 层。

### 4.10 任务与提醒

当前提醒主要是 CRUD 和测试通知。推荐分阶段：

第一阶段：

- 保持同步逻辑。
- 提醒列表、状态、通知生成都在数据库内完成。

第二阶段：

- 增加轻量调度器，例如 APScheduler。
- 每分钟扫描到期提醒，生成通知。

第三阶段：

- 如果部署规模扩大，再考虑 Celery/RQ。

### 4.11 报告与统计

报告类接口不要散落在 `main.py`，统一放到 `reports` 或 `analytics`：

```text
domains/reports/
├─ router.py
├─ service.py
└─ queries.py
```

建议统计从 `space_id` 维度计算：

- 总回忆数
- 足迹地点数
- 图片/视频数量
- 高频心情
- 月度回忆数量
- 最近纪念日
- 愿望完成率

---

## 5. 前端架构设计

### 5.1 推荐目录结构

```text
frontend/src/
├─ app/
│  ├─ App.vue
│  ├─ providers.ts
│  └─ bootstrap.ts
├─ shared/
│  ├─ api/
│  │  ├─ client.ts
│  │  ├─ error.ts
│  │  └─ types.ts
│  ├─ components/
│  ├─ composables/
│  ├─ utils/
│  └─ styles/
├─ layouts/
│  ├─ AppShell.vue
│  ├─ AuthLayout.vue
│  ├─ CoupleSetupLayout.vue
│  └─ SettingsLayout.vue
├─ features/
│  ├─ auth/
│  ├─ couple/
│  ├─ home/
│  ├─ memories/
│  ├─ bucket/
│  ├─ capsules/
│  ├─ anniversaries/
│  ├─ questions/
│  ├─ reports/
│  ├─ media/
│  ├─ notifications/
│  ├─ reminders/
│  ├─ security/
│  └─ backup/
├─ router/
├─ styles/
└─ main.ts
```

每个 feature 内部：

```text
features/memories/
├─ api.ts
├─ types.ts
├─ store.ts
├─ composables.ts
├─ components/
└─ views/
```

### 5.2 API Client 统一

当前旧业务 Store 直接用硬编码 Axios 地址，新 P0 业务使用 `apiClient`。建议统一：

```text
shared/api/client.ts
features/*/api.ts
```

所有请求必须走 `apiClient`：

- 自动带 token。
- 自动刷新 token。
- 统一错误结构。
- 统一 baseURL。
- 统一超时。

旧代码迁移示例：

```ts
// before
axios.get("http://localhost:8000/api/moments")

// after
apiClient.get("/api/v1/memories")
```

如果后端新接口 prefix 已经设置为 `/api/v1`，前端 baseURL 可以是：

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 5.3 Store 设计

当前 `useLoveStore` 承担了太多业务：

- 情侣信息
- 回忆
- 愿望
- 胶囊
- 音乐
- 纪念日
- 封面
- 报告
- 每日问答
- 上传
- 登录兼容

建议拆分：

```text
useSessionStore
useCoupleStore
useHomeStore
useMemoryStore
useBucketStore
useCapsuleStore
useAnniversaryStore
useQuestionStore
useMusicStore
useMediaStore
useNotificationStore
useReminderStore
useSecurityStore
useBackupStore
```

拆分原则：

- 一个 Store 只管理一个业务领域。
- Store 不直接拼 URL，调用对应 feature API。
- Store 不做复杂业务计算，复杂计算放 service/composable。
- 页面只依赖自己需要的 Store。

### 5.4 路由与权限

建议统一路由元信息：

```ts
meta: {
  layout: "app" | "auth" | "setup" | "settings",
  public: boolean,
  requiresAuth: boolean,
  requiresPair: boolean,
  sensitive: boolean,
}
```

路由守卫逻辑顺序：

1. 初始化 session。
2. 如果页面需要登录但没有 token，跳转 `/auth`。
3. 如果页面需要情侣空间但没有配对，跳转 `/couple/create` 或 `/couple/invite`。
4. 如果页面敏感但未二次验证，跳转安全验证页。
5. 通过。

旧 `localStorage.isLoggedIn` 建议只保留一个兼容周期。

### 5.5 Layout 分层

当前 `App.vue` 挂载了太多全局内容。建议拆为：

```text
App.vue
  -> RouterView

AppShell.vue
  -> SideNav
  -> FallingHearts
  -> main content
  -> BGMPlayer
  -> GlobalDialogs

AuthLayout.vue
  -> 登录/注册/忘记密码

SettingsLayout.vue
  -> 设置类页面布局
```

好处：

- 登录页不会被主应用 Shell 影响。
- 设置页可以更工具化。
- 主应用视觉和功能挂件集中管理。
- 后续移动端 Shell 更容易拆。

### 5.6 UI 体系

当前已有 `FRONTEND_LAYOUT_CARD_OPTIMIZATION_PLAN.md`，建议继续沿用其方向。

架构层补充：

```text
shared/components/layout/PageFrame.vue
shared/components/layout/PageHeader.vue
shared/components/layout/MetricStrip.vue
shared/components/card/ContentCard.vue
shared/components/card/CompactItemCard.vue
shared/components/state/EmptyState.vue
shared/components/state/RequestStatePanel.vue
```

页面层只组合这些基础结构，不重复写布局细节。

### 5.7 类型来源

短期：

- 继续手写 `features/*/types.ts`。
- 按后端 Schema 对齐。

中期：

- 后端 OpenAPI 导出。
- 使用 `openapi-typescript` 生成前端 API 类型。

这样可以减少接口字段名不一致的问题，例如：

- `hasVideo` vs `has_video`
- `created_at` vs `createdAt`
- `days_left` vs `daysLeft`

建议最终统一 API 对外使用 `camelCase`，数据库和 Python 内部使用 `snake_case`。

---

## 6. 领域模块设计

### 6.1 Auth 认证模块

职责：

- 注册
- 登录
- 刷新 token
- 登出
- 修改密码
- 忘记密码
- 用户资料
- 设备会话

后端模块：

```text
domains/auth/
├─ router.py
├─ service.py
├─ repository.py
├─ models.py
├─ schemas.py
└─ dependencies.py
```

前端模块：

```text
features/auth/
├─ api.ts
├─ store.ts
├─ types.ts
├─ views/AuthView.vue
└─ views/ForgotPasswordView.vue
```

### 6.2 Couple 情侣空间模块

职责：

- 创建情侣空间
- 邀请码
- 加入空间
- 配对状态
- 解绑流程
- 成员昵称/角色

关键规则：

- 一个用户同一时间只能属于一个情侣空间。
- 一个情侣空间最多两个成员。
- 邀请码有有效期，使用后失效。
- 解绑是敏感操作，需要二次验证和操作日志。

### 6.3 Memories 回忆模块

对应当前 `moments`。

职责：

- 创建回忆
- 编辑回忆
- 删除/恢复回忆
- 图片/视频关联
- 时间线筛选
- 地图足迹

建议接口：

```text
GET    /api/v1/memories
POST   /api/v1/memories
GET    /api/v1/memories/{id}
PATCH  /api/v1/memories/{id}
DELETE /api/v1/memories/{id}
POST   /api/v1/memories/{id}/assets
DELETE /api/v1/memories/{id}/assets/{assetId}
GET    /api/v1/memories/map-points
```

### 6.4 Bucket 愿望模块

职责：

- 愿望 CRUD
- 状态流转：pending -> planned -> completed
- 完成图片
- 完成时间
- 统计完成率

建议状态流转放在 service：

```text
pending
planned
completed
archived
```

### 6.5 Time Capsules 时光胶囊模块

职责：

- 创建胶囊
- 到期解锁
- 未解锁内容隐藏
- 胶囊状态分组

关键规则：

- 未到 `open_at` 前，接口不返回真实内容。
- 解锁判断必须在后端做，前端只负责展示。

### 6.6 Anniversaries 纪念日模块

职责：

- 新增纪念日
- 删除纪念日
- 周年/一次性事件
- 最近事件计算

关键规则：

- 处理 2 月 29 日等特殊日期。
- `days_left` 由后端计算，不建议存库。

### 6.7 Questions 每日问答模块

职责：

- 每日问题生成
- A/B 回答
- 历史问答
- 题库管理
- 指定日期问题

关键规则：

- 每个情侣空间每天最多一个 DailyQuestion。
- 优先使用指定日期题目。
- 其次随机通用题库。
- 最后兜底内置题库。

### 6.8 Media 媒体模块

职责：

- 上传图片/视频
- 返回可访问 URL
- 文件校验
- 文件元数据
- 未来扩展对象存储

建议接口：

```text
POST /api/v1/media/uploads
GET  /api/v1/media/assets/{id}
DELETE /api/v1/media/assets/{id}
```

### 6.9 Notifications 通知模块

职责：

- 通知列表
- 已读/全部已读
- 删除已读
- 系统通知
- 提醒通知

建议通知只由后端创建，前端不要直接创建业务通知。

### 6.10 Backup 备份导出模块

职责：

- 手动备份
- 自动备份
- 恢复前快照
- 导出 ZIP
- 下载过期

当前实现是模拟型，后续应拆成：

```text
backup service
export service
snapshot repository
archive builder
```

导出内容建议：

```text
manifest.json
memories.json
bucket-items.json
time-capsules.json
anniversaries.json
questions.json
media/
```

---

## 7. 数据迁移方案

### 7.1 引入 Alembic

新增：

```text
alembic.ini
migrations/
  env.py
  versions/
```

命令：

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### 7.2 迁移顺序

第一步：只引入迁移工具，不改业务。

第二步：把当前表结构记录为 baseline。

第三步：新增标准字段：

```text
space_id
created_by
created_at
updated_at
deleted_at
occurred_at
```

第四步：写数据回填脚本：

- 给旧数据创建默认用户。
- 给旧数据创建默认情侣空间。
- 所有旧业务数据绑定到默认 `space_id`。

第五步：前端切换新接口。

第六步：删除旧字段和旧接口。

### 7.3 默认数据处理

因为旧数据没有用户归属，建议创建：

```text
default_user_a
default_user_b
default_couple_space
```

迁移脚本将：

- `moments` -> `memories`
- `bucket_list` -> `bucket_items`
- `time_capsules` -> `time_capsules`
- `anniversaries` -> `anniversaries`
- `daily_questions` -> `daily_questions`
- `question_bank` -> `question_bank`

全部绑定到默认情侣空间。

---

## 8. 测试方案

### 8.1 后端测试

推荐引入：

```text
pytest
httpx
pytest-asyncio
```

测试分层：

- repository 测试：数据库查询是否正确。
- service 测试：业务规则是否正确。
- API 测试：状态码、鉴权、响应结构。

优先测试模块：

1. auth 登录/刷新/过期
2. couple 创建/邀请/加入
3. memories CRUD 和空间隔离
4. capsules 未到期内容隐藏
5. anniversaries 剩余天数计算
6. backup/export 权限和过期

### 8.2 前端测试

推荐引入：

```text
vitest
@vue/test-utils
playwright
```

优先测试：

- API client token refresh
- router guard
- auth store
- couple store
- 核心页面加载状态
- 移动端布局不横向溢出

### 8.3 验收标准

- 登录后刷新页面仍保持会话。
- 未登录访问业务页跳转登录。
- 未配对访问业务页跳转配对流程。
- A 用户不能访问其他情侣空间的数据。
- 上传文件后刷新仍可访问。
- 备份导出生成文件且过期后不可用。
- 375px、768px、1024px、1440px 下主页面无布局破裂。

---

## 9. 部署与环境方案

### 9.1 开发环境

```text
backend:  http://localhost:8000
frontend: http://localhost:5174
mysql:    127.0.0.1:3306
```

### 9.2 生产环境建议

简单部署即可：

```text
Nginx
  ├─ /              -> frontend dist
  ├─ /api/v1        -> uvicorn/gunicorn
  └─ /uploads       -> static files

MySQL
Local disk or OSS for uploads
```

### 9.3 Docker 化

后续可以增加：

```text
docker-compose.yml
backend/Dockerfile
frontend/Dockerfile
```

服务：

```text
mysql
api
web
```

但 Docker 化不是当前第一优先级。先把应用边界整理清楚更重要。

---

## 10. 分阶段实施路线

### 阶段 1：止血与统一入口

目标：不大改业务，只统一调用方式和配置。

任务：

- 新增 `.env.example`。
- 后端抽出 `config.py`。
- 前端旧业务改用统一 `apiClient`。
- 去掉前端硬编码 `http://localhost:8000`。
- CORS 改为环境变量。
- 上传 URL 改为基于配置生成。
- 修复明显乱码文案入口。

收益：

- 本地、部署环境不再改代码。
- 新旧 API 的错误处理和 token 逻辑可以统一。

### 阶段 2：后端从 main.py 拆模块

目标：把旧业务从 `main.py` 迁出。

建议顺序：

1. `media`：上传逻辑最独立。
2. `memories`：核心业务，但边界清晰。
3. `bucket`
4. `capsules`
5. `anniversaries`
6. `questions`
7. `reports`
8. `dashboard`

每迁一个模块：

- 新建 router/service/repository/schemas。
- 保留旧 endpoint 或做兼容 redirect。
- 前端对应 API 改到 feature api。
- 补最小 API 测试。

### 阶段 3：数据归属和 `/api/v1`

目标：所有业务数据绑定情侣空间。

任务：

- 引入 Alembic。
- 新增 `space_id`。
- 回填历史数据。
- 新接口统一校验当前用户的情侣空间。
- 前端切换到 `/api/v1`。

收益：

- 真正支持多用户/多情侣空间。
- 后续权限和备份有稳定基础。

### 阶段 4：前端 feature 化

目标：拆掉超大 `useLoveStore`。

建议顺序：

1. `features/memories`
2. `features/bucket`
3. `features/capsules`
4. `features/anniversaries`
5. `features/questions`
6. `features/home`
7. `features/reports`
8. `features/media`

同步建立：

- `layouts/AppShell.vue`
- `layouts/AuthLayout.vue`
- `shared/components/layout/*`
- `shared/components/state/*`

### 阶段 5：质量、安全和部署

目标：从演示项目提升到可长期使用。

任务：

- 密码哈希升级 bcrypt。
- token hash 存储。
- 上传文件校验。
- 操作日志增强。
- 备份导出真实数据。
- 增加自动备份调度。
- 增加 pytest / vitest / playwright。
- Docker Compose 可选。

---

## 11. 优先级清单

### P0 必做

- 统一前端 API Client。
- 后端配置环境化。
- 从 `main.py` 拆出旧业务路由。
- 引入 `/api/v1`。
- 所有业务数据增加 `space_id`。
- 引入 Alembic。
- 修复历史乱码。

### P1 强烈建议

- 拆分 `useLoveStore`。
- 抽出 Layout 和共享页面组件。
- 上传文件安全校验。
- 日期字段标准化。
- API 错误格式统一。
- 增加后端 API 测试。

### P2 后续增强

- OpenAPI 生成前端类型。
- 备份导出真实完整数据。
- 回收站。
- 自动提醒调度器。
- Docker Compose。
- E2E 测试。

---

## 12. 推荐最终开发规范

### 12.1 后端新增功能流程

```text
1. 定义 schema
2. 定义 model 或复用现有 model
3. 写 repository
4. 写 service
5. 写 router
6. 注册到 api/v1/router.py
7. 写 API 测试
8. 前端 feature/api.ts 对接
```

### 12.2 前端新增功能流程

```text
1. features/{domain}/types.ts
2. features/{domain}/api.ts
3. features/{domain}/store.ts
4. features/{domain}/components
5. features/{domain}/views
6. router 注册
7. 页面接入 Layout 和 shared components
```

### 12.3 命名规范

后端：

- Python 内部：`snake_case`
- 数据库字段：`snake_case`
- API 路径：`kebab-case`

前端：

- TypeScript 变量：`camelCase`
- Vue 组件：`PascalCase`
- 文件夹：`kebab-case` 或领域名小写

API：

- 建议响应字段最终统一 `camelCase`
- 兼容期可以同时返回 `snake_case` 和 `camelCase`

---

## 13. 参考目标结构细化

### 后端目标结构

```text
backend/app/
├─ main.py
├─ api/
│  └─ v1/
│     ├─ router.py
│     └─ endpoints/
├─ core/
│  ├─ config.py
│  ├─ security.py
│  ├─ time.py
│  ├─ errors.py
│  └─ logging.py
├─ db/
│  ├─ base.py
│  ├─ session.py
│  └─ init_db.py
├─ domains/
│  ├─ auth/
│  ├─ couple/
│  ├─ memories/
│  ├─ bucket/
│  ├─ capsules/
│  ├─ anniversaries/
│  ├─ questions/
│  ├─ media/
│  ├─ reports/
│  ├─ reminders/
│  ├─ notifications/
│  ├─ security/
│  └─ backup/
├─ storage/
│  ├─ base.py
│  └─ local.py
├─ scripts/
│  ├─ seed.py
│  └─ migrate_legacy_data.py
└─ tests/
```

### 前端目标结构

```text
frontend/src/
├─ app/
│  ├─ App.vue
│  └─ bootstrap.ts
├─ shared/
│  ├─ api/
│  ├─ components/
│  ├─ composables/
│  ├─ constants/
│  ├─ types/
│  └─ utils/
├─ layouts/
├─ features/
│  ├─ auth/
│  ├─ couple/
│  ├─ home/
│  ├─ memories/
│  ├─ bucket/
│  ├─ capsules/
│  ├─ anniversaries/
│  ├─ questions/
│  ├─ reports/
│  ├─ media/
│  ├─ notifications/
│  ├─ reminders/
│  ├─ security/
│  └─ backup/
├─ router/
├─ styles/
└─ main.ts
```

---

## 14. 第一轮落地建议

如果现在开始动手，建议第一轮只做 5 件事：

1. 新建后端 `app/core/config.py`，把数据库、CORS、上传路径、前端地址全部环境化。
2. 前端 `useLoveStore.ts` 改为统一使用 `apiClient`，去掉硬编码 API 地址。
3. 把 `main.py` 里的上传逻辑迁到 `media` router。
4. 把 `main.py` 里的 moments 迁到 `memories` router/service/repository。
5. 建立 `docs/api-contract.md`，记录旧接口和目标 `/api/v1` 的映射。

第一轮完成后，项目的“骨架感”就会明显变强，后续再拆其他模块会顺很多。

---

## 15. 最终验收标准

架构层：

- `main.py` 不再包含业务路由。
- 每个业务模块有独立 router/service/repository/schema/model。
- 前端每个业务模块有独立 api/store/types/views。
- 所有 HTTP 请求走统一 `apiClient`。
- 所有核心业务数据有 `space_id`。
- 数据库结构通过 Alembic 管理。

体验层：

- 登录、配对、首页、时间线、愿望、地图、胶囊、纪念日、每日问答都能正常使用。
- 旧数据迁移后不丢失。
- 移动端和桌面端布局保持当前设计方向。
- 备份、导出、通知、提醒不被重构破坏。

质量层：

- 后端核心 API 有测试。
- 前端构建通过。
- 无硬编码 API 地址。
- 无新增乱码。
- 无明显权限越权。

---

## 16. 总结

LOVE 当前已经不是一个纯 demo，它已经长出了账号、配对、安全、提醒、备份这些“长期产品”能力。下一步最重要的是把这些能力放进稳定的结构里。

推荐路线是：

```text
配置统一 -> API Client 统一 -> main.py 拆模块 -> 数据归属 space_id -> 前端 feature 化 -> 测试和安全增强
```

这样做的好处是每一步都能独立交付，不需要停下来大重写，也不会破坏当前已经完成的视觉和业务成果。
