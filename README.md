# 天号城 企微CRM系统

> 📅 **最后更新**：2026-01-26  
> 🏗️ **项目路径**：`D:\tianhao-webhook\wecom-crm\backend\`  
> 📦 **数据库**：`data/crm.db` (17 MB, 19,610 客户)

---

## 🚀 快速启动

### 启动服务
```bash
cd D:\tianhao-webhook\wecom-crm\backend
python start.py
```

### 停止服务
```bash
taskkill /F /IM python.exe
```

### 访问地址
- **前端界面**：http://localhost:9999
- **API 文档**：http://localhost:9999/docs

---

## 📚 核心文档索引

| 文档 | 说明 |
|------|------|
| [SESSION_MEMORY_SNAPSHOT_20260126.md](SESSION_MEMORY_SNAPSHOT_20260126.md) | 📋 完整会话记忆快照（用于 AI 会话迁移） |
| [PROJECT_STATE_SUMMARY.md](PROJECT_STATE_SUMMARY.md) | 📊 项目状态总结 |
| [MEMORY_MIGRATION_GUIDE.md](MEMORY_MIGRATION_GUIDE.md) | 🔄 记忆迁移操作指南 |
| [SUPPLIER_NOTIFY_STATUS.md](SUPPLIER_NOTIFY_STATUS.md) | 🤖 供应商通知群开发状态 |
| [REFLECTION_AND_IMPROVEMENT.md](REFLECTION_AND_IMPROVEMENT.md) | 💡 问题反思与改进 |

---

## ✅ 已完成的功能模块

### 1️⃣ 客户管理
- ✅ 客户列表（分页、搜索、筛选）
- ✅ 客户详情查看
- ✅ 客户标签管理
- ✅ 批量操作（导出、打标签）
- ✅ 客户同步（全量、增量、定时）

### 2️⃣ 企业通讯录
- ✅ 员工列表
- ✅ 部门树结构
- ✅ 员工详情

### 3️⃣ 客户群列表
- ✅ 群聊列表展示
- ✅ 群聊筛选
- ✅ 群聊同步
- ✅ 批量打标签
- ⚠️ **待修复**：按钮文字颜色需改为白色

### 4️⃣ 客户群标签
- ✅ 标签组管理
- ✅ 标签 CRUD
- ✅ 标签检查同步
- ⚠️ **待修复**：按钮文字颜色需改为白色

### 5️⃣ 客户画像
- ✅ 核心标签统计（6个关键标签）
- ✅ 所有标签统计
- ✅ 标签客户列表
- ✅ 数据准确性已修复

### 6️⃣ 供应商通知群
- ✅ 基础功能（添加群、发送通知、查看记录）
- ⚠️ **待开发**：Markdown、模板、定时推送、统计

---

## 🐛 最近修复的问题

### 问题 1：标签统计不准确 ✅
- **现象**：原有老代理商显示 5000+，实际 2585 人
- **原因**：后端 API 使用 `"代理" in tag_name` 导致误匹配
- **解决**：重写 `get_tag_stats()` API，使用精确匹配
- **文件**：`app.py` 行 2618-2755

### 问题 2：供应商通知群按钮报错 ✅
- **现象**：点击"添加群"报错 `showAddWebhookDialog is not defined`
- **原因**：wecom-bot.js 有语法错误的残留代码
- **解决**：删除残留代码，修复函数导出
- **文件**：`static/wecom-bot.js`, `static/index.html`

### 问题 3：同步任务无法取消 ✅
- **现象**：点击"取消同步"后仍在继续
- **解决**：在 3 个关键位置加入停止检查
- **文件**：`sync_service.py`

### 问题 4：定时自动同步 ✅
- **需求**：每小时自动增量同步
- **实现**：安装 `schedule` 库，添加定时任务
- **文件**：`sync_service.py`

---

## 🔥 当前待处理

### 🚨 紧急
1. **客户群列表**：按钮文字改为白色
2. **客户群标签**：按钮文字改为白色

### 📋 待开发
- 供应商通知群：Markdown 消息
- 供应商通知群：消息模板
- 供应商通知群：定时推送
- 数据统计仪表板优化

---

## 📁 项目结构

```
wecom-crm/backend/
├── app.py                          # FastAPI 主应用
├── start.py                        # 启动脚本
├── sync_service.py                 # 同步服务
├── config.py                       # 配置文件
├── data/
│   └── crm.db                     # SQLite 数据库
├── static/                         # 前端静态文件
│   ├── index.html                 # 主页面 (v=20260126026)
│   ├── style.css                  # 样式 (v=20260126019)
│   ├── script.js                  # 主脚本 (v=20260126004)
│   ├── wecom-bot.js               # 机器人模块 (v=20260126025)
│   └── group-tags-v2.js           # 标签模块 (v=20260125010)
└── docs/                           # 文档目录
    ├── README.md                  # 本文件
    ├── SESSION_MEMORY_SNAPSHOT_20260126.md
    ├── PROJECT_STATE_SUMMARY.md
    └── ...
```

---

## 🔧 依赖环境

### Python 依赖
```bash
pip install fastapi uvicorn schedule
```

### 已安装版本
- Python: 3.x
- schedule: 1.2.2
- fastapi: 最新
- uvicorn: 最新

---

## 📊 数据统计

- **客户总数**：19,610 人
- **有企业标签**：19,191 人
- **原有老代理商**：2,585 人
- **代理商**：1 人
- **客户标签**：15,944 人
- **上游同行**：80 人

---

## 🔄 标准部署流程

1. **停止服务**：`taskkill /F /IM python.exe`
2. **替换文件**：将修改的文件复制到项目目录
3. **启动服务**：`cd D:\tianhao-webhook\wecom-crm\backend && python start.py`
4. **清除缓存**：浏览器 Ctrl+Shift+Delete，清除缓存
5. **验证功能**：F12 查看 Console，测试功能

---

## 💡 AI 会话迁移指南

### 当会话接近 20W tokens 时：

1. **准备工作**：
   - 复制 `SESSION_MEMORY_SNAPSHOT_20260126.md` 的全部内容

2. **开启新会话**：
   - 第一条消息粘贴快照内容
   - 加上当前最紧急的任务

3. **示例提示词**：
   ```
   你好！我是天号城 CRM 系统的项目负责人。
   我们的上一个会话达到 token 限制，现在需要继续开发。
   
   以下是项目的完整状态：
   
   [粘贴 SESSION_MEMORY_SNAPSHOT_20260126.md 的内容]
   
   当前最紧急的任务：
   1. 修复客户群列表和客户群标签模块的按钮文字颜色
   
   请确认你已理解项目状态，然后我们继续开发。
   ```

---

## 📞 问题排查

### 前端功能不工作
```bash
# 检查服务
netstat -ano | findstr :9999

# 查看日志
cd D:\tianhao-webhook\wecom-crm\backend
python start.py

# 浏览器 Console
F12 → Console → 查看错误
```

### 数据统计异常
```python
import sqlite3
conn = sqlite3.connect('data/crm.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM customers")
print(cursor.fetchone())
```

---

## 🎯 下一步计划

### 短期（1-2 周）
1. 修复按钮文字颜色 ⚠️
2. Markdown 消息支持
3. 消息模板功能

### 中期（1 个月）
1. 客户跟进记录
2. 销售漏斗分析
3. 定时报表推送

### 长期（3 个月）
1. 移动端适配
2. 权限管理
3. 多企业支持

---

## 📝 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-01-26 | v1.0 | 创建 README，整理项目状态 |

---

**维护者**：天号城团队  
**技术支持**：AI 辅助开发  
**最后更新**：2026-01-26 23:50
