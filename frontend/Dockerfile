# 前端 Dockerfile - 多阶段构建
# 阶段1: 构建
FROM node:18-alpine AS builder

WORKDIR /app

# 接收构建参数（不设置默认值，必须通过构建参数传入）
ARG VITE_API_BASE_URL=http://localhost:8000/api
ARG VITE_AMAP_KEY
ARG VITE_AMAP_SECURITY_CODE

# 设置为环境变量供构建使用
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_AMAP_KEY=$VITE_AMAP_KEY
ENV VITE_AMAP_SECURITY_CODE=$VITE_AMAP_SECURITY_CODE

# 复制 package 文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci

# 复制源代码（包括 .env 文件）
COPY . .

# 构建生产版本
RUN npm run build:prod

# 阶段2: 运行
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
