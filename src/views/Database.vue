<template>
  <div class="min-h-screen bg-[#F2F5F8]">
    <TheHeader />

    <!-- Subheader -->
    <div class="bg-[#348fef] py-6 px-4 border-t border-white border-opacity-10">
      <div class="container mx-auto px-10 flex items-center space-x-2">
        <arrow-down-wide-narrow class="h-5 w-5 text-gray-200" />
        <span class="text-sm text-gray-200">数据筛选</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="p-6">
        <!-- Tabs and Search -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between mb-6 bg-white rounded-lg p-4 shadow space-y-4 lg:space-y-0">
          <!-- Left Side: Tabs -->
          <div class="flex flex-wrap gap-2 lg:gap-4 w-full lg:w-auto">
            <button class="text-[#4080ff] font-medium border-b-2 border-[#4080ff] px-4 py-2">
              全部
            </button>
            <div class="relative group">
              <button 
                class="text-gray-600 hover:text-[#4080ff] px-4 py-2 flex items-center"
                @click="toggleDropdown('region')"
              >
                区域
                <ChevronDownIcon class="h-4 w-4 ml-1" />
              </button>
              <div 
                v-if="activeDropdown === 'region'"
                class="absolute z-10 mt-2 w-40 bg-white rounded-lg shadow-lg py-2 border border-gray-200"
              >
                <button 
                  v-for="region in regions" 
                  :key="region"
                  class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 hover:text-[#4080ff]"
                >
                  {{ region }}
                </button>
              </div>
            </div>
            <div class="relative group">
              <button 
                class="text-gray-600 hover:text-[#4080ff] px-4 py-2 flex items-center"
                @click="toggleDropdown('policy')"
              >
                政策
                <ChevronDownIcon class="h-4 w-4 ml-1" />
              </button>
              <div 
                v-if="activeDropdown === 'policy'"
                class="absolute z-10 mt-2 w-40 bg-white rounded-lg shadow-lg py-2 border border-gray-200"
              >
                <!-- Policy items would go here -->
              </div>
            </div>
          </div>

          <!-- Right Side: Search and Compare -->
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full lg:w-auto">
            <div class="relative flex-grow sm:flex-grow-0 sm:w-64">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索"
                @keyup.enter="handleSearch"
                :disabled="isInitialLoading || isSearching"
                class="pl-10 pr-8 py-2 w-64 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4080ff] disabled:bg-gray-100 disabled:cursor-not-allowed bg-[#F2F5F8]/50"
              />
              <div class="absolute left-3 top-1/2 transform -translate-y-1/2">
                <SearchIcon v-if="!isSearching" class="h-5 w-5 text-gray-400" />
                <svg v-else class="animate-spin h-5 w-5 text-[#4080ff]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <button 
                v-if="searchQuery && !isSearching"
                @click="clearSearch"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <XIcon class="h-4 w-4" />
              </button>
            </div>
            <button 
              @click="handleComparisonClick"
              :disabled="isInitialLoading || isSearching || (isComparisonMode && selectedCharts.length < 2)"
              :class="[
                'px-6 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors whitespace-nowrap',
                (isInitialLoading || isSearching) ? 'bg-gray-400 text-white cursor-not-allowed' :
                isComparisonMode 
                  ? 'bg-gray-400 text-white cursor-not-allowed' 
                  : 'bg-[#348FEF] text-white hover:bg-[#348FEF]/90',
                selectedCharts.length >= 2 && isComparisonMode
                  ? '!bg-[#348FEF] !cursor-pointer'
                  : ''
              ]"
            >
              <BarChartIcon class="h-5 w-5" />
              <span>{{ isComparisonLoading ? '对比中...' : '对比' }}</span>
            </button>
          </div>
        </div>

        <!-- Comparison Selection Panel -->
        <div v-if="isComparisonMode" class="mb-6 px-4 py-1 border-2 border-dashed border-gray-200 rounded-lg bg-transparent">
          <div class="flex items-center justify-between mb-4">
            <button
              @click="closeComparisonMode"
              class="text-gray-500 hover:text-gray-700 ml-auto"
            >
              <XIcon class="h-5 w-5" />
            </button>
          </div>
          <div v-if="selectedCharts.length === 0" class="flex flex-col justify-center items-center mb-6">
            <img src="@/assets/database-selection-are-chart.png" alt="选择图表" class="max-w-[80px] opacity-50" />
            <p class="text-gray-500 mt-4 font-medium">请勾选需要进行的图表</p>
          </div>
          <div v-else class="flex flex-wrap gap-3">
            <div
              v-for="item in selectedCharts"
              :key="item.id"
              class="flex flex-col items-center bg-gray-100 p-3 rounded-lg relative"
            >
              <BarChartIcon class="h-8 w-8 text-green-500 mb-2" />
              <span class="text-sm text-gray-700 text-center">{{ item.title }}</span>
              <button
                @click="removeFromComparison(item)"
                class="absolute top-1 right-1 text-gray-400 hover:text-gray-600"
              >
                <XIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

                <!-- Initial Loading State -->
        <div v-if="isInitialLoading" class="bg-white rounded-lg p-8 shadow">
          <div class="flex flex-col items-center justify-center space-y-4">
            <svg class="animate-spin h-10 w-10 text-[#4080ff]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-gray-600">正在加载数据...</p>
          </div>
        </div>

                <!-- Comparison Loading State -->
        <div v-if="isComparisonLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 flex flex-col items-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4080ff] mb-4"></div>
            <span class="text-gray-700">对比分析中...</span>
          </div>
        </div>

        <!-- No Results Message -->
        <div v-else-if="searchResults && searchResults.length === 0" class="bg-white rounded-lg p-8 shadow">
          <div class="flex flex-col items-center justify-center space-y-4">
            <div class="rounded-full bg-gray-100 p-3">
              <SearchIcon class="h-8 w-8 text-gray-400" />
            </div>
            <p class="text-gray-600">未找到匹配的结果</p>
            <button 
              @click="clearSearch"
              class="text-[#4080ff] hover:text-[#3070ff] font-medium"
            >
              返回全部图表
            </button>
          </div>
        </div>

        <!-- Charts -->
        <template v-else>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="(chart, i) in displayedCharts" 
              :key="chart.id" 
              class="bg-white shadow rounded-lg border-t border-gray-200"
            >
              <!-- 标题栏 -->
              <div class="flex flex-col p-3 rounded-t-lg">
                <!-- 标题行 -->
                <div class="flex items-center space-x-4">
                  <input
                    v-if="isComparisonMode"
                    type="checkbox"
                    :id="'chart-' + chart.id"
                    :checked="isChartSelected(chart)"
                    @change="toggleChartSelection(chart)"
                    class="w-4 h-4 text-[#4080ff] rounded border-gray-300 focus:ring-[#4080ff] bg-[#F2F5F8] bg-opacity-50"
                  />
                  <img src="@/assets/database-chart-icon.png" class="w-4 h-4" />
                  <h2 class="text-sm  max-w-[180px] sm:max-w-[200px] lg:max-w-[250px]">{{ chart.title }}</h2>
                </div>
                
                <!-- 代码和来源行 -->
                <div class="mt-2 text-sm text-mute text-gray-500 flex items-center space-x-2 sm:space-x-4">
                  <span class="text-xs">{{ chart.code }}</span>
                  <span class="text-xs text-gray-500">来源：{{ chart.source }}</span>
                </div>
              </div>

              <!-- 时间维度切换 tabs -->
              <div class="flex border-b border-gray-100 bg-[#F2F5F8] m-2 p-1 rounded-lg">
                <button 
                  v-for="tab in ['月度', '季度', '年度']" 
                  :key="tab"
                  class="flex-1 py-2 text-sm transition-all relative"
                  :class="[
                    tab === '月度' 
                      ? 'text-gray-700 bg-white rounded-lg shadow-[0_-2px_4px_rgba(0,0,0,0.05)] font-medium' 
                      : 'text-gray-600 hover:text-gray-700'
                  ]"
                >
                  <span class="relative z-10">{{ tab }}</span>
                  <!-- 活跃状态下的白色背景延伸遮挡下方边框 -->
                  <!-- 这里的白色背景条是为了遮挡tab下方的灰色边框,使active状态的tab看起来更加突出和连贯
                  <div 
                    v-if="tab === '月度'" 
                    class="absolute bottom-0 left-0 right-0 h-[1px] bg-white"
                  ></div> -->
                </button>
              </div>

              <!-- 图表区域 -->
              <div class="h-[360px] w-full">
                <v-chart class="chart" :option="chart.option" autoresize />
              </div>

              <!-- 预测按钮 -->
              <div class="p-6 border-t border-gray-100">
                <button 
                  class="w-full py-2 bg-white border border-[#348FEF] text-[#348FEF] font-medium rounded-lg hover:bg-[#348FEF] hover:text-white transition-colors text-sm"
                >
                  预测次季数据
                </button>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex flex-col sm:flex-row justify-between items-center bg-white p-4 rounded-lg shadow mt-6 space-y-4 sm:space-y-0">
            <!-- 显示条数信息 -->
            <div class="text-sm text-gray-700 w-full sm:w-auto text-center sm:text-left">
              显示 {{ ((currentPage - 1) * pageSize) + 1 }} - {{ Math.min(currentPage * pageSize, totalCharts) }} 条，共 {{ totalCharts }} 条
            </div>

            <!-- 分页控制区 -->
            <div class="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-2 w-full sm:w-auto">
              <!-- 页码导航 -->
              <div class="flex items-center space-x-2 w-full sm:w-auto justify-center">
                <!-- 上一页按钮 -->
                <button 
                  @click="handlePageChange(currentPage - 1)"
                  :disabled="currentPage === 1 || isPageLoading"
                  class="px-2 sm:px-3 py-1 rounded-lg flex items-center space-x-1 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  :class="[
                    isPageLoading ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
                  ]"
                >
                  <span>上一页</span>
                  <span v-if="isPageLoading" class="w-4 h-4 border-2 border-gray-300 border-t-[#4080ff] rounded-full animate-spin"></span>
                </button>
                
                <!-- 页码按钮 - 在移动端隐藏部分页码 -->
                <div class="hidden sm:flex space-x-1">
                  <template v-for="page in displayedPages" :key="page">
                    <button
                      v-if="page !== '...'"
                      @click="handlePageChange(page)"
                      :disabled="isPageLoading || currentPage === page"
                      :class="[
                        'w-8 h-8 rounded-lg relative',
                        currentPage === page
                          ? 'bg-[#348FEF] text-white'
                          : isPageLoading 
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-white text-gray-700 hover:bg-gray-50'
                      ]"
                    >
                      {{ page }}
                      <span 
                        v-if="isPageLoading && currentPage === page" 
                        class="absolute inset-0 flex items-center justify-center"
                      >
                        <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      </span>
                    </button>
                    <span 
                      v-else 
                      class="w-8 h-8 flex items-center justify-center text-gray-400"
                    >
                      ...
                    </span>
                  </template>
                </div>
                
                <!-- 移动端简化的页码显示 -->
                <div class="flex sm:hidden items-center space-x-2">
                  <span class="text-sm text-gray-600">{{ currentPage }}/{{ totalPages }}</span>
                </div>

                <!-- 下一页按钮 -->
                <button 
                  @click="handlePageChange(currentPage + 1)"
                  :disabled="currentPage === totalPages || isPageLoading"
                  class="px-2 sm:px-3 py-1 rounded-lg flex items-center space-x-1 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  :class="[
                    isPageLoading ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
                  ]"
                >
                  <span>下一页</span>
                  <span v-if="isPageLoading" class="w-4 h-4 border-2 border-gray-300 border-t-[#4080ff] rounded-full animate-spin"></span>
                </button>
              </div>

              <!-- 跳转区域 -->
              <div class="flex items-center space-x-2 w-full sm:w-auto justify-center">
                <input 
                  v-model="jumpPage"
                  type="number"
                  placeholder="页码"
                  :disabled="isPageLoading"
                  @keyup.enter="handlePageJump"
                  class="w-16 h-8 pl-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4080ff] bg-[#F2F5F8]/50 disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
                />
                <button 
                  @click="handlePageJump"
                  :disabled="isPageLoading"
                  class="px-3 py-1 rounded-lg transition-colors text-sm"
                  :class="[
                    isPageLoading 
                      ? 'bg-gray-400 text-white cursor-not-allowed' 
                      : 'bg-[#348FEF] text-white hover:bg-[#348FEF]/90'
                  ]"
                >
                  跳转
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>
    <TheFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, DataZoomComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import axios from 'axios'

import { 
  HomeIcon, 
  ArrowDownWideNarrow, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  XIcon
} from 'lucide-vue-next'

const router = useRouter()

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
])

// 注册 VChart 组件
const chart = VChart

// 状态定义
const isLoading = ref(false)
const isInitialLoading = ref(true)
const isSearching = ref(false)
const searchQuery = ref('')
const activeDropdown = ref(null)
const searchResults = ref(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)

// 图表数据
const charts = ref([])
const selectedCharts = ref([])
const isComparisonMode = ref(false)

// 修改API基础URL
const API_BASE_URL = 'http://120.48.150.254:8888'

// 添加新的状态变量
const isPageLoading = ref(false)  // 分页加载状态
const isComparisonLoading = ref(false)

// 修改 fetchChartData 函数
async function fetchChartData() {
  console.log('fetchChartData called with page:', currentPage.value)
  
  try {
    console.log('Making API request with params:', {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value
    })
    
    const response = await axios.get(`${API_BASE_URL}/api/chart-data`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value || undefined
      }
    })
    
    console.log('API response received:', response.data)
    
    // 更新数据
    const { data, total: totalCount } = response.data
    
    // 将后端数据转换为图表格式
    charts.value = data.map(item => ({
      id: item.id,
      title: item.title,
      source: item.code,
      code: item.code,
      option: generateChartOption({
        name: item.title,
        unit: '',
        time: item.times,
        data: item.values
      })
    }))
    
    total.value = totalCount
    
    if (isInitialLoading.value) {
      isInitialLoading.value = false
    }
  } catch (error) {
    console.error('Failed to fetch chart data:', error)
    throw error // 向上抛出错误
  }
}

// 生命周期
onMounted(() => {
  fetchChartData() // 直接调用API获取数据
})

// 计算属性
const totalCharts = computed(() => total.value)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const displayedPages = computed(() => {
  const pages = []
  const maxVisiblePages = 7
  
  if (totalPages.value <= maxVisiblePages) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)
    
    if (currentPage.value > 3) {
      pages.push('...')
    }
    
    const start = Math.max(2, currentPage.value - 1)
    const end = Math.min(totalPages.value - 1, currentPage.value + 1)
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    
    if (currentPage.value < totalPages.value - 2) {
      pages.push('...')
    }
    
    pages.push(totalPages.value)
  }
  
  return pages
})

const displayedCharts = computed(() => charts.value)

// 加载更多数据
function loadMore() {
  if (currentPage.value * pageSize.value < totalCharts.value) {
    currentPage.value++
  }
}

function toggleComparisonMode() {
  isComparisonMode.value = !isComparisonMode.value
  if (!isComparisonMode.value) {
    selectedCharts.value = []
  }
}

function closeComparisonMode() {
  isComparisonMode.value = false
  selectedCharts.value = []
}

function toggleChartSelection(chart) {
  const index = selectedCharts.value.findIndex(c => c.id === chart.id)
  if (index === -1) {
    selectedCharts.value.push(chart)
  } else {
    selectedCharts.value.splice(index, 1)
  }
}

function isChartSelected(chart) {
  return selectedCharts.value.some(c => c.id === chart.id)
}

function removeFromComparison(chart) {
  const index = selectedCharts.value.findIndex(c => c.id === chart.id)
  if (index !== -1) {
    selectedCharts.value.splice(index, 1)
  }
}

// 修改 handleComparisonClick 函数
async function handleComparisonClick() {
  if (!isComparisonMode.value) {
    toggleComparisonMode()
    return
  }
  
  if (selectedCharts.value.length >= 2) {
    try {
      isComparisonLoading.value = true
      
      // 保存选中的图表数据到 sessionStorage
      if (!saveSelectedChartsToCache(selectedCharts.value)) {
        throw new Error('保存图表数据失败')
      }

      // 导航���分析结果页面
      await router.push({
        name: 'analysis-result',
        query: {
          charts: selectedCharts.value.map(chart => chart.id).join(',')
        }
      })
    } catch (error) {
      console.error('对比失败:', error)
    } finally {
      isComparisonLoading.value = false
      closeComparisonMode()
    }
  }
}

// 添加 saveSelectedChartsToCache 函数
const saveSelectedChartsToCache = (charts) => {
  try {
    // 清理之前的数据
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i)
      if (key.startsWith('selectedChart')) {
        sessionStorage.removeItem(key)
      }
    }

    // 保存图表基本信息
    const chartMeta = charts.map(chart => ({
      id: chart.id,
      name: chart.title
    }))
    sessionStorage.setItem('selectedChartMeta', JSON.stringify(chartMeta))

    // 分块保存完整的图表数据
    const chunkSize = 2
    const chartData = charts.map(chart => ({
      id: chart.id,
      time: chart.option.xAxis.data,
      data: chart.option.series[0].data
    }))

    for (let i = 0; i < chartData.length; i += chunkSize) {
      const chunk = chartData.slice(i, i + chunkSize)
      try {
        sessionStorage.setItem(`selectedChartData_${Math.floor(i / chunkSize)}`, JSON.stringify(chunk))
      } catch (e) {
        console.error(`保存数据块 ${i} 失败:`, e)
        return false
      }
    }

    // 保存块数量
    sessionStorage.setItem('selectedChartChunks', Math.ceil(chartData.length / chunkSize))
    return true
  } catch (error) {
    console.error('保存选中图表数据失败:', error)
    return false
  }
}

const toggleDropdown = (dropdown) => {
  if (activeDropdown.value === dropdown) {
    activeDropdown.value = null
  } else {
    activeDropdown.value = dropdown
  }
}

// 修改 handleSearch 函数
async function handleSearch() {
  if (!searchQuery.value.trim()) {
    clearSearch()
    return
  }
  
  isSearching.value = true
  try {
    // 调用后端API进行搜索
    const response = await axios.get(`${API_BASE_URL}/api/chart-data`, {
      params: {
        page: 1, // 搜索时重置到第一页
        page_size: pageSize.value,
        search: searchQuery.value
      }
    })
    
    const { data, total: totalCount } = response.data
    
    // 更新图表数据和总数
    charts.value = data.map(item => ({
      id: item.id,
      title: item.title,
      source: item.code,
      code: item.code,
      option: generateChartOption({
        name: item.title,
        unit: '',
        time: item.times,
        data: item.values
      })
    }))
    
    total.value = totalCount
    currentPage.value = 1 // 重置到第一页
    
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    isSearching.value = false
  }
}

// 修改 clearSearch 函数
async function clearSearch() {
  // 如果正在搜索或加载中，直接返回
  if (isSearching.value || isInitialLoading.value) return
  
  isSearching.value = true
  try {
    searchQuery.value = ''  // 清空搜索框
    currentPage.value = 1   // 重置页码
    
    // 清空搜索时重新获取所有数据
    const response = await axios.get(`${API_BASE_URL}/api/chart-data`, {
      params: {
        page: 1,
        page_size: pageSize.value
      }
    })
    
    const { data, total: totalCount } = response.data
    
    // 更新图表数据和总数
    charts.value = data.map(item => ({
      id: item.id,
      title: item.title,
      source: item.code,
      code: item.code,
      option: generateChartOption({
        name: item.title,
        unit: '',
        time: item.times,
        data: item.values
      })
    }))
    
    total.value = totalCount
    
  } catch (error) {
    console.error('清空搜索失败:', error)
  } finally {
    isSearching.value = false
  }
}

// 处理页码跳转
async function handlePageJump() {
  if (isPageLoading.value) return
  
  const page = parseInt(jumpPage.value)
  if (page && page >= 1 && page <= totalPages.value) {
    await handlePageChange(page)
  }
  jumpPage.value = ''
}

// 修改 generateChartOption 函数
function generateChartOption({ name, unit, time, data }) {
  const validDataPoints = data.map((value, index) => ({ value, index }))
    .filter(item => item.value !== null && item.value !== undefined && item.value !== '')
  
  if (validDataPoints.length === 0) {
    return {
      graphic: {
        type: 'text',
        left: 'center',
        top: 'middle',
        style: {
          text: '暂无数据',
          fontSize: 14,
          fill: '#999'
        }
      }
    }
  }

  const startIndex = validDataPoints[0].index
  const endIndex = validDataPoints[validDataPoints.length - 1].index
  
  const filteredTime = time.slice(startIndex, endIndex + 1)
  const filteredData = data.slice(startIndex, endIndex + 1)

  return {
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        const value = params[0].value === null ? '暂无数据' : params[0].value
        return `${params[0].axisValue}<br/>${value}`
      }
    },
    xAxis: {
      type: 'category',
      data: filteredTime,
      axisLabel: {
        rotate: 45,
        fontSize: 9,
        margin: 14
      }
    },
    yAxis: {
      type: 'value',
      name: unit,
      nameTextStyle: {
        fontSize: 10
      },
      axisLabel: {
        formatter: '{value}',
        fontSize: 10
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#eee',
          type: 'dashed'
        }
      },
      min: function(value) {
        const minValue = value.min + (value.max - value.min) * 0.3;
        return Math.floor(minValue);  // 向下取整
      },
      max: function(value) {
        const maxValue = value.max + (value.max - value.min) * 0.3;
        return Math.ceil(maxValue);   // 向上取整
      }
    },
    series: [{
      name: name,
      data: filteredData,
      type: 'line',
      smooth: true,
      showSymbol: false,
      connectNulls: true,
      areaStyle: {
        opacity: 0.6,
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, 
            color: 'rgba(52, 143, 239, 0.2)'
          }, {
            offset: 1, 
            color: 'rgba(52, 143, 239, 0)'
          }],
        }
      },
      itemStyle: {
        color: '#348FEF'
      },
      lineStyle: {
        width: 1.5,
        color: '#348FEF'
      }
    }],
    grid: {
      left: '8%',
      right: '8%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100
      }
    ]
  }
}

onUnmounted(() => {
  document.removeEventListener('click', (e) => {
    if (!e.target.closest('.group')) {
      activeDropdown.value = null
    }
  })
})

// 添加新的方法来处理分页变化
async function handlePageChange(newPage) {
  console.log('handlePageChange called with page:', newPage)
  console.log('Current loading state:', isPageLoading.value)
  
  // 如果正在加载或页码无效,直接返回
  if (isPageLoading.value || newPage < 1 || newPage > totalPages.value) {
    console.log('Page change rejected - loading or invalid page')
    return
  }
  
  try {
    console.log('Starting page change to:', newPage)
    isPageLoading.value = true
    currentPage.value = newPage
    await fetchChartData()
  } catch (error) {
    console.error('Failed to change page:', error)
  } finally {
    isPageLoading.value = false 
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.chart {
  height: 100%;
  width: 100%;
}
</style>
