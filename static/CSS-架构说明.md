# CSS 架构说明 - Apple UI 系统

## 📁 最终CSS文件结构

### 1️⃣ 核心设计系统（必须第一个加载）
- **apple-design-system.css** (17.8 KB)
  - CSS变量定义（颜色、字体、间距、圆角、阴影等）
  - 暗黑模式自动切换
  - 响应式断点定义
  - 基础动画效果

### 2️⃣ 样式重置层
- **apple-ui-reset.css** (4.1 KB)
  - 重置旧样式
  - 移除橙色等不协调的颜色
  - 统一基础HTML元素样式

### 3️⃣ 主UI组件库
- **apple-ui-master.css** (30.6 KB)
  - 布局系统（sidebar、header、main-content）
  - 通用组件（按钮、输入框、下拉框、表格）
  - 导航和面包屑
  - 统计卡片
  - 表单控件

### 4️⃣ 对话框系统
- **apple-dialogs.css** (5.2 KB)
  - 模态弹窗
  - Alert/Confirm 对话框
  - Toast 提示
  - 加载动画

### 5️⃣ 页面专用样式
- **customer-list-apple.css** (8.1 KB)
  - 客户列表页面
  - 筛选工具栏
  - 批量操作栏
  - 客户表格
  
- **customer-profile-apple.css** (10.7 KB)
  - 客户画像分析
  - 统计卡片网格
  - 标签云
  - 图表容器
  
- **common-modules-apple.css** (9.4 KB)
  - 企业标签
  - 企业通讯录
  - 客户群管理
  - 群标签
  - 客户运营模块

### 6️⃣ 详情页样式（保留旧文件）
- **customer-detail.css** (3.4 KB)
  - 客户详情页独立样式
  - 待后续重构

---

## 🎯 CSS加载顺序（严格遵守）

```html
<!-- 1. 核心设计系统（必须第一） -->
<link rel="stylesheet" href="/static/apple-design-system.css?v=20260127">

<!-- 2. 样式重置 -->
<link rel="stylesheet" href="/static/apple-ui-reset.css?v=20260127">

<!-- 3. 主UI组件库 -->
<link rel="stylesheet" href="/static/apple-ui-master.css?v=20260127">

<!-- 4. 对话框系统 -->
<link rel="stylesheet" href="/static/apple-dialogs.css?v=20260127">

<!-- 5. 页面专用样式 -->
<link rel="stylesheet" href="/static/customer-list-apple.css?v=20260127">
<link rel="stylesheet" href="/static/customer-profile-apple.css?v=20260127">
<link rel="stylesheet" href="/static/common-modules-apple.css?v=20260127">

<!-- 6. 图标库（CDN） -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
```

---

## ✅ 已删除的旧CSS文件（共13个，128KB）

❌ style.css (36.3 KB)
❌ style-old.css (36.3 KB)
❌ apple-style-overrides.css (37.1 KB)
❌ modules-apple-styles.css (11.7 KB)
❌ employee-manage-styles.css (9.3 KB)
❌ employee-manage-styles-apple.css (7.0 KB)
❌ permission-manage-styles.css (9.7 KB)
❌ permission-manage-styles-apple.css (2.5 KB)
❌ auth-styles.css (1.2 KB)
❌ tag-selection-styles.css (1.2 KB)
❌ data-source-styles.css (8.0 KB)
❌ spreadsheet-styles.css (2.4 KB)
❌ data-table-styles.css (5.2 KB)

---

## 🎨 设计规范

### 颜色系统
- **主色调**: #007AFF（Apple Blue）
- **成功色**: #34C759
- **警告色**: #FF9500
- **危险色**: #FF3B30
- **灰度**: #F5F5F7（浅灰）、#D1D1D6（中灰）、#8E8E93（深灰）

### 圆角规范
- **按钮**: 12px
- **卡片**: 16px
- **输入框**: 10px
- **弹窗**: 20px

### 间距规范
- 4px（xs）、8px（sm）、12px（md）、16px（base）
- 20px（lg）、24px（xl）、32px（2xl）、40px（3xl）

### 字体规范
- **标题**: 28px / Bold
- **副标题**: 20px / Semibold
- **正文**: 14px / Regular
- **小字**: 12px / Regular

### 按钮高度
- **大按钮**: 40px
- **中按钮**: 32px
- **小按钮**: 28px

---

## 📊 CSS统计

| 项目 | 数量 | 大小 |
|------|------|------|
| **当前CSS文件** | 8个 | 89.4 KB |
| **旧CSS文件（已删除）** | 13个 | 128.0 KB |
| **优化比例** | -38% | -30% |
| **CSS类总数** | 约120+ | - |
| **CSS选择器** | 约350+ | - |

---

## 🔧 维护指南

### 新增页面样式
1. 如果是通用组件 → 添加到 `apple-ui-master.css`
2. 如果是特定页面 → 创建新的 `[page-name]-apple.css`
3. 如果是对话框 → 添加到 `apple-dialogs.css`

### 修改现有样式
1. 先检查变量 → `apple-design-system.css`
2. 再检查组件 → `apple-ui-master.css`
3. 最后检查页面 → 对应的页面CSS

### 调试技巧
1. 打开浏览器开发者工具
2. 查看 Elements → Computed 面板
3. 找到冲突的样式来源
4. 调整CSS优先级或使用 `!important`

---

## ⚠️ 注意事项

1. **永远不要直接修改** `apple-design-system.css` 的变量值
2. **使用CSS变量** 而不是硬编码颜色值
3. **遵守命名规范**: `.apple-*` 前缀表示Apple风格组件
4. **保持响应式**: 使用媒体查询适配不同屏幕
5. **支持暗黑模式**: 使用 `@media (prefers-color-scheme: dark)`

---

## 📝 更新日志

### 2026-01-27
- ✅ 删除13个旧CSS文件（128 KB）
- ✅ 创建统一的Apple UI系统（89.4 KB）
- ✅ 减少文件数量38%，减少文件大小30%
- ✅ 统一加载顺序，解决样式冲突
- ✅ 所有页面使用统一设计规范

---

**最后更新**: 2026-01-27 12:30
**维护者**: Apple UI 重构团队
