# Frontend - AI Travel Planner Web App

AI旅行规划师的前端应用，基于Vue 3 + TypeScript开发，提供现代化的用户界面和流畅的交互体验。

## 🎨 功能特性

- ✅ **现代化UI** - 基于Element Plus的精美界面设计
- ✅ **响应式布局** - 完美适配PC和移动端设备
- ✅ **用户认证** - 注册、登录、个人中心管理
- ✅ **智能规划** - AI生成个性化旅行行程
- ✅ **费用管理** - 预算分析和支出记录
- ✅ **实时交互** - 流畅的页面切换和数据更新
- ✅ **类型安全** - TypeScript提供完整的类型检查

## 🛠 技术栈

- **Vue 3** - 渐进式JavaScript框架，Composition API
- **TypeScript** - 静态类型检查，提供更好的开发体验
- **Element Plus** - 基于Vue 3的组件库，企业级UI设计
- **Pinia** - Vue官方状态管理库，替代Vuex
- **Vue Router** - 官方路由管理器
- **Vite** - 现代化构建工具，极速热重载
- **Axios** - HTTP客户端，处理API请求

## 📁 项目结构

```
frontend/
├── public/
│   └── images/              # 静态图片资源
├── src/
│   ├── api/                 # API接口定义
│   │   ├── auth.ts          # 认证相关API
│   │   ├── expense.ts       # 费用管理API
│   │   ├── travel-plan.ts   # 行程规划API
│   │   └── request.ts       # Axios配置
│   ├── components/          # 公共组件
│   │   └── AppLayout.vue    # 应用布局组件
│   ├── router/              # 路由配置
│   │   └── index.ts         # 路由定义
│   ├── stores/              # Pinia状态管理
│   │   └── user.ts          # 用户状态管理
│   ├── types/               # TypeScript类型定义
│   │   └── index.ts         # 全局类型
│   ├── utils/               # 工具函数
│   ├── views/               # 页面组件
│   │   ├── Auth/            # 认证页面
│   │   ├── Planning/        # 行程规划页面
│   │   ├── Expenses/        # 费用管理页面
│   │   ├── Profile/         # 个人中心页面
│   │   └── Error/           # 错误页面
│   ├── App.vue              # 根组件
│   └── main.ts              # 应用入口
├── index.html               # HTML模板
├── package.json             # 项目配置
├── tsconfig.json            # TypeScript配置
└── vite.config.ts           # Vite配置
```

## 🚀 快速开始

### 环境要求
- Node.js 16+
- npm 或 yarn

### 1. 安装依赖
```bash
npm install
# 或
yarn install
```

### 2. 环境配置
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件，设置后端API地址
# VITE_API_BASE_URL=http://localhost:8000/api
```

### 3. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

应用将在 http://localhost:5173 启动

### 4. 构建生产版本
```bash
npm run build
# 或
yarn build
```

### 5. 预览生产版本
```bash
npm run preview
# 或
yarn preview
```

## 🎯 页面路由

### 公开页面
- `/` - 首页，展示产品特性和快速入口
- `/login` - 用户登录页面
- `/register` - 用户注册页面

### 认证页面（需要登录）
- `/planning` - 行程规划列表页
- `/planning/:id` - 行程详情页
- `/expenses` - 费用管理页面
- `/profile` - 个人中心页面

## 🔧 开发工具

### 推荐IDE配置
- **VS Code** + Vue (Official) 插件
- 禁用 Vetur 插件以避免冲突

### 浏览器开发工具
- **Chrome/Edge**: [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- **Firefox**: [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

### 代码格式化
```bash
# 代码检查
npm run lint

# 自动修复
npm run lint:fix

# 类型检查
npm run type-check
```

## 📦 状态管理

使用Pinia进行状态管理：

```typescript
// stores/user.ts
export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoggedIn = computed(() => !!token.value)

  const login = async (loginData: UserLogin) => {
    // 登录逻辑
  }

  return { user, token, isLoggedIn, login }
})
```

## 🌐 API集成

```typescript
// api/request.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## 🎨 UI组件

使用Element Plus组件库：

```vue
<template>
  <el-button type="primary" @click="handleClick">
    <el-icon><Plus /></el-icon>
    添加行程
  </el-button>
</template>
```

## 📱 响应式设计

使用Element Plus的栅格系统实现响应式布局：

```vue
<el-row :gutter="20">
  <el-col :xs="24" :sm="12" :md="8" :lg="6">
    <!-- 内容 -->
  </el-col>
</el-row>
```

## 🔍 类型定义

完整的TypeScript类型支持：

```typescript
// types/index.ts
export interface User {
  id: number
  email: string
  username: string
  avatar?: string
  phone?: string
  created_at: string
  updated_at: string
}

export interface TravelPlan {
  id: number
  title: string
  destination: string
  start_date: string
  end_date: string
  budget: number
  // ...更多字段
}
```

## 🚀 构建优化

- **代码分割** - 路由级别的懒加载
- **Tree Shaking** - 自动移除未使用的代码
- **资源压缩** - 自动压缩JS、CSS和图片
- **模块化导入** - 按需导入Element Plus组件

## 🐛 常见问题

### 开发服务器启动失败
- 检查Node.js版本是否>= 16
- 清除node_modules重新安装依赖
- 检查端口是否被占用

### API请求失败
- 检查后端服务是否启动
- 验证API_BASE_URL配置是否正确
- 查看浏览器开发者工具的Network面板

### 路由跳转问题
- 检查路由配置是否正确
- 验证认证状态是否有效
- 确认路由守卫逻辑

## 📈 性能优化

- 使用Vue 3的Composition API提高组件性能
- 实现虚拟滚动处理大量数据
- 使用keep-alive缓存页面状态
- 懒加载图片和组件
- 使用CDN加速静态资源

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

MIT License

## 🔗 相关链接

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Vite 文档](https://vitejs.dev/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [TypeScript 文档](https://www.typescriptlang.org/)
