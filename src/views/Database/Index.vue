<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <router-link to="/" class="text-xl font-bold text-primary">Macro-Eco</router-link>
            </div>
            <!-- 桌面端导航 -->
            <div class="hidden md:ml-6 md:flex md:space-x-8">
              <router-link 
                to="/" 
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                首页
              </router-link>
              <router-link 
                to="/database" 
                class="border-primary text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                数据库
              </router-link>
            </div>
          </div>

          <!-- 移动端菜单按钮 -->
          <div class="flex items-center md:hidden">
            <button 
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
            >
              <span class="sr-only">打开菜单</span>
              <!-- 菜单图标 -->
              <svg 
                class="h-6 w-6" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  v-if="!mobileMenuOpen" 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path 
                  v-else 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 移动端菜单 -->
      <div 
        v-show="mobileMenuOpen" 
        class="md:hidden"
      >
        <div class="pt-2 pb-3 space-y-1">
          <router-link 
            to="/" 
            class="border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          >
            首页
          </router-link>
          <router-link 
            to="/database" 
            class="bg-primary bg-opacity-50 text-white block pl-3 pr-4 py-2 border-l-4 border-primary text-base font-medium"
          >
            数据库
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="py-6">
        <div class="flex flex-col lg:flex-row gap-6">
          <!-- 筛选面板 -->
          <div class="w-full lg:w-64 lg:flex-shrink-0">
            <!-- 移动端筛选按钮 -->
            <div class="lg:hidden mb-4">
              <button 
                @click="filterPanelOpen = !filterPanelOpen"
                class="w-full flex items-center justify-between px-4 py-2 border rounded-lg bg-white shadow-sm"
              >
                <span class="text-sm font-medium text-gray-700">筛选条件</span>
                <svg 
                  class="h-5 w-5 text-gray-500"
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path 
                    v-if="!filterPanelOpen"
                    fill-rule="evenodd" 
                    d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" 
                    clip-rule="evenodd"
                  />
                  <path 
                    v-else
                    fill-rule="evenodd" 
                    d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" 
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>

            <!-- 筛选面板内容 -->
            <div 
              :class="{'hidden': !filterPanelOpen && !isLargeScreen}"
              class="card"
            >
              <h3 class="text-lg font-medium text-gray-900 mb-4">筛选条件</h3>
              <div class="space-y-4">
                <!-- 时间范围 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700">时间范围</label>
                  <select 
                    v-model="store.filters.timeRange"
                    @change="store.updateFilters({ timeRange: $event.target.value })"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
                  >
                    <option>最近一年</option>
                    <option>最近三年</option>
                    <option>最近五年</option>
                    <option>自定义</option>
                  </select>
                </div>
                <!-- 指标类型 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700">指标类型</label>
                  <div class="mt-2 space-y-2">
                    <label class="inline-flex items-center">
                      <input 
                        type="checkbox" 
                        :checked="store.filters.indicators.includes('GDP')"
                        @change="toggleIndicator('GDP')"
                        class="rounded border-gray-300 text-primary focus:ring-primary"
                      >
                      <span class="ml-2 text-sm text-gray-600">GDP</span>
                    </label>
                    <label class="inline-flex items-center">
                      <input 
                        type="checkbox"
                        :checked="store.filters.indicators.includes('CPI')"
                        @change="toggleIndicator('CPI')"
                        class="rounded border-gray-300 text-primary focus:ring-primary"
                      >
                      <span class="ml-2 text-sm text-gray-600">CPI</span>
                    </label>
                    <label class="inline-flex items-center">
                      <input 
                        type="checkbox"
                        :checked="store.filters.indicators.includes('失业率')"
                        @change="toggleIndicator('失业率')"
                        class="rounded border-gray-300 text-primary focus:ring-primary"
                      >
                      <span class="ml-2 text-sm text-gray-600">失业率</span>
                    </label>
                  </div>
                </div>
                <!-- 地区 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700">地区</label>
                  <select 
                    v-model="store.filters.region"
                    @change="store.updateFilters({ region: $event.target.value })"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
                  >
                    <option>全球</option>
                    <option>中国</option>
                    <option>美国</option>
                    <option>欧盟</option>
                  </select>
                </div>
              </div>
              <div class="mt-6">
                <button @click="store.fetchData()" class="btn-primary w-full">应用筛选</button>
              </div>
            </div>
          </div>

          <!-- 数据展示 -->
          <div class="flex-1">
            <div class="card">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                <h2 class="text-lg font-medium text-gray-900">数据列表</h2>
                <div class="flex flex-wrap gap-2">
                  <button class="btn-primary">导出数据</button>
                  <button class="btn-primary">数据分析</button>
                </div>
              </div>
              <!-- 数据表格 -->
              <div class="overflow-x-auto -mx-4 sm:mx-0">
                <div class="inline-block min-w-full align-middle">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">指标</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">地区</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数值</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">同比</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <template v-if="!store.loading">
                        <tr v-for="item in store.data" :key="item.time">
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.indicator }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.region }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.time }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.value }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm" :class="item.yoy.startsWith('+') ? 'text-green-600' : 'text-red-600'">
                            {{ item.yoy }}
                          </td>
                        </tr>
                      </template>
                      <tr v-else>
                        <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">
                          加载中...
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <!-- 分页 -->
              <div class="mt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="text-sm text-gray-700 w-full sm:w-auto text-center sm:text-left">
                  显示 {{ (store.currentPage - 1) * store.itemsPerPage + 1 }} - {{ Math.min(store.currentPage * store.itemsPerPage, store.totalPages * store.itemsPerPage) }} 条，
                  共 {{ store.totalPages * store.itemsPerPage }} 条
                </div>
                <div class="flex gap-2 w-full sm:w-auto justify-center">
                  <button 
                    @click="store.setPage(store.currentPage - 1)"
                    :disabled="store.currentPage === 1"
                    class="px-3 py-1 border rounded text-sm"
                    :class="{ 'opacity-50 cursor-not-allowed': store.currentPage === 1 }"
                  >
                    上一页
                  </button>
                  <button 
                    v-for="page in store.totalPages"
                    :key="page"
                    @click="store.setPage(page)"
                    class="px-3 py-1 border rounded text-sm"
                    :class="{ 'bg-primary text-white': store.currentPage === page }"
                  >
                    {{ page }}
                  </button>
                  <button 
                    @click="store.setPage(store.currentPage + 1)"
                    :disabled="store.currentPage === store.totalPages"
                    class="px-3 py-1 border rounded text-sm"
                    :class="{ 'opacity-50 cursor-not-allowed': store.currentPage === store.totalPages }"
                  >
                    下一页
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeMount } from 'vue'
import { useDatabaseStore } from '../../stores/database'

const store = useDatabaseStore()
const mobileMenuOpen = ref(false)
const filterPanelOpen = ref(false)
const isLargeScreen = ref(false)

const toggleIndicator = (indicator) => {
  const indicators = new Set(store.filters.indicators)
  if (indicators.has(indicator)) {
    indicators.delete(indicator)
  } else {
    indicators.add(indicator)
  }
  store.updateFilters({ indicators: Array.from(indicators) })
}

const checkScreenSize = () => {
  isLargeScreen.value = window.innerWidth >= 1024 // lg breakpoint
  if (isLargeScreen.value) {
    filterPanelOpen.value = true
  }
}

onBeforeMount(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onMounted(() => {
  store.fetchData()
})
</script>
