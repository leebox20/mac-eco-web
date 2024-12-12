<template>
  <nav :style="headerStyle" class="nav-base">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 shadow">
      <div class="flex justify-between h-20">
        <div class="flex items-center">
          <div class="flex-shrink-0 flex items-center">
            <img :src="logoImg" alt="Logo" class="h-20">
          </div>
        </div>

        <div class="flex md:hidden items-center">
          <button @click="isOpen = !isOpen" class="text-white">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="!isOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              <path v-if="isOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="hidden md:flex items-center space-x-8">
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
              <img :src="menuLoginImg" alt="" class="w-4 h-4">
            </router-link>
          </router-link>
        </div>
      </div>

      <div v-show="isOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="block px-3 py-2 text-white text-sm"
            :class="{
              'opacity-100': $route.path === item.path,
              'opacity-60': $route.path !== item.path
            }"
            @click="isOpen = false"
          >
            <div class="flex items-center">
              <img :src="item.icon" alt="" class="w-5 h-5 mr-2">
              {{ item.label }}
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import logoImg from '../assets/logo.png'
import menuHomeImg from '../assets/menu-home.png'
import menuRobotImg from '../assets/menu-robot.png'
import menuChartImg from '../assets/menu-chart.png'
import menuUserImg from '../assets/menu-user.png'
import menuLoginImg from '../assets/menu-login.png'
import headerBgImg from '../assets/home-header-bg.png'
import { computed, ref } from 'vue'

const headerStyle = computed(() => ({
  backgroundColor: '#348fef',
  backgroundImage: `url(${headerBgImg})`,
  backgroundSize: 'contain',
  backgroundPosition: 'left center',
  backgroundRepeat: 'no-repeat'
}))

const menuItems = [
  {
    path: '/',
    icon: menuHomeImg,
    label: '首页'
  },
  {
    path: '/ai-assistant',
    icon: menuRobotImg,
    label: 'AI智能助手'
  },
  {
    path: '/database',
    icon: menuChartImg,
    label: '数据库'
  },
  {
    path: '/prediction',
    icon: menuChartImg,
    label: '宏观预测'
  },
  {
    path: '/login',
    icon: menuUserImg,
    label: '社科小智',
    hasLoginArrow: true
  }
]

const isOpen = ref(false)
</script>

<style scoped>
.nav-base {
  position: relative;
}
</style> 