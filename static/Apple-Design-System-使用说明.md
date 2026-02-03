# 🍎 Apple Design System - 使用说明

## 📦 文件信息
- **文件名**: `apple-design-system.css`
- **路径**: `wecom-crm/backend/static/`
- **大小**: 17.2 KB
- **版本**: 1.0
- **创建日期**: 2026-01-27

---

## ✨ 功能概览

这是一个完整的 Apple 设计系统基础库，包含：

### 🎨 设计令牌 (Design Tokens)
- ✅ **颜色系统** - 10级灰度 + Apple 标准色
- ✅ **字体系统** - SF Pro 字体栈 + 9级字号
- ✅ **圆角系统** - 7级圆角 (4px ~ 28px)
- ✅ **阴影系统** - 6级阴影 + 焦点阴影
- ✅ **间距系统** - 基于4px网格
- ✅ **动画系统** - Apple 标准缓动函数

### 🌓 暗黑模式
- ✅ 自动跟随系统设置
- ✅ 所有颜色变量自动切换
- ✅ 阴影和边框自适应

### 🎬 动画关键帧
- ✅ 10种预定义动画
- ✅ 淡入/淡出/缩放/旋转等

### 🛠️ 工具类
- ✅ Flexbox 和 Grid 布局
- ✅ 间距 (margin/padding)
- ✅ 文字样式
- ✅ 颜色和背景
- ✅ 60+ 实用类

---

## 📖 使用方法

### 1. 引入样式文件

在 HTML `<head>` 中引入（放在所有其他CSS之前）：

```html
<link rel="stylesheet" href="/static/apple-design-system.css">
```

### 2. 在其他CSS中使用变量

```css
/* 使用颜色变量 */
.my-button {
    background-color: var(--color-primary);
    color: var(--text-inverse);
    border-radius: var(--radius-md);
    padding: var(--space-2) var(--space-4);
    box-shadow: var(--shadow-md);
    transition: all var(--duration-fast) var(--ease-out);
}

.my-button:hover {
    background-color: var(--color-primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}

/* 使用字体变量 */
.heading {
    font-family: var(--font-family-base);
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    line-height: var(--line-height-tight);
    color: var(--text-primary);
}
```

### 3. 直接使用工具类

```html
<!-- Flexbox 布局 -->
<div class="flex items-center justify-between gap-4">
    <span class="text-lg font-semibold">标题</span>
    <button class="rounded-lg shadow-md transition-fast">按钮</button>
</div>

<!-- 间距和圆角 -->
<div class="p-6 m-4 rounded-xl bg-primary shadow-lg">
    <p class="text-base text-secondary">内容</p>
</div>

<!-- Grid 布局 -->
<div class="grid grid-cols-3 gap-6">
    <div class="bg-secondary rounded-lg p-4">卡片1</div>
    <div class="bg-secondary rounded-lg p-4">卡片2</div>
    <div class="bg-secondary rounded-lg p-4">卡片3</div>
</div>
```

---

## 🎨 颜色系统

### 主题颜色
```css
--color-primary: #007AFF    /* iOS 蓝 */
--color-secondary: #5856D6  /* 紫色 */
--color-success: #34C759    /* 绿色 */
--color-warning: #FF9500    /* 橙色 */
--color-danger: #FF3B30     /* 红色 */
--color-info: #5AC8FA       /* 青色 */
```

### 灰度系统 (10级)
```css
--gray-50   #FAFAFA  /* 最亮 */
--gray-100  #F5F5F7
--gray-200  #E8E8ED
--gray-300  #D1D1D6
--gray-400  #C7C7CC
--gray-500  #AEAEB2
--gray-600  #8E8E93
--gray-700  #636366
--gray-800  #48484A
--gray-900  #1C1C1E  /* 最暗 */
```

### 文字颜色
```css
--text-primary    #000000 (浅色) / #FFFFFF (暗黑)
--text-secondary  #6E6E73
--text-tertiary   #8E8E93
```

### 背景颜色
```css
--bg-primary     #FFFFFF (浅色) / #000000 (暗黑)
--bg-secondary   #F5F5F7 (浅色) / #1C1C1E (暗黑)
--bg-tertiary    #E8E8ED (浅色) / #2C2C2E (暗黑)
```

---

## 📏 间距系统

基于 **4px 网格**：

| 变量 | 值 | 使用场景 |
|------|-----|---------|
| `--space-1` | 4px | 最小间距 |
| `--space-2` | 8px | 小间距 |
| `--space-3` | 12px | 中小间距 |
| `--space-4` | 16px | 标准间距 |
| `--space-6` | 24px | 大间距 |
| `--space-8` | 32px | 超大间距 |
| `--space-12` | 48px | 区块间距 |

---

## ⭕ 圆角系统

| 变量 | 值 | 使用场景 |
|------|-----|---------|
| `--radius-xs` | 4px | 小标签 |
| `--radius-sm` | 6px | 小按钮 |
| `--radius-md` | 10px | 标准按钮、卡片 |
| `--radius-lg` | 14px | 大卡片、弹窗 |
| `--radius-xl` | 20px | 欢迎卡片 |
| `--radius-2xl` | 28px | 大型容器 |
| `--radius-full` | 9999px | 圆形元素 |

---

## 🌫️ 阴影系统

| 变量 | 值 | 使用场景 |
|------|-----|---------|
| `--shadow-xs` | 0 1px 2px | 微阴影 |
| `--shadow-sm` | 0 1px 3px | 小阴影 |
| `--shadow-md` | 0 4px 12px | 中阴影 (按钮、卡片) |
| `--shadow-lg` | 0 8px 24px | 大阴影 (悬停效果) |
| `--shadow-xl` | 0 16px 48px | 超大阴影 (弹窗) |
| `--shadow-2xl` | 0 24px 64px | 巨大阴影 (模态框) |

### 焦点阴影
```css
--shadow-focus-primary  /* 蓝色光晕 */
--shadow-focus-danger   /* 红色光晕 */
--shadow-focus-success  /* 绿色光晕 */
```

---

## 🔤 字体系统

### 字体族
```css
--font-family-base  /* SF Pro Display / PingFang SC */
--font-family-mono  /* SF Mono / Consolas */
```

### 字号 (9级)
```css
--font-size-xs    11px  /* 小标签 */
--font-size-sm    13px  /* 辅助文字 */
--font-size-base  15px  /* 正文 */
--font-size-lg    17px  /* 小标题 */
--font-size-xl    20px  /* 标题 */
--font-size-2xl   24px  /* 大标题 */
--font-size-3xl   28px  /* 页面标题 */
--font-size-4xl   34px  /* 欢迎标题 */
--font-size-5xl   40px  /* 超大标题 */
```

### 字重
```css
--font-weight-light     300
--font-weight-normal    400
--font-weight-medium    500
--font-weight-semibold  600  /* 推荐按钮使用 */
--font-weight-bold      700
--font-weight-heavy     800
```

---

## ⚡ 动画系统

### 缓动函数
```css
--ease-in       cubic-bezier(0.4, 0, 1, 1)
--ease-out      cubic-bezier(0, 0, 0.2, 1)        /* 推荐 */
--ease-in-out   cubic-bezier(0.4, 0, 0.2, 1)      /* Apple 标准 */
--ease-spring   cubic-bezier(0.175, 0.885, 0.32, 1.275)
```

### 动画时长
```css
--duration-instant  100ms  /* 瞬间 */
--duration-fast     200ms  /* 快速 */
--duration-normal   300ms  /* 标准 */
--duration-slow     500ms  /* 缓慢 */
```

### 预定义动画
```css
@keyframes fadeIn           /* 淡入 */
@keyframes fadeInUp         /* 淡入上升 */
@keyframes fadeInDown       /* 淡入下降 */
@keyframes fadeInLeft       /* 淡入左移 */
@keyframes fadeInRight      /* 淡入右移 */
@keyframes fadeInScale      /* 缩放淡入 */
@keyframes spin             /* 旋转 */
@keyframes pulse            /* 脉冲 */
@keyframes bounce           /* 弹跳 */
@keyframes shake            /* 抖动 */
```

使用示例：
```css
.fade-in {
    animation: fadeInUp 0.6s var(--ease-out);
}

.loading-spinner {
    animation: spin 1s linear infinite;
}

.error-shake {
    animation: shake 0.5s var(--ease-in-out);
}
```

---

## 🛠️ 工具类速查

### Flexbox 布局
```html
<div class="flex items-center justify-between gap-4">
    <!-- 水平居中，两端对齐，间距 16px -->
</div>
```

| 类名 | 效果 |
|------|------|
| `.flex` | display: flex |
| `.flex-column` | flex-direction: column |
| `.items-center` | align-items: center |
| `.items-start` | align-items: flex-start |
| `.items-end` | align-items: flex-end |
| `.justify-center` | justify-content: center |
| `.justify-between` | justify-content: space-between |
| `.justify-around` | justify-content: space-around |
| `.gap-2` / `.gap-4` / `.gap-6` | 间距 |
| `.flex-1` | flex: 1 |

### Grid 布局
```html
<div class="grid grid-cols-4 gap-6">
    <!-- 4列网格，间距 24px -->
</div>
```

| 类名 | 效果 |
|------|------|
| `.grid` | display: grid |
| `.grid-cols-1` ~ `.grid-cols-4` | 列数 |

### 文字样式
```html
<h1 class="text-3xl font-bold text-primary">标题</h1>
<p class="text-base text-secondary">正文</p>
```

| 类名 | 效果 |
|------|------|
| `.text-xs` ~ `.text-3xl` | 字号 |
| `.font-light` ~ `.font-bold` | 字重 |
| `.text-primary` | 主文字色 |
| `.text-secondary` | 次要文字色 |
| `.text-center` | 居中对齐 |

### 间距
```html
<div class="p-6 m-4">
    <!-- padding: 24px, margin: 16px -->
</div>
```

| 类名 | 效果 |
|------|------|
| `.m-0` ~ `.m-8` | margin |
| `.mt-4` | margin-top |
| `.mb-4` | margin-bottom |
| `.p-0` ~ `.p-8` | padding |

### 圆角和阴影
```html
<div class="rounded-lg shadow-md">
    <!-- 圆角 14px，中阴影 -->
</div>
```

| 类名 | 效果 |
|------|------|
| `.rounded-sm` ~ `.rounded-xl` | 圆角 |
| `.rounded-full` | 圆形 |
| `.shadow-sm` ~ `.shadow-xl` | 阴影 |

### 其他
```html
<div class="cursor-pointer transition-fast">
    <!-- 手型光标，快速过渡 -->
</div>
```

| 类名 | 效果 |
|------|------|
| `.hidden` | 隐藏 |
| `.block` | 块级元素 |
| `.relative` / `.absolute` | 定位 |
| `.w-full` / `.h-full` | 100% 宽高 |
| `.cursor-pointer` | 手型光标 |
| `.transition-fast` | 快速过渡 |

---

## 📱 响应式断点

虽然设计系统本身不包含断点，但推荐使用：

```css
/* 移动端 */
@media (max-width: 768px) {
    /* 手机样式 */
}

/* 平板端 */
@media (min-width: 769px) and (max-width: 1024px) {
    /* 平板样式 */
}

/* 桌面端 */
@media (min-width: 1025px) {
    /* 桌面样式 */
}
```

---

## 🌙 暗黑模式

### 自动切换
设计系统会自动跟随系统设置切换暗黑模式，无需任何配置。

### 手动测试
在浏览器开发工具中：
1. 按 `F12` 打开开发者工具
2. `Cmd/Ctrl + Shift + P` 打开命令面板
3. 输入 "Rendering"
4. 选择 "Emulate CSS prefers-color-scheme: dark"

### 自定义暗黑模式样式
```css
/* 浅色模式 */
.my-component {
    background: var(--bg-primary);
    color: var(--text-primary);
}

/* 暗黑模式会自动使用变量的暗黑值 */
@media (prefers-color-scheme: dark) {
    /* 如需特殊处理，可在这里添加 */
    .my-component {
        /* 特殊样式 */
    }
}
```

---

## 📋 最佳实践

### ✅ 推荐做法

1. **优先使用变量**
   ```css
   /* 好 ✅ */
   color: var(--text-primary);
   padding: var(--space-4);
   
   /* 不好 ❌ */
   color: #000000;
   padding: 16px;
   ```

2. **使用语义化的变量名**
   ```css
   /* 好 ✅ */
   background: var(--color-primary);
   
   /* 不好 ❌ */
   background: var(--apple-blue);
   ```

3. **使用工具类快速开发**
   ```html
   <!-- 好 ✅ -->
   <div class="flex items-center gap-4 p-6 rounded-lg shadow-md">
   
   <!-- 不好 ❌ -->
   <div style="display: flex; align-items: center; gap: 16px; padding: 24px;">
   ```

4. **使用预定义动画**
   ```css
   /* 好 ✅ */
   animation: fadeInUp var(--duration-normal) var(--ease-out);
   
   /* 不好 ❌ */
   animation: fadeInUp 300ms cubic-bezier(0, 0, 0.2, 1);
   ```

### ❌ 避免的做法

1. 不要覆盖 CSS 变量的值（除非有特殊需求）
2. 不要使用硬编码的颜色值
3. 不要使用不符合 4px 网格的间距
4. 不要使用非标准的圆角值

---

## 🔄 版本更新

### v1.0 (2026-01-27)
- ✅ 初始版本
- ✅ 完整的 Apple 设计系统
- ✅ 暗黑模式支持
- ✅ 60+ 工具类
- ✅ 10种预定义动画

---

## 📚 参考资源

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SF Symbols](https://developer.apple.com/sf-symbols/)
- [Apple Design Resources](https://developer.apple.com/design/resources/)

---

## 💡 示例代码

### 按钮组件
```html
<button class="btn-primary">
    主按钮
</button>

<style>
.btn-primary {
    background: var(--color-primary);
    color: white;
    padding: var(--space-2) var(--space-6);
    border-radius: var(--radius-md);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    border: none;
    cursor: pointer;
    box-shadow: var(--shadow-sm);
    transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary:hover {
    background: var(--color-primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.btn-primary:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
}
</style>
```

### 卡片组件
```html
<div class="card">
    <h3 class="card-title">标题</h3>
    <p class="card-content">内容</p>
</div>

<style>
.card {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-color);
    transition: all var(--duration-normal) var(--ease-in-out);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.card-title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    margin-bottom: var(--space-2);
}

.card-content {
    font-size: var(--font-size-base);
    color: var(--text-secondary);
    line-height: var(--line-height-relaxed);
}
</style>
```

---

**创建时间**: 2026-01-27  
**版本**: 1.0  
**作者**: AI Assistant  
**项目**: 天号城企微CRM系统
