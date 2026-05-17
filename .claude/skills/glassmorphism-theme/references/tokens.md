# Glassmorphism Design Tokens

完整的设计 token 定义，覆盖 Glass Light 和 Glass Dark 两种模式。

## 背景色 (Backgrounds)

| Token | Glass Light | Glass Dark |
|-------|-------------|------------|
| bg-base | #f0f0f5 | #1a1a2e |
| bg-warm | #faeef2 | #1e1e32 |
| bg-spot-1 | #ffe0e8 (pink glow) | #2a1a3e (purple glow) |
| bg-spot-2 | #e0e8ff (blue glow) | #1a2a3e (blue glow) |
| bg-spot-3 | #f0e8ff (purple glow) | #1e2a2e (teal glow) |

## 玻璃材质 (Glass Materials)

| Token | Glass Light | Glass Dark |
|-------|-------------|------------|
| glass-bg | rgba(255,255,255,0.25) | rgba(30,30,45,0.45) |
| glass-bg-hover | rgba(255,255,255,0.38) | rgba(40,40,55,0.55) |
| glass-bg-strong | rgba(255,255,255,0.50) | rgba(50,50,65,0.60) |
| glass-bg-subtle | rgba(255,255,255,0.12) | rgba(30,30,45,0.25) |
| glass-border | rgba(255,255,255,0.30) | rgba(255,255,255,0.08) |
| glass-border-hover | rgba(255,255,255,0.50) | rgba(255,255,255,0.15) |
| glass-border-strong | rgba(255,255,255,0.60) | rgba(255,255,255,0.20) |

## 模糊值 (Blur Radius)

| Token | Value | Usage |
|-------|-------|-------|
| blur-xs | 4px | inline chips, small badges |
| blur-sm | 8px | buttons, inputs |
| blur-md | 16px | cards, panels |
| blur-lg | 20px | nav bar, toolbar |
| blur-xl | 24px | modals, dialogs, sheets |

## 阴影 (Shadows) — 漂浮感核心

| Token | Value |
|-------|-------|
| shadow-sm | 0 2px 8px rgba(0,0,0,0.04) |
| shadow-md | 0 4px 20px rgba(0,0,0,0.06) |
| shadow-lg | 0 8px 32px rgba(0,0,0,0.07) |
| shadow-xl | 0 12px 48px rgba(0,0,0,0.09) |
| shadow-dark-sm | 0 2px 8px rgba(0,0,0,0.15) |
| shadow-dark-md | 0 4px 20px rgba(0,0,0,0.20) |
| shadow-dark-lg | 0 8px 32px rgba(0,0,0,0.25) |
| shadow-dark-xl | 0 12px 48px rgba(0,0,0,0.30) |

## 文字色 (Text)

| Token | Glass Light | Glass Dark |
|-------|-------------|------------|
| text-main | #2c2c2c | #f0f0f0 |
| text-sub | #6e6e6e | #a0a0a0 |
| text-muted | #9e9e9e | #707070 |
| text-inverse | #ffffff | #1a1a1a |

## 强调色 (Accent)

| Token | Value |
|-------|-------|
| accent | #ff8ca0 |
| accent-light | rgba(255,140,160,0.25) |
| accent-glow | rgba(255,140,160,0.15) |
| accent-hover | #ff7090 |
| accent-text | #d46070 |

## 圆角 (Border Radius)

| Token | Value | Usage |
|-------|-------|-------|
| radius-sm | 10px | buttons, inputs, chips |
| radius-md | 16px | cards |
| radius-lg | 20px | large cards, panels |
| radius-xl | 24px | modals, dialogs |
| radius-full | 9999px | pills, avatars |

## 行高/间距 (Line & Spacing)

| Token | Value |
|-------|-------|
| line-soft-glass | rgba(255,255,255,0.20) (light) / rgba(255,255,255,0.06) (dark) |

## CSS 用法

```css
/* Glass Light */
[data-theme="glass"] {
  --glass-bg: rgba(255,255,255,0.25);
  --glass-border: rgba(255,255,255,0.30);
  --glass-blur: 16px;
  --glass-shadow: 0 4px 20px rgba(0,0,0,0.06);
  --text-main: #2c2c2c;
  --text-sub: #6e6e6e;
  --accent: #ff8ca0;
  --card-radius: 20px;
}

/* Glass Dark */
[data-theme="glass-dark"] {
  --glass-bg: rgba(30,30,45,0.45);
  --glass-border: rgba(255,255,255,0.08);
  --glass-blur: 20px;
  --glass-shadow: 0 4px 20px rgba(0,0,0,0.20);
  --text-main: #f0f0f0;
  --text-sub: #a0a0a0;
  --accent: #ff8ca0;
  --card-radius: 20px;
}
```
