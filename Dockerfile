# 完整应用 Dockerfile - 前后端一体化
# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build:prod

# 阶段2: 构建后端
FROM python:3.11-slim AS backend

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖并安装
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物到 nginx 目录
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY docker/nginx.conf /etc/nginx/sites-available/default

# 创建启动脚本
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# 暴露端口
EXPOSE 80 8000

# 启动命令
CMD ["/start.sh"]
