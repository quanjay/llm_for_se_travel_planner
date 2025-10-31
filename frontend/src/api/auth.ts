import api from './request'
import type { User, UserLogin, UserRegister, ApiResponse } from '@/types'

export const authApi = {
  // 用户登录
  login: (data: UserLogin): Promise<ApiResponse<{ token: string; user: User }>> => {
    return api.post('/auth/login', data)
  },

  // 用户注册
  register: (data: UserRegister): Promise<ApiResponse<{ message: string }>> => {
    return api.post('/auth/register', data)
  },

  // 获取当前用户信息
  getCurrentUser: (): Promise<ApiResponse<User>> => {
    return api.get('/auth/me')
  },

  // 刷新token
  refreshToken: (): Promise<ApiResponse<{ token: string }>> => {
    return api.post('/auth/refresh')
  },

  // 修改密码
  changePassword: (data: { old_password: string; new_password: string }): Promise<ApiResponse<{ message: string }>> => {
    return api.post('/auth/change-password', data)
  }
}