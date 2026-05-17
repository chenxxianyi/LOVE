# Glassmorphism Component Specs

毛玻璃组件规格参考。

## 卡片 (Card)

核心组件，承载内容的主要容器。

```
Height: auto (content-driven)
Radius: 20px (--card-radius)
Background: var(--glass-bg)
Border: 1px solid var(--glass-border)
Backdrop-filter: blur(var(--glass-blur))  [16px/20px]
Box-shadow: var(--glass-shadow)
Padding: 20-24px
Transition: transform 0.35s, box-shadow 0.35s
```

Hover 状态：
```
transform: translateY(-4px)
box-shadow: 0 12px 40px rgba(0,0,0,0.10)   // shadow increases
background: var(--glass-bg-hover)            // opacity increases
border-color: var(--glass-border-hover)      // border brightens
```

CSS 示例：
```css
.glass-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--card-radius, 20px);
  backdrop-filter: blur(var(--glass-blur, 16px));
  -webkit-backdrop-filter: blur(var(--glass-blur, 16px));
  box-shadow: var(--glass-shadow, 0 4px 20px rgba(0,0,0,0.06));
  transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1.0),
              box-shadow 0.35s ease,
              background 0.35s ease,
              border-color 0.35s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  box-shadow: var(--glass-shadow-hover, 0 12px 40px rgba(0,0,0,0.10));
}
```

## 导航栏 (Nav Bar)

固定在顶部的毛玻璃导航。

```
Height: 56px
Background: var(--glass-bg-strong)
Border-bottom: 1px solid var(--glass-border)
Blur: 20px (light) / 24px (dark)
Position: sticky, top: 0
Z-index: 100
```

特性：
- 滚动时背景模糊增强，内容在下方透过
- 链接 hover 使用 accent-light 背景
- active 链接使用 accent-glow 背景 + accent 文字色

## 按钮 (Button)

```
Primary (玻璃):
  Height: 40px
  Padding: 0 24px
  Radius: 14px
  Background: var(--accent)
  Color: #fff
  Backdrop-filter: blur(8px)
  Box-shadow: 0 2px 12px rgba(255,140,160,0.30)
  Hover: translateY(-2px), shadow increase

Secondary (玻璃勾勒):
  Background: transparent
  Border: 1px solid var(--glass-border-strong)
  Color: var(--text-main)
  Hover: background var(--glass-bg-subtle)

Ghost:
  Background: transparent
  Border: none
  Color: var(--text-sub)
  Hover: color var(--text-main), background var(--glass-bg-subtle)
```

## 输入框 (Input)

```
Height: 44px
Radius: 12px
Padding: 0 16px
Background: var(--glass-bg-subtle)
Border: 1px solid var(--glass-border)
Blur: 4px
Focus: border-color accent, shadow accent-glow
```

## 对话框/模态框 (Modal/Dialog)

```
Radius: 24px
Background: var(--glass-bg-strong)
Border: 1px solid var(--glass-border-strong)
Blur: 24px
Box-shadow: shadow-xl
Backdrop: rgba(0,0,0,0.15) overlay
Animation: scale(0.95→1) + opacity(0→1), 0.3s ease-out
```

## 标签/芯片 (Chip/Badge)

```
Height: 28px
Padding: 0 14px
Radius: 9999px (pill)
Background: rgba(255,255,255,0.35) light / rgba(255,255,255,0.10) dark
Border: 1px solid var(--glass-border)
Blur: 4px
Font-size: 12px
Color: var(--text-sub)
```

## 头像 (Avatar)

```
Size: 32-48px
Radius: 50%
Border: 2px solid var(--glass-border-strong)
Box-shadow: 0 2px 8px rgba(0,0,0,0.06)
```
