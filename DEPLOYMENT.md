# Docker 部署指南

本文档介绍如何使用 Docker 和 GitHub Actions 部署旅行规划应用。

## 目录

- [Docker 镜像构建](#docker-镜像构建)
- [GitHub Actions 自动化部署](#github-actions-自动化部署)
- [阿里云容器镜像服务配置](#阿里云容器镜像服务配置)
- [本地部署](#本地部署)
- [生产环境部署](#生产环境部署)

## Docker 镜像构建

### 项目结构

```
.
├── Dockerfile                    # 一体化镜像
├── backend/Dockerfile           # 后端镜像
├── frontend/Dockerfile          # 前端镜像
├── docker/
│   ├── nginx.conf              # Nginx 配置
│   └── start.sh                # 启动脚本
└── docker-compose.yml          # Docker Compose 配置
```

### 单独构建镜像

#### 后端镜像
```bash
cd backend
docker build -t travel-planner-backend:latest .
```

#### 前端镜像
```bash
cd frontend
docker build -t travel-planner-frontend:latest .
```

#### 一体化镜像
```bash
docker build -t travel-planner:latest .
```

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## GitHub Actions 自动化部署

### 配置步骤

#### 1. 在阿里云容器镜像服务创建命名空间

1. 访问[阿里云容器镜像服务控制台](https://cr.console.aliyun.com/)
2. 选择地域（如：华东1-杭州）
3. 创建命名空间（如：`my-namespace`）
4. 创建镜像仓库：
   - `travel-planner-backend`
   - `travel-planner-frontend`
   - `travel-planner-all-in-one`

#### 2. 获取访问凭证

1. 在阿里云容器镜像服务控制台，点击右上角头像
2. 选择"访问凭证"
3. 设置或重置固定密码（记录用户名和密码）

#### 3. 配置 GitHub Secrets

在 GitHub 仓库中添加以下 Secrets（Settings → Secrets and variables → Actions）：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云容器镜像服务用户名 | `your-username` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云容器镜像服务密码 | `your-password` |

#### 4. 修改工作流配置

编辑 `.github/workflows/docker-build-push.yml`：

```yaml
env:
  ALIYUN_REGISTRY: registry.cn-hangzhou.aliyuncs.com  # 根据你的区域修改
  ALIYUN_NAMESPACE: my-namespace  # 替换为你的命名空间
  IMAGE_NAME: travel-planner
```

### 触发构建

GitHub Actions 会在以下情况自动触发：

- **推送到 main 分支**：构建并推送 `latest` 标签
- **推送到 develop 分支**：构建并推送 `develop` 标签
- **创建标签** (如 `v1.0.0`)：构建版本化镜像
- **Pull Request**：仅构建测试，不推送
- **手动触发**：在 Actions 页面手动运行

### 镜像标签策略

工作流会自动生成以下标签：

- `latest` - 最新的 main 分支构建
- `main` - main 分支最新构建
- `develop` - develop 分支最新构建
- `v1.0.0` - 版本标签
- `1.0` - 主次版本号
- `1` - 主版本号
- `main-abc1234` - 分支名 + Git SHA

## 阿里云容器镜像服务配置

### 区域选择

阿里云容器镜像服务支持多个区域：

| 区域 | Registry 地址 |
|------|--------------|
| 华东1（杭州） | `registry.cn-hangzhou.aliyuncs.com` |
| 华东2（上海） | `registry.cn-shanghai.aliyuncs.com` |
| 华北2（北京） | `registry.cn-beijing.aliyuncs.com` |
| 华南1（深圳） | `registry.cn-shenzhen.aliyuncs.com` |

选择离你的服务器最近的区域以获得最佳性能。

### 拉取镜像

```bash
# 登录阿里云镜像仓库
docker login --username=your-username registry.cn-hangzhou.aliyuncs.com

# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-backend:latest
docker pull registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-frontend:latest
docker pull registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-all-in-one:latest
```

## 本地部署

### 使用 Docker Compose

1. 克隆项目：
```bash
git clone https://github.com/quanjay/llm_for_se_travel_planner.git
cd llm_for_se_travel_planner
```

2. 配置环境变量：
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入你的配置
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问应用：
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 使用预构建镜像

```bash
# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-all-in-one:latest

# 运行容器
docker run -d \
  --name travel-planner \
  -p 80:80 \
  -p 8000:8000 \
  --env-file backend/.env \
  registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-all-in-one:latest
```

## 生产环境部署

### 方案 1：独立部署前后端

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-backend:latest
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    restart: always

  frontend:
    image: registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always
```

### 方案 2：一体化部署

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-all-in-one:latest
    ports:
      - "80:80"
      - "8000:8000"
    env_file:
      - ./backend/.env
    restart: always
```

### 启动生产环境

```bash
# 拉取最新镜像
docker-compose -f docker-compose.prod.yml pull

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 环境变量配置

创建 `backend/.env` 文件：

```env
# 应用配置
PROJECT_NAME=AI旅行规划师
VERSION=1.0.0
ENVIRONMENT=production

# 跨域配置
ALLOWED_HOSTS=["*"]

# 安全配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase 配置
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# OpenAI 配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 讯飞语音配置
XFYUN_APP_ID=your-xfyun-app-id
XFYUN_API_KEY=your-xfyun-api-key
XFYUN_API_SECRET=your-xfyun-api-secret
```

## 监控和维护

### 查看容器状态

```bash
docker ps
docker-compose ps
```

### 查看日志

```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 更新镜像

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d

# 清理旧镜像
docker image prune -f
```

### 备份和恢复

```bash
# 导出镜像
docker save -o travel-planner-backup.tar \
  registry.cn-hangzhou.aliyuncs.com/my-namespace/travel-planner-all-in-one:latest

# 导入镜像
docker load -i travel-planner-backup.tar
```

## 故障排查

### 常见问题

1. **容器无法启动**
   - 检查环境变量配置
   - 查看容器日志：`docker logs <container-name>`

2. **端口冲突**
   - 修改 docker-compose.yml 中的端口映射
   - 检查端口占用：`lsof -i :8000`

3. **镜像拉取失败**
   - 检查网络连接
   - 验证阿里云凭证是否正确
   - 确认镜像仓库地址和命名空间

4. **健康检查失败**
   - 检查应用是否正常启动
   - 验证健康检查端点是否可访问

## 安全建议

1. **使用 HTTPS**：在生产环境中使用 Nginx 反向代理配置 SSL 证书
2. **限制访问**：配置防火墙规则，只开放必要的端口
3. **定期更新**：及时更新基础镜像和依赖包
4. **备份数据**：定期备份数据库和配置文件
5. **监控日志**：设置日志监控和告警

## 性能优化

1. **镜像大小优化**
   - 使用多阶段构建
   - 使用 alpine 基础镜像
   - 清理不必要的文件

2. **缓存优化**
   - 利用 Docker 层缓存
   - 配置 Nginx 静态资源缓存
   - 使用 CDN 加速静态资源

3. **资源限制**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [阿里云容器镜像服务](https://help.aliyun.com/product/60716.html)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Compose 文档](https://docs.docker.com/compose/)
