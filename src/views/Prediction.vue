<template>
  <div class="min-h-screen bg-[#F2F5F8]">
    <TheHeader />

    <!-- Subheader -->
    <div class="bg-[#348fef] py-6 px-4 border-t border-white border-opacity-10">
      <div class="container mx-auto px-10 flex items-center space-x-2">
        <chart-bar-icon class="h-5 w-5 text-gray-200" />
        <span class="text-sm text-gray-200">经济指标预测</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="flex gap-6 px-10">
        <!-- Left Sidebar - Indicator Selection -->
        <div class="w-1/4 bg-white rounded-lg shadow p-4">
          <h3 class="text-lg font-medium text-gray-800 mb-4">指标选择</h3>
          <div class="space-y-3">
            <div v-for="indicator in indicators" :key="indicator.id" class="flex items-center">
              <input
                type="checkbox"
                :id="indicator.id"
                v-model="selectedIndicators"
                :value="indicator.id"
                class="w-4 h-4 text-[#4080ff] border-gray-300 rounded focus:ring-[#4080ff]"
              />
              <label :for="indicator.id" class="ml-2 text-sm text-gray-700">
                {{ indicator.name }}
              </label>
            </div>
          </div>
        </div>

        <!-- Right Content - Charts -->
        <div class="w-3/4 space-y-6">
          <div v-if="selectedIndicators.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
            <chart-bar-icon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">请在左侧选择需要预测的经济指标</p>
          </div>
          <template v-else>
            <div
              v-for="indicatorId in selectedIndicators"
              :key="indicatorId"
              class="bg-white rounded-lg shadow p-4"
            >
              <h4 class="text-lg font-medium text-gray-800 mb-4">
                {{ getIndicatorName(indicatorId) }}预测
              </h4>
              <div class="h-[400px]">
                <v-chart :option="generateChartOption(indicatorId)" autoresize />
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
import { ref, computed } from 'vue'
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

// 模拟指标数据
const indicators = ref([
  { id: 'gdp', name: 'GDP增长率' },
  { id: 'cpi', name: '消费者物价指数(CPI)' },
  { id: 'ppi', name: '生产者物价指数(PPI)' },
  { id: 'unemployment', name: '失业率' },
  { id: 'retail', name: '社会消费品零售总额' },
  { id: 'investment', name: '固定资产投资' },
  { id: 'export', name: '进出口总额' },
  { id: 'm2', name: 'M2货币供应量' },
])

const selectedIndicators = ref([])

// 获取指标名称
const getIndicatorName = (id) => {
  const indicator = indicators.value.find(ind => ind.id === id)
  return indicator ? indicator.name : ''
}

// 生成图表配置
const generateChartOption = (indicatorId) => {
  // 模拟数据
  const dates = Array.from({ length: 12 }, (_, i) => {
    const date = new Date()
    date.setMonth(date.getMonth() + i)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit' })
  })

  const historicalData = Array.from({ length: 12 }, () => Math.random() * 10)
  const predictedData = Array.from({ length: 6 }, () => Math.random() * 10)

  return {
    title: {
      text: getIndicatorName(indicatorId),
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['历史数据', '预测数据'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '历史数据',
        type: 'line',
        data: historicalData,
        color: '#4080ff'
      },
      {
        name: '预测数据',
        type: 'line',
        data: Array(6).fill('-').concat(predictedData),
        color: '#ff4d4f',
        lineStyle: {
          type: 'dashed'
        }
      }
    ]
  }
}
</script>

<style scoped>
.v-chart {
  width: 100%;
  height: 100%;
}
</style>
