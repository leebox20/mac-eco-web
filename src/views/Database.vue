<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />

    <!-- Subheader -->
    <div class="bg-[#4080ff]  py-6 px-4 border-t border-gray-400 border-capacity-40">
      <div class="container mx-auto px-10 flex items-center space-x-2 ">
        <arrow-down-wide-narrow class="h-5 w-5 text-gray-200" />
        <span class="text-sm text-gray-200">数据筛选</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="p-6">
        <!-- Tabs and Search -->
        <div class="flex items-center justify-between mb-6 bg-white rounded-lg p-4 shadow">
          <div class="flex space-x-4">
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
          <div class="flex items-center space-x-4">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索"
                @keyup.enter="handleSearch"
                :disabled="isLoading || isSearching"
                class="pl-10 pr-8 py-2 w-64 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4080ff] disabled:bg-gray-100 disabled:cursor-not-allowed"
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
              :disabled="isLoading || isSearching || (isComparisonMode && selectedCharts.length < 2)"
              :class="[
                'px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors',
                (isLoading || isSearching) ? 'bg-gray-400 text-white cursor-not-allowed' :
                isComparisonMode 
                  ? 'bg-gray-400 text-white cursor-not-allowed' 
                  : 'bg-[#4080ff] text-white hover:bg-[#3070ff]',
                selectedCharts.length >= 2 && isComparisonMode
                  ? '!bg-[#4080ff] !cursor-pointer'
                  : ''
              ]"
            >
              <BarChartIcon class="h-5 w-5" />
              <span>{{ isLoading ? '对比中...' : '对比' }}</span>
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="bg-white rounded-lg p-8 text-center">
          <div class="flex flex-col items-center justify-center space-y-4">
            <svg class="animate-spin h-10 w-10 text-[#4080ff]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-gray-600">正在加载数据...</p>
          </div>
        </div>

        <!-- Chart Section -->
        <div v-else class="space-y-6" ref="containerRef">
          <div 
            v-for="(chart, i) in displayedCharts" 
            :key="chart.id" 
            class="bg-white shadow rounded-lg border-t border-gray-200 rounded-lg"
          >
            <div class="flex items-center justify-between bg-gray-50  p-3 rounded-lg ">
              <div class="flex items-center space-x-4">
                <input
                  v-if="isComparisonMode"
                  type="checkbox"
                  :id="'chart-' + chart.id"
                  :checked="isChartSelected(chart)"
                  @change="toggleChartSelection(chart)"
                  class="w-4 h-4 text-[#4080ff] rounded border-gray-300 focus:ring-[#4080ff]"
                />
                <h2 class="text-sm">{{ chart.title }}</h2>
              </div>
              <div class="text-sm text-mute flex items-center space-x-4">
                <span>来源：{{ chart.source }}</span>
                <span>{{ chart.code }}</span>
              </div>
            </div>
            <div class="h-80 w-full border-t border-gray-200">
              <v-chart class="chart" :option="chart.option" autoresize />
            </div>
          </div>

          <!-- Pagination -->
          <div class="flex justify-between items-center bg-white p-4 rounded-lg shadow mt-6">
            <div class="text-sm text-gray-700">
              显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalCharts) }} 条，共 {{ totalCharts }} 条
            </div>
            <div class="flex items-center space-x-2">
              <button 
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage === 1"
                :class="[
                  'px-3 py-1 rounded-lg',
                  currentPage === 1 
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                ]"
              >
                上一页
              </button>
              
              <div class="flex space-x-1">
                <template v-for="page in displayedPages" :key="page">
                  <button
                    v-if="page !== '...'"
                    @click="currentPage = page"
                    :class="[
                      'w-8 h-8 rounded-lg',
                      currentPage === page
                        ? 'bg-[#4080ff] text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    ]"
                  >
                    {{ page }}
                  </button>
                  <span 
                    v-else 
                    class="w-8 h-8 flex items-center justify-center text-gray-400"
                  >
                    ...
                  </span>
                </template>
              </div>

              <button 
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
                :class="[
                  'px-3 py-1 rounded-lg',
                  currentPage === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                ]"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
    <TheFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { 
  HomeIcon, 
  ArrowDownWideNarrow, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  XIcon
} from 'lucide-vue-next'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
])

// State
const isComparisonMode = ref(false)
const selectedCharts = ref([])
const isLoading = ref(false)
const isSearching = ref(false)
const activeDropdown = ref(null)
const regions = ref(['北京', '上海', '四川', '云南', '湖北', '贵州'])
const charts = ref([])
const pageSize = 10
const currentPage = ref(1)
const totalCharts = ref(0)
const searchQuery = ref('')
const searchResults = ref(null)
const containerRef = ref(null)

// 分页相关计算属性
const totalPages = computed(() => {
  const total = searchResults.value 
    ? searchResults.value.length 
    : totalCharts.value
  return Math.ceil(total / pageSize)
})

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

// 虚拟列表相关
const displayedCharts = computed(() => {
  const data = searchResults.value || charts.value
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return data.slice(start, end)
})

// 缓存相关函数
function saveToCache(rawData) {
  try {
    const { indicators, timeData, values } = rawData
    localStorage.setItem('chartMetadata', JSON.stringify({
      timestamp: Date.now(),
      indicators,
      timeData
    }))
    
    // 将数值数据分块存储，减小每块的大小
    const chunkSize = 5 // 减小到每块5个指标
    for (let i = 0; i < indicators.length; i += chunkSize) {
      const chunk = {}
      for (let j = i; j < Math.min(i + chunkSize, indicators.length); j++) {
        // 只存储必要的数据，移除null值
        chunk[j] = values[j].filter(v => v !== null)
      }
      try {
        localStorage.setItem(`chartValues_${i}`, JSON.stringify(chunk))
      } catch (e) {
        console.warn(`无法存储数据块 ${i}, 跳过缓存`)
        return false
      }
    }
    return true
  } catch (error) {
    console.warn('缓存存储失败:', error)
    clearCache()
    return false
  }
}

function loadFromCache() {
  try {
    const metadata = localStorage.getItem('chartMetadata')
    if (!metadata) return null
    
    const { timestamp, indicators, timeData } = JSON.parse(metadata)
    if (Date.now() - timestamp > 3600000) {
      clearCache()
      return null
    }
    
    const values = {}
    for (let i = 0; i < indicators.length; i += 5) { // 使用相同的块大小
      const chunk = localStorage.getItem(`chartValues_${i}`)
      if (!chunk) {
        clearCache()
        return null
      }
      Object.assign(values, JSON.parse(chunk))
    }
    
    // 恢复完整的数据数组，包括null值
    indicators.forEach((_, index) => {
      if (values[index]) {
        const fullData = new Array(timeData.length).fill(null)
        let valueIndex = 0
        for (let i = 0; i < timeData.length && valueIndex < values[index].length; i++) {
          if (values[index][valueIndex] !== null) {
            fullData[i] = values[index][valueIndex]
            valueIndex++
          }
        }
        values[index] = fullData
      }
    })
    
    return { indicators, timeData, values }
  } catch (error) {
    console.warn('缓存加载失败:', error)
    clearCache()
    return null
  }
}

function clearCache() {
  try {
    const metadata = localStorage.getItem('chartMetadata')
    if (metadata) {
      const { indicators } = JSON.parse(metadata)
      for (let i = 0; i < indicators.length; i += 5) {
        localStorage.removeItem(`chartValues_${i}`)
      }
    }
    localStorage.removeItem('chartMetadata')
  } catch (error) {
    console.warn('缓存清理失败:', error)
  }
}

// Methods
async function loadCSVData() {
  isLoading.value = true
  try {
    // 尝试从缓存加载
    const cachedData = loadFromCache()
    if (cachedData) {
      const { indicators, timeData, values } = cachedData
      // 生成图表配置
      charts.value = indicators.map((indicator, index) => {
        if (!indicator || !values[index]) {
          return null
        }
        
        return {
          id: index + 1,
          title: indicator,
          source: '数据来源：DATALF',
          code: `indicator_${index + 1}`,
          option: generateChartOption({
            name: indicator,
            unit: '',
            time: timeData,
            data: values[index]
          })
        }
      }).filter(Boolean)
      
      totalCharts.value = charts.value.length
      return
    }

    const response = await fetch('/src/assets/DATALF-20241103 - DAY.csv')
    const csvText = await response.text()
    
    const rows = csvText.replace(/^\ufeff/, '').split('\n')
      .map(row => row.trim())
      .filter(row => row.length > 0)
      .map(row => {
        const cells = []
        let cell = ''
        let inQuotes = false
        
        for (let i = 0; i < row.length; i++) {
          const char = row[i]
          if (char === '"') {
            inQuotes = !inQuotes
          } else if (char === ',' && !inQuotes) {
            cells.push(cell.trim())
            cell = ''
          } else {
            cell += char
          }
        }
        cells.push(cell.trim())
        return cells
      })

    if (rows.length < 2) {
      throw new Error('CSV 数据格式不正确：需要至少包含标题行和一行数据')
    }

    const indicators = rows[0].slice(1).filter(Boolean)
    
    const timeData = []
    const values = {}
    
    indicators.forEach((_, index) => {
      values[index] = []
    })
    
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i]
      if (!row[0]) continue
      
      timeData.push(row[0])
      
      for (let j = 1; j <= indicators.length; j++) {
        let value = null
        if (row[j]) {
          const cleanValue = row[j].replace(/[^\d.-]/g, '')
          value = cleanValue ? parseFloat(cleanValue) : null
          if (isNaN(value)) value = null
        }
        if (values[j-1]) {
          values[j-1].push(value)
        }
      }
    }

    saveToCache({ indicators, timeData, values })
    
    charts.value = indicators.map((indicator, index) => {
      if (!indicator || !values[index]) {
        return null
      }
      
      return {
        id: index + 1,
        title: indicator,
        source: '数据来源：DATALF',
        code: `indicator_${index + 1}`,
        option: generateChartOption({
          name: indicator,
          unit: '',
          time: timeData,
          data: values[index]
        })
      }
    }).filter(Boolean)

    totalCharts.value = charts.value.length
    console.log('成功加载了', charts.value.length, '个图表')
  } catch (error) {
    console.error('加载CSV数据失败:', error)
    alert('数据加载失败：' + error.message)
  } finally {
    isLoading.value = false
  }
}

// 监听滚动更新可视区域
function updateVisibleArea() {
  if (!containerRef.value) return
  const scrollTop = containerRef.value.scrollTop
  // startIndex.value = Math.floor(scrollTop / itemHeight)
}

// 加载更多数据
function loadMore() {
  if (currentPage.value * pageSize < totalCharts.value) {
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

async function handleComparisonClick() {
  if (!isComparisonMode.value) {
    toggleComparisonMode()
    return
  }
  
  if (selectedCharts.value.length >= 2) {
    try {
      isLoading.value = true
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // router.push({
      //   name: 'analysis-result',
      //   query: {
      //     charts: selectedCharts.value.map(chart => chart.id).join(',')
      //   }
      // })
    } catch (error) {
      console.error('对比失败:', error)
    } finally {
      isLoading.value = false
      closeComparisonMode()
    }
  }
}

const toggleDropdown = (dropdown) => {
  if (activeDropdown.value === dropdown) {
    activeDropdown.value = null
  } else {
    activeDropdown.value = dropdown
  }
}

// 搜索相关
async function handleSearch() {
  if (!searchQuery.value.trim()) {
    clearSearch()
    return
  }
  
  isSearching.value = true
  try {
    const query = searchQuery.value.toLowerCase()
    // 模拟搜索延迟
    await new Promise(resolve => setTimeout(resolve, 300))
    
    searchResults.value = charts.value.filter(chart => 
      chart.title.toLowerCase().includes(query) ||
      chart.code.toLowerCase().includes(query)
    )
    
    // 重置到第一页
    currentPage.value = 1
  } finally {
    isSearching.value = false
  }
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = null
  currentPage.value = 1
}

// 图表配置生成函数
function generateChartOption({ name, unit, time, data }) {
  return {
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        const value = params[0].value === null ? '暂无数据' : params[0].value
        return `${params[0].axisValue}<br/>${value}`
      }
    },
    title: {
      text: name,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 14
      }
    },
    xAxis: {
      type: 'category',
      data: time,
      axisLabel: {
        rotate: 45,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: unit,
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [{
      name: name,
      data: data,
      type: 'line',
      smooth: true,
      showSymbol: false,
      connectNulls: true,
      areaStyle: {
        opacity: 0.8,
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(64, 128, 255, 0.3)'
          }, {
            offset: 1, color: 'rgba(64, 128, 255, 0)'
          }],
        }
      },
      itemStyle: {
        color: '#4080ff'
      },
      lineStyle: {
        width: 2,
        color: '#4080ff'
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
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

// Lifecycle
onMounted(() => {
  loadCSVData()
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.group')) {
      activeDropdown.value = null
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('click', (e) => {
    if (!e.target.closest('.group')) {
      activeDropdown.value = null
    }
  })
})
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
