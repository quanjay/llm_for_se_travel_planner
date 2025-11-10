#!/bin/bash

# 启动 nginx
service nginx start

# 启动后端服务
cd /app/backend
exec uvicorn main:app --host 0.0.0.0 --port 8000
