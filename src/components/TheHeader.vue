<template>
  <nav class="nav-bg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 shadow">
      <div class="flex justify-between h-20">
        <div class="flex items-center">
          <div class="flex-shrink-0 flex items-center">
            <img src="@/assets/logo.png" alt="Logo" class="h-20">
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
            <img :src="item.icon" alt="" class="w-5 h-5 mr-2">
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
              <img src="/src/assets/menu-login.png" alt="" class="w-4 h-4">
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
    icon: '/src/assets/menu-home.png',
    label: '首页'
  },
  {
    path: '/ai-assistant',
    icon: '/src/assets/menu-robot.png',
    label: 'AI智能助手'
  },
  {
    path: '/database',
    icon: '/src/assets/menu-chart.png',
    label: '数据库'
  },
  {
    path: '/login',
    icon: '/src/assets/menu-user.png',
    label: '社科小智',
    hasLoginArrow: true
  }
]
</script>

<style scoped>
.nav-bg {
  background-color: #348fef;
  background-image: url('/src/assets/home-header-bg.png');
  background-size: contain;
  background-position: left center;
  background-repeat: no-repeat;
}
/* 移除之前的router-link-active样式，现在使用动态class控制 */
</style> 