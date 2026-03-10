# LOVE Frontend

`LOVE Frontend` 是一个基于 `Vue 3 + Vite + TypeScript + Element Plus` 的情侣纪念站前端项目，包含回忆时间线、地图足迹、愿望清单、时光胶囊、纪念日、恋爱报告、每日问答、背景音乐等模块。

## 项目状态

- 前端开发端口：`http://localhost:5174`（见 `vite.config.ts`）
- 后端 API 端口：`http://localhost:8000`（见项目根目录 `main.py`）
- 登录口令（当前写死在前端）：`5201314`（见 `src/views/LoginView.vue`）
- 已验证 `npm run build` 可正常打包

## 技术栈

- Vue 3（Composition API + `<script setup>`）
- Vite 4
- TypeScript
- Pinia（全局状态）
- Vue Router
- Element Plus
- Axios
- Leaflet / Vue-Leaflet（地图）

## 功能模块

- 登录页：口令登录与路由守卫
- 首页：情侣信息、统计卡片、最近回忆、封面管理、信息编辑
- 时间线：回忆列表、关键词筛选、心情筛选、视频筛选
- 地图：展示含经纬度的回忆点位
- 愿望清单：新增愿望、状态流转（未开始/计划中/已完成）
- 时光胶囊：创建未来信件，按解锁时间查看内容
- 纪念日：新增/删除纪念日，展示剩余天数
- 恋爱报告：多页滑动统计展示
- 恋爱转盘：自定义选项并抽取结果
- 每日问答：今日问题答题、历史问答查看
- 全局组件：顶部导航、飘落爱心、BGM 播放器、回忆新增弹窗

## 目录结构

```text
frontend/
├─ src/
│  ├─ components/        # 通用组件
│  ├─ views/             # 各页面视图
│  ├─ stores/            # Pinia 状态管理（核心 API 调用集中在 useLoveStore）
│  ├─ router/            # 路由与登录守卫
│  ├─ styles/            # 主题与全局样式
│  └─ main.ts            # 应用入口
├─ index.html
├─ vite.config.ts
└─ package.json
```

## 本地开发（推荐联调方式）

### 1) 启动后端（FastAPI）

后端在项目根目录，前端所有请求默认指向 `http://localhost:8000`。

```bash
cd ..
pip install -r requirements.txt
python .\main.py
```

默认会启动在：

- API：`http://localhost:8000`
- Swagger：`http://localhost:8000/docs`
- 上传文件静态目录：`/uploads`

注意：后端当前使用 MySQL（连接字符串在项目根目录 `database.py`），请先确保数据库可连接。

### 2) 启动前端

```bash
cd ../frontend
npm install
npm run dev
```

访问：

- 前端：`http://localhost:5174`

## 打包与预览

```bash
npm run build
npm run preview
```

## 前端与后端接口约定（摘要）

主要接口在 `src/stores/useLoveStore.ts` 中统一调用，包括：

- `GET/POST /api/info`
- `GET/POST /api/moments`
- `POST /api/upload`
- `GET/POST/PUT /api/bucket`
- `GET/POST /api/capsules`
- `GET/POST/DELETE /api/music`
- `GET/POST/DELETE /api/anniversaries`
- `GET/POST/DELETE /api/covers`
- `GET /api/questions/today`
- `POST /api/questions/{id}/answer`
- `GET /api/questions/history`
- `GET /api/report`

## 当前实现注意点

- API 基础地址在前端代码中硬编码为 `http://localhost:8000`，如需部署到其他环境，建议改为 `.env` 配置。
- 登录口令目前为前端硬编码，仅适合演示环境。
- 文案中存在部分历史乱码（字符编码遗留问题），建议统一按 UTF-8 修复。
- 构建时会提示主包体积偏大（`> 500KB`），后续可做按路由或模块拆包优化。

## 常见问题排查

- 前端能打开但无数据  
  检查后端是否运行在 `8000` 端口；浏览器 Network 是否出现 `ERR_CONNECTION_REFUSED`。

- 图片上传失败  
  检查后端 `uploads` 目录写权限与 `/api/upload` 是否可访问。

- 地图不显示底图  
  地图瓦片依赖 `https://{s}.tile.openstreetmap.org`，请确认网络可访问该域名。

- 登录后仍跳回登录页  
  检查浏览器是否禁用了 `localStorage`，或手动清理 `localStorage` 后重试。

## 后续优化建议

- 将 API 地址、上传地址、登录机制改为环境配置 + 后端鉴权
- 补充单元测试和 E2E 测试
- 增加 i18n 和编码统一检查，避免乱码回归
