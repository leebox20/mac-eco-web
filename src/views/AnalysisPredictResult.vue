<template>
  <div class="min-h-screen bg-[#F2F5F8]">
    <TheHeader />
    
    <!-- 面包屑导航 -->

    <div class="bg-[#348fef]  py-6 px-4  border-t border-white border-opacity-10">
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
    <main class="container mx-auto py-6 px-4">
      <!-- 趋势对比图表 -->
      <div class="mb-8">
        <div class="bg-white rounded-lg shadow-sm">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="text-lg font-medium text-gray-900">预测走势</h2>
          </div>
          <div class="p-6 h-[400px]">
            <v-chart class="chart" :option="chartOption" autoresize />
          </div>
        </div>
      </div>

      <!-- 分析进度区域 -->
      <div v-if="isLoading" class="bg-white rounded-lg shadow-sm p-6 mb-8">
        <h3 class="text-lg font-medium text-center text-gray-900 mb-6">
          AI 正在分析数据
        </h3>
        
        <!-- 分析进度列表 -->
        <div class="max-w-2xl mx-auto space-y-4">
          <div v-for="(item, index) in analysisSteps" 
               :key="index"
               class="flex items-center space-x-4">
            <!-- 加载图标 -->
            <div class="flex-shrink-0">
              <div v-if="item.status === 'pending'"
                   class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin">
              </div>
              <CheckCircleIcon v-else-if="item.status === 'completed'"
                            class="w-6 h-6 text-green-500" />
              <CircleIcon v-else
                       class="w-6 h-6 text-gray-300" />
            </div>
            
            <!-- 进度文本 -->
            <div class="flex-grow">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-900">
                  {{ item.label }}
                </span>
                <span v-if="item.progress" 
                      class="text-sm text-gray-500">
                  {{ item.progress }}%
                </span>
              </div>
              <!-- 进度条 -->
              <div v-if="item.status === 'pending'"
                   class="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full transition-all duration-300"
                     :style="{ width: `${item.progress}%` }">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 提示文本 -->
        <p class="text-sm text-gray-500 text-center mt-6">
          {{ currentLoadingMessage }}
        </p>
      </div>

      <!-- 分析结果区域 -->
      <div v-show="!isLoading" 
           class="opacity-0 transition-all duration-500"
           :class="{ 'opacity-100': !isLoading }">
        <div class="grid-container">
          <!-- 左右卡片内容 -->
          <template v-if="parsedReferences.length && parsedInterpretation.length">
            <!-- 滑动控制区 -->
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-medium text-gray-900">分析结果</h2>
              <div class="flex items-center space-x-4">
                <span class="text-base font-medium text-gray-600">
                  {{ currentPage + 1 }} / {{ totalPages }}
                </span>
              </div>
            </div>

            <!-- 卡片容器 -->
            <div class="relative">
              <!-- 左箭头 -->
              <button @click="prevPage" 
                      :disabled="currentPage === 0"
                      class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-6 z-10
                             transition-all duration-200 ease-in-out
                             disabled:opacity-0 disabled:invisible
                             hover:scale-110 focus:outline-none">
                <div class="flex items-center justify-center w-12 h-12 
                            bg-white rounded-full shadow-lg
                            text-gray-600 hover:text-blue-600">
                  <ChevronLeftIcon class="h-8 w-8" />
                </div>
              </button>

              <!-- 右箭头 -->
              <button @click="nextPage" 
                      :disabled="currentPage >= totalPages - 1"
                      class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-6 z-10
                             transition-all duration-200 ease-in-out
                             disabled:opacity-0 disabled:invisible
                             hover:scale-110 focus:outline-none">
                <div class="flex items-center justify-center w-12 h-12 
                            bg-white rounded-full shadow-lg
                            text-gray-600 hover:text-blue-600">
                  <ChevronRightIcon class="h-8 w-8" />
                </div>
              </button>

              <!-- 卡片容器 -->
              <div class="relative overflow-hidden">
                <div class="flex transition-transform duration-300 ease-in-out"
                     :style="{ transform: `translateX(-${currentPage * 100}%)` }">
                  <div v-for="(_, index) in totalPages" 
                       :key="index"
                       class="w-full flex-shrink-0 grid grid-cols-2 gap-8 px-4">
                    <!-- 左侧：相关资料卡片 -->
                    <div v-if="parsedReferences[index]"
                         class="bg-white rounded-lg shadow-sm">
                      <div class="px-6 py-4 border-b border-gray-100">
                        <h3 class="text-base font-medium text-gray-900">
                          {{ parsedReferences[index].title }}
                        </h3>
                      </div>
                      <div class="p-6">
                        <div class="prose prose-sm max-w-none" 
                             v-html="renderMarkdown(parsedReferences[index].content)">
                        </div>
                      </div>
                    </div>

                    <!-- 右侧：AI解读卡片 -->
                    <div v-if="parsedInterpretation[index]"
                         class="bg-white rounded-lg shadow-sm">
                      <div class="px-6 py-4 border-b border-gray-100">
                        <h3 class="text-base font-medium text-gray-900">
                          {{ getAIInterpretationTitle(parsedInterpretation[index].title) }}
                        </h3>
                      </div>
                      <div class="p-6">
                        <div class="prose prose-sm max-w-none" 
                             v-html="renderMarkdown(parsedInterpretation[index].content)">
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 改进的页面指示器 -->
            <div class="flex justify-center items-center space-x-3 mt-8">
              <div v-for="index in totalPages" 
                   :key="index"
                   @click="currentPage = index - 1"
                   :class="[
                     'cursor-pointer transition-all duration-200 ease-in-out',
                     currentPage === index - 1 
                       ? 'w-8 h-3 bg-blue-600' 
                       : 'w-3 h-3 bg-gray-300 hover:bg-gray-400',
                     'rounded-full'
                   ]"
                   :title="`第 ${index} 页`">
              </div>
            </div>

            <!-- 添加键盘快捷键提示 -->
            <div class="text-center mt-4 text-sm text-gray-500">
              使用键盘 ← → 快捷键可快速翻页
            </div>
          </template>
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
  XIcon,
  ChevronLeftIcon,
  CheckCircleIcon,
  CircleIcon
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
  linkify: true,
  typographer: true
})

// 自定义渲染规则
md.renderer.rules.paragraph_open = () => '<p class="mb-4 text-gray-600 leading-relaxed">'
md.renderer.rules.list_item_open = () => '<li class="mb-2 text-gray-600">'
md.renderer.rules.heading_open = (tokens, idx) => {
  const tag = tokens[idx].tag
  return `<${tag} class="text-gray-900 font-medium mb-4">`
}

// 解析markdown内容
const renderMarkdown = (content) => {
  if (!content) return ''
  
  content = content.replace(/\^(\[.*?\])+\^/g, (match, p1) => {
    const citations = p1.replace(/\[(\d+)\]/g, 
      '<span class="citation-tag">$1</span>')
    return citations
  })
  
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

  // 分离��际值和预测值
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

// 添加 isLoading ref 定义
const isLoading = ref(false)

// 分析结果内容
const analysisContent = ref({
  aiInterpretation: '',
  references: ''
})

// 分析步骤状态
const analysisSteps = ref([
  { label: '收集历史数据', status: 'waiting', progress: 0 },
  { label: '分析宏观趋势', status: 'waiting', progress: 0 },
  { label: '评估市场影响', status: 'waiting', progress: 0 },
  { label: '生成预期预测', status: 'waiting', progress: 0 }
])

// 加载提示消息
const loadingMessages = [
  '正在深入分析历史数据模式...',
  '正在评估宏观经济指标关联性...',
  '正在计算市场影响因素权重...',
  '正在生成综合预测结论...',
  '正在优化分析报告格式...'
]

const currentLoadingMessage = ref(loadingMessages[0])

// 模拟进度更新
const simulateProgress = async () => {
  for (let stepIndex = 0; stepIndex < analysisSteps.value.length; stepIndex++) {
    const step = analysisSteps.value[stepIndex]
    step.status = 'pending'
    currentLoadingMessage.value = loadingMessages[stepIndex]
    
    // 模拟该步骤的进度
    for (let progress = 0; progress <= 100; progress += 5) {
      step.progress = progress
      await new Promise(resolve => setTimeout(resolve, 100)) // 每5%增加100ms
    }
    
    step.status = 'completed'
  }
  
  currentLoadingMessage.value = loadingMessages[4]
  await new Promise(resolve => setTimeout(resolve, 500))
}

// 修改获取分析方法
const getAnalysis = async (chartData) => {
  try {
    isLoading.value = true
    
    // 重置所有步骤状态和内容
    analysisSteps.value.forEach(step => {
      step.status = 'waiting'
      step.progress = 0
    })
    
    // 重置分析内容
    analysisContent.value = {
      aiInterpretation: '',
      references: ''
    }
    
    // 开始模拟进度
    await simulateProgress()
    
    // 实际的API调用
    if (!chartData || !chartData.values || !Array.isArray(chartData.values)) {
      throw new Error('图表数据无效')
    }

    // 获取最新的预测值
    const predictedValues = chartData.values.filter((_, index) => chartData.isPredicted[index])
    if (!predictedValues.length) {
      throw new Error('没有找到预测值')
    }
    const latestPrediction = predictedValues[0]

    // 定义所有需要请求的分析模块
    const analysisModules = [
      { endpoint: 'historical', name: '历史资料' },
      { endpoint: 'macro', name: '宏观分析' },
      { endpoint: 'market', name: '市场分析' },
      { endpoint: 'expectation', name: '预期分析' }
    ]

    // 并行请求所有分析模块
    const analysisPromises = analysisModules.map(async module => {
      const response = await fetch(`${API_BASE_URL}/api/gdp-analysis/${module.endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(latestPrediction)
      })

      if (!response.ok) {
        throw new Error(`${module.name}请求失败`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let moduleContent = {
        aiInterpretation: [],
        references: []
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        try {
          const data = JSON.parse(chunk)
          if (data.result) {
            Object.entries(data.result).forEach(([key, text]) => {
              if (key.includes('Paragraph')) {
                moduleContent.aiInterpretation.push(text)
              } else {
                moduleContent.references.push(text)
              }
            })
          }
        } catch (e) {
          console.error('解析流数据失败:', e)
        }
      }

      return { 
        module: module.endpoint, 
        content: moduleContent 
      }
    })

    // 等待所有分析完成
    const results = await Promise.all(analysisPromises)
    
    // 组合所有分析结果
    let finalContent = {
      aiInterpretation: '',
      references: ''
    }

    // 确保按固定顺序处理结果
    analysisModules.forEach(module => {
      const result = results.find(r => r.module === module.endpoint)
      if (result) {
        const moduleName = module.name
        
        // 添加AI解读内容
        if (result.content.aiInterpretation.length > 0) {
          finalContent.aiInterpretation += `## ${moduleName}\n\n`
          finalContent.aiInterpretation += result.content.aiInterpretation.join('\n\n') + '\n\n'
        }
        
        // 添加参考资料内容
        if (result.content.references.length > 0) {
          finalContent.references += `## ${moduleName}\n\n`
          finalContent.references += result.content.references.join('\n\n') + '\n\n'
        }
      }
    })

    // 更新分析内容
    analysisContent.value = finalContent

    // 确保加载动画完全展示完毕后再显示结果
    await new Promise(resolve => setTimeout(resolve, 500))
    isLoading.value = false

  } catch (error) {
    console.error('分析过程出错:', error)
    await new Promise(resolve => setTimeout(resolve, 500))
    isLoading.value = false
    analysisContent.value = {
      aiInterpretation: '**分析失败**\n\n无法获取AI解读结果，请稍后重试。',
      references: '**分析失败**\n\n无法获取相关资料，请稍后重试。'
    }
  }
}

const route = useRoute()
const indicatorId = computed(() => route.params.indicatorId)

// 在组挂载时加载数据
onMounted(async () => {
  if (indicatorId.value) {
    const data = await loadCSVData(indicatorId.value)
    if (data) {
      updateChartOption([data])
      await getAnalysis(data)
    }
  }

  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})

const handleKeyPress = (event) => {
  if (event.key === 'ArrowLeft') {
    prevPage()
  } else if (event.key === 'ArrowRight') {
    nextPage()
  }
}

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

// 移除之前的 getReferencesTitle 函数，不再需要

// 移除之前的 parsedReferences 修改，保持原样
const parsedReferences = computed(() => {
  if (!analysisContent.value.references) return []
  return parseContentSections(analysisContent.value.references)
})

// AI解读部分保持不变
const parsedInterpretation = computed(() => {
  if (!analysisContent.value.aiInterpretation) return []
  return parseContentSections(analysisContent.value.aiInterpretation)
})

// 解析 markdown 内容中的部分
function parseContentSections(content) {
  const sections = []
  const lines = content.split('\n')
  let currentSection = null

  lines.forEach(line => {
    if (line.startsWith('## ')) {
      if (currentSection) {
        sections.push(currentSection)
      }
      currentSection = {
        title: line.replace('## ', '').trim(),
        content: ''
      }
    } else if (currentSection) {
      currentSection.content += line + '\n'
    }
  })

  if (currentSection) {
    sections.push(currentSection)
  }

  return sections
}

// 添加 AI 解读标题转换函数
const getAIInterpretationTitle = (title) => {
  const titleMap = {
    '历史分析': 'AI历史解读',
    '宏观分析': 'AI宏观解读',
    '市场分析': 'AI市场解读',
    '预期分析': 'AI预期解读'
  }
  return titleMap[title] || `AI${title}`
}

// 分页控制
const currentPage = ref(0)

// 计算总页数
const totalPages = computed(() => {
  return Math.max(
    parsedReferences.value.length,
    parsedInterpretation.value.length
  )
})

// 翻页方法
const nextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
  }
}
</script>

<style scoped>
/* 所有样式都限定在 analysis-predict-result 类下 */
.analysis-predict-result {
  background-color: #fff;
}

.analysis-predict-result .grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  padding: 1rem;
}

.analysis-predict-result .card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.analysis-predict-result .prose {
  color: #374151;
  line-height: 1.75;
  font-size: 0.875rem;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 添加淡入效果 */
.opacity-0 {
  opacity: 0;
}

.opacity-100 {
  opacity: 1;
}

.transition-all {
  transition-property: all;
  transition-duration: 500ms;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* 进度条动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>