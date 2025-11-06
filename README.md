# AI Travel Planner - Web版AI旅行规划师

一款基于人工智能的智能旅行规划Web应用，帮助用户轻松规划个性化的旅行路线，管理费用预算，记录美好旅程。

## 🌟 项目特色

- 🤖 **AI智能规划**: 基于通义千问大模型，根据用户偏好自动生成个性化行程
- 💰 **预算管理**: 智能预算分析和费用跟踪，实时掌控旅行开支
- 📱 **响应式设计**: 完美适配PC和移动端，随时随地管理行程
- 🔐 **安全可靠**: JWT身份认证，数据加密存储，保护用户隐私
- 🎨 **现代UI**: 基于Element Plus的精美界面，操作简单直观

## 📁 项目结构

```
llm_for_se_travel_planner/
├── frontend/                    # Vue3 + TypeScript 前端项目
│   ├── src/
│   │   ├── components/         # 公共组件
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API接口
│   │   ├── stores/             # Pinia状态管理
│   │   ├── router/             # 路由配置
│   │   └── types/              # TypeScript类型定义
│   ├── package.json
│   └── vite.config.ts
├── backend/                     # FastAPI + Python 后端项目
│   ├── app/
│   │   ├── api/routes/         # API路由
│   │   ├── core/               # 核心配置
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic模式
│   │   └── services/           # 业务逻辑
│   ├── alembic/                # 数据库迁移
│   ├── requirements.txt
│   └── main.py
├── 需求PRD.txt                  # 产品需求文档
├── README.md                   # 项目说明文档
└── LICENSE                     # 许可证文件
```

## 🛠 技术栈

### 前端
- **Vue 3** + **TypeScript** - 现代化前端框架
- **Element Plus** - 企业级UI组件库
- **Pinia** - 新一代状态管理
- **Vue Router** - 官方路由管理
- **Vite** - 高性能构建工具
- **Axios** - HTTP客户端

### 后端
- **Python 3.8+** - 编程语言
- **FastAPI** - 高性能Web框架
- **MySQL** - 关系型数据库
- **SQLAlchemy** - ORM框架
- **Alembic** - 数据库迁移工具
- **JWT** - 身份认证
- **Pydantic** - 数据验证

### AI与第三方服务
- **通义千问** - 大语言模型，智能行程生成
- **科大讯飞** - 语音识别API（计划中）
- **高德地图** - 地图服务API（计划中）

## ✨ 核心功能

### 已完成功能
- ✅ **用户认证系统** - 注册、登录、JWT Token管理
- ✅ **智能行程规划** - AI生成个性化旅行路线
- ✅ **费用管理** - 预算分析、支出记录、统计报表
- ✅ **响应式布局** - 适配PC和移动端
- ✅ **个人中心** - 用户信息管理、密码修改

### 开发中功能
- ⏳ **语音输入** - 语音描述行程需求
- ⏳ **地图集成** - 可视化展示行程路线
- ⏳ **离线缓存** - 支持离线查看行程

### 计划功能
- 📋 **协作规划** - 多人共同规划行程
- 📷 **行程分享** - 生成精美的行程海报
- 🏆 **积分系统** - 用户活跃度奖励

## 🚀 快速开始

### 环境要求

- **Node.js** 16+ 
- **Python** 3.8+
- **MySQL** 8.0+

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/llm_for_se_travel_planner.git
cd llm_for_se_travel_planner
```

### 2. 前端配置

```bash
cd frontend

# 安装依赖
npm install

# 复制环境配置文件
cp .env.example .env

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

### 3. 后端配置

```bash
cd backend

# 创建虚拟环境
python -m venv travel_planner
source travel_planner/bin/activate  # Windows: travel_planner\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置文件
cp .env.example .env

# 配置数据库和API密钥（编辑.env文件）
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/travel_planner
# QIANWEN_API_KEY=your-api-key

# 运行数据库迁移
alembic upgrade head

# 启动后端服务器
python main.py
```

后端将在 http://localhost:8000 启动

### 4. 数据库初始化

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE travel_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 运行迁移
cd backend
alembic upgrade head
```

## 📱 功能截图

### 首页
- 现代化设计的欢迎页面
- 功能特性展示
- 热门目的地推荐

### 行程规划
- AI智能生成行程
- 详细的日程安排
- 活动类型分类展示

### 费用管理
- 预算使用情况分析
- 分类费用统计
- 支出记录管理

### 个人中心
- 用户信息管理
- 行程统计数据
- 密码修改功能

## 🔧 开发指南

### 前端开发

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码格式化
npm run lint
```

### 后端开发

```bash
# 启动开发服务器
uvicorn main:app --reload

# 运行测试
pytest

# 代码格式化
black .
```

### 数据库迁移

```bash
# 生成新的迁移文件
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 📊 开发进度

### 第一阶段（MVP版本）- ✅ 已完成
- [x] 项目基础架构搭建
- [x] Vue3前端项目初始化
- [x] FastAPI后端项目初始化
- [x] MySQL数据库设计
- [x] 用户注册登录系统
- [x] 基础页面结构和导航
- [x] 文字输入行程规划功能
- [x] 费用预算管理系统

### 第二阶段（完整版本）- 🔄 开发中
- [ ] 语音识别功能集成
- [ ] AI行程规划算法优化
- [ ] 地图可视化展示
- [ ] 完整的费用分析报表
- [ ] 云端数据同步

### 第三阶段（优化版本）- 📋 计划中
- [ ] 用户体验优化
- [ ] 性能调优和缓存
- [ ] 移动端PWA支持
- [ ] 多语言国际化
- [ ] 高级功能扩展

## 🤝 贡献指南

我们欢迎任何形式的贡献！

1. **Fork** 本仓库
2. **创建** 特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **创建** Pull Request

### 贡献类型
- 🐛 Bug修复
- ✨ 新功能开发  
- 📝 文档改进
- 🎨 UI/UX优化
- ⚡ 性能优化
- 🧪 测试用例

## 📝 更新日志

### v1.0.0 (2024-10-31)
- ✨ 完成MVP版本开发
- 🔐 实现用户认证系统
- 🤖 集成AI行程规划功能
- 💰 完善费用管理模块
- 📱 优化响应式设计

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Element Plus](https://element-plus.gitee.io/) - UI组件库
- [通义千问](https://tongyi.aliyun.com/) - AI大语言模型

---

**如果这个项目对你有帮助，请给我们一个 ⭐️ Star！**