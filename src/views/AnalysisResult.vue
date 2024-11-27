<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />
    
    <!-- 面包屑导航 -->

    <div class="bg-[#4080ff]  py-6 px-4 border-t border-gray-400 border-capacity-40">
      <div class="container mx-auto px-10 flex items-center space-x-2 ">
        <arrow-down-wide-narrow class="h-5 w-5 text-gray-200" />
        <router-link to="/database" class="text-gray-200 text-sm">
          数据库
        </router-link>
          <ChevronRightIcon class="h-4 w-4 text-gray-200" />
          <span class="text-gray-200 text-sm">对比结果</span>
      </div>
    </div>


    <!-- 主要内容区域 -->
    <main class="container mx-auto py-6 px-4  ">
        <!-- 趋势对比图表 -->
      <div class="rounded-lg  mb-6 px-6">
        <div class="px-4  py-2 border-b  rounded-t-lg bg-gray shadow">
          <h2 class="text-sm text-left font-medium">趋势对比</h2>
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
        </div>
      </div>
    </main>
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
    const decoder = new TextDecoder()
    let result = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      // 处理 SSE 格式的数据
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.answer) {
              result += data.answer
              // 直接更新markdown内容
              analysisContent.value = result
            }
          } catch (e) {
            console.error('解析响应数据失败:', e)
          }
        }
      }
    }
  } catch (error) {
    console.error('获取分析失败:', error)
    analysisContent.value = '**分析失败**\n\n抱歉，获取分析结果时发生错误，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}

const route = useRoute()
const chartIds = computed(() => {
  const ids = route.query.charts
  return ids ? ids.split(',') : []
})

// 从缓存中获取图表数据
const loadChartData = (chartIds) => {
  try {
    // 验证元数据
    const chartMetaStr = sessionStorage.getItem('selectedChartMeta')
    const totalChunks = sessionStorage.getItem('selectedChartChunks')
    if (!chartMetaStr || !totalChunks) {
      console.error('No chart metadata or chunk info found')
      return null
    }

    const chartMeta = JSON.parse(chartMetaStr)
    const selectedMeta = chartMeta.filter(meta => chartIds.includes(String(meta.id)))

    // 从所有数据块中加载数据
    const chartsData = []
    const numChunks = parseInt(totalChunks)
    
    for (let i = 0; i < numChunks; i++) {
      const chunkStr = sessionStorage.getItem(`selectedChartData_${i}`)
      if (!chunkStr) {
        console.error(`Missing chunk ${i}`)
        continue
      }
      
      const chunk = JSON.parse(chunkStr)
      chunk.forEach(chart => {
        if (chartIds.includes(String(chart.id))) {
          const meta = selectedMeta.find(m => m.id === chart.id)
          if (meta) {
            chartsData.push({
              id: chart.id,
              name: meta.name,
              time: chart.time,
              data: chart.data
            })
          }
        }
      })
    }

    // 验证是否所有选中的图表都被加载
    if (chartsData.length !== selectedMeta.length) {
      console.error(`Not all charts were loaded. Expected ${selectedMeta.length}, got ${chartsData.length}`)
      return null
    }

    // 按照原始顺序排序
    chartsData.sort((a, b) => {
      const aIndex = chartIds.indexOf(String(a.id))
      const bIndex = chartIds.indexOf(String(b.id))
      return aIndex - bIndex
    })

    return chartsData
  } catch (e) {
    console.error('Failed to load chart data:', e)
    return null
  }
}

// 更新图表配置
const updateChartOption = async (selectedCharts) => {
  const chartData = loadChartData(selectedCharts)
  if (!chartData || !chartData.length) {
    console.error('No chart data found in cache')
    return
  }

  // 更新图表配置
  chartOption.value = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(param => {
          result += param.marker + ' ' + param.seriesName + ': ' + param.value + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: chartData.map(d => d.name),
      type: 'scroll',
      orient: 'horizontal',
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData[0].time,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(chartData[0].time.length / 10)
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: chartData.map(d => ({
      name: d.name,
      type: 'line',
      data: d.data,
      smooth: true,
      showSymbol: false,
      emphasis: {
        focus: 'series'
      }
    }))
  }

  // 在图表数据加载完成后获取分析
  if (chartData.length > 0) {
    await getAnalysis(chartData[0])
  }
}

// 根据 chartIds 获取对应的图表数据
onMounted(() => {
  if (chartIds.value.length) {
    updateChartOption(chartIds.value)
  }
})
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style>