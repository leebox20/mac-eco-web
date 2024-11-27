<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />
    
    <!-- 面包屑导航 -->
    <div class="bg-white border-b">
      <div class="container mx-auto px-4 py-2">
        <div class="flex items-center space-x-2 text-sm">
          <router-link to="/database" class="text-gray-500 hover:text-[#4080ff]">数据库</router-link>
          <ChevronRightIcon class="h-4 w-4 text-gray-400" />
          <span class="text-gray-900">对比结果</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <main class="container mx-auto py-6 px-4">
      <!-- 趋势对比图表 -->
      <div class="bg-white rounded-lg shadow mb-6">
        <div class="p-4 border-b">
          <h2 class="text-lg font-medium">趋势对比</h2>
        </div>
        <div class="p-4 h-[400px]">
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>
      </div>

      <!-- 结果分析 -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-4 border-b">
          <h2 class="text-lg font-medium">结果分析</h2>
        </div>
        <div class="p-6 space-y-6">
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
import { ref } from 'vue'
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
import { ChevronRightIcon } from 'lucide-vue-next'
import TheHeader from '@/components/TheHeader.vue'

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
    data: [
      '中国:金融机构:各项贷款余额:人民币:同比',
      '中国:金融机构:外汇贷款余额:同比',
      '中国银行间债券市场回购加权平均利率:当月值',
      '中国人民银行对金融机构贷款利率:超额准备金'
    ]
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '中国:金融机构:各项贷款余额:人民币:同比',
      type: 'line',
      data: [150, 200, 180, 200, 220, 250, 230]
    },
    // ... 其他数据系列
  ]
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
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style> 