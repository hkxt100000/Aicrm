# Apple UI 彻底重构计划

## 📅 创建日期
2026-01-27

## 🎯 重构目标

**问题分析**：
1. ❌ CSS 文件过多（15个），加载顺序混乱
2. ❌ 原有 `style.css` 权重过高，覆盖样式无法生效
3. ❌ 各模块样式分散，难以统一管理
4. ❌ Apple 样式覆盖不完整，部分元素仍显示旧样式

**解决方案**：
1. ✅ 创建单一的 `apple-ui-master.css` 作为主样式文件
2. ✅ 禁用或最小化 `style.css` 的影响
3. ✅ 按模块重构每个页面，确保无遗漏
4. ✅ 统一所有弹窗、表单、反馈组件的样式

---

## 📋 重构策略

### 方案A：覆盖式重构（推荐）
**优点**：
- 不破坏原有功能
- 可以逐步迁移
- 出问题可快速回滚

**步骤**：
1. 创建 `apple-ui-master.css`（权重最高）
2. 在 HTML 中最后加载，确保覆盖所有样式
3. 使用 `!important` 确保优先级
4. 逐页面、逐组件重构

### 方案B：替换式重构
**优点**：
- 彻底清除旧样式
- 代码更简洁

**缺点**：
- 风险较高
- 需要完整测试

**步骤**：
1. 备份 `style.css` → `style-old-backup.css`
2. 创建全新的 `style.css`（纯 Apple 风格）
3. 删除或禁用旧的 CSS 文件
4. 全量测试

---

## 🗂️ 当前 CSS 文件分析

### 现有 CSS 文件（15个）：

| 文件名 | 大小 | 用途 | 处理方式 |
|-------|------|------|---------|
| `apple-design-system.css` | 17.8 KB | Apple 设计系统基础 | ✅ 保留 |
| `apple-style-overrides.css` | 35 KB | Apple 样式覆盖 | 🔄 合并到 master |
| `modules-apple-styles.css` | 11.7 KB | 模块样式 | 🔄 合并到 master |
| `employee-manage-styles-apple.css` | 7 KB | 员工管理 | 🔄 合并到 master |
| `permission-manage-styles-apple.css` | 2.5 KB | 权限管理 | 🔄 合并到 master |
| `style.css` | 36.3 KB | **原有主样式** | ⚠️ 禁用或最小化 |
| `style-old.css` | 36.3 KB | 备份 | ⏸️ 保留备份 |
| `auth-styles.css` | 1.2 KB | 登录样式 | 🔄 合并到 master |
| `employee-manage-styles.css` | 9.3 KB | 员工管理（旧） | ❌ 禁用 |
| `permission-manage-styles.css` | 9.7 KB | 权限管理（旧） | ❌ 禁用 |
| `data-source-styles.css` | 8 KB | 数据源样式 | 🔄 重构 |
| `data-table-styles.css` | 5.2 KB | 表格样式 | 🔄 重构 |
| `spreadsheet-styles.css` | 2.4 KB | 表格样式 | 🔄 重构 |
| `tag-selection-styles.css` | 1.2 KB | 标签选择 | 🔄 重构 |
| `customer-detail.css` | 3.4 KB | 客户详情 | 🔄 重构 |

### CSS 加载顺序（当前）：
```html
1. apple-design-system.css         ← 基础系统
2. style.css                        ← ⚠️ 权重过高，干扰 Apple 样式
3. apple-style-overrides.css        ← Apple 覆盖
4. modules-apple-styles.css         ← 模块覆盖
5. auth-styles.css
6. employee-manage-styles.css
7. employee-manage-styles-apple.css
8. permission-manage-styles.css
9. permission-manage-styles-apple.css
10. tag-selection-styles.css
11. data-source-styles.css
12. spreadsheet-styles.css
13. data-table-styles.css
```

**问题**：`style.css` 在第2位加载，其样式权重高，导致后续的 Apple 覆盖样式无法完全生效。

---

## 🛠️ 新的 CSS 架构

### 推荐架构：

```
1. apple-design-system.css          ← 设计系统基础（CSS 变量、主题）
2. apple-ui-reset.css               ← 重置原有样式
3. apple-ui-master.css              ← 主样式文件（包含所有组件）
   ├── 布局系统
   ├── 导航和侧边栏
   ├── 按钮系统
   ├── 表单控件
   ├── 表格组件
   ├── 卡片组件
   ├── 弹窗组件
   ├── 标签和徽章
   ├── 分页组件
   └── 反馈组件
4. apple-ui-modules.css             ← 各页面模块样式
   ├── 工作台
   ├── 客户管理
   ├── 客户群管理
   ├── 客户运营
   ├── 客户群运营
   ├── 系统管理
   └── 数据中心
```

---

## 📅 13 个阶段详细计划

### 【阶段 0】准备工作（当前阶段）
**时间**：2小时

**任务**：
- [x] 分析现有 CSS 文件结构
- [x] 制定重构策略
- [ ] 创建 `apple-ui-reset.css`（重置旧样式）
- [ ] 创建 `apple-ui-master.css`（主样式文件骨架）
- [ ] 更新 `index.html` CSS 加载顺序

**产出文件**：
- `apple-ui-reset.css`（新建）
- `apple-ui-master.css`（新建）
- `index.html`（更新 CSS 引用）

---

### 【阶段 1】工作台页面
**时间**：3小时

**涉及元素**：
1. 页面标题和面包屑
2. 统计卡片（4个）- 客户总数、活跃员工、客户群、本月订单
3. 快捷入口（可选）
4. 数据图表（可选）

**设计规范**：
- 统计卡片：白色背景 + 16px 圆角 + 渐变图标
- 图标尺寸：64×64px
- 数字字体：32px，加粗
- 标签字体：13px，medium
- 趋势指示器：绿色向上箭头

**产出样式**：
```css
/* 工作台 - 统计卡片 */
.dashboard-stats { }
.stat-card { }
.stat-icon { }
.stat-content { }
.stat-value { }
.stat-trend { }
```

---

### 【阶段 2】客户管理 - 客户列表
**时间**：4小时

**涉及元素**：
1. 页面标题和操作按钮（增量同步、全量同步、导出）
2. 搜索框（左侧图标，灰色背景）
3. 筛选器（多个按钮）
4. 数据表格（表头、表格行、悬停效果）
5. 表格内按钮（查看、编辑、删除）
6. 分页组件

**设计规范**：
- 搜索框高度：36px，圆角 12px
- 筛选按钮高度：36px，间距 8px
- 表格表头高度：44px，浅灰背景
- 表格行高度：52px，内边距 16px
- 悬停背景：`rgba(0, 0, 0, 0.02)`
- 分页按钮：32×32px，圆角 8px

**产出样式**：
```css
/* 客户列表 */
.customer-list-header { }
.search-toolbar { }
.search-box { }
.filter-buttons { }
.customer-table { }
.customer-table-row { }
.pagination { }
```

---

### 【阶段 3】客户管理 - 客户画像
**时间**：4小时

**涉及元素**：
1. 统计卡片（6个）- 活跃人数、来访次数、咨询次数、成交次数、成交金额、转介绍次数
2. 标签分类区域（多个彩色标签）
3. 数据趋势图表（Chart.js）
4. 筛选时间范围

**设计规范**：
- 统计卡片尺寸：`minmax(200px, 1fr)`
- 图标样式：彩色圆形背景 + 白色图标
- 标签样式：半透明彩色背景 + 圆角 8px
- 图表样式：白色背景 + 16px 圆角
- 颜色方案：蓝、绿、黄、橙、红、紫

**产出样式**：
```css
/* 客户画像 */
.profile-stats { }
.profile-stat-card { }
.tag-categories { }
.tag-category-item { }
.trend-charts { }
.chart-container { }
```

---

### 【阶段 4】客户管理 - 企业标签 & 企业通讯录
**时间**：3小时

**涉及元素**：
1. 标签管理界面（新建、编辑、删除标签）
2. 标签列表（卡片式或表格式）
3. 企业通讯录表格
4. 同步按钮

**设计规范**：
- 标签卡片：白色背景 + 12px 圆角
- 标签颜色：12种预设颜色
- 通讯录表格：同客户列表表格

---

### 【阶段 5】客户群管理
**时间**：3小时

**涉及元素**：
1. 客户群列表表格
2. 客户群标签管理
3. 搜索和筛选
4. 同步按钮

---

### 【阶段 6】客户运营
**时间**：3小时

**涉及元素**：
1. 欢迎语设置（文本编辑器 + 预览）
2. 客户广播（群发消息）
3. 发朋友圈（图文编辑器）
4. 朋友圈记录列表

---

### 【阶段 7】客户群运营
**时间**：3小时

**涉及元素**：
1. 进群欢迎语设置
2. 群发消息
3. 群发记录

---

### 【阶段 8】系统管理
**时间**：4小时

**涉及元素**：
1. 员工管理表格
2. 权限管理（角色列表、权限配置）
3. 数据源管理
4. 对内智能表格
5. 对外智能表

---

### 【阶段 9】通用组件 - 弹窗
**时间**：4小时 ⭐ 高优先级

**涉及元素**：
1. 新增/编辑弹窗（表单）
2. 删除确认弹窗
3. 详情查看弹窗
4. 选择器弹窗（标签选择、员工选择）

**设计规范**：
- 弹窗背景：半透明黑色 `rgba(0, 0, 0, 0.4)`
- 弹窗容器：白色 + 16px 圆角 + 阴影
- 标题栏高度：56px
- 内容区内边距：24px
- 底部按钮栏高度：64px
- 按钮间距：12px

**产出样式**：
```css
/* 弹窗系统 */
.modal-overlay { }
.modal-container { }
.modal-header { }
.modal-body { }
.modal-footer { }
.modal-close-btn { }
```

---

### 【阶段 10】通用组件 - 表单控件
**时间**：4小时 ⭐ 高优先级

**涉及元素**：
1. 文本输入框（text, email, password, number, tel）
2. 多行文本框（textarea）
3. 下拉选择器（select）
4. 单选框（radio）
5. 复选框（checkbox）
6. 开关（switch）
7. 日期选择器
8. 时间选择器
9. 文件上传组件

**设计规范**：
- 输入框高度：36px
- 背景：灰色半透明 `rgba(0, 0, 0, 0.06)`
- 圆角：12px
- 焦点状态：蓝色描边 + 光晕
- 标签字体：13px，medium

**产出样式**：
```css
/* 表单控件 */
.form-group { }
.form-label { }
.form-input { }
.form-textarea { }
.form-select { }
.form-checkbox { }
.form-radio { }
.form-switch { }
.form-upload { }
```

---

### 【阶段 11】通用组件 - 反馈组件
**时间**：2小时

**涉及元素**：
1. Toast 提示（成功、警告、错误、信息）
2. Loading 加载（全屏、局部）
3. 进度条
4. 空状态
5. 错误状态

**设计规范**：
- Toast 高度：48px
- Toast 圆角：12px
- Toast 位置：顶部居中
- Loading 动画：Apple 风格旋转器
- 空状态图标：64px，透明度 30%

**产出样式**：
```css
/* 反馈组件 */
.toast { }
.toast-success { }
.toast-warning { }
.toast-error { }
.loading-overlay { }
.loading-spinner { }
.empty-state { }
```

---

### 【阶段 12】最终测试
**时间**：3小时 ⭐ 高优先级

**测试清单**：

#### 页面测试（13个页面）：
- [ ] 工作台
- [ ] 客户列表
- [ ] 客户画像
- [ ] 企业标签
- [ ] 企业通讯录
- [ ] 客户群列表
- [ ] 客户群标签
- [ ] 欢迎语设置
- [ ] 客户广播
- [ ] 发朋友圈
- [ ] 进群欢迎语
- [ ] 群发
- [ ] 员工管理
- [ ] 权限管理
- [ ] 数据源管理

#### 组件测试：
- [ ] 所有弹窗正常显示
- [ ] 所有表单控件样式统一
- [ ] 所有按钮样式统一
- [ ] 所有表格样式统一
- [ ] Toast 提示正常
- [ ] Loading 加载正常

#### 兼容性测试：
- [ ] Chrome 浏览器
- [ ] Safari 浏览器
- [ ] Firefox 浏览器
- [ ] Edge 浏览器

#### 主题测试：
- [ ] 浅色模式正常
- [ ] 暗黑模式自动切换
- [ ] 所有颜色正确

#### 响应式测试：
- [ ] 小屏幕（< 768px）
- [ ] 中屏幕（768px - 1024px）
- [ ] 大屏幕（> 1024px）
- [ ] 超大屏幕（> 1920px）

#### 交互测试：
- [ ] 悬停动画流畅
- [ ] 焦点状态正确
- [ ] 激活状态正确
- [ ] 禁用状态正确
- [ ] 加载状态正确

---

## 🎨 Apple UI 设计规范总结

### 颜色系统：
```css
--color-primary: #007AFF;           /* Apple 蓝 */
--color-success: #34c759;           /* 成功绿 */
--color-warning: #ff9f0a;           /* 警告黄 */
--color-danger: #ff3b30;            /* 危险红 */
```

### 圆角系统：
```css
--radius-sm: 8px;                   /* 小圆角 */
--radius-md: 12px;                  /* 中圆角 */
--radius-lg: 16px;                  /* 大圆角 */
--radius-xl: 20px;                  /* 超大圆角 */
```

### 阴影系统：
```css
--shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
--shadow-md: 0 4px 12px rgba(0,0,0,0.12);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.16);
```

### 间距系统：
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
```

### 字体系统：
```css
--font-size-xs: 11px;
--font-size-sm: 12px;
--font-size-base: 13px;
--font-size-lg: 15px;
--font-size-xl: 17px;
--font-size-2xl: 20px;
--font-size-3xl: 28px;
```

---

## 📦 产出文件清单

### 新建文件：
1. `apple-ui-reset.css` - 重置旧样式
2. `apple-ui-master.css` - 主样式文件（~1000行）
3. `apple-ui-modules.css` - 模块样式文件（~800行）

### 更新文件：
1. `index.html` - 更新 CSS 引用顺序

### 备份文件：
1. `style-old-backup.css` - 备份原 style.css

### 禁用文件（可选）：
1. `employee-manage-styles.css` → 重命名为 `.css.bak`
2. `permission-manage-styles.css` → 重命名为 `.css.bak`

---

## 🔄 实施顺序

### 第一优先级（必须先完成）：
1. ✅ 阶段 0 - 准备工作
2. ⏳ 阶段 9 - 通用组件（弹窗）
3. ⏳ 阶段 10 - 通用组件（表单）
4. ⏳ 阶段 11 - 通用组件（反馈）

### 第二优先级（页面重构）：
5. ⏳ 阶段 1 - 工作台
6. ⏳ 阶段 2 - 客户列表
7. ⏳ 阶段 3 - 客户画像
8. ⏳ 阶段 4-8 - 其他页面

### 第三优先级（测试）：
9. ⏳ 阶段 12 - 最终测试

---

## ✅ 验收标准

### 视觉标准：
- ✅ 所有元素符合 Apple 设计规范
- ✅ 无橙色或不协调的颜色
- ✅ 圆角统一（8/12/16/20px）
- ✅ 间距统一
- ✅ 字体统一

### 交互标准：
- ✅ 悬停动画流畅（0.2s）
- ✅ 焦点状态清晰
- ✅ 按钮反馈及时
- ✅ 加载状态明确

### 兼容性标准：
- ✅ 支持 Chrome、Safari、Firefox、Edge
- ✅ 支持暗黑模式
- ✅ 支持响应式（< 768px、768-1024px、> 1024px）

---

## 📝 备注

- 每个阶段完成后，立即测试该页面/组件
- 出现问题及时调整，不留技术债
- 保持代码注释清晰
- 使用语义化的 class 命名

---

## 🚀 开始重构！

现在进入 **阶段 0 - 准备工作**，创建基础文件。

准备好了吗？让我们开始吧！ 💪
