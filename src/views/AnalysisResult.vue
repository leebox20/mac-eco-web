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
          <div v-for="(section, index) in analysisContent" :key="index">
            <h3 class="text-base font-medium mb-3">{{ section.title }}</h3>
            <div class="text-gray-600 space-y-2">
              <p v-for="(point, i) in section.points" :key="i">{{ point }}</p>
            </div>
          </div>
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

import { useRoute } from 'vue-router'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

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

// 分析内容
const analysisContent = ref([
  {
    title: '1. 市场规模与增长',
    points: [
      '2020年：新能源行业整体市场规模较小，尽管增长显著，但基数较低。',
      '• 太阳能 和 风能 是增长的主要领域。',
      '• 储能技术仍处于研发阶段，市场普及率较低。',
      '2023年：行业市场规模快速扩张，增速达两位数。'
    ]
  },
  {
    title: '2. 政策与资金支持',
    points: [
      '2020年：政策驱动力强，但多以补贴、减税等方式为主，推动行业初步发展。',
      '• 例如，中国出台了对光伏产业的"领跑者计划"，推动技术升级。'
    ]
  }
])

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
const updateChartOption = (selectedCharts) => {
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