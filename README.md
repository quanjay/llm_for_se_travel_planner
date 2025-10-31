# AI Travel Planner - Web版AI旅行规划师

一款基于人工智能的智能旅行规划Web应用，帮助用户轻松规划个性化的旅行路线。

## 项目结构

```
llm_for_se_travel_planner/
├── frontend/          # Vue3 + TypeScript 前端项目
├── backend/           # FastAPI + Python 后端项目
├── 需求PRD.txt        # 产品需求文档
├── README.md          # 项目说明文档
└── LICENSE           # 许可证文件
```

## 技术栈

### 前端
- Vue 3 + TypeScript
- Element Plus UI组件库
- Pinia 状态管理
- Vue Router 路由管理
- Vite 构建工具

### 后端
- Python 3.8+
- FastAPI Web框架
- MySQL 数据库
- SQLAlchemy ORM
- JWT 身份认证

### AI集成
- 通义千问大语言模型
- 科大讯飞语音识别API（后续集成）
- 高德地图API（后续集成）

## 核心功能

- ✅ 用户注册登录系统
- ✅ 智能行程规划（文字输入）
- ✅ 费用预算管理
- ⏳ 语音输入功能（第二阶段）
- ⏳ 地图集成展示（第二阶段）
- ⏳ 云端数据同步（第二阶段）

## 快速开始

### 环境要求

- Node.js 16+ 
- Python 3.8+
- MySQL 8.0+

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 开发进度

### 第一阶段（MVP版本）- 进行中
- [x] 项目基础结构搭建
- [ ] Vue3前端项目初始化
- [ ] FastAPI后端项目初始化
- [ ] 数据库设计
- [ ] 用户注册登录系统
- [ ] 基础页面结构
- [ ] 文字输入行程规划
- [ ] 基础预算计算

### 第二阶段（完整版本）- 待开发
- [ ] 语音识别功能集成
- [ ] AI行程规划优化
- [ ] 完整费用管理模块
- [ ] 云端同步功能

### 第三阶段（优化版本）- 待开发
- [ ] 用户体验优化
- [ ] 性能调优
- [ ] 移动端深度适配
- [ ] 高级功能扩展

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。