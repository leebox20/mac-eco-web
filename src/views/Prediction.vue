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
    
    <!-- 宏观解读浮动按钮 -->
    <div class="fixed bottom-8 right-8 z-50">
      <router-link
        :to="{ name: 'AnalysisPredictResult', params: { indicatorId: 'macro' } }"
        class="group flex items-center justify-center w-16 h-16 bg-[#348FEF] text-white rounded-full shadow-lg hover:bg-[#348FEF]/90 hover:shadow-xl transition-all duration-300 transform hover:scale-110"
        title="整体宏观解读"
      >
        <div class="relative">
          <TrendingUpIcon class="h-8 w-8" />
          <div class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
        </div>
      </router-link>
      
      <!-- 悬浮提示 -->
      <div class="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
        <div class="bg-gray-900 text-white text-sm px-3 py-2 rounded-lg whitespace-nowrap">
          查看所有指标的整体宏观分析
          <div class="absolute top-full right-4 w-0 h-0 border-t-8 border-t-gray-900 border-x-4 border-x-transparent"></div>
        </div>
      </div>
    </div>
    
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
  ChevronRightIcon,
  TrendingUpIcon
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

// 加载数据 - 使用新的API端点
const loadData = async () => {
  try {
    isLoading.value = true
    hasError.value = false

    console.log('开始从新API加载预测页面数据...')

    // 1. 获取关键经济指标数据（用于顶部卡片显示）
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

    // 3. 获取关键指标时间序列数据（用于图表显示）
    const seriesResponse = await axios.get(`${API_BASE_URL}/api/key-indicators-series`)
    console.log('关键指标时间序列API响应:', seriesResponse.data)

    if (!seriesResponse.data) {
      throw new Error('关键指标时间序列API返回数据格式错误')
    }

    const seriesData = seriesResponse.data

    // 3. 处理GDP季度数据
    if (gdpApiData.quarters && gdpApiData.values && gdpApiData.quarters.length > 0) {
      // 只显示最近24个季度的数据（6年）
      const allQuarters = gdpApiData.quarters
      const allValues = gdpApiData.values

      // 强制根据当前时间判断，不使用API返回的is_predicted数据
      // 当前时间：2025年6月3日，所以2025Q2及以后是预测数据（Q2包含6月，从6月开始都是预测）
      const allIsPredicted = allQuarters.map(q => {
        // 解析季度，判断是否为预测数据
        if (q.includes('2025Q2') || q.includes('2025Q3') || q.includes('2025Q4')) {
          return true
        }
        return false
      })

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
      console.log('GDP isPredicted数据:', allIsPredicted.slice(startIndex))
    } else {
      // 使用默认的季度数据
      console.log('GDP API数据格式不正确，使用默认季度数据')
      gdpData.value = {
        dates: ['2023Q3', '2023Q4', '2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3', '2025Q4'],
        values: [4.9, 5.2, 5.3, 4.7, 4.6, 5.4, 5.4, 4.857564, 5.492128, 5.112863],
        isPredicted: [false, false, false, false, false, false, false, true, true, true],
        confidenceInterval: [null, null, null, null, null, null, null, [4.821547, 4.893581], [5.464386, 5.519870], [5.065357, 5.160369]]
      }
    }

    // 4. 处理月度指标数据（使用新的时间序列API）
    console.log('处理预测页面月度时间序列数据:', seriesData)

    // 映射月度指标到对应的数据结构
    const indicatorMappingForSeries = {
      '社会消费品零售总额': { key: 'retail', unit: '%' },
      'CPI': { key: 'cpi', unit: '%' },
      'PPI': { key: 'ppi', unit: '%' },
      '固定资产投资': { key: 'investment', unit: '%' },
      '工业增加值': { key: 'industrial', unit: '%' },
      '出口金额': { key: 'export', unit: '%' },
      '进口金额': { key: 'import', unit: '%' },
      '房地产投资': { key: 'realestate', unit: '%' },
      '制造业投资': { key: 'manufacturing', unit: '%' },
      '基础设施投资': { key: 'infrastructure', unit: '%' },
      'M2货币供应量': { key: 'm2', unit: '%' },
      '社会融资规模': { key: 'financing', unit: '万亿元' }
    }

    // 处理每个月度指标 - 使用新API的时间序列数据
    monthlyIndicators.value = []

    if (seriesData.indicators && Array.isArray(seriesData.indicators)) {
      seriesData.indicators.forEach(indicator => {
        const mapping = indicatorMappingForSeries[indicator.name]
        if (mapping && indicator.data && Array.isArray(indicator.data)) {
          // 直接使用API返回的时间序列数据
          const dates = []
          const values = []
          const isPredicted = []
          const confidenceInterval = []

          indicator.data.forEach(dataPoint => {
            dates.push(dataPoint.date)

            // 对社会融资规模特殊处理（转换为万亿元）
            if (indicator.name === '社会融资规模' && indicator.unit === '亿元') {
              values.push(dataPoint.value / 10000) // 转换为万亿元
              // 转换置信区间
              if (dataPoint.confidence_interval) {
                confidenceInterval.push([
                  dataPoint.confidence_interval[0] / 10000,
                  dataPoint.confidence_interval[1] / 10000
                ])
              } else {
                confidenceInterval.push(null)
              }
            } else {
              values.push(dataPoint.value)
              confidenceInterval.push(dataPoint.confidence_interval || null)
            }

            // 直接使用API返回的is_predicted字段（2025-06开始为预测数据）
            isPredicted.push(dataPoint.is_predicted)
          })

          monthlyIndicators.value.push({
            id: mapping.key,
            name: indicator.name,
            key: mapping.key,
            unit: mapping.unit,
            dates,
            values,
            isPredicted,
            confidenceInterval
          })

          // 统计历史数据和预测数据的数量
          const historicalCount = isPredicted.filter(p => !p).length
          const predictedCount = isPredicted.filter(p => p).length

          console.log(`预测页面 ${indicator.name} 时间序列数据处理完成:`, {
            总数据点: dates.length,
            日期范围: dates.length > 0 ? `${dates[0]} 到 ${dates[dates.length - 1]}` : '无数据',
            历史数据: `${historicalCount}个月`,
            预测数据: `${predictedCount}个月 (从2025-06开始)`,
            单位: indicator.unit,
            数据源: '新API时间序列'
          })
        } else {
          console.warn(`预测页面指标 ${indicator.name} 无法映射到数据结构或数据格式错误`)
        }
      })
    } else {
      console.warn('预测页面时间序列API返回数据格式错误，indicators不是数组')
    }

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
  // 对于GDP数据，使用gdpData
  if (indicatorId === 'gdp') {
    return gdpData.value
  }

  // 对于月度指标，从monthlyIndicators数组中查找
  return monthlyIndicators.value.find(item => item.id === indicatorId)
}

const getIndicatorName = (id) => {
  // 对于GDP，直接返回名称
  if (id === 'gdp') {
    return 'GDP增长率'
  }

  // 对于月度指标，从monthlyIndicators数组中查找
  const indicator = monthlyIndicators.value.find(item => item.id === id)
  return indicator?.name || ''
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
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}${data.unit}</span>`
          if (confidenceInterval) {
            tooltip += `<br/><span style="color: #F56C6C">置信区间: [${confidenceInterval[0].toFixed(2)}${data.unit}, ${confidenceInterval[1].toFixed(2)}${data.unit}]</span>`
          }
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}${data.unit}</span>`
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
      name: data.unit || '%',
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
      // 历史数据线
      {
        name: '历史数据',
        type: 'line',
        data: data.values.map((value, index) =>
          !data.isPredicted[index] ? value : null
        ),
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'emptyCircle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#409EFF',
          type: 'solid'
        },
        z: 3,
        showSymbol: true
      },
      // 预测数据线
      {
        name: '预测数据',
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
          color: '#F56C6C',
          type: 'dashed'
        },
        z: 4,
        showSymbol: true
      },
      // 连接线（从历史数据最后一点到预测数据第一点）
      {
        name: '连接线',
        type: 'line',
        data: data.values.map((value, index) => {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          // 只在连接点和第一个预测点显示数据
          if (firstPredictedIndex > 0 && (index === firstPredictedIndex - 1 || index === firstPredictedIndex)) {
            return value
          }
          return null
        }),
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'none', // 不显示符号，避免重复
        lineStyle: {
          width: 2,
          color: '#409EFF',
          type: 'solid'
        },
        z: 2,
        showSymbol: false
      },

      {
        name: '预测区间上界',
        type: 'line',
        data: data.confidenceInterval.map((interval, index) =>
          (interval && data.isPredicted[index]) ? interval[1] : null
        ),
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
        data: data.confidenceInterval.map((interval, index) =>
          (interval && data.isPredicted[index]) ? interval[0] : null
        ),
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
        const confidenceInterval = data.confidenceInterval[dataIndex]

        let tooltip = `${date}<br/>`
        if (isPredicted) {
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}${data.unit}</span>`
          if (confidenceInterval) {
            tooltip += `<br/><span style="color: #F56C6C">置信区间: [${confidenceInterval[0].toFixed(2)}${data.unit}, ${confidenceInterval[1].toFixed(2)}${data.unit}]</span>`
          }
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}${data.unit}</span>`
        }
        return tooltip
      }
    },
    legend: {
      data: ['历史数据', '预测数据', '预测区间'],
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
      // 历史数据线
      {
        name: '历史数据',
        type: 'line',
        data: data.values.map((value, index) =>
          !data.isPredicted[index] ? value : null
        ),
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'emptyCircle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#409EFF',
          type: 'solid'
        },
        z: 3,
        showSymbol: true
      },
      // 预测数据线
      {
        name: '预测数据',
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
          color: '#F56C6C',
          type: 'dashed'
        },
        z: 4,
        showSymbol: true
      },
      // 连接线（从历史数据最后一点到预测数据第一点）
      {
        name: '连接线',
        type: 'line',
        data: data.values.map((value, index) => {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
          // 只在连接点和第一个预测点显示数据
          if (firstPredictedIndex > 0 && (index === firstPredictedIndex - 1 || index === firstPredictedIndex)) {
            return value
          }
          return null
        }),
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'none', // 不显示符号，避免重复
        lineStyle: {
          width: 2,
          color: '#409EFF',
          type: 'solid'
        },
        z: 2,
        showSymbol: false
      },
      {
        name: '预测区间上界',
        type: 'line',
        data: data.confidenceInterval.map((interval, index) =>
          (interval && data.isPredicted[index]) ? interval[1] : null
        ),
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
        data: data.confidenceInterval.map((interval, index) =>
          (interval && data.isPredicted[index]) ? interval[0] : null
        ),
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
