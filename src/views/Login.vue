<template>
  <div class="min-h-screen flex flex-col">
    <!-- 主体内容 -->
    <div class="flex-1 flex">
      <!-- 左侧背景 -->
      <div class="hidden lg:block lg:w-7/12 relative bg-gradient-to-br from-blue-100 to-blue-500">
        <!-- 系统名称 -->
        <div class="absolute top-8 left-8">
          <div class="flex items-center gap-2">
            <img src="@/assets/logo.svg" alt="Logo" class="w-12 h-12" />
            <div>
              <div class="text-lg font-medium text-left">中国宏观经济大数据AI预测系统</div>
              <div class="text-sm text-gray-600">China Macroeconomic Big Data AI Forecasting System</div>
            </div>
          </div>
        </div>
        
        <!-- 装饰性圆形渐变 -->
        <div class="absolute inset-0 overflow-hidden">
          <div class="absolute w-[800px] h-[800px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div class="w-full h-full bg-gradient-to-r from-blue-300 to-blue-500 rounded-full opacity-30"></div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="w-full lg:w-5/12 flex flex-col justify-center px-8 lg:px-12">
        <!-- 移动端显示的logo -->
        <div class="lg:hidden mb-8">
          <div class="flex items-center gap-2 justify-center">
            <img src="@/assets/logo.svg" alt="Logo" class="w-8 h-8" />
            <div class="text-lg font-medium">中国宏观经济大数据AI预测系统</div>
          </div>
        </div>

        <h1 class="text-2xl font-medium mb-8">登录</h1>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <input 
              type="tel"
              v-model="phone"
              placeholder="请输入11位手机号"
              class="w-full px-4 py-2 bg-gray-50 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div class="relative">
            <input 
              type="text"
              v-model="verificationCode"
              placeholder="请输入短信验证码"
              class="w-full px-4 py-2 bg-gray-50 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-28"
            />
            <button 
              type="button"
              @click="sendVerificationCode"
              class="absolute right-2 top-1/2 -translate-y-1/2 text-blue-500 hover:text-blue-600"
            >
              发送验证码
            </button>
          </div>

          <div class="text-right">
            <a href="#" class="text-sm text-gray-500 hover:text-gray-700">收不到验证码？</a>
          </div>

          <button 
            type="submit"
            class="w-full py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            登录
          </button>
        </form>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="py-4 text-center text-gray-500 text-sm">
      Copyright © 2011 — {{ new Date().getFullYear() }} China Macroeconomic Big Data AI Forecasting System. All rights reserved.
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const phone = ref('')
const verificationCode = ref('')

const sendVerificationCode = () => {
  // TODO: 实现发送验证码逻辑
  console.log('Sending verification code to:', phone.value)
}

const handleLogin = async () => {
  // TODO: 实现登录逻辑
  console.log('Login attempt:', { phone: phone.value, code: verificationCode.value })
  router.push('/')
}
</script>

<style scoped>
/* 如果需要添加自定义样式 */
</style>
