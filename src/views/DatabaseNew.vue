<template>
  <div class="min-h-screen bg-[#F2F5F8]">
    <TheHeader />

    <!-- Subheader -->
    <div class="bg-[#348fef] py-6 px-4 border-t border-white border-opacity-10">
      <div class="container mx-auto px-10 flex items-center space-x-2">
        <svg class="h-5 w-5 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"></path>
        </svg>
        <span class="text-sm text-gray-200">数据筛选</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="p-6">
        <!-- 顶部搜索栏 -->
        <div class="flex justify-between items-center mb-6 bg-white rounded-lg p-4 shadow">
          <h1 class="text-xl font-semibold text-gray-900">数据库</h1>
          <div class="relative">
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="搜索指标..."
              class="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              <svg class="h-4 w-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <div class="flex gap-6">
          <!-- 左侧指标选择器 -->
          <div class="w-80 flex-shrink-0">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h2 class="text-lg font-medium text-gray-900 mb-4">选择指标</h2>
              
              <!-- 加载状态 -->
              <div v-if="isLoadingIndicators" class="flex justify-center items-center py-8">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="ml-2 text-gray-600">加载指标...</span>
              </div>
              
              <!-- 指标列表 -->
              <div v-else class="space-y-2 max-h-[calc(100vh-200px)] overflow-y-auto">
                <div
                  v-for="indicator in indicators"
                  :key="indicator.id"
                  @click="selectIndicator(indicator)"
                  class="p-3 border border-gray-200 rounded-lg cursor-pointer transition-all hover:bg-blue-50 hover:border-blue-300"
                  :class="{
                    'bg-blue-50 border-blue-500': selectedIndicator?.id === indicator.id,
                    'bg-white': selectedIndicator?.id !== indicator.id
                  }"
                >
                  <div class="font-medium text-gray-900">{{ indicator.title }}</div>
                  <div class="text-sm text-gray-500 mt-1">{{ indicator.code }}</div>
                </div>
              </div>
              
              <!-- 分页控制 -->
              <div v-if="totalPages > 1" class="mt-4 pt-4 border-t border-gray-200">
                <div class="flex justify-between items-center">
                  <button
                    @click="loadPreviousPage"
                    :disabled="currentPage <= 1"
                    class="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    上一页
                  </button>
                  <span class="text-sm text-gray-600">
                    {{ currentPage }} / {{ totalPages }}
                  </span>
                  <button
                    @click="loadNextPage"
                    :disabled="currentPage >= totalPages"
                    class="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    下一页
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧图表区域 -->
          <div class="flex-1">
            <!-- 未选择指标时的提示 -->
            <div v-if="!selectedIndicator" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
              <div class="text-gray-400 mb-4">
                <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">请选择一个指标</h3>
              <p class="text-gray-500">从左侧列表中选择一个指标来查看其日度、月度和季度数据</p>
            </div>

            <!-- 选中指标时显示图表 -->
            <div v-else class="space-y-6">
              <!-- 指标标题 -->
              <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <h2 class="text-xl font-semibold text-gray-900">{{ selectedIndicator.title }}</h2>
                <p class="text-sm text-gray-500 mt-1">数据来源：{{ selectedIndicator.code }}</p>
              </div>

              <!-- 三个时间维度的图表 -->
              <div class="space-y-6">
                <!-- 日度图表 -->
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 class="text-lg font-medium text-gray-900 mb-4">日度数据</h3>
                  <div v-if="isLoadingCharts" class="flex justify-center items-center py-12">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span class="ml-2 text-gray-600">加载图表...</span>
                  </div>
                  <div v-else class="h-80">
                    <v-chart class="chart" :option="dailyChartOption" autoresize />
                  </div>
                </div>

                <!-- 月度图表 -->
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 class="text-lg font-medium text-gray-900 mb-4">月度数据</h3>
                  <div v-if="isLoadingCharts" class="flex justify-center items-center py-12">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span class="ml-2 text-gray-600">加载图表...</span>
                  </div>
                  <div v-else class="h-80">
                    <v-chart class="chart" :option="monthlyChartOption" autoresize />
                  </div>
                </div>

                <!-- 季度图表 -->
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 class="text-lg font-medium text-gray-900 mb-4">季度数据</h3>
                  <div v-if="isLoadingCharts" class="flex justify-center items-center py-12">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span class="ml-2 text-gray-600">加载图表...</span>
                  </div>
                  <div v-else class="h-80">
                    <v-chart class="chart" :option="quarterlyChartOption" autoresize />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import axios from 'axios'
import TheHeader from '@/components/TheHeader.vue'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

// API 基础URL
const API_BASE_URL = 'http://120.48.150.254:8888'

// 响应式数据
const searchQuery = ref('')
const indicators = ref([])
const selectedIndicator = ref(null)
const isLoadingIndicators = ref(true)
const isLoadingCharts = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 图表选项
const dailyChartOption = ref({})
const monthlyChartOption = ref({})
const quarterlyChartOption = ref({})

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 生命周期
onMounted(() => {
  fetchIndicators()
})

// 监听搜索查询
watch(searchQuery, (newQuery) => {
  if (newQuery.trim() === '') {
    fetchIndicators()
  }
})

// 获取指标列表
async function fetchIndicators() {
  isLoadingIndicators.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/monthly-prediction-data`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value || undefined
      }
    })

    const { data, total: totalCount } = response.data
    indicators.value = data.map(item => ({
      id: item.id,
      title: item.title,
      code: item.code,
      times: item.times,
      values: item.values,
      is_predicted: item.is_predicted || []
    }))

    total.value = totalCount
  } catch (error) {
    console.error('获取指标列表失败:', error)
  } finally {
    isLoadingIndicators.value = false
  }
}

// 选择指标
async function selectIndicator(indicator) {
  selectedIndicator.value = indicator
  await generateCharts(indicator)
}

// 生成图表
async function generateCharts(indicator) {
  isLoadingCharts.value = true

  try {
    // 处理数据，只显示最近2年
    const currentDate = new Date()
    const twoYearsAgo = new Date(currentDate.getFullYear() - 2, 0, 1)

    // 过滤数据
    let filteredTimes = []
    let filteredValues = []
    let filteredIsPredicted = []

    if (indicator.times && indicator.values && indicator.is_predicted) {
      for (let i = 0; i < indicator.times.length; i++) {
        const date = new Date(indicator.times[i])
        if (date >= twoYearsAgo) {
          filteredTimes.push(indicator.times[i])
          filteredValues.push(indicator.values[i])
          // 使用对应索引的预测标记
          filteredIsPredicted.push(indicator.is_predicted[i] || false)
        }
      }
    }

    // 生成不同时间维度的数据
    const dailyData = generateTimeSeriesData(filteredTimes, filteredValues, filteredIsPredicted, 'daily')
    const monthlyData = generateTimeSeriesData(filteredTimes, filteredValues, filteredIsPredicted, 'monthly')
    const quarterlyData = generateTimeSeriesData(filteredTimes, filteredValues, filteredIsPredicted, 'quarterly')

    // 生成图表选项
    dailyChartOption.value = generateChartOption({
      name: indicator.title,
      unit: '',
      time: dailyData.times,
      data: dailyData.values,
      isPredicted: dailyData.isPredicted,
      timeType: '日度'
    })

    monthlyChartOption.value = generateChartOption({
      name: indicator.title,
      unit: '',
      time: monthlyData.times,
      data: monthlyData.values,
      isPredicted: monthlyData.isPredicted,
      timeType: '月度'
    })

    quarterlyChartOption.value = generateChartOption({
      name: indicator.title,
      unit: '',
      time: quarterlyData.times,
      data: quarterlyData.values,
      isPredicted: quarterlyData.isPredicted,
      timeType: '季度'
    })

  } catch (error) {
    console.error('生成图表失败:', error)
  } finally {
    isLoadingCharts.value = false
  }
}

// 生成时间序列数据
function generateTimeSeriesData(times, values, isPredicted, timeType) {
  // 根据时间类型聚合数据
  const aggregatedData = {}

  for (let i = 0; i < times.length; i++) {
    const date = new Date(times[i])
    let key

    switch (timeType) {
      case 'daily':
        key = date.toISOString().split('T')[0] // YYYY-MM-DD
        break
      case 'monthly':
        key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}` // YYYY-MM
        break
      case 'quarterly':
        const quarter = Math.floor(date.getMonth() / 3) + 1
        key = `${date.getFullYear()}-Q${quarter}` // YYYY-QX
        break
    }

    if (!aggregatedData[key]) {
      aggregatedData[key] = {
        values: [],
        isPredicted: isPredicted[i]
      }
    }

    if (values[i] !== null && values[i] !== undefined) {
      aggregatedData[key].values.push(values[i])
    }
  }

  // 计算平均值并排序
  const sortedKeys = Object.keys(aggregatedData).sort()
  const resultTimes = []
  const resultValues = []
  const resultIsPredicted = []

  sortedKeys.forEach(key => {
    const data = aggregatedData[key]
    if (data.values.length > 0) {
      resultTimes.push(key)
      resultValues.push(data.values.reduce((a, b) => a + b, 0) / data.values.length)
      resultIsPredicted.push(data.isPredicted)
    }
  })

  return {
    times: resultTimes,
    values: resultValues,
    isPredicted: resultIsPredicted
  }
}

// 生成图表选项
function generateChartOption({ name, unit, time, data, isPredicted = null, timeType = '' }) {
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
  const filteredIsPredicted = isPredicted ? isPredicted.slice(startIndex, endIndex + 1) : null

  // 如果有预测数据标记，分别处理历史和预测数据
  let series = []

  if (filteredIsPredicted && filteredIsPredicted.some(p => p)) {
    // 找到预测数据开始的位置
    const predictionStartIndex = filteredIsPredicted.findIndex(p => p)

    // 历史数据系列（包含连接点，到预测开始位置）
    const historicalData = filteredData.map((value, index) =>
      index <= predictionStartIndex ? value : null
    )

    // 预测数据系列（从预测开始位置，包含连接点）
    const predictedData = filteredData.map((value, index) =>
      index >= predictionStartIndex ? value : null
    )

    // 历史数据系列
    series.push({
      name: name + ' (历史)',
      data: historicalData,
      type: 'line',
      smooth: true,
      showSymbol: false,
      connectNulls: false,
      itemStyle: {
        color: '#348FEF'
      },
      lineStyle: {
        width: 2,
        color: '#348FEF',
        type: 'solid'
      },
      areaStyle: {
        opacity: 0.3,
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(52, 143, 239, 0.2)' },
            { offset: 1, color: 'rgba(52, 143, 239, 0)' }
          ]
        }
      }
    })

    // 预测数据系列
    series.push({
      name: name + ' (预测)',
      data: predictedData,
      type: 'line',
      smooth: true,
      showSymbol: false,
      connectNulls: false,
      itemStyle: {
        color: '#FF6B6B'
      },
      lineStyle: {
        width: 2,
        color: '#FF6B6B',
        type: 'dashed'
      },
      areaStyle: {
        opacity: 0.2,
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(255, 107, 107, 0.2)' },
            { offset: 1, color: 'rgba(255, 107, 107, 0)' }
          ]
        }
      }
    })
  } else {
    // 没有预测数据标记，使用单一系列
    series.push({
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
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(52, 143, 239, 0.2)' },
            { offset: 1, color: 'rgba(52, 143, 239, 0)' }
          ]
        }
      },
      itemStyle: {
        color: '#348FEF'
      },
      lineStyle: {
        width: 1.5,
        color: '#348FEF'
      }
    })
  }

  return {
    title: {
      text: `${timeType}数据`,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        let result = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          const value = param.value === null ? '暂无数据' : param.value
          result += `${param.seriesName}: ${value}<br/>`
        })
        return result
      }
    },
    legend: {
      show: series.length > 1,
      top: 30,
      textStyle: {
        fontSize: 10
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
      }
    },
    series: series,
    grid: {
      left: '8%',
      right: '8%',
      bottom: '15%',
      top: series.length > 1 ? '25%' : '20%',
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
        end: 100,
        bottom: 10
      }
    ]
  }
}

// 搜索处理
async function handleSearch() {
  if (!searchQuery.value.trim()) {
    await fetchIndicators()
    return
  }

  currentPage.value = 1
  await fetchIndicators()
}

// 清除搜索
async function clearSearch() {
  searchQuery.value = ''
  currentPage.value = 1
  await fetchIndicators()
}

// 分页控制
async function loadPreviousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    await fetchIndicators()
  }
}

async function loadNextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    await fetchIndicators()
  }
}
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}

/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 指标卡片悬停效果 */
.indicator-card {
  transition: all 0.2s ease-in-out;
}

.indicator-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 选中状态的指标卡片 */
.indicator-card.selected {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

/* 图表容器样式 */
.chart-container {
  border-radius: 8px;
  overflow: hidden;
}

/* 加载动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
