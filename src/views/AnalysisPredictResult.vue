<template>
  <div class="min-h-screen bg-[#F2F5F8]">
    <TheHeader />
    
    <!-- 面包屑导航 -->

    <div class="bg-[#348fef]  py-6 px-4 border-t border-gray-400 border-capacity-40">
      <div class="container mx-auto px-10 flex items-center space-x-2 ">
        <arrow-down-wide-narrow class="h-5 w-5 text-gray-200" />
        <router-link to="/prediction" class="text-gray-200 text-sm">
          宏观预测
        </router-link>
          <ChevronRightIcon class="h-4 w-4 text-gray-200" />
          <span class="text-gray-200 text-sm">分析结果</span>
      </div>
    </div>


    <!-- 主要内容区域 -->
    <main class="container mx-auto py-6 px-4  ">
        <!-- 趋势对比图表 -->
      <div class="rounded-lg  mb-6 px-6">
        <div class="px-4  py-2 border-b  rounded-t-lg bg-gray shadow">
          <h2 class="text-sm text-left font-medium">预测走势</h2>
        </div>
        <div class="p-4 h-[400px]  bg-white rounded-b-lg shadow">
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>
      </div>

      <!-- 结果分析 -->
      <div class="rounded-lg  mb-6 px-6">
        <div class="px-4 py-2 border-b  rounded-t-lg bg-gray shadow">
            <h2 class="text-sm text-left font-medium">结果分析</h2>
        </div>
        <div class="p-6 space-y-6 bg-white rounded-b-lg shadow text-left">
          <div v-if="analysisContent" class="prose prose-sm max-w-none" v-html="renderMarkdown(analysisContent)"></div>
          <div v-if="isLoading" class="text-gray-600">分析中...</div>
          <div v-if="!analysisContent && !isLoading" class="text-gray-600">暂无数据可供分析。</div>
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
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent 
} from 'echarts/components'
import VChart from 'vue-echarts'
import { 
  HomeIcon, 
  ArrowDownWideNarrow, 
  ChevronRightIcon,
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  XIcon
} from 'lucide-vue-next'

import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import MarkdownIt from 'markdown-it'

import { useRoute } from 'vue-router'
import { API_BASE_URL } from '../config'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

// 初始化markdown解析器
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
})

// 自定义渲染规则，减少空行
md.renderer.rules.paragraph_open = () => '<p class="mb-1">'
md.renderer.rules.list_item_open = () => '<li class="mb-1">'

// 解析markdown内容
const renderMarkdown = (content) => {
  if (!content) return ''
  return md.render(content)
}

// 图表配置
const chartOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: []
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: {
    type: 'value'
  },
  series: []
})

// 分析结果内容
const analysisContent = ref('')
const isLoading = ref(false)
const currentConversationId = ref(null)

// 发送数据到后端API获取分析
const getAnalysis = async (chartData) => {
  try {
    isLoading.value = true
    
    console.log('原始图表数据:', chartData)
    
    // 验证数据是否有效
    if (!chartData.data || !chartData.time || !chartData.data.length || !chartData.time.length) {
      throw new Error('图表数据无效')
    }

    // 获取最近30条数据
    const startIndex = Math.max(0, chartData.data.length - 30)
    const recentData = chartData.time.slice(startIndex).map((time, index) => {
      const dataIndex = startIndex + index
      const value = chartData.data[dataIndex]
      return {
        date: time,
        value: typeof value === 'number' ? value.toFixed(4) : null
      }
    })
    
    // 检查是否所有数据都为空
    const hasValidData = recentData.some(item => item.value !== null)
    if (!hasValidData) {
      analysisContent.value = '**数据无效**\n\n当前数据集中所有值均为空，无法进行分析。请选择包含有效数据的时间范围。'
      return
    }
    
    console.log('处理后的数据:', recentData)
    
    // 构建prompt
    const prompt = `你是一名专业的经济分析师。现在，我将提供一个名为【${chartData.name}】的经济数据，该数据集涵盖了从【${recentData[0].date}】至【${recentData[recentData.length-1].date}】的${recentData.length}条数据。在分析这些数据时，你需要重点关注数据的来源、分类、可靠性和时效性。
以下是你将遵循的分析步骤：
#趋势和变化分析：
首先识别数据中的主要趋势和周期性变化。
#原因和影响因素探究：
探讨可能影响数据变化的经济、政治和社会因素。
分析这些因素如何与数据变化相关联，并尝试建立因果关系。
#综合经济指标分析：
结合其他相关经济指标，以获得更全面的视角。
评估这些指标如何相互影响，并共同作用于提供的数据。
#为了确保分析的时效性和准确性，请使用百度搜索插件来获取最新的经济资讯和数据。确保这些资讯与分析报告的关联性，并在报告中注明来源。引用习近平总书记或政府官方部门在相关领域的最新论述和政策指导。这些论述将作为分析报告的重要论据，以增强报告的权威性和深度。
以下是具体的数据内容：【${JSON.stringify(recentData)}】`

    // 创建新会话
    const convResponse = await fetch(`${API_BASE_URL}/conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!convResponse.ok) {
      throw new Error('创建会话失败')
    }
    
    const convData = await convResponse.json()
    currentConversationId.value = convData.conversation_id

    // 发送流式请求
    const response = await fetch(`${API_BASE_URL}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        conversation_id: currentConversationId.value,
        query: prompt
      })
    })

    if (!response.ok) {
      throw new Error('分析请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let result = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      result += decoder.decode(value, { stream: true })
      analysisContent.value = result
    }

    isLoading.value = false
  } catch (error) {
    console.error('分析过程出错:', error)
    analysisContent.value = '**分析失败**\n\n无法获取分析结果，请稍后重试。'
    isLoading.value = false
  }
}

const route = useRoute()
const chartIds = computed(() => {
  const ids = route.query.charts
  return ids ? ids.split(',') : []
})

// 根据 chartIds 获取对应的图表数据
onMounted(() => {
  const indicatorId = route.params.indicatorId
  if (chartIds.value.length) {
    updateChartOption(chartIds.value)
    loadChartData(chartIds.value)
  } else if (indicatorId) {
    loadCSVData(indicatorId)
  }
})

// Function to load CSV data based on indicatorId
const chartData = ref({ time: [], data: [] })
const loadCSVData = async (indicatorId) => {
  try {
    // Load seasonal GDP data
    const gdpResponse = await fetch(new URL(`/data/seasonal_gdp.csv`, window.location.origin))
    const gdpText = await gdpResponse.text()
    const gdpRows = gdpText.replace(/^\ufeff/, '').split('\n').slice(1) // Skip header row
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
      if (!valueStr) return // Add null check
      
      // Check for prediction interval (±)
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

    // Load monthly data
    const monthlyResponse = await fetch(new URL('/data/monthly_data.csv', window.location.origin))
    const monthlyText = await monthlyResponse.text()
    const monthlyRows = monthlyText.replace(/^\ufeff/, '').split('\n').slice(1)
    
    monthlyData.value = {
      retail: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      cpi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      ppi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      investment: { dates: [], values: [], isPredicted: [], confidenceInterval: [] }
    }

    monthlyRows.forEach(row => {
      if (!row.trim()) return
      const [date, retail, cpi, ppi, investment] = row.split(',')
      
      // Process each indicator
      const processIndicator = (valueStr, indicator) => {
        if (!valueStr) return // Add null check
        
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

    console.log('调用getAnalysis函数')
    console.log('传递的数据:', chartData.value)
    getAnalysis(chartData.value)
  } catch (error) {
    console.error('加载CSV数据出错:', error)
  }
}

// 更新图表配置
const updateChartOption = (selectedCharts) => {
  // 更新图表逻辑
}

const generateCombinedChartOption = (indicatorId) => {
  const data = getIndicatorData(indicatorId)
  if (!data) return {}

  const indicator = indicators.value.find(item => item.id === indicatorId)
  const interval = indicator?.type === 'seasonal' ? 3 : 11

  // Handle confidence interval data
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
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>