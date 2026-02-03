# 天号城企微CRM系统

> 基于企业微信的客户关系管理系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

---

## 📋 项目简介

天号城企微CRM系统是一个基于企业微信的客户关系管理系统，提供客户管理、客户群管理、数据统计分析等功能。

### ✨ 主要特性

- 🔄 **自动同步** - 每小时自动增量同步企业微信客户数据
- 📊 **数据分析** - 客户画像、标签统计、数据可视化
- 👥 **客户管理** - 客户列表、详情查看、标签管理
- 💬 **群聊管理** - 客户群列表、群标签管理
- 🤖 **通知机器人** - 企业微信群机器人消息推送
- 📱 **响应式设计** - 支持桌面端和移动端

---

## 🏗️ 技术架构

### 后端
- **框架**: FastAPI
- **数据库**: SQLite
- **同步**: schedule (定时任务)
- **并发**: ThreadPoolExecutor

### 前端
- **HTML5 + CSS3 + JavaScript**
- **图表**: Chart.js
- **图标**: Font Awesome

---

## 📦 已实现的功能模块

### 1️⃣ 客户管理模块 ✅
- 客户列表（分页、搜索、筛选）
- 客户详情查看
- 客户标签管理
- 批量操作（导出、打标签）
- 客户同步（全量、增量、定时）

### 2️⃣ 企业通讯录模块 ✅
- 员工列表展示
- 部门树结构
- 员工详情查看

### 3️⃣ 客户群列表模块 ✅
- 群聊列表展示
- 群聊筛选（群主、类型、标签）
- 群聊同步
- 批量打标签
- 导出功能

### 4️⃣ 客户群标签模块 ✅
- 标签组管理
- 标签增删改查
- 标签检查同步
- 搜索功能

### 5️⃣ 客户画像模块 ✅
- 核心标签统计（6个关键标签）
- 所有标签统计
- 标签客户列表查看
- 数据准确性已优化

### 6️⃣ 供应商通知群模块 ✅
- 前端 UI 设计
- 添加群功能（Webhook）
- 发送通知功能
- 查看通知记录
- 后端 API（CRUD）

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/tianhao-crm.git
cd tianhao-crm
```

#### 2. 安装依赖
```bash
pip install fastapi uvicorn schedule
```

#### 3. 配置
```bash
# 复制配置文件模板
cp config.example.py config.py

# 编辑 config.py，填入真实的企业微信配置
# CORP_ID = "你的企业ID"
# SECRET = "你的应用Secret"
# AGENT_ID = "你的应用AgentID"
```

#### 4. 启动服务
```bash
python start.py
```

#### 5. 访问系统
打开浏览器访问：http://localhost:9999

---

## 📂 项目结构

```
wecom-crm/backend/
├── app.py                      # FastAPI 主应用
├── start.py                    # 启动脚本
├── sync_service.py            # 同步服务
├── config.py                  # 配置文件（需自己创建）
├── config.example.py          # 配置文件模板
├── data/                      # 数据目录（不提交到 Git）
│   └── crm.db                # SQLite 数据库
├── static/                    # 前端静态文件
│   ├── index.html            # 主页面
│   ├── style.css             # 样式文件
│   ├── script.js             # 主脚本
│   ├── wecom-bot.js          # 机器人模块
│   └── group-tags-v2.js      # 标签模块
└── docs/                      # 文档目录
    ├── README.md             # 本文件
    ├── SESSION_MEMORY_SNAPSHOT_20260126.md
    ├── MEMORY_MIGRATION_GUIDE.md
    └── ...
```

---

## 🔧 配置说明

### config.py

```python
# 企业微信配置
CORP_ID = "你的企业ID"
SECRET = "你的应用Secret"
AGENT_ID = "你的应用AgentID"

# 数据库配置
DB_PATH = "data/crm.db"

# 同步配置
SYNC_MAX_WORKERS = 10
SYNC_INTERVAL_HOURS = 1

# 服务器配置
HOST = "0.0.0.0"
PORT = 9999
```

---

## 📊 数据统计

截至 2026-01-26：
- **客户总数**: 19,610 人
- **数据库大小**: 17 MB
- **有企业标签**: 19,191 人
- **原有老代理商**: 2,585 人
- **代理商**: 1 人
- **客户**: 15,944 人
- **上游同行**: 80 人

---

## 🐛 最近修复的问题

### 问题 1: 客户画像标签统计不准确 ✅
- **原因**: 后端 API 使用了 `"代理" in tag_name` 导致误匹配
- **修复**: 重写 `get_tag_stats()` API，使用精确匹配
- **文件**: `app.py` 第 2618-2755 行

### 问题 2: 供应商通知群按钮报错 ✅
- **原因**: `wecom-bot.js` 有语法错误的残留代码
- **修复**: 删除残留代码，修复函数导出逻辑

### 问题 3: 同步任务无法取消 ✅
- **原因**: 停止信号检查不完整
- **修复**: 在 3 个关键位置加入停止检查

### 问题 4: 定时自动同步 ✅
- **实现**: 使用 schedule 库，每小时自动增量同步

---

## 🔄 部署流程

### 停止服务
```bash
taskkill /F /IM python.exe  # Windows
# 或
kill -9 $(lsof -ti:9999)    # Linux/Mac
```

### 启动服务
```bash
cd D:\tianhao-webhook\wecom-crm\backend
python start.py
```

### 更新前端版本
修改前端文件后，记得更新版本号：
```html
<!-- 例如 -->
<link rel="stylesheet" href="style.css?v=20260126027">
```

### 清除浏览器缓存
- 按 `Ctrl + Shift + Delete`
- 选择"缓存的图片和文件"
- 清除并重启浏览器

---

## 🎯 待开发功能

### 短期（1-2 周）
- [ ] 修复客户群列表和客户群标签的按钮文字颜色
- [ ] 供应商通知群：支持 Markdown 消息
- [ ] 供应商通知群：消息模板功能

### 中期（1 个月）
- [ ] 客户跟进记录功能
- [ ] 客户生命周期管理
- [ ] 销售漏斗分析
- [ ] 定时报表推送

### 长期（3 个月）
- [ ] 移动端适配
- [ ] 权限管理系统
- [ ] 数据备份与恢复
- [ ] 多企业支持

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [SESSION_MEMORY_SNAPSHOT_20260126.md](SESSION_MEMORY_SNAPSHOT_20260126.md) | 完整会话记忆快照（用于 AI 会话迁移） |
| [MEMORY_MIGRATION_GUIDE.md](MEMORY_MIGRATION_GUIDE.md) | 记忆迁移操作指南 |
| [NEW_SESSION_PROMPT_V3.md](NEW_SESSION_PROMPT_V3.md) | 新会话启动提示词 |
| [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md) | GitHub 上传指南 |
| [SUPPLIER_NOTIFY_STATUS.md](SUPPLIER_NOTIFY_STATUS.md) | 供应商通知群开发状态 |

---

## ⚠️ 注意事项

### 安全提醒
1. **不要提交敏感信息**: `config.py`、`data/crm.db` 已添加到 `.gitignore`
2. **保护 API 密钥**: 企业微信的 Secret 不要泄露
3. **数据备份**: 定期备份 `data/crm.db` 数据库文件

### 开发规范
1. **前端修改后必须更新版本号**
2. **前端报错先查看 F12 Console**
3. **代码修改前必须先用 Read 工具读取文件**
4. **不要假设是缓存问题，先看实际错误**

---

## 🤝 贡献

本项目为私有项目，暂不接受外部贡献。

---

## 📄 许可证

本项目为私有项目，版权所有。

---

## 📞 联系方式

- **项目负责人**: 天号城团队
- **技术支持**: AI 辅助开发

---

**最后更新**: 2026-01-26  
**当前版本**: v1.0  
**数据库版本**: 17MB (19,610 客户)
