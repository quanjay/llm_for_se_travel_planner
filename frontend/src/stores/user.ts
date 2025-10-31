import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserLogin, UserRegister } from '@/types'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 方法
  const login = async (loginData: UserLogin) => {
    loading.value = true
    try {
      const response = await authApi.login(loginData)
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', response.data.token)
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const register = async (registerData: UserRegister) => {
    loading.value = true
    try {
      const response = await authApi.register(registerData)
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const getCurrentUser = async () => {
    if (!token.value) return null
    
    loading.value = true
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
      return response.data
    } catch (error) {
      // Token可能已过期，清除本地存储
      logout()
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    isLoggedIn,
    login,
    register,
    logout,
    getCurrentUser
  }
})