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
      <div class="flex flex-col lg:flex-row gap-6 px-4 lg:px-10">
        <!-- Left Sidebar - Indicator Selection -->
        <div class="w-full lg:w-1/4">
          <div class="bg-white rounded-lg shadow">
            <!-- Card Header -->
            <div class="px-4 py-3 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-800">指标选择</h3>
            </div>
            
            <!-- Card Body -->
            <div class="p-4">
              <div class="space-y-3">
                <div v-for="indicator in indicators" 
                     :key="indicator.id" 
                     class="flex items-center hover:bg-gray-50 p-2 rounded-md transition-colors">
                  <input
                    type="checkbox"
                    :id="indicator.id"
                    v-model="selectedIndicators"
                    :value="indicator.id"
                    class="w-4 h-4 text-[#4080ff] border-gray-300 rounded focus:ring-[#4080ff]"
                  />
                  <label :for="indicator.id" class="ml-2 text-sm text-gray-700 cursor-pointer flex-1">
                    {{ indicator.name }} 
                    <span class="text-gray-500">({{ indicator.type === 'seasonal' ? '季度' : '月度' }})</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Content - Charts -->
        <div class="w-full lg:w-3/4 space-y-6">
          <div v-if="selectedIndicators.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
            <arrow-down-wide-narrow class="h-5 w-5 text-gray-200 mx-auto mb-2" />
            <p class="text-gray-600">请在左侧选择需要预测的经济指标</p>
          </div>
          <template v-else>
            <div
              v-for="indicatorId in selectedIndicators"
              :key="indicatorId"
              class="bg-white rounded-lg shadow"
            >
              <!-- Card Header -->
              <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                <h4 class="text-lg font-medium text-gray-800">
                  {{ getIndicatorName(indicatorId) }}预测
                </h4>
                <router-link 
                  :to="{ name: 'AnalysisPredictResult', params: { indicatorId: indicatorId } }" 
                  class="inline-flex items-center px-3 py-1.5 bg-[#348FEF] text-white text-sm rounded-md hover:bg-[#348FEF]/90 transition-colors"
                >
                  <span class="mr-1 flex items-center pl-3">AI解读</span>
                  <chevron-right-icon class="h-4 w-4" />
                </router-link>
              </div>

              <!-- Card Body -->
              <div class="p-4">
                <div class="h-[400px]">
                  <v-chart :option="generateCombinedChartOption(indicatorId)" :init-options="chartConfig" autoresize />
                </div>
                
                <!-- Analysis Results -->
                <div v-if="analysisResults[indicatorId]" class="mt-6 border-t border-gray-100 pt-4">
                  <h5 class="text-lg font-medium text-gray-800 mb-3">分析结果</h5>
                  <div v-html="renderMarkdown(analysisResults[indicatorId])" class="markdown-body text-gray-600"></div>
                </div>
              </div>
            </div>
          </template>
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
import { marked } from 'marked'

import { 
  HomeIcon, 
  ArrowDownWideNarrow, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  XIcon
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

// 指标数据
const indicators = ref([
  { id: 'gdp', name: 'GDP增长率', type: 'seasonal', csvName: '中国:GDP:不变价:当季同比' },
  { id: 'retail', name: '社会消费品零售总额', type: 'monthly', csvName: '中国:社会消费品零售总额:当月同比' },
  { id: 'cpi', name: 'CPI同比', type: 'monthly', csvName: '中国:CPI:当月同比' },
  { id: 'ppi', name: 'PPI同比', type: 'monthly', csvName: '中国:PPI:全部工业品:当月同比' },
  { id: 'investment', name: '固定资产投资', type: 'monthly', csvName: '中国:固定资产投资完成额:累计同比' }
])

// 默认选中GDP增长率
const selectedIndicators = ref(['gdp'])

// 数据存储
const seasonalData = ref(null)
const monthlyData = ref(null)
const analysisResults = ref({})
const loadingIndicators = ref([])

// 加载CSV数据
const loadData = async () => {
  try {
    // 确保请求的 URL 是正确的
    const gdpResponse = await fetch(new URL('/data/seasonal_gdp.csv', window.location.origin))
    const gdpText = await gdpResponse.text()
    const gdpRows = gdpText.replace(/^\\ufeff/, '').split('\n').slice(1) // 跳过标题行
    seasonalData.value = {
      gdp: {
        dates: [],
        values: [],
        isPredicted: [],
        confidenceInterval: []
      }
    }
    
    gdpRows.forEach(row => {
      if (!row.trim()) return
      const [date, valueStr] = row.split(',')
      if (!valueStr) return // 添加空值检查
      
      // 检查是否包含预测区间 (±)
      if (valueStr.trim().includes('±')) {
        const [baseValue, interval] = valueStr.trim().split('±')
        const value = parseFloat(baseValue)
        const intervalValue = parseFloat(interval)
        seasonalData.value.gdp.dates.push(date.trim())
        seasonalData.value.gdp.values.push(value)
        seasonalData.value.gdp.isPredicted.push(true)
        seasonalData.value.gdp.confidenceInterval.push([
          value - intervalValue,
          value + intervalValue
        ])
      } else {
        seasonalData.value.gdp.dates.push(date.trim())
        seasonalData.value.gdp.values.push(parseFloat(valueStr))
        seasonalData.value.gdp.isPredicted.push(false)
        seasonalData.value.gdp.confidenceInterval.push(null)
      }
    })

    // 加载月度数据
    const monthlyResponse = await fetch(new URL('/data/monthly_data.csv', window.location.origin))
    const monthlyText = await monthlyResponse.text()
    const monthlyRows = monthlyText.replace(/^\\ufeff/, '').split('\n').slice(1)
    
    monthlyData.value = {
      retail: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      cpi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      ppi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      investment: { dates: [], values: [], isPredicted: [], confidenceInterval: [] }
    }

    monthlyRows.forEach(row => {
      if (!row.trim()) return
      const [date, retail, cpi, ppi, investment] = row.split(',')
      
      // 处理每个指标
      const processIndicator = (valueStr, indicator) => {
        if (!valueStr) return // 添加空值检查
        
        if (valueStr.trim().includes('±')) {
          const [baseValue, interval] = valueStr.trim().split('±')
          const value = parseFloat(baseValue)
          const intervalValue = parseFloat(interval)
          monthlyData.value[indicator].dates.push(date.trim())
          monthlyData.value[indicator].values.push(value)
          monthlyData.value[indicator].isPredicted.push(true)
          monthlyData.value[indicator].confidenceInterval.push([
            value - intervalValue,
            value + intervalValue
          ])
        } else {
          monthlyData.value[indicator].dates.push(date.trim())
          monthlyData.value[indicator].values.push(parseFloat(valueStr))
          monthlyData.value[indicator].isPredicted.push(false)
          monthlyData.value[indicator].confidenceInterval.push(null)
        }
      }

      processIndicator(retail, 'retail')
      processIndicator(cpi, 'cpi')
      processIndicator(ppi, 'ppi')
      processIndicator(investment, 'investment')
    })
  } catch (error) {
    console.error('Error loading data:', error)
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

// Function to call backend API for analysis
const analyze = async (indicatorId) => {
  if (loadingIndicators.value.includes(indicatorId)) return
  loadingIndicators.value.push(indicatorId)

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
  } finally {
    loadingIndicators.value = loadingIndicators.value.filter(id => id !== indicatorId)
  }
}

// Markdown rendering function
const renderMarkdown = (content) => {
  if (!content) return ''
  return marked(content)
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
