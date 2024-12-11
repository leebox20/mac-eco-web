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

// 响应式数据
const seasonalData = ref({
  gdp: {
    dates: [],
    values: [],
    isPredicted: [],
    confidenceInterval: []
  }
})

const monthlyData = ref({
  retail: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
  cpi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
  ppi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
  investment: { dates: [], values: [], isPredicted: [], confidenceInterval: [] }
})

const chartData = ref(null)

// 图表配置
const chartOption = ref({
  tooltip: {
    trigger: 'axis',
    formatter: function(params) {
      let result = params[0].axisValue + '<br/>'
      params.forEach(param => {
        result += param.seriesName + ': ' + param.value + '<br/>'
      })
      return result
    }
  },
  legend: {
    data: ['实际值', '预测值', '预测区间']
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
  series: [
    {
      name: '实际值',
      type: 'line',
      data: []
    },
    {
      name: '预测值',
      type: 'line',
      data: []
    },
    {
      name: '预测区间',
      type: 'line',
      data: [],
      lineStyle: { opacity: 0 },
      areaStyle: {
        opacity: 0.3
      }
    }
  ]
})

const updateChartOption = (data) => {
  if (!data || !data.length || !data[0]) return
  
  const currentData = data[0]
  const dates = currentData.dates || []
  const values = currentData.values || []
  const isPredicted = currentData.isPredicted || []
  const confidenceInterval = currentData.confidenceInterval || []

  // 分离实际值和预测值
  const actualData = dates.map((date, i) => !isPredicted[i] ? [date, values[i]] : [date, null])
  const predictedData = dates.map((date, i) => isPredicted[i] ? [date, values[i]] : [date, null])
  
  // 处理预测区间
  const areaData = dates.map((date, i) => {
    if (isPredicted[i] && confidenceInterval[i]) {
      return [
        date,
        confidenceInterval[i][0],
        confidenceInterval[i][1]
      ]
    }
    return [date, null, null]
  })

  chartOption.value = {
    ...chartOption.value,
    xAxis: {
      ...chartOption.value.xAxis,
      data: dates
    },
    series: [
      {
        name: '实际值',
        type: 'line',
        data: actualData
      },
      {
        name: '预测值',
        type: 'line',
        data: predictedData
      },
      {
        name: '预测区间',
        type: 'line',
        data: areaData,
        lineStyle: { opacity: 0 },
        areaStyle: {
          opacity: 0.3
        }
      }
    ]
  }
}

// 分析结果内容
const analysisContent = ref('')
const isLoading = ref(false)
const currentConversationId = ref(null)

// 发送数据到后端API获取分析
const getAnalysis = async (chartData) => {
  try {
    isLoading.value = true
    
    console.log('原始图表数据:', chartData)
    console.log('图表数据类型:', typeof chartData)
    console.log('图表数据结构:', Object.keys(chartData))
    
    // 验证数据是否有效
    if (!chartData || typeof chartData !== 'object') {
      console.error('图表数据不是有效的对象')
      throw new Error('图表数据无效')
    }

    if (!chartData.dates || !chartData.values || !Array.isArray(chartData.dates) || !Array.isArray(chartData.values)) {
      console.error('缺少必要的数据数组:', {
        hasDates: !!chartData.dates,
        hasValues: !!chartData.values,
        datesIsArray: Array.isArray(chartData.dates),
        valuesIsArray: Array.isArray(chartData.values)
      })
      throw new Error('图表数据无效')
    }

    if (chartData.dates.length === 0 || chartData.values.length === 0) {
      console.error('数据数组为空:', {
        datesLength: chartData.dates.length,
        valuesLength: chartData.values.length
      })
      throw new Error('图表数据无效')
    }

    // 获取最近15条数据
    const startIndex = Math.max(0, chartData.dates.length - 15)
    const recentData = []
    
    // 只处理最近15条数据
    for (let i = startIndex; i < chartData.dates.length; i++) {
      const value = chartData.values[i]
      if (value !== null && value !== undefined) {
        recentData.push({
          date: chartData.dates[i],
          value: Number(value).toFixed(2),
          type: chartData.isPredicted[i] ? '预测值' : '实际值'
        })
      }
    }
    
    // 检查是否有有效数据
    if (recentData.length === 0) {
      analysisContent.value = '**数据无效**\n\n当前数据集中所有值均为空，无法进行分析。请选择包含有效数据的时间范围。'
      return
    }
    
    console.log('处理后的数据:', recentData)

    // 获取指标名称
    const indicatorNames = {
      gdp: 'GDP增速',
      retail: '社会消费品零售总额',
      cpi: '居民消费价格指数(CPI)',
      ppi: '工业生产者出厂价格指数(PPI)',
      investment: '固定资产投资完成额'
    }
    
    const indicatorId = route.params.indicatorId
    const indicatorName = indicatorNames[indicatorId] || chartData.name
    
    // 构建prompt
    const prompt = `请你以中国宏观经济分析专家的身份，为下列数据编写一份报告，并以"${indicatorName}指标预测依据分析"为标题。报告应简述预测值的合理性与依据。

已知信息：
• 历史数据（最近15期）：${recentData.filter(d => d.type === '实际值').slice(-15).map(d => d.value).join(', ')}
• 预测数据：${recentData.filter(d => d.type === '预测值').slice(-15).map(d => d.value).join(', ')}
• 数据时间范围：${recentData[Math.max(0, recentData.length - 15)].date} 至 ${recentData[recentData.length-1].date}

报告结构如下：

1. 标题："${indicatorName}指标预测依据分析"

2. 宏观背景与政策导向
- 简述中国当前经济形势
- 引用习近平总书记及党的重要会议关于经济工作的指导思想
- 说明政策环境对该指标影响

3. 历史趋势分析
- 回顾历史数据中该指标的波动与趋势
- 分析关键转折点及其原因

4. 国际对标与参考
- 比较国际机构（IMF、世行等）对中国相关指标的预测
- 说明所处合理区间

5. 支撑预测的关键因素
- 产业升级对指标的影响
- 内需外需变化趋势
- 宏观调控手段的作用

6. 预测值合理性说明
- 结合官方与国际预测
- 论证预测值的适度性与合理性

7. 风险与展望
- 分析潜在不确定性
- 说明政策应对措施
- 强调在党的坚强领导下，中国经济的韧性与预测的依据

请以专业、权威的语言撰写报告，确保逻辑清晰、论述有力。重点引用：
1. 习近平总书记关于经济高质量发展、供给侧结构性改革的论述
2. 党的重要会议（如中央经济工作会议）对经济工作的指导精神
3. 国际权威机构对中国经济指标的评估
4. 中国官方经济数据（国家统计局、人民银行、财政部等）

以下是具体的数据内容：${JSON.stringify(recentData)}`

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
    let buffer = ''
    let result = ''
    let isFirstMessage = true

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      // Decode the current chunk and add it to the buffer
      buffer += decoder.decode(value, { stream: true })
      
      // Split the buffer by newlines to process each complete message
      const lines = buffer.split('\n')
      
      // Keep the last (potentially incomplete) line in the buffer
      buffer = lines.pop() || ''
      
      // Process each complete line
      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          try {
            const jsonStr = line.slice(5).trim() // Remove 'data: ' prefix
            if (jsonStr) {
              const data = JSON.parse(jsonStr)
              // Check if this is a content message
              if (data.content && Array.isArray(data.content)) {
                for (const item of data.content) {
                  if (item.outputs && item.outputs.text) {
                    // Skip the first message
                    if (isFirstMessage) {
                      isFirstMessage = false
                      continue
                    }
                    
                    // For thought and text content types, append the text
                    if (typeof item.outputs.text === 'string') {
                      result += item.outputs.text
                    }
                  }
                }
                // Update the display after each processed message
                analysisContent.value = result
              }
            }
          } catch (e) {
            console.error('Error parsing stream data:', e)
          }
        }
      }
    }

    // Process any remaining data in the buffer
    if (buffer.trim().startsWith('data: ')) {
      try {
        const jsonStr = buffer.slice(5).trim()
        if (jsonStr) {
          const data = JSON.parse(jsonStr)
          if (data.content && Array.isArray(data.content)) {
            for (const item of data.content) {
              if (item.outputs && item.outputs.text) {
                // Skip the first message (if it's in the buffer)
                if (isFirstMessage) {
                  isFirstMessage = false
                  continue
                }
                
                if (typeof item.outputs.text === 'string') {
                  result += item.outputs.text
                }
              }
            }
            analysisContent.value = result
          }
        }
      } catch (e) {
        console.error('Error parsing final buffer:', e)
      }
    }

    isLoading.value = false
  } catch (error) {
    console.error('分析过程出错:', error)
    analysisContent.value = '**分析失败**\n\n无法获取分析结果，请稍后重试。'
    isLoading.value = false
  }
}

const route = useRoute()
const indicatorId = computed(() => route.params.indicatorId)

// 在组件挂载时加载数据
onMounted(async () => {
  if (indicatorId.value) {
    const data = await loadCSVData(indicatorId.value)
    if (data) {
      updateChartOption([data])
      await getAnalysis(data)
    }
  }
})

// Function to load CSV data based on indicatorId
const loadCSVData = async (indicatorId) => {
  try {
    // Load seasonal GDP data
    const gdpResponse = await fetch(new URL(`/data/seasonal_gdp.csv`, window.location.origin))
    const gdpText = await gdpResponse.text()
    const gdpRows = gdpText.replace(/^\ufeff/, '').split('\n').slice(1) // Skip header row
    
    if (indicatorId === 'gdp') {
      const data = {
        dates: [],
        values: [],
        isPredicted: [],
        confidenceInterval: []
      }
      
      gdpRows.forEach(row => {
        if (!row.trim()) return
        const [date, valueStr] = row.split(',')
        if (!valueStr) return
        
        // Check for prediction interval (±)
        if (valueStr.trim().includes('±')) {
          const [baseValue, interval] = valueStr.trim().split('±')
          const value = parseFloat(baseValue)
          const intervalValue = parseFloat(interval)
          data.dates.push(date.trim())
          data.values.push(value)
          data.isPredicted.push(true)
          data.confidenceInterval.push([
            value - intervalValue,
            value + intervalValue
          ])
        } else {
          data.dates.push(date.trim())
          data.values.push(parseFloat(valueStr))
          data.isPredicted.push(false)
          data.confidenceInterval.push(null)
        }
      })
      
      chartData.value = data
      return data
    }

    // Load monthly data
    const monthlyResponse = await fetch(new URL('/data/monthly_data.csv', window.location.origin))
    const monthlyText = await monthlyResponse.text()
    const monthlyRows = monthlyText.replace(/^\ufeff/, '').split('\n').slice(1)
    
    if (['retail', 'cpi', 'ppi', 'investment'].includes(indicatorId)) {
      const data = {
        dates: [],
        values: [],
        isPredicted: [],
        confidenceInterval: []
      }

      const indicatorIndex = {
        retail: 1,
        cpi: 2,
        ppi: 3,
        investment: 4
      }[indicatorId]

      monthlyRows.forEach(row => {
        if (!row.trim()) return
        const columns = row.split(',')
        const date = columns[0]
        const valueStr = columns[indicatorIndex]
        
        if (!valueStr) return
        
        if (valueStr.trim().includes('±')) {
          const [baseValue, interval] = valueStr.trim().split('±')
          const value = parseFloat(baseValue)
          const intervalValue = parseFloat(interval)
          data.dates.push(date.trim())
          data.values.push(value)
          data.isPredicted.push(true)
          data.confidenceInterval.push([
            value - intervalValue,
            value + intervalValue
          ])
        } else {
          data.dates.push(date.trim())
          data.values.push(parseFloat(valueStr))
          data.isPredicted.push(false)
          data.confidenceInterval.push(null)
        }
      })
      
      chartData.value = data
      return data
    }

    return null
  } catch (error) {
    console.error('加载CSV数据出错:', error)
    return null
  }
}
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>