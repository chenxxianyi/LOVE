---
name: glassmorphism-theme
description: |
  Glassmorphism frosted-glass design system for web applications.
  Semi-transparent, blurred, floating aesthetic with light/dark variants.

  Use when:
  - Building UI with frosted glass, semi-transparent aesthetic
  - User mentions "毛玻璃", "glassmorphism", "frosted glass", "漂浮感", "半透明"
  - Creating cards, navbars, modals with backdrop blur effects
  - Implementing light + dark glass themes
  - Needing floating, elevated UI components with soft shadows
  - Questions about backdrop-filter, blur radius, glass opacity

  Do NOT use for: flat design, material design, neumorphism, general CSS unrelated to glass effects.
---

# Glassmorphism Design System

毛玻璃漂浮风格设计系统。核心美学：半透明材质 + 背景模糊 + 柔和阴影 = 漂浮感。

## 设计理念

- **毛玻璃 (Frosted Glass)**：`backdrop-filter: blur()` 实现透过卡片看到背景的磨砂效果
- **半透明 (Semi-transparent)**：`rgba()` 低不透明度背景，保留色彩倾向
- **漂浮感 (Floating)**：大范围柔和阴影 + 轻微 Y 轴偏移，营造卡片悬浮于背景之上的错觉
- **光感 (Light Play)**：背景点缀柔和渐变光斑，透过毛玻璃产生折射感

## Typography

字体沿用项目现有体系：标题 `Cormorant Garamond`，正文 `Noto Sans SC`。

玻璃主题下文字增强对比度以确保在半透明背景上的可读性。

## Spacing & Radius

```
Glass 专用圆角:
  card: 20px
  button: 14px
  modal: 24px
  chip: 9999px (pill)

阴影偏移 (漂浮感):
  elevation-1: Y=2px  blur=16px
  elevation-2: Y=4px  blur=24px
  elevation-3: Y=8px  blur=32px
  elevation-4: Y=12px blur=48px
```

## Glass Materials

```
Light Glass:
  card-bg: rgba(255,255,255,0.25)
  card-bg-hover: rgba(255,255,255,0.38)
  card-border: rgba(255,255,255,0.30)
  card-border-hover: rgba(255,255,255,0.45)
  blur: 16px (card), 20px (nav), 12px (button)
  shadow-color: rgba(0,0,0,0.06)

Dark Glass:
  card-bg: rgba(30,30,45,0.45)
  card-bg-hover: rgba(40,40,55,0.55)
  card-border: rgba(255,255,255,0.08)
  card-border-hover: rgba(255,255,255,0.14)
  blur: 20px (card), 24px (nav), 16px (button)
  shadow-color: rgba(0,0,0,0.25)

Accent:
  primary: #ff8ca0 (rose pink)
  primary-glass: rgba(255,140,160,0.25)
  primary-glow: rgba(255,140,160,0.15)
```

## Background Effects

Glass Light 背景：
- 柔和渐变基色 `#f0f0f5` → `#faeef2`
- 多个大尺寸径向渐变模拟光斑（粉、蓝、紫）
- 光斑位置固定，透过毛玻璃组件产生折射视觉

Glass Dark 背景：
- 深色基色 `#1a1a2e` → `#16213e`
- 暗色光斑（深蓝、暗紫），模拟夜晚玻璃反光
- 整体氛围神秘高级

## Animations

```
Hover float:
  card hover → translateY(-4px) + shadow increase
  duration: 0.35s, easing: cubic-bezier(0.34, 1.56, 0.64, 1.0)

Theme switch:
  background + card colors crossfade
  duration: 0.5s, easing: ease-in-out

Card enter (staggered):
  fade-up with translateY(20px→0) + opacity(0→1)
  interval: 60ms per card
  duration: 0.5s, easing: cubic-bezier(0.25, 0.46, 0.45, 0.94)
```

## Component Dimensions

| Component | Glass Specs |
|-----------|-------------|
| Nav Bar | height 56px, blur 20px, border-bottom 1px glass |
| Card | radius 20px, blur 16px, shadow elevation-2 |
| Button | height 40px, radius 14px, blur 8px |
| Modal | radius 24px, blur 24px, shadow elevation-4 |
| Chip | pill 9999px, blur 6px, bg rgba(255,255,255,0.35) |
| Input | height 44px, radius 12px, blur 4px |

## Rules

**DO**: Use `backdrop-filter: blur()` on cards/nav, keep opacity 0.15-0.45 for glass, add soft large-blur shadows, preserve border for glass edge definition, use smooth transitions for hover.

**DON'T**: Use opacity > 0.6 (loses glass feel), omit borders (glass needs edge), use hard shadows, forget -webkit-backdrop-filter for Safari.

## Detailed References

- **Full design tokens** (color, shadow, radius, spacing): [references/tokens.md](references/tokens.md)
- **Component specs**: [references/components.md](references/components.md)
- **Layout patterns & background**: [references/layouts.md](references/layouts.md)
