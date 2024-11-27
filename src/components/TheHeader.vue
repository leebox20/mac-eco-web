<template>
  <nav class="bg-primary ">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 shadow">
      <div class="flex justify-between h-20">
        <div class="flex items-center">
          <div class="flex-shrink-0 flex items-center">
            <img src="@/assets/logo.svg" alt="Logo" class="h-10 custom-italic">
            <div class="ml-2 text-left">
              <div class="text-white text-lg custom-italic">中国宏观经济大数据AI预测系统</div>
              <div class="text-white text-sm opacity-75">China Macroeconomic Big Data AI Forecasting System</div>
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-8">
          <router-link
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="inline-flex items-center px-4 py-3 text-sm text-white transition-opacity duration-200"
            :class="{ 
              'opacity-100': $route.path === item.path,
              'opacity-60 hover:text-white hover:opacity-100': $route.path !== item.path
            }"
          >
            <i :class="[item.icon, 'mr-2']"></i>
            {{ item.label }}
            
            <!-- 登录箭头 -->
            <router-link
              v-if="item.hasLoginArrow"
              to="/login"
              class="ml-2 text-white transition-opacity duration-200"
              :class="{ 
                'opacity-100': $route.path === '/login', 
                'opacity-60 hover:text-white hover:opacity-100': $route.path !== '/login' 
              }"
            >
              <i class="fas fa-arrow-right"></i>
            </router-link>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
const menuItems = [
  {
    path: '/',
    icon: 'fas fa-home',
    label: '首页'
  },
  {
    path: '/ai-assistant',
    icon: 'fas fa-robot',
    label: 'AI智能助手'
  },
  {
    path: '/database',
    icon: 'fas fa-database',
    label: '数据库'
  },
  {
    path: '/login',
    icon: 'fas fa-brain',
    label: '社科小智',
    hasLoginArrow: true
  }
]
</script>

<style scoped>
/* 移除之前的router-link-active样式，现在使用动态class控制 */
</style> 