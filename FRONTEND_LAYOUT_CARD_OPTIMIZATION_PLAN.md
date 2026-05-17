# LOVE 前端布局与卡片优化方案

## 1. 方案边界

本方案只优化前端布局、卡片层级、卡片位置与页面信息组织。

明确保留：

- 保留现有液态玻璃主题，不修改 `theme-glass.css` 的玻璃材质、背景光斑、透明度和模糊逻辑。
- 保留现有漂浮感，不取消 `soft-card`、`fade-up`、卡片 hover、轻微上浮、阴影等视觉语言。
- 保留当前温柔、私密、恋爱纪念馆的产品气质。
- 保留桌面端左侧导航和移动端底部 Tab 的基本方向。

需要优化：

- 减少同一页面里卡片视觉权重过于平均的问题。
- 减少页面头部、统计、筛选、内容列表都被强卡片包裹导致的拥挤感。
- 统一页面宽度、卡片间距、双栏比例和移动端堆叠规则。
- 让每张卡片承担清晰的信息职责，而不是只作为装饰容器。

## 2. 当前布局判断

当前前端主壳在 `frontend/src/App.vue`，结构是：

```text
SideNav
FallingHearts
app-main / RouterView
BGMPlayer
AddMomentForm
```

当前页面的主要问题不是视觉风格，而是布局层级：

- 首页、时间线、愿望、地图、纪念日、胶囊等页面大量使用 `soft-card`。
- 页面头部卡片、统计卡片、筛选卡片、内容卡片的视觉重量接近。
- 多个页面使用不同的最大宽度、间距和卡片内部布局。
- 部分页面存在卡片套卡片或容器卡过多的问题。
- 移动端容易出现首屏被头部、筛选区、底部 Tab、悬浮播放器共同挤压。

## 3. 总体设计目标

目标风格：玻璃质感不变，信息层级减法。

核心原则：

1. 每个页面只允许一个主要视觉中心。
2. 卡片只承载信息单元，不作为默认页面分隔线。
3. 首屏优先展示可操作内容，而不是过多介绍性区块。
4. 统计信息合并为轻量条，不拆成多个同权重大卡片。
5. 页面头部、筛选栏、内容区、辅助区在所有页面中保持一致位置。
6. 移动端所有主要卡片单列排列，避免左右双栏。

## 4. 全局布局规范

### 4.1 页面容器

建议新增或统一以下布局类：

```text
.page-frame
  用于大多数业务页面，控制最大宽度和水平居中。

.page-frame-narrow
  用于每日一问、纪念日、安全设置等偏阅读或表单页面。

.page-frame-wide
  用于地图、时间线、报告等需要更大展示面积的页面。
```

建议尺寸：

```text
page-frame:        max-width 1120px
page-frame-narrow: max-width 820px
page-frame-wide:   max-width 1280px
```

桌面端：

```text
app-main padding: 40px 48px 48px
page gap: 18px-24px
card gap: 14px-18px
```

移动端：

```text
app-main padding: 16px 16px 100px
page gap: 14px-18px
card gap: 12px-16px
```

### 4.2 页面基础结构

大多数页面统一为：

```text
PageHeader
PrimaryArea
SecondaryArea
```

说明：

- `PageHeader` 放标题、说明、主操作按钮。
- `PrimaryArea` 放该页面最重要的卡片或列表。
- `SecondaryArea` 放统计、补充列表、历史记录、快捷入口等。

### 4.3 页面头部规则

页面头部不再承担过重装饰任务，而是承担导航和操作任务。

推荐结构：

```text
[ 标题 + 说明 ]                         [ 主按钮 ]
```

规则：

- 桌面端标题左对齐，主按钮右对齐。
- 移动端标题在上，主按钮在下或右侧收为小按钮。
- 页面头部可继续使用 `soft-card`，但一个页面只保留一个头部卡片。
- 如果页面首屏已有强主卡片，头部应做轻量处理，避免两个主视觉抢焦点。

## 5. 卡片体系

建议将现有卡片统一为 4 类。

### 5.1 HeroCard

用途：

- 首页首屏。
- 配对成功页。
- 需要强情绪表达的单页入口。

布局：

```text
[ 文案区 + 主操作 ]    [ 封面图 / 关键视觉 ]
```

规则：

- 每个页面最多一个 `HeroCard`。
- 只出现在页面顶部。
- 可以使用最大尺寸、最强玻璃效果和更明显漂浮感。
- 内部不要再嵌套其他 `soft-card`。

### 5.2 MetricStrip

用途：

- 首页统计。
- 愿望清单状态统计。
- 地图足迹统计。
- 报告概览。

布局：

```text
[ 指标 ][ 指标 ][ 指标 ][ 指标 ]
```

规则：

- 用一张横向卡片承载多个数字。
- 不建议拆成多张同等重量卡片。
- 指标数量控制在 3-5 个。
- 移动端改成 2 列或横向滑动。

### 5.3 ContentCard

用途：

- 回忆卡片。
- 地图主卡片。
- 每日一问主卡片。
- 胶囊卡片。
- 报告卡片。

规则：

- 承载页面的主要内容。
- 可以保留现有玻璃、阴影、hover 漂浮。
- 卡片内部信息顺序应稳定：媒体或核心内容在上，文本与操作在下。

### 5.4 CompactItemCard

用途：

- 愿望清单。
- 纪念日列表。
- 提醒列表。
- 消息列表。
- 安全设置入口。

布局：

```text
[ 图标/状态 ] [ 标题 + 描述 + 标签 ] [ 操作 ]
```

规则：

- 高度更紧凑，便于扫视。
- 适合列表或网格。
- 卡片 hover 保留，但不应大幅移动。
- 操作按钮固定在右侧或右上角。

## 6. 关键页面布局方案

### 6.1 首页 HomeView

当前问题：

- `hero`、`stats`、`featured` 都有较强视觉权重。
- 统计卡片分散，首页首屏略显堆叠。

建议结构：

```text
[ HeroCard: 情侣名 + 在一起天数 + 写回忆按钮 + 封面图 ]

[ MetricStrip: 回忆数 / 足迹数 / 愿望完成 / 下个纪念日 ]

[ 最近回忆 ContentArea ]       [ 今日问题 / 下个纪念日 / 快捷入口 ]
```

位置规则：

- `HeroCard` 位于最上方，占满页面宽度。
- `MetricStrip` 紧跟 HeroCard，作为轻量数据概览。
- 下方采用 7:5 或 2:1 双栏。
- 左侧放最近回忆，右侧放短信息卡。
- 移动端顺序为：HeroCard、MetricStrip、最近回忆、今日问题、纪念日。

### 6.2 时间线 TimelineView

当前问题：

- 页面头部和筛选区都是独立强卡片，内容卡片需要更突出。

建议结构：

```text
PageHeader: 时光时间线 + 描述

[ FilterBar: 搜索 / 心情 / 仅视频 ]

[ TimelineList ]
  日期轴
  [ MomentCard ]
  [ MomentCard ]
```

位置规则：

- 筛选卡片保持轻量，放在标题下方。
- 时间线轴固定靠左，卡片统一在右侧。
- MomentCard 保持图片上、文字下。
- 移动端筛选区吸顶可以保留，但高度要控制。

### 6.3 愿望清单 BucketListView

当前问题：

- 头部、统计、愿望卡片都较重。
- 愿望卡片可扫视性需要提升。

建议结构：

```text
PageHeader: 愿望清单 + 许个愿望

[ MetricStrip: 未完成 / 计划中 / 已实现 ]

[ CompactItemCard Grid ]
```

卡片内部：

```text
左侧: 图标或状态点
中间: 愿望标题 + 描述 + 状态标签
右侧: 更多操作
```

位置规则：

- 桌面端 3 列网格，最小列宽 280px。
- 中屏 2 列。
- 移动端 1 列。
- 已完成状态用边框、标签或轻背景区分，不额外放大卡片。

### 6.4 地图 MapView

当前问题：

- 地图页顶部统计和足迹列表有较多装饰元素，地图主体应该更明确。

建议结构：

```text
PageHeader: 恋爱足迹地图 + 描述 + 统计摘要

[ MapCard: 地图主卡片 ]

[ FootprintListCard: 足迹列表 ]
```

位置规则：

- 地图卡片是页面唯一主卡片。
- 桌面端地图高度建议 560px-640px。
- 足迹列表放地图下方，不与地图并列抢空间。
- 统计信息放 PageHeader 右侧或地图卡片左上角。

### 6.5 纪念日 AnniversaryView

当前问题：

- 所有纪念日卡片权重接近，但纪念日天然有时间优先级。

建议结构：

```text
PageHeader: 纪念日 + 添加纪念日

[ FeaturedEventCard: 最近的重要纪念日 ]

[ CompactItemCard List: 其他纪念日 ]
```

位置规则：

- 距离最近或今天的纪念日放大为主卡片。
- 其他纪念日列表化，按时间排序。
- 最近 7 天用左侧强调线或标签，不额外改变布局尺寸。

### 6.6 时光胶囊 TimeCapsuleView

当前问题：

- 胶囊混排时，用户需要先判断能否打开。

建议结构：

```text
PageHeader: 时光胶囊 + 埋下胶囊

[ 待开启胶囊区 ]
  [ CapsuleCard ][ CapsuleCard ]

[ 已开启胶囊区 ]
  [ CapsuleCard ][ CapsuleCard ]
```

位置规则：

- 先展示待开启，再展示已开启。
- 卡片视觉效果保留。
- 状态徽标继续保留，但位置统一在右上角。
- 移动端两个分区纵向排列。

### 6.7 每日一问 DailyQuestionView

当前问题：

- 当前主卡片很强，适合保留，但页面内的小视觉效果偏多。

建议结构：

```text
PageHeader: 每日一问 + 问答档案馆 + 题库管理

[ DailyQuestionCard ]
  日期
  问题
  [ A 回答区 ] [ B 回答区 ]
  锁定提示
```

位置规则：

- 页面只保留一张核心主卡片。
- A/B 回答区桌面端双栏，移动端上下排列。
- 锁定提示放在主卡片底部，避免漂浮在内容中间。

### 6.8 报告 ReportView

当前问题：

- 报告页本身是沉浸式卡片，方向合理。

建议结构：

```text
[ ReportCard 居中 ]
  Slides
  Dots
  Arrows
```

位置规则：

- 不额外增加页面头部。
- 报告卡片保持居中。
- 左右切换按钮贴近卡片边缘。
- 移动端高度控制在视口内，底部进度点不要被 Tab 遮挡。

### 6.9 P0 设置类页面

适用页面：

- 安全设置。
- 设备管理。
- 操作日志。
- 备份中心。
- 提醒中心。
- 消息中心。

建议结构：

```text
PageHeader

[ Toolbar / FilterBar ]

[ Panel / Table / List ]
```

位置规则：

- 设置类页面偏工具型，应更紧凑。
- 表单页使用 `page-frame-narrow`。
- 表格页使用 `page-frame-wide`。
- 操作按钮统一右对齐。

## 7. 导航布局建议

当前 `SideNav` 导航项较多，建议进行分组。

主入口：

```text
首页
时间线
地图
愿望
```

更多入口：

```text
胶囊
纪念日
报告
转盘
每日一问
```

账户与系统：

```text
提醒
消息
安全
```

桌面端：

- 侧边栏保留玻璃效果。
- 一级入口固定展示。
- 次级入口可以放在分组下方或折叠菜单中。

移动端：

- 底部 Tab 保留 4-5 个入口。
- 推荐：首页、时间线、愿望、地图、我的。
- 新增回忆按钮保留为中间主操作。

## 8. 移动端卡片规则

移动端布局顺序：

```text
PageHeader
PrimaryAction
PrimaryCard
MetricStrip
ContentList
SecondaryCards
```

移动端规则：

- 所有主内容单列。
- 不使用左右双栏。
- `MetricStrip` 可以 2 列排列。
- 筛选栏高度要小于一屏高度的 20%。
- 底部 Tab 上方至少预留 80px。
- BGM 悬浮播放器不要遮挡底部 Tab 和主要按钮。

## 9. 实施优先级

第一阶段：全局规范

1. 统一 `global.css` 中页面容器、间距、宽度。
2. 统一 `PageHeader`、`MetricStrip`、`ContentCard`、`CompactItemCard` 的布局类。
3. 不修改 `theme-glass.css` 的视觉效果。

第二阶段：首页和核心内容页

1. 优化 `HomeView.vue` 的首屏结构。
2. 优化 `TimelineView.vue` 的筛选区和时间线位置。
3. 优化 `BucketListView.vue` 的统计条和愿望卡片网格。
4. 优化 `MapView.vue` 的地图主卡片和足迹列表位置。

第三阶段：辅助功能页

1. 优化 `AnniversaryView.vue` 的最近纪念日主卡片。
2. 优化 `TimeCapsuleView.vue` 的待开启和已开启分区。
3. 优化 `DailyQuestionView.vue` 的主卡片内部布局。
4. 统一 P0 设置类页面结构。

## 10. 验收标准

布局验收：

- 每个页面首屏只有一个明确视觉中心。
- 页面卡片间距统一，无明显拥挤或空洞。
- 不出现无意义的卡片套卡片。
- 统计信息优先使用横向指标条。
- 列表类内容优先使用紧凑卡片。

视觉保留验收：

- 液态玻璃效果仍然存在。
- 卡片 hover 漂浮感仍然存在。
- 背景光斑和主题切换不受影响。
- `soft-card`、`fade-up`、`glow-chip` 仍可继续使用。

响应式验收：

- 375px 移动端无横向滚动。
- 底部 Tab 不遮挡主要操作。
- 768px 下双栏自动变单列。
- 1024px 和 1440px 下页面宽度稳定。

## 11. 推荐最终页面骨架

通用页面：

```text
<main class="page-frame">
  <header class="page-header">
    <div>
      <h1>页面标题</h1>
      <p>页面说明</p>
    </div>
    <div class="page-actions">
      主按钮
    </div>
  </header>

  <section class="metric-strip soft-card fade-up">
    指标内容
  </section>

  <section class="content-grid">
    内容卡片
  </section>
</main>
```

首页：

```text
<main class="page-frame-wide">
  <section class="hero-card soft-card fade-up">
    情侣概览 + 封面图
  </section>

  <section class="metric-strip soft-card fade-up">
    关键指标
  </section>

  <section class="home-grid">
    <div class="home-main">
      最近回忆
    </div>
    <aside class="home-aside">
      今日问题 / 纪念日 / 快捷入口
    </aside>
  </section>
</main>
```

列表页：

```text
<main class="page-frame">
  <PageHeader />
  <FilterBar class="soft-card fade-up" />
  <section class="item-grid">
    <CompactItemCard />
  </section>
</main>
```

本方案的关键不是改变 LOVE 的视觉个性，而是让玻璃卡片更有秩序：少一点同权重堆叠，多一点主次关系。
