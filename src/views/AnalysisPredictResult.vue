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
          <span class="text-gray-200 text-sm">{{ indicatorId === 'macro' ? '整体宏观分析' : '分析结果' }}</span>
      </div>
    </div>


    <!-- 主要内容区域 -->
    <main class="container mx-auto py-6 px-4">
      <!-- 趋势对比图表 -->
      <div class="mb-8">
        <div class="bg-white rounded-lg shadow-sm">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="text-lg font-medium text-gray-900">
              {{ indicatorId === 'macro' ? '关键经济指标走势' : '预测走势' }}
            </h2>
          </div>
          <div class="p-6 h-[500px]">
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

        <!-- 宏观分析额外loading提示 -->
        <div v-if="indicatorId === 'macro'" class="mt-4 text-center">
          <div class="inline-flex items-center px-4 py-2 bg-blue-50 rounded-lg">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span class="text-sm text-blue-700">AI正在深度分析中，预计还需60-90秒...</span>
          </div>
        </div>
      </div>

      <!-- 分析结果区域 -->
      <div v-show="!isLoading" 
           class="opacity-0 transition-all duration-500"
           :class="{ 'opacity-100': !isLoading }">
        <div class="grid-container">
          <!-- 分析结果标题 -->
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-medium text-gray-900">{{ indicatorId === 'macro' ? '宏观经济整体分析' : '分析结果' }}</h2>
          </div>

          <!-- 简化的卡片容器 - 宏观分析使用单列布局 -->
          <div v-if="indicatorId === 'macro'" class="space-y-8">
            <!-- 宏观分析：AI解读卡片 -->
            <div class="bg-white rounded-lg shadow-sm">
              <div class="px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-medium text-gray-900">宏观经济综合分析</h3>
              </div>
              <div class="p-6">
                <div class="prose prose-sm max-w-none"
                     v-html="renderMarkdown(analysisContent.aiInterpretation)">
                </div>
              </div>
            </div>

            <!-- 宏观分析：参考资料卡片 -->
            <div class="bg-white rounded-lg shadow-sm">
              <div class="px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-medium text-gray-900">数据来源与参考</h3>
              </div>
              <div class="p-6">
                <div class="prose prose-sm max-w-none"
                     v-html="renderMarkdown(analysisContent.references)">
                </div>
              </div>
            </div>
          </div>

          <!-- 单个指标分析：双列布局 -->
          <div v-else class="grid grid-cols-2 gap-8">
            <!-- 左侧：参考资料卡片 -->
            <div class="bg-white rounded-lg shadow-sm">
              <div class="px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-medium text-gray-900">参考资料</h3>
              </div>
              <div class="p-6">
                <div class="prose prose-sm max-w-none"
                     v-html="renderMarkdown(analysisContent.references)">
                </div>
              </div>
            </div>

            <!-- 右侧：AI解读卡片 -->
            <div class="bg-white rounded-lg shadow-sm">
              <div class="px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-medium text-gray-900">AI解读</h3>
              </div>
              <div class="p-6">
                <div class="prose prose-sm max-w-none"
                     v-html="renderMarkdown(analysisContent.aiInterpretation)">
                </div>
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
  UserIcon,
  SearchIcon,
  ChevronDownIcon,
  BarChartIcon,
  XIcon,
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

// 图表配置 - 初始化为空配置，将由updateChartOption函数填充
const chartOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: [],
    top: 0,
    textStyle: {
      color: '#666'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '80px',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: {
    type: 'value',
    name: '%',
    nameLocation: 'end'
  },
  series: []
})

// 宏观分析多指标图表更新函数
const updateMacroChartOption = (indicators) => {
  if (!indicators || indicators.length === 0) return

  console.log('更新宏观分析图表，指标数量:', indicators.length)

  // 选择主要指标进行显示（避免图表过于复杂）
  const selectedIndicators = indicators.filter(indicator =>
    ['GDP不变价:当季同比', '社会消费品零售总额', 'CPI', 'PPI', '工业增加值', 'M2货币供应量'].includes(indicator.name)
  ).slice(0, 6) // 最多显示6个指标

  if (selectedIndicators.length === 0) return

  // 获取所有时间点的并集
  const allDates = new Set()
  selectedIndicators.forEach(indicator => {
    indicator.data.forEach(point => allDates.add(point.date))
  })
  const sortedDates = Array.from(allDates).sort()

  // 按单位分组指标
  const percentageIndicators = [] // 百分比指标（左Y轴）
  const absoluteIndicators = [] // 绝对值指标（右Y轴）

  selectedIndicators.forEach(indicator => {
    if (indicator.unit === '%' || indicator.name.includes('同比')) {
      percentageIndicators.push(indicator)
    } else {
      absoluteIndicators.push(indicator)
    }
  })

  // 构建系列数据
  const series = []
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272']
  let colorIndex = 0

  // 添加百分比指标系列
  percentageIndicators.forEach(indicator => {
    const seriesData = sortedDates.map(date => {
      const dataPoint = indicator.data.find(d => d.date === date)
      return dataPoint ? dataPoint.value : null
    })

    series.push({
      name: indicator.name,
      type: 'line',
      yAxisIndex: 0, // 使用左Y轴
      data: seriesData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: {
        width: 2,
        color: colors[colorIndex % colors.length]
      },
      itemStyle: {
        color: colors[colorIndex % colors.length]
      }
    })
    colorIndex++
  })

  // 添加绝对值指标系列
  absoluteIndicators.forEach(indicator => {
    const seriesData = sortedDates.map(date => {
      const dataPoint = indicator.data.find(d => d.date === date)
      return dataPoint ? dataPoint.value : null
    })

    series.push({
      name: indicator.name,
      type: 'line',
      yAxisIndex: 1, // 使用右Y轴
      data: seriesData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: {
        width: 2,
        color: colors[colorIndex % colors.length],
        type: 'dashed' // 用虚线区分
      },
      itemStyle: {
        color: colors[colorIndex % colors.length]
      }
    })
    colorIndex++
  })

  // 更新图表配置
  chartOption.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(param => {
          const indicator = selectedIndicators.find(ind => ind.name === param.seriesName)
          const unit = indicator ? indicator.unit : ''
          result += param.marker + ' ' + param.seriesName + ': ' +
                   (param.value !== null ? param.value.toFixed(2) + unit : '无数据') + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: selectedIndicators.map(ind => ind.name),
      top: 10,
      type: 'scroll',
      textStyle: {
        color: '#666'
      }
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '80px',
      top: '60px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: sortedDates,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(sortedDates.length / 12) // 控制标签密度
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '百分比 (%)',
        nameLocation: 'middle',
        nameGap: 50,
        position: 'left',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      {
        type: 'value',
        name: '绝对值',
        nameLocation: 'middle',
        nameGap: 50,
        position: 'right',
        axisLabel: {
          formatter: function(value) {
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + '万'
            }
            return value.toFixed(1)
          }
        }
      }
    ],
    series: series,
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: Math.max(0, 100 - (24 / sortedDates.length) * 100), // 默认显示最近24个月
        end: 100
      }
    ]
  }

  console.log('宏观分析图表配置更新完成')
}

const updateChartOption = (data) => {
  if (!data || !data.length || !data[0]) return

  const currentData = data[0]

  // 检查是否为宏观分析多指标数据
  if (currentData.isMacroAnalysis && currentData.multiIndicatorData) {
    updateMacroChartOption(currentData.multiIndicatorData)
    return
  }

  const dates = currentData.dates || []
  const values = currentData.values || []
  const isPredicted = currentData.isPredicted || []
  const confidenceInterval = currentData.confidenceInterval || []
  const unit = currentData.unit || '%'

  // 生成完整的图表配置，与Prediction组件保持一致
  chartOption.value = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const date = dates[dataIndex]
        const value = values[dataIndex]
        const isPred = isPredicted[dataIndex]
        const confInterval = confidenceInterval[dataIndex]

        let tooltip = `${date}<br/>`
        if (isPred) {
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}${unit}</span>`
          if (confInterval) {
            tooltip += `<br/><span style="color: #F56C6C">置信区间: [${confInterval[0].toFixed(2)}${unit}, ${confInterval[1].toFixed(2)}${unit}]</span>`
          }
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}${unit}</span>`
        }
        return tooltip
      }
    },
    legend: {
      data: ['数据线', '预测段', '预测区间上界', '预测区间下界'],
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
        start: Math.max(0, (dates.length - 8) / dates.length * 100),
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
        start: Math.max(0, (dates.length - 8) / dates.length * 100),
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      data: dates,
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
      name: unit,
      nameLocation: 'end'
    },
    series: [
      // 历史数据线
      {
        name: '历史数据',
        type: 'line',
        data: values.map((value, index) =>
          !isPredicted[index] ? value : null
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
        data: values.map((value, index) =>
          isPredicted[index] ? value : null
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
        data: values.map((value, index) => {
          const firstPredictedIndex = isPredicted.findIndex(p => p)
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
        data: confidenceInterval.map((interval, index) =>
          (interval && isPredicted[index]) ? interval[1] : null
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
        data: confidenceInterval.map((interval, index) =>
          (interval && isPredicted[index]) ? interval[0] : null
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



// 从关键数据报告.md获取预设分析内容
const getPresetAnalysisContent = (indicatorId) => {
  const analysisData = {
    retail: {
      title: '社会消费品零售总额',
      content: '社会消费品零售总额当月同比增速预测为5.30%，置信区间±0.28个百分点。本系统预测消费延续复苏态势。4月社零同比增长5.1%，略低于上月，表明消费回暖基础仍需巩固。耐用品消费在以旧换新等政策带动下回升，服务消费保持旺盛。在政策持续提振下，社零增速有望保持中速增长。'
    },
    cpi: {
      title: '消费者价格指数(CPI)',
      content: 'CPI当月同比预计仅+0.03%（±0.01个百分点），几乎零增长。物价低迷主要受国际油价下跌拖累：能源价格同比下降4.8%，对CPI下拉作用明显。核心CPI同比涨0.5%，显示内需依然温和。官方表态目前未现通缩风险。预计随着基数效应减退，下半年CPI涨幅将温和回升。'
    },
    ppi: {
      title: '生产者价格指数(PPI)',
      content: 'PPI当月同比预测为-2.43%（±0.11个百分点）。受全球大宗商品价格走低影响，4月PPI同比下降2.7%。尽管上游行业价格低迷，但中游材料价格降幅收窄，高端制造品价格转为同比上涨，工业品价格呈现企稳迹象。预计在稳增长政策带动下，PPI降幅将逐步收窄，下半年内需回暖有望促使价格企稳。'
    },
    industrial: {
      title: '工业增加值',
      content: '工业增加值当月同比预测增长9.16%（±0.03个百分点）。4月工业增加值同比增长6.1%，高技术和装备制造业增速达9-10%，新能源、新材料等产业产出强劲。出口需求回升和政策支持进一步巩固工业增长韧性。预计工业增速将保持平稳较快增长趋势。'
    },
    export: {
      title: '出口金额',
      content: '出口金额当月同比预测增长10.72%（±0.97个百分点），延续两位数增势。4月出口同比增9.3%（人民币计价），增速较3月回落但仍超预期。对美出口同比降21%，而对欧盟、东盟分别增8.3%、20.7%，有效弥补对美下滑。多元市场开拓和制造业竞争力使出口保持强劲，预计这一势头将在政策支持下延续。'
    },
    import: {
      title: '进口金额',
      content: '进口金额当月同比预测增长0.69%（±0.21个百分点），总体基本持平。3月进口同比下降3.5%，4月微增0.8%，显示国内需求略有改善但整体仍偏弱。主要大宗商品进口量价齐跌，对进口金额形成明显拖累。随着出口回暖带动部分原材料进口，加之稳内需政策逐步显效，进口降幅收窄并小幅转正。但整体内需偏弱，短期内进口仍将在低位徘徊。'
    },
    investment: {
      title: '固定资产投资',
      content: '固定资产投资累计同比预测增长3.91%（±0.09个百分点）。1-4月全国固定资产投资同比增长4.0%。房地产开发投资下滑(-10.3%)拖累总投资，但制造业和基础设施投资较快增长（+8.8%、+5.8%）提供支撑。各地加快专项债发行，推进重大项目建设，在一定程度上对冲了房地产低迷影响。预计基建和制造业投资增势延续，但房地产疲软将使总投资增速难以大幅回升。'
    },
    realestate: {
      title: '房地产开发投资',
      content: '房地产开发投资累计同比预测-10.27%（±0.15个百分点）。1-4月房地产投资同比下降10.3%。需求低迷、房企资金紧张导致投资持续萎缩。尽管去年底以来一线城市房价企稳、二手房交易回暖，楼市呈筑底迹象，但多数中小城市仍在下行调整。各地虽出台因城施策稳楼市政策，但购房信心恢复尚需时日。预计房地产投资降幅短期内难以明显收窄，下半年或在低位企稳。'
    },
    m2: {
      title: 'M2货币供应量',
      content: 'M2同比预测增长8.36%（±0.06个百分点），保持平稳适度扩张。当前M2增速虽较去年有所回落但仍高于名义GDP增速，显示货币政策维持宽松取向以支撑经济。5月央行下调政策利率并加大流动性投放，引导市场利率下行，支持信贷和社融增长。总体来看，M2适度扩张为经济复苏提供充裕资金。未来货币政策将平衡稳增长与防风险，M2增速有望与经济需求保持匹配水平。'
    },
    financing: {
      title: '社会融资规模',
      content: '社会融资规模当月新增预测为26451.18亿元（±150.77亿元），保持充裕增长。在银行信贷和政府债券双重支撑下，社融增量持续高位运行。前4月政府债券净融资4.85万亿元，同比多增3.58万亿元，为社融扩张提供强力支撑。央行5月下调政策利率并释放增量流动性，将进一步提振信贷投放和社融规模。社融增长势头良好，为实体经济提供有力资金支持。预计在政策推动下，社融增量将继续保持高位，以满足经济运行的融资需求。'
    },
    gdp: {
      title: '国内生产总值(GDP)',
      content: 'GDP增长保持稳定态势，经济运行总体平稳。在各项稳增长政策的支撑下，经济基本面持续向好。消费、投资、出口三大需求协调发力，为经济增长提供有力支撑。预计GDP将继续在合理区间运行，为实现全年经济社会发展目标奠定坚实基础。'
    },
    macro: {
      title: '中国宏观经济整体分析',
      content: `## 宏观经济运行总体评估

当前中国经济呈现稳中向好、结构优化、动力增强的运行特征。从最新预测数据看，主要经济指标保持在合理区间，经济韧性持续显现。

### 经济增长动能分析

**GDP增长稳健**：2025年Q2-Q4季度GDP增速预测分别为4.86%、5.49%、5.11%，显示经济增长动能稳定。从季度走势看，经济运行呈现先抑后扬态势，下半年增长动能有望增强。

**三驾马车协调发力**：
- **消费复苏稳健**：社会消费品零售总额同比增长5.30%，消费市场持续回暖
- **投资结构优化**：固定资产投资增长3.91%，其中制造业和基建投资保持较高增速
- **外贸韧性强劲**：出口增长10.72%，显著超出预期，展现较强国际竞争力

### 产业运行特征

**工业生产强劲**：工业增加值同比增长9.16%，高技术制造业和装备制造业引领增长，产业结构持续优化升级。新能源汽车、光伏、新材料等新兴产业保持高速增长。

**房地产调整延续**：房地产投资下降10.27%，行业仍在深度调整期。但一线城市房价企稳，政策效应逐步显现，预计下半年降幅有望收窄。

### 价格走势分析

**通胀压力较小**：
- CPI同比仅增0.03%，物价水平保持低位运行
- PPI同比下降2.43%，工业品价格仍有下行压力
- 核心CPI保持稳定，显示内需温和复苏

低通胀环境为货币政策提供了充足操作空间，有利于继续实施稳健偏宽松的政策取向。

### 金融环境评估

**流动性合理充裕**：
- M2同比增长8.36%，保持适度扩张
- 社会融资规模月增2.65万亿元，为实体经济提供有力支持
- 央行维持宽松政策基调，市场流动性充裕

金融对实体经济的支持力度持续加大，企业融资成本下降，有利于投资和消费需求释放。

### 风险因素与政策建议

**主要风险点**：
1. 外部环境不确定性增加，地缘政治风险上升
2. 房地产市场调整压力仍大，对相关产业链影响持续
3. 地方政府债务风险需密切关注
4. 青年就业压力较大，结构性矛盾突出

**政策建议**：
1. 继续实施积极的财政政策，加大基建投资力度
2. 保持货币政策稳健偏宽松，降低实体经济融资成本
3. 深化供给侧结构性改革，培育新质生产力
4. 稳妥推进房地产市场调整，防范系统性风险
5. 强化就业优先政策，特别关注青年群体就业

### 展望与结论

综合判断，中国经济正处于恢复向好的关键期。尽管面临诸多挑战，但经济长期向好的基本面没有改变。在政策持续发力和改革深化推进下，预计2025年经济将保持稳定增长，全年GDP增速有望达到5%左右的预期目标。

建议投资者和企业密切关注政策动向，把握结构性机会，特别是在新能源、高端制造、数字经济等领域的投资机会。同时要做好风险管理，应对可能的市场波动。`
    }
  }

  const data = analysisData[indicatorId] || analysisData.gdp

  // 对于宏观分析，直接返回完整内容
  if (indicatorId === 'macro') {
    return {
      aiInterpretation: data.content,
      references: `## 数据来源与参考

### 官方统计机构
- **国家统计局**：GDP、CPI、PPI、工业增加值、固定资产投资、社会消费品零售总额等核心指标
- **海关总署**：进出口贸易数据
- **中国人民银行**：M2货币供应量、社会融资规模等金融数据
- **国家发展改革委**：宏观经济政策与投资项目审批信息

### 权威研究报告
- **政府工作报告(2025年)**：年度经济目标与政策导向
- **中央经济工作会议公报**：经济工作总体部署
- **一季度货币政策执行报告**：货币政策取向与金融市场分析
- **国际货币基金组织(IMF)报告**：中国经济展望与政策建议

### 行业分析数据
- **中国银行研究院**：宏观经济金融展望
- **国务院发展研究中心**：产业发展与改革研究
- **中国社会科学院**：经济形势分析与预测
- **主要券商研究所**：行业深度分析报告

### 国际比较参考
- **世界银行**：全球经济展望与中国专章
- **经合组织(OECD)**：成员国经济数据对比
- **亚洲开发银行**：亚洲经济一体化报告
- **国际清算银行(BIS)**：全球金融市场分析`
    }
  }

  return {
    aiInterpretation: `## 核心数据解读

**${data.title}预测分析报告**

${data.content}

## 深度趋势分析

### 宏观经济背景
当前中国经济正处于转型升级的关键阶段，${data.title}作为重要经济指标，其表现直接反映了经济运行的内在动力和结构变化。在全球经济复苏不确定性增强的背景下，该指标的稳定性对于维护经济大局稳定具有重要意义。

### 政策传导机制
近期出台的一系列宏观调控政策正在逐步发挥作用，通过财政政策的精准发力和货币政策的灵活适度，为${data.title}的平稳运行创造了良好的政策环境。政策效应的逐步显现将为指标的中长期走势提供有力支撑。

### 市场动力分析
从市场层面看，${data.title}的变化体现了供需关系的动态调整。需求侧管理政策的持续优化，供给侧结构性改革的深入推进，以及新发展格局的加快构建，都为该指标的健康发展注入了新的活力。

## 风险因素评估

### 内部风险
- **结构性矛盾**：经济结构调整过程中可能出现的短期波动
- **区域差异**：不同地区发展不平衡对整体指标的影响
- **行业分化**：传统行业与新兴行业发展速度差异

### 外部风险
- **国际环境**：全球经济复苏节奏不一致带来的外部冲击
- **贸易摩擦**：国际贸易环境变化对相关指标的潜在影响
- **金融市场**：国际金融市场波动的传导效应

## 政策建议与展望

### 短期建议
1. **加强监测预警**：建立健全指标监测体系，及时识别潜在风险
2. **精准政策调控**：根据指标变化趋势，适时调整政策力度和方向
3. **优化市场环境**：继续深化改革，为市场主体创造更好的发展条件

### 中长期展望
展望未来，${data.title}有望在新发展理念指引下，实现更高质量、更可持续的发展。随着经济结构的持续优化和发展动能的加快转换，该指标将为中国经济的高质量发展提供更加坚实的支撑。`,

    references: `## 权威数据来源

### 官方统计机构
- **国家统计局**：《中华人民共和国2025年国民经济和社会发展统计公报》
- **中国人民银行**：《2025年第一季度货币政策执行报告》
- **国家发展改革委**：《2025年4月份宏观经济运行情况分析》
- **财政部**：《2025年1-4月全国财政收支情况》

### 行业监管部门
- **商务部**：对外贸易发展统计数据及分析报告
- **工业和信息化部**：工业经济运行监测分析
- **住房城乡建设部**：房地产市场运行情况统计
- **银保监会**：银行业保险业运行情况通报

## 政策文件依据

### 国家层面政策
- **《政府工作报告》(2025年)**：明确了${data.title}的年度目标和政策导向
- **《"十四五"规划纲要》**：提出了中长期发展目标和战略部署
- **中央经济工作会议精神**：确定了宏观政策的基调和重点任务

### 部门政策措施
- **国务院常务会议决定**：关于稳经济一揽子政策措施
- **央行货币政策委员会例会**：货币政策取向和操作指引
- **发改委投资政策**：重大项目投资和产业政策指导

## 专业机构分析

### 国际组织评估
- **国际货币基金组织(IMF)**：《世界经济展望》中国经济专章
- **世界银行**：《中国经济简报》季度更新
- **经济合作与发展组织(OECD)**：中国经济政策评估报告

### 国内研究机构
- **中国社会科学院**：《经济蓝皮书》年度报告
- **国务院发展研究中心**：宏观经济研究报告
- **中国人民大学国家发展与战略研究院**：宏观经济月度数据分析报告

### 金融机构观点
- **中国银行研究院**：宏观经济金融展望报告
- **招商银行研究院**：月度宏观经济分析
- **中信证券研究所**：宏观策略深度报告

## 历史数据对比

### 近期表现回顾
- **2024年全年**：${data.title}年度表现及主要特征分析
- **2023-2024年对比**：同期数据变化趋势及影响因素
- **季度环比分析**：最近8个季度的波动规律

### 长期趋势分析
- **"十三五"期间表现**：2016-2020年发展轨迹总结
- **疫情前后对比**：2019年与2021-2025年数据比较
- **改革开放以来**：长周期历史数据的演变规律

## 国际比较研究

### 主要经济体对比
- **美国**：相关指标的表现差异及政策环境比较
- **欧盟**：发展模式和政策工具的异同分析
- **日本**：结构调整期的经验借鉴和启示

### 新兴市场比较
- **金砖国家**：发展阶段相似经济体的表现对比
- **东南亚国家**：区域经济一体化背景下的协同发展
- **"一带一路"沿线国家**：合作发展的机遇与挑战`
  }
}

// 修改获取分析方法 - 支持真实API调用
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

    // 获取当前指标ID
    const currentIndicatorId = indicatorId.value || 'gdp'

    // 如果是宏观分析，调用真实API
    if (currentIndicatorId === 'macro') {
      console.log('开始调用宏观分析API...')

      // 开始模拟进度
      const progressPromise = simulateProgress()

      try {
        // 调用宏观分析API
        const response = await fetch(`${API_BASE_URL}/api/macro-analysis`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('宏观分析API响应:', result)
        
        if (result.status === 'success' && result.data) {
          // 等待进度动画完成
          await progressPromise

          // 解析API返回的分析内容
          let formattedAnalysis = ''
          try {
            // 尝试解析JSON格式的分析内容
            const analysisData = JSON.parse(result.data.analysis)

            // 格式化为Markdown
            if (analysisData.Historical_Economic_Cycle_Analysis_Module) {
              formattedAnalysis += `## 历史经济周期分析\n\n${analysisData.Historical_Economic_Cycle_Analysis_Module}\n\n`
            }

            if (analysisData.Long_term_trend_analysis_module) {
              formattedAnalysis += `## 长期趋势分析\n\n${analysisData.Long_term_trend_analysis_module}\n\n`
            }

            if (analysisData.First_Paragraph) {
              formattedAnalysis += `## 综合分析结论\n\n${analysisData.First_Paragraph}\n\n`
            }

            // 如果没有找到预期的字段，尝试其他可能的字段
            if (!formattedAnalysis) {
              Object.entries(analysisData).forEach(([key, value]) => {
                if (typeof value === 'string' && value.trim()) {
                  const title = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                  formattedAnalysis += `## ${title}\n\n${value}\n\n`
                }
              })
            }

          } catch (parseError) {
            // 如果不是JSON格式，直接使用原始内容
            console.log('分析内容不是JSON格式，使用原始内容')
            formattedAnalysis = result.data.analysis || '暂无分析内容'
          }

          // 使用格式化后的分析内容
          analysisContent.value = {
            aiInterpretation: formattedAnalysis || '暂无分析内容',
            references: `## 数据来源与参考

### 数据统计
- **指标数量**：${result.data.indicators_count || 0} 个
- **更新时间**：${result.data.update_time || '未知'}
- **数据来源**：${result.data.data_source || '实时分析'}

### 官方统计机构
- **国家统计局**：GDP、CPI、PPI、工业增加值、固定资产投资、社会消费品零售总额等核心指标
- **海关总署**：进出口贸易数据
- **中国人民银行**：M2货币供应量、社会融资规模等金融数据
- **国家发展改革委**：宏观经济政策与投资项目审批信息

### 权威研究报告
- **政府工作报告(2025年)**：年度经济目标与政策导向
- **中央经济工作会议公报**：经济工作总体部署
- **一季度货币政策执行报告**：货币政策取向与金融市场分析
- **国际货币基金组织(IMF)报告**：中国经济展望与政策建议`
          }
        } else {
          throw new Error('API返回数据格式错误')
        }
        
      } catch (apiError) {
        console.error('宏观分析API调用失败:', apiError)
        // 等待进度动画完成
        await progressPromise
        // 如果API调用失败，使用预设内容作为降级方案
        const presetContent = getPresetAnalysisContent(currentIndicatorId)
        analysisContent.value = presetContent
      }
      
    } else {
      // 其他指标继续使用预设内容
      await simulateProgress()
      
      // 验证数据
      if (!chartData || !chartData.values || !Array.isArray(chartData.values)) {
        throw new Error('图表数据无效')
      }
      
      // 使用关键数据报告.md中的预设分析内容
      const presetContent = getPresetAnalysisContent(currentIndicatorId)
      analysisContent.value = presetContent
    }

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
  console.log('AnalysisPredictResult组件挂载，indicatorId:', indicatorId.value)

  if (indicatorId.value) {
    console.log('开始加载数据，indicatorId:', indicatorId.value)
    const data = await loadAPIData(indicatorId.value)
    console.log('数据加载结果:', data)

    if (data) {
      // 更新图表配置（包括宏观分析的多指标图表）
      console.log('更新图表配置')
      updateChartOption([data])

      console.log('开始AI分析')
      await getAnalysis(data)
    } else {
      console.error('数据加载失败，data为null')
    }
  } else {
    console.error('indicatorId为空')
  }

})

// Function to load API data based on indicatorId - 与Prediction组件保持一致
const loadAPIData = async (indicatorId) => {
  try {
    console.log('开始从API加载分析结果页面数据...')

    // 处理宏观整体分析
    if (indicatorId === 'macro') {
      // 对于宏观分析，加载多指标数据
      console.log('加载宏观分析多指标数据...')

      try {
        // 获取关键指标时间序列数据
        const seriesResponse = await fetch(`${API_BASE_URL}/api/key-indicators-series`)
        if (!seriesResponse.ok) {
          throw new Error('关键指标时间序列API请求失败')
        }

        const seriesData = await seriesResponse.json()
        console.log('关键指标时间序列数据:', seriesData)

        return {
          isMacroAnalysis: true,
          multiIndicatorData: seriesData.indicators || []
        }
      } catch (error) {
        console.error('加载宏观分析数据失败:', error)
        return {
          isMacroAnalysis: true,
          multiIndicatorData: []
        }
      }
    }
    
    if (indicatorId === 'gdp') {
      // 获取GDP季度数据
      const gdpResponse = await fetch(`${API_BASE_URL}/api/gdp-data`)
      console.log('GDP数据API响应:', gdpResponse)

      if (!gdpResponse.ok) {
        throw new Error('GDP数据API请求失败')
      }

      const gdpApiData = await gdpResponse.json()
      console.log('GDP API数据:', gdpApiData)

      if (gdpApiData.quarters && gdpApiData.values && gdpApiData.quarters.length > 0) {
        // 只显示最近24个季度的数据（6年）
        const allQuarters = gdpApiData.quarters
        const allValues = gdpApiData.values
        // 强制根据当前时间判断，不使用API返回的is_predicted数据
        // 当前时间：2025年6月3日，所以2025Q2及以后是预测数据
        const allIsPredicted = allQuarters.map(q => {
          if (q.includes('2025Q2') || q.includes('2025Q3') || q.includes('2025Q4')) {
            return true
          }
          return false
        })
        const allConfidenceIntervals = gdpApiData.confidence_intervals || []

        // 显示最近24个季度
        const displayCount = Math.min(24, allQuarters.length)
        const startIndex = Math.max(0, allQuarters.length - displayCount)

        const data = {
          dates: allQuarters.slice(startIndex),
          values: allValues.slice(startIndex),
          isPredicted: allIsPredicted.slice(startIndex),
          confidenceInterval: allConfidenceIntervals.slice(startIndex).map(interval => {
            if (interval && Array.isArray(interval) && interval.length === 2) {
              return [parseFloat(interval[0]), parseFloat(interval[1])]
            }
            return null
          })
        }

        console.log(`GDP数据：显示最近${displayCount}个季度`)
        console.log('GDP数据处理结果:', data)

        chartData.value = data
        return data
      } else {
        // 使用默认的季度数据
        console.log('GDP API数据格式不正确，使用默认季度数据')
        const data = {
          dates: ['2023Q3', '2023Q4', '2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3', '2025Q4'],
          values: [4.9, 5.2, 5.3, 4.7, 4.6, 5.4, 5.4, 4.857564, 5.492128, 5.112863],
          isPredicted: [false, false, false, false, false, false, false, true, true, true],
          confidenceInterval: [null, null, null, null, null, null, null, [4.821547, 4.893581], [5.464386, 5.519870], [5.065357, 5.160369]]
        }

        chartData.value = data
        return data
      }
    }

    // 处理月度指标数据
    if (['retail', 'cpi', 'ppi', 'investment', 'industrial', 'export', 'import', 'realestate', 'm2', 'financing'].includes(indicatorId)) {
      // 获取关键经济指标数据
      const keyIndicatorsResponse = await fetch(`${API_BASE_URL}/api/key-indicators`)
      console.log('关键指标API响应:', keyIndicatorsResponse)

      if (!keyIndicatorsResponse.ok) {
        throw new Error('关键指标API请求失败')
      }

      const keyData = await keyIndicatorsResponse.json()
      console.log('关键指标数据:', keyData)

      const monthlyIndicatorsData = keyData.monthly_indicators || []

      // 指标映射 - 与Prediction组件保持一致
      const indicatorMapping = {
        retail: { name: '社会消费品零售总额', unit: '%' },
        cpi: { name: 'CPI', unit: '%' },
        ppi: { name: 'PPI', unit: '%' },
        investment: { name: '固定资产投资', unit: '%' },
        industrial: { name: '工业增加值', unit: '%' },
        export: { name: '出口金额', unit: '%' },
        import: { name: '进口金额', unit: '%' },
        realestate: { name: '房地产投资', unit: '%' },
        m2: { name: 'M2货币供应量', unit: '%' },
        financing: { name: '社会融资规模', unit: '万亿元' }
      }

      const mapping = indicatorMapping[indicatorId]
      if (!mapping) {
        throw new Error(`未找到指标映射: ${indicatorId}`)
      }

      console.log('可用的月度指标:', monthlyIndicatorsData.map(item => item.name))
      console.log('查找指标名称:', mapping.name)

      const indicator = monthlyIndicatorsData.find(item => item.name === mapping.name)
      if (!indicator) {
        console.error(`未找到指标数据: ${mapping.name}`)
        console.error('可用指标列表:', monthlyIndicatorsData)
        throw new Error(`未找到指标数据: ${mapping.name}`)
      }

      console.log('找到指标数据:', indicator)

      // 生成24个月的数据（2年）
      const dates = []
      const values = []
      const isPredicted = []
      const confidenceInterval = []

      const currentDate = new Date()
      for (let i = 23; i >= 0; i--) {
        const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1)
        const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
        dates.push(dateStr)

        // 判断是否为历史数据（2025年6月之前）
        const isHistorical = date < new Date(2025, 5, 1) // 2025年6月之前

        // 如果是当前指标的日期，使用实际数据
        if (dateStr === indicator.date) {
          // 对社会融资规模特殊处理（转换为万亿元）
          if (indicator.name === '社会融资规模') {
            values.push(indicator.value / 10000) // 转换为万亿元
            // 转换置信区间
            if (indicator.confidence_interval) {
              confidenceInterval.push([
                indicator.confidence_interval[0] / 10000,
                indicator.confidence_interval[1] / 10000
              ])
            } else {
              confidenceInterval.push(null)
            }
          } else {
            values.push(indicator.value)
            confidenceInterval.push(indicator.confidence_interval || null)
          }
          // 强制使用我们的时间判断逻辑，不使用API返回的is_predicted
          isPredicted.push(!isHistorical)
        } else {
          // 生成基于当前值的模拟数据
          let simulatedValue

          // 对社会融资规模特殊处理（绝对数值，单位万亿元）
          if (indicator.name === '社会融资规模') {
            // 社会融资规模的基准值（万亿元）
            const baseValue = indicator.value / 10000 // 转换为万亿元

            if (isHistorical) {
              // 历史数据：基于月份生成合理的历史值
              const monthsFromCurrent = Math.abs(new Date(2025, 5, 1) - date) / (1000 * 60 * 60 * 24 * 30)
              // 历史数据在基准值附近波动，越早的数据稍微小一些
              const historicalTrend = -monthsFromCurrent * 0.02 // 每月递减0.02万亿
              const randomVariation = (Math.random() - 0.5) * 0.5 // ±0.25万亿的随机波动
              simulatedValue = Math.max(0.5, baseValue + historicalTrend + randomVariation)
            } else {
              // 预测数据：基于当前值的合理预测
              const monthsFromCurrent = Math.abs(date - new Date(2025, 5, 1)) / (1000 * 60 * 60 * 24 * 30)
              const predictionTrend = monthsFromCurrent * 0.03 // 每月递增0.03万亿
              const randomVariation = (Math.random() - 0.5) * 0.3 // ±0.15万亿的随机波动
              simulatedValue = baseValue + predictionTrend + randomVariation
            }

            confidenceInterval.push(!isHistorical ? [simulatedValue * 0.95, simulatedValue * 1.05] : null)
          } else {
            // 其他指标的原有逻辑（百分比指标）
            const variation = (Math.random() - 0.5) * 2
            simulatedValue = indicator.value + variation

            // 确保值在合理范围内
            if (mapping.unit === '%') {
              simulatedValue = Math.max(-10, Math.min(20, simulatedValue))
            }

            confidenceInterval.push(!isHistorical ? [simulatedValue - 0.5, simulatedValue + 0.5] : null)
          }

          values.push(simulatedValue)
          isPredicted.push(!isHistorical)
        }
      }

      const data = {
        dates,
        values,
        isPredicted,
        confidenceInterval,
        unit: mapping.unit
      }

      console.log(`${indicatorId}数据处理完成:`, data)
      chartData.value = data
      return data
    }

    console.log(`未知的indicatorId: ${indicatorId}`)
    return null
  } catch (error) {
    console.error('加载API数据出错:', error)
    console.error('错误详情:', error.message)

    // 如果是月度指标，提供fallback数据
    if (['retail', 'cpi', 'ppi', 'investment', 'industrial', 'export', 'import', 'realestate', 'm2', 'financing'].includes(indicatorId)) {
      console.log('提供fallback月度数据')

      // 为社会融资规模提供特殊的fallback数据
      if (indicatorId === 'financing') {
        const fallbackData = {
          dates: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12'],
          values: [3.2, 3.5, 3.1, 2.8, 3.0, 3.4, 3.6, 3.8, 3.2, 2.9, 3.1, 3.3, 3.5, 3.7, 3.4, 3.2, 3.0, 3.1, 3.3, 3.5, 3.7, 3.4, 3.2, 3.0],
          isPredicted: [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, true, true, true, true, true],
          confidenceInterval: [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, [2.8, 3.4], [3.0, 3.8], [3.2, 4.0], [3.4, 4.2], [3.1, 3.7], [2.9, 3.5], [2.7, 3.3]],
          unit: '万亿元'
        }
        chartData.value = fallbackData
        return fallbackData
      } else {
        const fallbackData = {
          dates: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12'],
          values: [3.2, 3.5, 3.1, 2.8, 3.0, 3.4, 3.6, 3.8, 3.2, 2.9, 3.1, 3.3, 3.5, 3.7, 3.4, 3.2, 3.0, 3.1, 3.3, 3.5, 3.7, 3.4, 3.2, 3.0],
          isPredicted: [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, true, true, true, true, true],
          confidenceInterval: [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, [2.8, 3.4], [3.0, 3.8], [3.2, 4.0], [3.4, 4.2], [3.1, 3.7], [2.9, 3.5], [2.7, 3.3]],
          unit: '%'
        }
        chartData.value = fallbackData
        return fallbackData
      }
    }

    return null
  }
}

// 移除分页相关代码，直接显示完整内容
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