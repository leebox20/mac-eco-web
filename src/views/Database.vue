<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />


    <!-- Subheader -->
    <div class="bg-[#4080ff] text-white py-4">
      <div class="container mx-auto px-4 flex items-center space-x-2">
        <DatabaseIcon class="h-5 w-5" />
        <span class="text-lg">数据筛选</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="bg-white rounded-lg p-6">
        <!-- Tabs and Search -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex space-x-4">
            <button class="text-[#4080ff] font-medium border-b-2 border-[#4080ff] px-4 py-2">全部</button>
            <button class="text-gray-600 hover:text-[#4080ff] px-4 py-2 flex items-center">
              区域
              <ChevronDownIcon class="h-4 w-4 ml-1" />
            </button>
            <button class="text-gray-600 hover:text-[#4080ff] px-4 py-2 flex items-center">
              政策
              <ChevronDownIcon class="h-4 w-4 ml-1" />
            </button>
          </div>
          <div class="flex items-center space-x-4">
            <div class="relative">
              <input
                type="text"
                placeholder="搜索"
                class="pl-10 pr-4 py-2 w-64 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4080ff]"
              />
              <SearchIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            </div>
            <button class="bg-[#4080ff] text-white px-6 py-2 rounded-lg hover:bg-[#3070ff] flex items-center space-x-2">
              <BarChartIcon class="h-5 w-5" />
              <span>对比</span>
            </button>
          </div>
        </div>

        <!-- Chart Section -->
        <div class="space-y-6">
          <div v-for="i in 2" :key="i" class="border border-gray-200 rounded-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium">中国金融机构:各项贷款余额:人民币:同比</h2>
              <div class="text-gray-500 text-sm flex items-center space-x-4">
                <span>来源：中国人民银行</span>
                <span>M0001381</span>
              </div>
            </div>
            <!-- ECharts Area Chart -->
            <div class="h-80 w-full">
              <v-chart class="chart" :option="chartOption" autoresize />
            </div>
          </div>
        </div>
      </div>
    </main>

    <TheFooter />

  </div>
</template>

<script setup>
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { 
  HomeIcon, 
  DatabaseIcon, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  BrainCircuitIcon
} from 'lucide-vue-next'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
])

const generateData = () => {
  const baseValue = Math.random() * 1000
  const time = []
  const value = []
  for (let i = 0; i < 100; i++) {
    const date = new Date(1990, 0, 1)
    date.setDate(date.getDate() + i * 30)
    time.push(date.getFullYear() + (date.getMonth() / 12))
    value.push(Math.round((Math.sin(i / 5) * (i / 5 - 10) + i / 6) * 10 + baseValue))
  }
  return { time, value }
}

const { time, value } = generateData()

const chartOption = ref({
  tooltip: {
    trigger: 'axis',
    formatter: function (params) {
      const date = new Date(params[0].value[0] * 1000)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      return year + '年' + month + '月: ' + params[0].value[1]
    }
  },
  xAxis: {
    type: 'value',
    min: 1990,
    max: 1998,
    axisLabel: {
      formatter: '{value}'
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value}'
    }
  },
  series: [{
    data: time.map((t, i) => [t, value[i]]),
    type: 'line',
    smooth: true,
    showSymbol: false,
    areaStyle: {
      opacity: 0.8,
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [{
          offset: 0, color: 'rgba(64, 128, 255, 0.3)'
        }, {
          offset: 1, color: 'rgba(64, 128, 255, 0)'
        }],
      }
    },
    itemStyle: {
      color: '#4080ff'
    },
    lineStyle: {
      width: 2,
      color: '#4080ff'
    }
  }],
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  dataZoom: [
    {
      type: 'inside',
      start: 0,
      end: 100
    }
  ]
})
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.chart {
  height: 100%;
  width: 100%;
}
</style>