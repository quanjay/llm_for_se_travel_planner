# AI Travel Planner - Web版AI旅行规划师

一款基于人工智能的智能旅行规划Web应用，帮助用户轻松规划个性化的旅行路线，管理费用预算，记录美好旅程。

## 项目特色

-  **AI智能规划**: 基于通义千问大模型，根据用户偏好自动生成个性化行程
-  **预算管理**: 智能预算分析和费用跟踪，实时掌控旅行开支
-  **语音输入** - 语音描述行程需求
-  **地图集成** - 高德地图可视化展示行程路线
-  **用户管理** - 支持用户管理多份行程和费用
-  **安全可靠**: JWT身份认证，云端数据加密存储，保护用户隐私
-  **现代UI**: 基于Element Plus的精美界面，操作简单直观

## 如何运行

1. clone项目至本地
2. 在 backend 文件夹下新建 .env :
    1. 按照模版配置：
    
    ```yaml
    # 安全认证密钥
    SECRET_KEY=YOUR_KEY
    
    # 通义千问API配置
    QIANWEN_API_KEY=YOUR_KEY
    
    # 讯飞开放平台配置
    XFYUN_APP_ID=YOUR_ID
    XFYUN_API_KEY=YOUR_KEY
    XFYUN_API_SECRET=YOUR_API_SECRET
    
    # Supabase 云端存储配置
    ENABLE_CLOUD_SYNC=True
    SUPABASE_URL=YOUR_URL
    SUPABASE_KEY=YOUR_KEY
    SUPABASE_SERVICE_KEY=YOUR_KEY
    ```
    
3. 在frontend 文件夹下新建 .env
    1. 按照模版配置：
    
    ```yaml
    # 后端API地址
    VITE_API_BASE_URL=http://localhost:8000/api
    
    # 高德地图配置
    VITE_AMAP_KEY=YOUR_KEY
    VITE_AMAP_SECURITY_CODE=YOUR_CODE
    ```
    
4. 配置后端环境：
    1. 创建conda环境，python==3.11
    2. 进入backend文件夹
    3. pip install -r requirements.txt
5. 配置前端环境：
    1. node 版本 20.19
    2. 进入frontend文件夹
    3. npm install
6. 在backend 文件夹下，运行 python main.py ，以启动后端
7. 在frontend 文件夹下，运行 npm run dev，以启动前端
