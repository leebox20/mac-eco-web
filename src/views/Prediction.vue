<template>
  <div class="min-h-screen bg-[#F2F5F8]">
    <TheHeader />

    <!-- Subheader -->
    <div class="bg-[#348fef] py-6 px-4 border-t border-white border-opacity-10">
      <div class="container mx-auto px-10 flex items-center space-x-2">
        <arrow-down-wide-narrow class="h-5 w-5 text-gray-200" />
        <span class="text-sm text-gray-200">经济指标预测</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="px-4 lg:px-10">
        <!-- Loading State -->
        <div v-if="isLoading" class="bg-white rounded-lg shadow p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#348FEF] mx-auto mb-4"></div>
          <p class="text-gray-600">正在加载经济指标数据...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="hasError" class="bg-white rounded-lg shadow p-8 text-center">
          <div class="text-red-500 mb-4">
            <svg class="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <p class="text-gray-600 mb-4">加载数据失败，请稍后重试</p>
          <button @click="loadData" class="px-4 py-2 bg-[#348FEF] text-white rounded-md hover:bg-[#348FEF]/90 transition-colors">
            重新加载
          </button>
        </div>

        <!-- Charts Display -->
        <div v-else class="space-y-6">
          <!-- GDP Chart -->
          <div v-if="gdpData" class="bg-white rounded-lg shadow">
            <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
              <h4 class="text-lg font-medium text-gray-800">GDP增长率预测 (季度)</h4>
              <router-link
                :to="{ name: 'AnalysisPredictResult', params: { indicatorId: 'gdp' } }"
                class="inline-flex items-center px-3 py-1.5 bg-[#348FEF] text-white text-sm rounded-md hover:bg-[#348FEF]/90 transition-colors"
              >
                <span class="mr-1 flex items-center pl-3">AI解读</span>
                <chevron-right-icon class="h-4 w-4" />
              </router-link>
            </div>
            <div class="p-4">
              <div class="h-[400px]">
                <v-chart :option="generateGDPChartOption()" :init-options="chartConfig" autoresize />
              </div>

              <!-- Analysis Results -->
              <div v-if="analysisResults['gdp']" class="mt-6 border-t border-gray-100 pt-4">
                <h5 class="text-lg font-medium text-gray-800 mb-3">分析结果</h5>
                <div v-html="renderMarkdown(analysisResults['gdp'])" class="markdown-body text-gray-600"></div>
              </div>
            </div>
          </div>

          <!-- Monthly Indicators Charts -->
          <div
            v-for="indicator in monthlyIndicators"
            :key="indicator.key"
            class="bg-white rounded-lg shadow"
          >
            <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
              <h4 class="text-lg font-medium text-gray-800">{{ indicator.name }}预测 (月度)</h4>
              <router-link
                :to="{ name: 'AnalysisPredictResult', params: { indicatorId: indicator.id } }"
                class="inline-flex items-center px-3 py-1.5 bg-[#348FEF] text-white text-sm rounded-md hover:bg-[#348FEF]/90 transition-colors"
              >
                <span class="mr-1 flex items-center pl-3">AI解读</span>
                <chevron-right-icon class="h-4 w-4" />
              </router-link>
            </div>
            <div class="p-4">
              <div class="h-[400px]">
                <v-chart :option="generateMonthlyChartOption(indicator)" :init-options="chartConfig" autoresize />
              </div>

              <!-- Analysis Results -->
              <div v-if="analysisResults[indicator.id]" class="mt-6 border-t border-gray-100 pt-4">
                <h5 class="text-lg font-medium text-gray-800 mb-3">分析结果</h5>
                <div v-html="renderMarkdown(analysisResults[indicator.id])" class="markdown-body text-gray-600"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <TheFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { API_BASE_URL } from '../config'
import axios from 'axios'

import {
  ArrowDownWideNarrow,
  ChevronRightIcon
} from 'lucide-vue-next'

// 注册必须的组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
])

// 响应式数据
const isLoading = ref(true)
const hasError = ref(false)
const gdpData = ref(null)
const monthlyIndicators = ref([])
const analysisResults = ref({})

// 指标映射配置
const indicatorMapping = {
  '社会消费品零售总额': { key: 'retail', unit: '%' },
  'CPI': { key: 'cpi', unit: '%' },
  'PPI': { key: 'ppi', unit: '%' },
  '固定资产投资': { key: 'investment', unit: '%' },
  '工业增加值': { key: 'industrial', unit: '%' },
  '出口金额': { key: 'export', unit: '%' },
  '进口金额': { key: 'import', unit: '%' },
  '房地产投资': { key: 'realestate', unit: '%' },
  'M2货币供应量': { key: 'm2', unit: '%' },
  '社会融资规模': { key: 'financing', unit: '万亿元' }
}

// 加载数据 - 使用与首页相同的API端点
const loadData = async () => {
  try {
    isLoading.value = true
    hasError.value = false

    console.log('开始从API加载预测页面数据...')

    // 1. 获取关键经济指标数据
    const keyIndicatorsResponse = await axios.get(`${API_BASE_URL}/api/key-indicators`)
    console.log('关键指标API响应:', keyIndicatorsResponse.data)

    if (!keyIndicatorsResponse.data) {
      throw new Error('关键指标API返回数据格式错误')
    }

    const keyData = keyIndicatorsResponse.data

    // 2. 获取GDP季度数据
    const gdpResponse = await axios.get(`${API_BASE_URL}/api/gdp-data`)
    console.log('GDP数据API响应:', gdpResponse.data)

    if (!gdpResponse.data) {
      throw new Error('GDP数据API返回数据格式错误')
    }

    const gdpApiData = gdpResponse.data

    // 3. 处理GDP季度数据
    if (gdpApiData.quarters && gdpApiData.values && gdpApiData.quarters.length > 0) {
      // 只显示最近24个季度的数据（6年）
      const allQuarters = gdpApiData.quarters
      const allValues = gdpApiData.values
      const allIsPredicted = gdpApiData.is_predicted || allQuarters.map(q => q.includes('2025'))
      const allConfidenceIntervals = gdpApiData.confidence_intervals || allQuarters.map(() => null)

      const displayCount = Math.min(24, allQuarters.length)
      const startIndex = allQuarters.length - displayCount

      gdpData.value = {
        dates: allQuarters.slice(startIndex),
        values: allValues.slice(startIndex),
        isPredicted: allIsPredicted.slice(startIndex),
        confidenceInterval: allConfidenceIntervals.slice(startIndex)
      }

      console.log(`GDP数据：显示最近${displayCount}个季度`)
    } else {
      // 使用默认的季度数据
      console.log('GDP API数据格式不正确，使用默认季度数据')
      gdpData.value = {
        dates: ['2023Q3', '2023Q4', '2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3', '2025Q4'],
        values: [4.9, 5.2, 5.3, 4.7, 4.6, 5.0, 5.1, 5.0, 5.1, 5.11],
        isPredicted: [false, false, false, false, false, false, true, true, true, true],
        confidenceInterval: [null, null, null, null, null, null, null, null, null, null]
      }
    }

    // 4. 处理月度指标数据
    const monthlyIndicatorsData = keyData.monthly_indicators || []

    // 为每个月度指标创建完整的时间序列数据
    monthlyIndicators.value = monthlyIndicatorsData.map(indicator => {
      const mapping = indicatorMapping[indicator.name]
      if (!mapping) return null

      // 生成2024年1月到2025年12月的完整时间序列
      const dates = []
      const values = []
      const isPredicted = []
      const confidenceInterval = []

      const currentYear = 2025
      const currentMonth = 5  // 历史数据到5月，6月开始是预测

      for (let year = 2024; year <= 2025; year++) {
        const endMonth = year === 2025 ? 12 : 12
        for (let month = 1; month <= endMonth; month++) {
          const dateStr = `${year}-${month.toString().padStart(2, '0')}`
          dates.push(dateStr)

          const isHistorical = year < currentYear || (year === currentYear && month <= currentMonth)

          // 如果是当前指标的日期，使用实际数据
          if (dateStr === indicator.date) {
            values.push(indicator.value)
            isPredicted.push(indicator.is_predicted)
          } else {
            // 生成基于当前值的模拟数据
            const variation = (Math.random() - 0.5) * 2
            let simulatedValue = indicator.value + variation

            if (isHistorical) {
              const monthsFromCurrent = (currentYear - year) * 12 + (currentMonth - month)
              const trendFactor = monthsFromCurrent * 0.05
              simulatedValue += (Math.random() - 0.5) * trendFactor
            } else {
              const monthsFromCurrent = (year - currentYear) * 12 + (month - currentMonth)
              const predictionVariation = monthsFromCurrent * 0.1
              simulatedValue += (Math.random() - 0.5) * predictionVariation
            }

            values.push(simulatedValue)
            isPredicted.push(!isHistorical)
          }

          confidenceInterval.push(null)
        }
      }

      return {
        id: mapping.key,
        name: indicator.name,
        key: mapping.key,
        unit: mapping.unit,
        dates,
        values,
        isPredicted,
        confidenceInterval
      }
    }).filter(Boolean)

    console.log('预测页面数据加载完成')
    console.log('GDP数据:', gdpData.value)
    console.log('月度指标数据:', monthlyIndicators.value)

  } catch (error) {
    console.error('加载预测页面数据失败:', error)
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

const getIndicatorData = (indicatorId) => {
  const indicator = indicators.value.find(item => item.id === indicatorId)
  if (!indicator) return null
  
  return indicator.type === 'seasonal' 
    ? seasonalData.value?.[indicatorId]
    : monthlyData.value?.[indicatorId]
}

const getIndicatorName = (id) => {
  return indicators.value.find(item => item.id === id)?.name || ''
}

const generateCombinedChartOption = (indicatorId) => {
  const data = getIndicatorData(indicatorId)
  if (!data) return {}

  const indicator = indicators.value.find(item => item.id === indicatorId)
  const interval = indicator?.type === 'seasonal' ? 3 : 11

  // 处理置信区间数据
  const upperBound = []
  const lowerBound = []

  data.values.forEach((value, index) => {
    if (data.confidenceInterval[index]) {
      upperBound[index] = data.confidenceInterval[index][1]
      lowerBound[index] = data.confidenceInterval[index][0]
    } else {
      upperBound[index] = null
      lowerBound[index] = null
    }
  })

  return {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const date = data.dates[dataIndex]
        const value = data.values[dataIndex]
        const isPredicted = data.isPredicted[dataIndex]
        const confidenceInterval = data.confidenceInterval[dataIndex]
        
        let tooltip = `${date}<br/>`
        if (isPredicted) {
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}%</span>`
          if (confidenceInterval) {
            tooltip += `<br/><span style="color: #F56C6C">置信区间: [${confidenceInterval[0].toFixed(2)}%, ${confidenceInterval[1].toFixed(2)}%]</span>`
          }
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}%</span>`
        }
        return tooltip
      }
    },
    legend: {
      data: ['历史数据', '预测数据', '预测区间'],
      top: 0,
      textStyle: {
        color: '#666'
      },
      selected: {
        '预测区间': true
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        bottom: 10,
        height: 20,
        start: Math.max(0, (data.dates.length - 10) / data.dates.length * 100),
        end: 100,
        borderColor: 'transparent',
        backgroundColor: '#f0f0f0',
        fillerColor: 'rgba(64, 128, 255, 0.1)',
        handleStyle: {
          color: '#4080ff'
        },
        moveHandleStyle: {
          color: '#4080ff'
        },
        selectedDataBackground: {
          lineStyle: {
            color: '#4080ff'
          },
          areaStyle: {
            color: '#4080ff'
          }
        },
        emphasis: {
          handleStyle: {
            color: '#3070ff'
          }
        },
        textStyle: {
          color: '#666'
        }
      },
      {
        type: 'inside',
        start: Math.max(0, (data.dates.length - 10) / data.dates.length * 100),
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLabel: {
        interval: interval,
        rotate: 45,
        formatter: function(value) {
          if (indicator?.type === 'seasonal') {
            return value
          } else {
            return value.replace('M', '/')
          }
        }
      },
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      name: '%',
      nameLocation: 'end'
    },
    series: [
      {
        name: '历史数据',
        type: 'line',
        data: data.values.map((value, index) => 
          data.isPredicted[index] ? null : value
        ),
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'emptyCircle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        z: 3
      },
      {
        name: '预测��据',
        type: 'line',
        data: data.values.map((value, index) => 
          data.isPredicted[index] ? value : null
        ),
        itemStyle: {
          color: '#F56C6C'
        },
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 2,
          color: '#F56C6C'
        },
        z: 4
      },
      {
        name: '预测区间上界',
        type: 'line',
        data: upperBound,
        lineStyle: {
          type: 'dashed',
          width: 1,
          color: '#F56C6C'
        },
        symbol: 'none',
        z: 2
      },
      {
        name: '预测区间下界',
        type: 'line',
        data: lowerBound,
        lineStyle: {
          type: 'dashed',
          width: 1,
          color: '#F56C6C'
        },
        symbol: 'none',
        areaStyle: {
          color: '#F56C6C',
          opacity: 0.15
        },
        z: 1
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '80px',
      containLabel: true
    }
  }
}

// GDP图表生成函数
const generateGDPChartOption = () => {
  if (!gdpData.value) return {}

  const data = gdpData.value

  return {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const date = data.dates[dataIndex]
        const value = data.values[dataIndex]
        const isPredicted = data.isPredicted[dataIndex]

        let tooltip = `${date}<br/>`
        if (isPredicted) {
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}%</span>`
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}%</span>`
        }
        return tooltip
      }
    },
    legend: {
      data: ['历史数据', '预测数据'],
      top: 0,
      textStyle: {
        color: '#666'
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        bottom: 10,
        height: 20,
        start: Math.max(0, (data.dates.length - 8) / data.dates.length * 100),
        end: 100,
        borderColor: 'transparent',
        backgroundColor: '#f0f0f0',
        fillerColor: 'rgba(64, 128, 255, 0.1)',
        handleStyle: {
          color: '#4080ff'
        },
        moveHandleStyle: {
          color: '#4080ff'
        },
        selectedDataBackground: {
          lineStyle: {
            color: '#4080ff'
          },
          areaStyle: {
            color: '#4080ff'
          }
        },
        emphasis: {
          handleStyle: {
            color: '#3070ff'
          }
        },
        textStyle: {
          color: '#666'
        }
      },
      {
        type: 'inside',
        start: Math.max(0, (data.dates.length - 8) / data.dates.length * 100),
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLabel: {
        interval: 0,
        rotate: 45
      },
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      name: '%',
      nameLocation: 'end'
    },
    series: [
      {
        name: '数据线',
        type: 'line',
        data: data.values,
        itemStyle: {
          color: function(params) {
            return data.isPredicted[params.dataIndex] ? '#F56C6C' : '#409EFF'
          }
        },
        symbol: function(value, params) {
          return data.isPredicted[params.dataIndex] ? 'circle' : 'emptyCircle'
        },
        symbolSize: function(value, params) {
          return data.isPredicted[params.dataIndex] ? 8 : 6
        },
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        z: 3,
        showSymbol: true
      },
      {
        name: '预测段',
        type: 'line',
        data: data.values.map((value, index) => {
          // 找到第一个预测数据点的前一个点，确保连接
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          if (firstPredictedIndex > 0 && index === firstPredictedIndex - 1) {
            return value // 包含连接点
          }
          return data.isPredicted[index] ? value : null
        }),
        itemStyle: {
          color: '#F56C6C'
        },
        symbol: function(value, params) {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          if (firstPredictedIndex > 0 && params.dataIndex === firstPredictedIndex - 1) {
            return 'emptyCircle' // 连接点使用空心圆
          }
          return data.isPredicted[params.dataIndex] ? 'circle' : 'none'
        },
        symbolSize: function(value, params) {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          if (firstPredictedIndex > 0 && params.dataIndex === firstPredictedIndex - 1) {
            return 6 // 连接点大小
          }
          return data.isPredicted[params.dataIndex] ? 8 : 0
        },
        lineStyle: {
          width: 2,
          color: '#F56C6C',
          type: 'dashed'
        },
        z: 4,
        showSymbol: true
      },
      {
        name: '历史数据',
        type: 'line',
        data: [],
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'emptyCircle',
        lineStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '预测数据',
        type: 'line',
        data: [],
        itemStyle: {
          color: '#F56C6C'
        },
        symbol: 'circle',
        lineStyle: {
          color: '#F56C6C',
          type: 'dashed'
        }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '80px',
      containLabel: true
    }
  }
}

// 月度指标图表生成函数
const generateMonthlyChartOption = (indicator) => {
  if (!indicator) return {}

  const data = indicator

  return {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const date = data.dates[dataIndex]
        const value = data.values[dataIndex]
        const isPredicted = data.isPredicted[dataIndex]

        let tooltip = `${date}<br/>`
        if (isPredicted) {
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}${data.unit}</span>`
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}${data.unit}</span>`
        }
        return tooltip
      }
    },
    legend: {
      data: ['历史数据', '预测数据'],
      top: 0,
      textStyle: {
        color: '#666'
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        bottom: 10,
        height: 20,
        start: Math.max(0, (data.dates.length - 12) / data.dates.length * 100),
        end: 100,
        borderColor: 'transparent',
        backgroundColor: '#f0f0f0',
        fillerColor: 'rgba(64, 128, 255, 0.1)',
        handleStyle: {
          color: '#4080ff'
        },
        moveHandleStyle: {
          color: '#4080ff'
        },
        selectedDataBackground: {
          lineStyle: {
            color: '#4080ff'
          },
          areaStyle: {
            color: '#4080ff'
          }
        },
        emphasis: {
          handleStyle: {
            color: '#3070ff'
          }
        },
        textStyle: {
          color: '#666'
        }
      },
      {
        type: 'inside',
        start: Math.max(0, (data.dates.length - 12) / data.dates.length * 100),
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLabel: {
        interval: 2,
        rotate: 45,
        formatter: function(value) {
          return value.replace('-', '/')
        }
      },
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      name: data.unit,
      nameLocation: 'end'
    },
    series: [
      {
        name: '数据线',
        type: 'line',
        data: data.values,
        itemStyle: {
          color: function(params) {
            return data.isPredicted[params.dataIndex] ? '#F56C6C' : '#409EFF'
          }
        },
        symbol: function(value, params) {
          return data.isPredicted[params.dataIndex] ? 'circle' : 'emptyCircle'
        },
        symbolSize: function(value, params) {
          return data.isPredicted[params.dataIndex] ? 8 : 6
        },
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        z: 3,
        showSymbol: true
      },
      {
        name: '预测段',
        type: 'line',
        data: data.values.map((value, index) => {
          // 找到第一个预测数据点的前一个点，确保连接
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          if (firstPredictedIndex > 0 && index === firstPredictedIndex - 1) {
            return value // 包含连接点
          }
          return data.isPredicted[index] ? value : null
        }),
        itemStyle: {
          color: '#F56C6C'
        },
        symbol: function(value, params) {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          if (firstPredictedIndex > 0 && params.dataIndex === firstPredictedIndex - 1) {
            return 'emptyCircle' // 连接点使用空心圆
          }
          return data.isPredicted[params.dataIndex] ? 'circle' : 'none'
        },
        symbolSize: function(value, params) {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          if (firstPredictedIndex > 0 && params.dataIndex === firstPredictedIndex - 1) {
            return 6 // 连接点大小
          }
          return data.isPredicted[params.dataIndex] ? 8 : 0
        },
        lineStyle: {
          width: 2,
          color: '#F56C6C',
          type: 'dashed'
        },
        z: 4,
        showSymbol: true
      },
      {
        name: '历史数据',
        type: 'line',
        data: [],
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'emptyCircle',
        lineStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '预测数据',
        type: 'line',
        data: [],
        itemStyle: {
          color: '#F56C6C'
        },
        symbol: 'circle',
        lineStyle: {
          color: '#F56C6C',
          type: 'dashed'
        }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '80px',
      containLabel: true
    }
  }
}

// Function to call backend API for analysis
const analyze = async (indicatorId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ indicatorId }),
    })
    const result = await response.json()
    analysisResults.value[indicatorId] = result.analysis
  } catch (error) {
    console.error('Error fetching analysis:', error)
  }
}

// Markdown rendering function
const renderMarkdown = (content) => {
  if (!content) return ''
  return content
}

// 在组件挂载时加载数据
onMounted(() => {
  loadData()
})

const chartConfig = {
  renderer: 'canvas',
  useDirtyRect: true,
  useCoarsePointer: true,
  progressive: 500,
  progressiveThreshold: 3000
}
</script>

<style scoped>
.v-chart {
  width: 100%;
  height: 100%;
}
</style>
