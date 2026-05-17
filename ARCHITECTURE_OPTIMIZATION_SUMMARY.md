# LOVE 项目架构优化总结

**日期**: 2026/05/17
**优化版本**: v1.0

---

## 1. 优化概述

本次架构优化基于 `ARCHITECTURE_OPTIMIZATION_PLAN.md` 文档，将 LOVE 项目从"单文件脚本式应用"演进为"模块化单体应用"。核心原则是保留现有产品功能和体验，先把模块边界立起来，再逐步迁移。

### 主要优化方向
- 后端按领域拆分为清晰的模块结构
- 前端按业务模块组织 features
- 统一 API Client，移除硬编码地址
- 引入标准化的配置层和安全工具

---

## 2. 后端架构优化

### 2.1 新增目录结构

```
backend/app/
├── __init__.py
├── core/                          # 核心工具层
│   ├── __init__.py
│   ├── config.py                  # 环境配置管理
│   ├── security.py                # 密码哈希、Token 生成工具
│   ├── errors.py                  # 自定义异常类
│   └── time.py                    # 时间工具函数
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py              # API v1 路由聚合
│       └── endpoints/            # 各业务领域端点
│           ├── auth.py            # 认证相关
│           ├── couple.py          # 情侣空间
│           ├── memories.py        # 回忆/时刻
│           ├── bucket.py          # 愿望清单
│           ├── capsules.py        # 时光胶囊
│           ├── anniversaries.py   # 纪念日
│           ├── questions.py       # 每日问答
│           ├── media.py          # 文件上传
│           └── reports.py         # 报告统计
├── db/
│   ├── __init__.py
│   └── session.py                 # 数据库连接管理
├── domains/                       # 业务领域模块
│   ├── auth/
│   ├── couple/
│   ├── memories/
│   ├── bucket/
│   ├── capsules/
│   ├── anniversaries/
│   ├── questions/
│   ├── media/
│   └── reports/
├── storage/
│   ├── __init__.py
│   └── service.py                 # 文件存储服务
└── scripts/                       # 脚本工具
```

### 2.2 核心模块说明

#### 2.2.1 app/core/config.py
基于 Pydantic Settings 的配置管理，支持：
- 环境变量加载
- 数据库连接配置
- CORS 白名单配置
- 文件上传配置
- JWT Token 有效期配置

#### 2.2.2 app/core/security.py
安全工具函数：
- `hash_password()` / `verify_password()`: 密码哈希
- `generate_access_token()` / `generate_refresh_token()`: Token 生成
- `hash_token()`: Token 哈希存储
- `generate_invite_code()`: 邀请码生成
- `generate_verify_code()`: 验证码生成

#### 2.2.3 app/core/errors.py
统一的异常体系：
- `AppException`: 基础异常
- `NotFoundException`: 404
- `UnauthorizedException`: 401
- `ForbiddenException`: 403
- `BadRequestException`: 400
- `ConflictException`: 409

#### 2.2.4 app/api/v1/endpoints/*
各业务领域的 REST API 端点，采用统一结构：
- 请求/响应 Schema 定义
- CRUD 操作
- 业务规则处理

### 2.3 API v1 端点概览

| 端点 | 说明 |
|------|------|
| `/api/v1/auth/*` | 注册、登录、Token 刷新、登出 |
| `/api/v1/couple-space/*` | 创建、邀请、加入情侣空间 |
| `/api/v1/memories/*` | 回忆 CRUD、时间线、地图点 |
| `/api/v1/bucket-items/*` | 愿望清单 CRUD、统计 |
| `/api/v1/time-capsules/*` | 时光胶囊 CRUD、解锁状态 |
| `/api/v1/anniversaries/*` | 纪念日 CRUD、倒计时 |
| `/api/v1/questions/*` | 每日问答、题库管理 |
| `/api/v1/media/*` | 文件上传 |
| `/api/v1/reports/*` | 数据报告、仪表盘统计 |

---

## 3. 前端架构优化

### 3.1 新增目录结构

```
frontend/src/
├── features/                      # 功能模块
│   ├── auth/
│   │   ├── api.ts               # 认证 API
│   │   └── types.ts             # 类型定义
│   ├── couple/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── memories/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── bucket/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── capsules/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── anniversaries/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── questions/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── reports/
│   │   ├── api.ts
│   │   └── types.ts
│   └── media/
│       ├── api.ts
│       └── types.ts
├── layouts/                       # 布局组件
│   ├── AppShell.vue             # 主应用 Shell
│   ├── AuthLayout.vue           # 认证页布局
│   └── SettingsLayout.vue       # 设置页布局
└── shared/
    ├── components/
    │   ├── layout/              # 布局组件
    │   │   ├── PageFrame.vue
    │   │   ├── PageHeader.vue
    │   │   └── MetricStrip.vue
    │   ├── card/               # 卡片组件
    │   │   ├── ContentCard.vue
    │   │   └── CompactItemCard.vue
    │   └── state/              # 状态组件
    │       ├── EmptyState.vue
    │       └── RequestStatePanel.vue
    └── composables/             # 组合式函数
        ├── index.ts
        ├── useLoading.ts
        └── useAsync.ts
```

### 3.2 API Client 统一

**修改前**:
```typescript
axios.get("http://localhost:8000/api/moments")
```

**修改后**:
```typescript
import { apiClient } from "@/api/client";
apiClient.get("/memories")  // 自动带 /api/v1 前缀
```

**apiClient 特性**:
- 自动携带 Authorization Token
- 自动刷新过期 Token
- 统一错误处理
- 统一 baseURL（可通过环境变量配置）

### 3.3 Feature 模块结构

每个 Feature 模块包含：
- `api.ts`: 对应后端 API 的调用封装
- `types.ts`: TypeScript 类型定义和常量

**好处**:
- 类型安全，接口契约清晰
- 便于代码分割（code splitting）
- 便于后续单元测试
- 减少大型 Store 的复杂度

### 3.4 共享组件

| 组件 | 说明 |
|------|------|
| `PageHeader.vue` | 统一页面标题栏 |
| `MetricStrip.vue` | 指标数据展示行 |
| `ContentCard.vue` | 通用内容卡片容器 |
| `CompactItemCard.vue` | 列表项紧凑卡片 |
| `EmptyState.vue` | 空状态提示 |
| `RequestStatePanel.vue` | 加载/错误/空状态切换 |

### 3.5 组合式函数

| 函数 | 说明 |
|------|------|
| `useLoading()` | 管理加载状态 |
| `useAsync()` | 处理异步操作，含加载/错误状态 |

---

## 4. 配置文件

### 4.1 新增 .env.example

```bash
# 应用环境
APP_ENV=development
APP_DEBUG=true

# API 配置
API_PREFIX=/api/v1
APP_PORT=8000

# 数据库配置
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/love_memory

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# 文件上传配置
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=10

# 安全配置
PASSWORD_SALT=your_secure_salt_here
ACCESS_TOKEN_TTL_MINUTES=120
REFRESH_TOKEN_TTL_DAYS=30
```

---

## 5. 迁移进度

### ✅ 已完成

| 任务 | 状态 |
|------|------|
| 创建 app/core 配置层 | ✅ 完成 |
| 创建 app/api/v1 路由结构 | ✅ 完成 |
| 创建后端 domains 模块 | ✅ 完成 |
| 统一前端 API Client | ✅ 完成 |
| 创建前端 features 目录结构 | ✅ 完成 |
| 创建前端 layouts 和 shared components | ✅ 完成 |

### ⏳ 下一阶段待做

| 任务 | 优先级 |
|------|--------|
| 从 main.py 拆出旧业务路由到 domains | P0 |
| 引入 Alembic 数据库迁移 | P0 |
| 所有业务数据增加 space_id | P1 |
| 拆分 useLoveStore 为独立 feature stores | P1 |
| 抽出一致的 Layout 和共享页面组件 | P1 |
| 上传文件安全校验 | P1 |
| 密码哈希升级 bcrypt | P2 |
| 增加后端 API 测试 | P2 |
| Docker Compose 支持 | P2 |

---

## 6. 命名规范

### 后端
- Python 内部: `snake_case`
- 数据库字段: `snake_case`
- API 路径: `kebab-case`
- Pydantic Schema: `PascalCase`

### 前端
- TypeScript 变量: `camelCase`
- Vue 组件: `PascalCase`
- 文件夹: `kebab-case` 或领域名小写

### API 响应
- 最终统一 `camelCase`
- 兼容期可同时返回 `snake_case` 和 `camelCase`

---

## 7. 架构验收标准

### 架构层
- [ ] `main.py` 不再包含业务路由
- [ ] 每个业务模块有独立 router/service/repository/schema/model
- [ ] 前端每个业务模块有独立 api/store/types/views
- [ ] 所有 HTTP 请求走统一 `apiClient`
- [ ] 所有核心业务数据有 `space_id`
- [ ] 数据库结构通过 Alembic 管理

### 体验层
- [ ] 登录、配对、首页、时间线、愿望、地图、胶囊、纪念日、每日问答都能正常使用
- [ ] 旧数据迁移后不丢失
- [ ] 移动端和桌面端布局保持当前设计方向
- [ ] 备份、导出、通知、提醒不被重构破坏

### 质量层
- [ ] 后端核心 API 有测试
- [ ] 前端构建通过
- [ ] 无硬编码 API 地址
- [ ] 无新增乱码
- [ ] 无明显权限越权

---

## 8. 参考

- 原始架构优化方案: [ARCHITECTURE_OPTIMIZATION_PLAN.md](./ARCHITECTURE_OPTIMIZATION_PLAN.md)
- 前端布局优化方案: [FRONTEND_LAYOUT_CARD_OPTIMIZATION_PLAN.md](./FRONTEND_LAYOUT_CARD_OPTIMIZATION_PLAN.md)

---

**文档版本**: 1.0
**更新时间**: 2026/05/17