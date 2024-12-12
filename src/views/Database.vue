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
                :disabled="isInitialLoading || isSearching"
                class="pl-10 pr-8 py-2 w-64  rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4080ff] disabled:bg-gray-100 disabled:cursor-not-allowed bg-[#F2F5F8]/50"
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
                'px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors',
                (isInitialLoading || isSearching) ? 'bg-gray-400 text-white cursor-not-allowed' :
                isComparisonMode 
                  ? 'bg-gray-400 text-white cursor-not-allowed' 
                  : 'bg-[#4080ff] text-white hover:bg-[#3070ff]',
                selectedCharts.length >= 2 && isComparisonMode
                  ? '!bg-[#4080ff] !cursor-pointer'
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
          <div 
            v-for="(chart, i) in displayedCharts" 
            :key="chart.id" 
            class="bg-white shadow rounded-lg border-t border-gray-200 rounded-lg mb-6"
          >
            <div class="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
              <div class="flex items-center space-x-4">
                <input
                  v-if="isComparisonMode"
                  type="checkbox"
                  :id="'chart-' + chart.id"
                  :checked="isChartSelected(chart)"
                  @change="toggleChartSelection(chart)"
                  class="w-4 h-4 text-[#4080ff] rounded border-gray-300 focus:ring-[#4080ff] bg-[#F2F5F8] bg-opacity-50"
                />
                <h2 class="text-sm">{{ chart.title }}</h2>
              </div>
              <div class="text-sm text-mute flex items-center space-x-4">
                <span>数据来源：{{ getFileDisplayName(chart.source) }}</span>
                <span>{{ chart.code }}</span>
              </div>
            </div>
            <div class="h-80 w-full border-t border-gray-200">
              <v-chart class="chart" :option="chart.option" autoresize />
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex justify-between items-center bg-white p-4 rounded-lg shadow mt-6">
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
              <input 
                v-model="jumpPage"
                type="number"
                placeholder="页码"
                @keyup.enter="handlePageJump"
                class="w-16 h-8 pl-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4080ff] bg-[#F2F5F8]/50"
              />
              <button 
                @click="handlePageJump"
                class="px-3 py-1 rounded-lg bg-[#4080ff] text-white hover:bg-[#3070ff]"
              >
                跳转
              </button>
            </div>
          </div>
        </template>
      </div>
    </main>
    <TheFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, DataZoomComponent } from 'echarts/components'
import { API_BASE_URL } from '../config'
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

// State
const isComparisonMode = ref(false)
const selectedCharts = ref([])
const isInitialLoading = ref(true)
const isComparisonLoading = ref(false)
const isSearching = ref(false)
const activeDropdown = ref(null)
const regions = ref(['北京', '上海', '四川', '云南', '湖北', '贵州'])
const charts = ref([])
const pageSize = ref(20)
const currentPage = ref(1)
const totalCharts = ref(0)
const searchQuery = ref('')
const searchResults = ref(null)
const containerRef = ref(null)
const jumpPage = ref('');

// 添加文件配置
const dataFiles = [
  {
    name: 'DATALF',
    path: 'assets/DATALF-20241103 - DAY.csv',
    loaded: false,
    displayName: '劳动力'
  },
  {
    name: 'DATACY',
    path: 'assets/DATACY20241103 - month.csv',
    loaded: false,
    displayName: '产业'
  },
  {
    name: 'DATADM1',
    path: 'assets/DATADM-20241103 - 季度.csv',
    loaded: false,
    displayName: '对美'
  },
  {
    name: 'DATADM2',
    path: 'assets/DATADM-20241103 - 月度.csv',
    loaded: false,
    displayName: '对美'
  },
  {
    name: 'DATADWL',
    path: 'assets/DATADWL-241103 - 月度.csv',
    loaded: false,
    displayName: '对外'
  }
]

// 分页相关计算属性
const totalPages = computed(() => {
  const total = searchResults.value 
    ? searchResults.value.length 
    : totalCharts.value
  return Math.ceil(total / pageSize.value)
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
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return data.slice(start, end)
})

// 处理 CSV 数据
function parseCSVData(rows) {
  try {
    // 获取并清理表头
    const headers = rows[0].split(',').map(h => h.trim());
    const timeData = [];
    const indicators = headers.slice(1); // 第一列是时间，其余是指标
    const values = Array(indicators.length).fill().map(() => []);
    
    // 从第二行开��处理数据
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i].split(',').map(cell => cell.trim());
      
      // 检查行是否包含足够的数据
      if (row.length >= 2) {  // 只要有时间列和至少一个数据列就处理
        const timeValue = row[0];
        if (timeValue && timeValue.trim()) {  // 确保时间值存在
          timeData.push(timeValue);
          
          // 处理每个指标的值，如果值不存在就用null
          for (let j = 1; j < headers.length; j++) {
            const value = row[j] ? parseFloat(row[j]) : null;
            values[j-1].push(value);
          }
        }
      }
    }
    
    // 输出一些调试信息
    console.log(`处理CSV数据: 发现 ${indicators.length} 个指标, ${timeData.length} 个时间点`);
    
    return {
      indicators,
      timeData,
      values
    };
  } catch (error) {
    console.error('解析 CSV 数据时出错:', error);
    return {
      indicators: [],
      timeData: [],
      values: []
    };
  }
}

// 处理文件数据
async function processFileData(csvText) {
  if (!csvText || typeof csvText !== 'string') {
    console.error('无效的 CSV 数据类型:', typeof csvText);
    return null;
  }

  try {
    // 移除 BOM 标记
    const cleanText = csvText.replace(/^\uFEFF/, '');
    
    // 按行分割，保留非空行
    const rows = cleanText.split('\n')
      .map(row => row.trim())
      .filter(row => row.length > 0);

    if (rows.length < 2) {
      console.error('CSV 数据行数不足');
      return null;
    }

    return rows;
  } catch (error) {
    console.error('处理 CSV 数据时出错:', error);
    return null;
  }
}

// 加载单个文件
async function loadFile(fileConfig) {
  console.log(`开始加载 ${fileConfig.name}...`);
  
  try {
    const response = await fetch(fileConfig.path);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const text = await response.text();
    const rows = await processFileData(text);
    if (!rows) {
      throw new Error('数据处理失败');
    }
    
    const parsedData = parseCSVData(rows);
    updateChartsWithData(parsedData, fileConfig.name);
    fileConfig.loaded = true;
    
    console.log(`${fileConfig.name} 加载完成`);
    return true;
  } catch (error) {
    console.error(`加载 ${fileConfig.name} 失败:`, error);
    return false;
  }
}

// 添加新的函数用于加载其他文件
async function loadAdditionalFiles() {
  for (let i = 0; i < dataFiles.length; i++) {
    const file = dataFiles[i];
    if (!file.loaded) {
      try {
        await loadFile(file);
        // 添加延迟
        if (i < dataFiles.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error) {
        console.error(`加载 ${file.name} 失败:`, error);
      }
    }
  }
}

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

// 将选中的图表数据保存到缓存
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

      // 导航到分析结果页面
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
    // await new Promise(resolve => setTimeout(resolve, 300))
    
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

// 处理页码跳转
function handlePageJump() {
  const page = parseInt(jumpPage.value);
  if (page && page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
  jumpPage.value = '';
}

// 图表配置生成数
function generateChartOption({ name, unit, time, data }) {
  // Find valid data range
  const validDataPoints = data.map((value, index) => ({ value, index }))
    .filter(item => item.value !== null && item.value !== undefined && item.value !== '')
  
  if (validDataPoints.length === 0) {
    return {
      title: {
        text: name,
        left: 'center',
        top: 'center',
        textStyle: {
          fontSize: 14
        }
      },
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
  
  // Filter time and data arrays to only include the valid range
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
      data: filteredTime,
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
      data: filteredData,
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

// 更新图表数据
function updateChartsWithData(parsedData, fileName) {
  const { indicators, timeData, values } = parsedData;
  
  if (!indicators || !timeData || !values || 
      !Array.isArray(indicators) || !Array.isArray(timeData) || !Array.isArray(values)) {
    console.error('无效的数据格式:', parsedData);
    return;
  }
  
  console.log(`处理文件 ${fileName}: ${indicators.length} 个指标`);
  
  const newCharts = indicators.map((indicator, index) => {
    if (!Array.isArray(values[index])) {
      console.error(`指标 ${indicator} 的数据无效`);
      return null;
    }
    
    // 过滤掉全是null的数据系列
    const hasValidData = values[index].some(v => v !== null);
    if (!hasValidData) {
      console.log(`跳过空指标: ${indicator}`);
      return null;
    }
    
    return {
      id: `${fileName}_${index + 1}`,
      title: indicator,
      source: fileName,
      code: `${fileName}_${index + 1}`,
      option: generateChartOption({
        name: indicator,
        unit: '',
        time: timeData,
        data: values[index]
      })
    };
  }).filter(Boolean);
  
  console.log(`${fileName} 生成图表: ${newCharts.length} 个`);
  
  charts.value = [...charts.value, ...newCharts];
  totalCharts.value = charts.value.length;
}

// 获取文件显示名称
function getFileDisplayName(source) {
  if (!source) return '';
  
  // 从文件名中提取日期之前的部分
  const match = source.match(/^(DATA[A-Z]+)-?\d/);
  if (match) {
    return match[1];
  }
  return source;
}

// Lifecycle
onMounted(async () => {
  isInitialLoading.value = true;
  try {
    // 加载主文件
    await loadFile(dataFiles[0]);
    
    // 延迟加载其他文件
    setTimeout(async () => {
      await loadAdditionalFiles();
    }, 1000);
  } catch (error) {
    console.error('加载数据失败:', error);
  } finally {
    isInitialLoading.value = false;
  }
});

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
