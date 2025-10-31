# AI旅行规划师后端API

基于FastAPI构建的AI旅行规划师后端服务。

## 功能特性

- 用户注册和登录系统
- JWT身份验证
- 旅行计划管理
- 费用记录和分析
- RESTful API设计

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)
- **数据迁移**: Alembic

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API路由
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── schemas/            # Pydantic模式
│   ├── services/           # 业务逻辑
│   └── utils/              # 工具函数
├── alembic/                # 数据库迁移
├── scripts/                # 初始化脚本
├── main.py                 # 应用入口
└── requirements.txt        # 依赖包
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env` 文件并修改配置：

```bash
cp .env.example .env
```

配置数据库连接和其他必要参数。

### 3. 初始化数据库

```bash
# 方式1: 使用Alembic迁移（推荐）
alembic upgrade head

# 方式2: 直接创建表
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 开发模式
python main.py

# 或使用uvicorn
uvicorn main:app --reload
```

服务将在 http://localhost:8000 启动。

## API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库表结构

### 用户表 (users)
- id: 主键
- email: 邮箱（唯一）
- username: 用户名（唯一）
- hashed_password: 加密密码
- phone: 手机号
- avatar: 头像URL
- created_at: 创建时间
- updated_at: 更新时间

### 旅行计划表 (travel_plans)
- id: 主键
- user_id: 用户ID（外键）
- title: 行程标题
- destination: 目的地
- start_date: 开始日期
- end_date: 结束日期
- budget: 预算
- people_count: 人数
- preferences: 偏好（JSON）
- itinerary: 详细行程（JSON）
- total_cost: 总花费
- status: 状态（draft/published/completed）
- created_at: 创建时间
- updated_at: 更新时间

### 费用记录表 (expenses)
- id: 主键
- travel_plan_id: 行程ID（外键）
- category: 费用类别
- amount: 金额
- description: 描述
- expense_date: 消费日期
- created_at: 创建时间
- updated_at: 更新时间

## 开发指南

### 添加新的API端点

1. 在 `app/api/routes/` 中创建或修改路由文件
2. 在 `app/schemas/` 中定义Pydantic模式
3. 在 `app/models/` 中定义数据模型（如需要）
4. 在 `main.py` 中注册路由

### 数据库迁移

```bash
# 生成新的迁移文件
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEBUG | 调试模式 | False |
| SECRET_KEY | JWT密钥 | 需要设置 |
| DATABASE_URL | 数据库连接URL | 需要设置 |
| QIANWEN_API_KEY | 通义千问API密钥 | 需要设置 |

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 许可证

MIT License