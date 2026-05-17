# Glassmorphism Layout Patterns

毛玻璃风格的布局模式和背景设计。

## 背景构成

毛玻璃效果的关键在于背景有足够丰富的视觉信息透过组件。Glass Light 主题使用多层径向渐变模拟柔和光斑。

### Glass Light 背景

```css
[data-theme="glass"] body {
  background:
    /* 光斑1：右上粉色 */
    radial-gradient(ellipse 600px 500px at 85% 10%, rgba(255,180,200,0.35) 0%, transparent 70%),
    /* 光斑2：左下蓝色 */
    radial-gradient(ellipse 500px 450px at 10% 90%, rgba(180,200,255,0.25) 0%, transparent 70%),
    /* 光斑3：左上紫色 */
    radial-gradient(ellipse 400px 350px at 15% 15%, rgba(210,190,255,0.20) 0%, transparent 70%),
    /* 光斑4：右下暖色 */
    radial-gradient(ellipse 350px 300px at 80% 80%, rgba(255,200,180,0.20) 0%, transparent 70%),
    /* 基底 */
    linear-gradient(160deg, #f0f0f5 0%, #faeef2 50%, #f5f0fa 100%);
  background-attachment: fixed;
}
```

### Glass Dark 背景

```css
[data-theme="glass-dark"] body {
  background:
    /* 光斑1：右上暗紫 */
    radial-gradient(ellipse 600px 500px at 85% 10%, rgba(100,60,140,0.20) 0%, transparent 70%),
    /* 光斑2：左下暗蓝 */
    radial-gradient(ellipse 500px 450px at 10% 90%, rgba(40,60,120,0.18) 0%, transparent 70%),
    /* 光斑3：左上暗青 */
    radial-gradient(ellipse 400px 350px at 15% 15%, rgba(30,80,100,0.15) 0%, transparent 70%),
    /* 基底 */
    linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #1a1e2e 100%);
  background-attachment: fixed;
}
```

## 页面布局模式

### 标准页面

```
┌──────────────────────────────────┐
│       Glass Nav (sticky 56px)    │  ← blur 20px, 漂浮于内容之上
├──────────────────────────────────┤
│                                  │
│    ┌────────────────────────┐    │
│    │   Glass Card            │    │  ← blur 16px, 透出背景光斑
│    │   ↑ hover 时上浮 4px    │    │
│    └────────────────────────┘    │
│                                  │
│    ┌──────┐ ┌──────┐ ┌──────┐   │
│    │ Card │ │ Card │ │ Card │   │  ← 并排玻璃卡片
│    └──────┘ └──────┘ └──────┘   │
│                                  │
├──────────────────────────────────┤
│         底部间距 36px             │
└──────────────────────────────────┘
```

### 卡片网格 (Card Grid)

```
  Grid: CSS Grid, 2-3 columns
  Gap: 16px
  Each card: glass-card, staggered fade-up animation
  Animation delay: index * 60ms
```

### 模态覆盖层 (Modal Overlay)

```
┌──────────────────────────────────┐
│   Dimmed Background (rgba 0.15)  │
│          ┌──────────┐            │
│          │  Modal   │            │  ← blur 24px, radius 24px
│          │  Card    │            │     scale(0.95→1) animate in
│          └──────────┘            │
└──────────────────────────────────┘
```

## 主题切换过渡

背景色和所有 glass 变量使用 CSS transition 平滑切换：

```css
body {
  transition: background 0.6s ease;
}

.glass-card, .soft-card {
  transition: background 0.5s ease,
              border-color 0.5s ease,
              box-shadow 0.5s ease,
              backdrop-filter 0.5s ease;
}
```

## 响应式

- 移动端减小 blur 值（性能）：card blur 12px, nav blur 14px
- 移动端减小阴影范围：shadow-lg → 0 4px 16px
- 移动端减小圆角：card 16px, modal 20px
- 光斑背景在移动端保留但减小尺寸
