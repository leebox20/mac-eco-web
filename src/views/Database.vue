<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />

    <!-- Subheader -->
    <div class="bg-[#4080ff] text-white py-6 px-4">
      <div class="container mx-auto px-10 flex items-center space-x-2">
        <arrow-down-wide-narrow class="h-5 w-5" />
        <span class="text-sm text-gray-200">数据筛选</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto py-6 px-4">
      <div class="bg-white rounded-lg p-6">
        <!-- Tabs and Search -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex space-x-4">
            <button class="text-[#4080ff] font-medium border-b-2 border-[#4080ff] px-4 py-2">
              全部
            </button>
            <div class="relative group">
              <button 
                class="text-gray-600 hover:text-[#4080ff] px-4 py-2 flex items-center"
                @click="toggleDropdown('region')"
              >
                区域
                <ChevronDownIcon class="h-4 w-4 ml-1" />
              </button>
              <div 
                v-if="activeDropdown === 'region'"
                class="absolute z-10 mt-2 w-40 bg-white rounded-lg shadow-lg py-2 border border-gray-200"
              >
                <button 
                  v-for="region in regions" 
                  :key="region"
                  class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 hover:text-[#4080ff]"
                >
                  {{ region }}
                </button>
              </div>
            </div>
            <div class="relative group">
              <button 
                class="text-gray-600 hover:text-[#4080ff] px-4 py-2 flex items-center"
                @click="toggleDropdown('policy')"
              >
                政策
                <ChevronDownIcon class="h-4 w-4 ml-1" />
              </button>
              <div 
                v-if="activeDropdown === 'policy'"
                class="absolute z-10 mt-2 w-40 bg-white rounded-lg shadow-lg py-2 border border-gray-200"
              >
                <!-- Policy items would go here -->
              </div>
            </div>
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
            <button 
              @click="handleComparisonClick"
              :class="[
                'px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors',
                isComparisonMode 
                  ? 'bg-gray-400 text-white cursor-not-allowed' 
                  : 'bg-[#4080ff] text-white hover:bg-[#3070ff]',
                selectedCharts.length >= 2 && isComparisonMode
                  ? '!bg-[#4080ff] !cursor-pointer'
                  : ''
              ]"
              :disabled="isComparisonMode && selectedCharts.length < 2"
            >
              <BarChartIcon class="h-5 w-5" />
              <span>{{ isLoading ? '对比中...' : '对比' }}</span>
            </button>
          </div>
        </div>

        <!-- Comparison Selection Panel -->
        <div v-if="isComparisonMode" class="mb-6 p-4 border border-gray-200 rounded-lg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-700">请为选择要进行对比的图表</h3>
            <button
              @click="closeComparisonMode"
              class="text-gray-500 hover:text-gray-700"
            >
              <XIcon class="h-5 w-5" />
            </button>
          </div>
          <div class="flex flex-wrap gap-3">
            <div
              v-for="item in selectedCharts"
              :key="item.id"
              class="flex items-center bg-gray-100 px-3 py-2 rounded-lg"
            >
              <span class="text-sm text-gray-700 mr-2">{{ item.title }}</span>
              <button
                @click="removeFromComparison(item)"
                class="text-gray-400 hover:text-gray-600"
              >
                <XIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 flex flex-col items-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4080ff] mb-4"></div>
            <span class="text-gray-700">对比分析中...</span>
          </div>
        </div>

        <!-- Chart Section -->
        <div v-else class="space-y-6">
          <div 
            v-for="(chart, i) in charts" 
            :key="i" 
            class="border border-gray-200 rounded-lg p-6"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-4">
                <input
                  v-if="isComparisonMode"
                  type="checkbox"
                  :id="'chart-' + i"
                  :checked="isChartSelected(chart)"
                  @change="toggleChartSelection(chart)"
                  class="w-4 h-4 text-[#4080ff] rounded border-gray-300 focus:ring-[#4080ff]"
                />
                <h2 class="text-lg font-medium">{{ chart.title }}</h2>
              </div>
              <div class="text-gray-500 text-sm flex items-center space-x-4">
                <span>来源：{{ chart.source }}</span>
                <span>{{ chart.code }}</span>
              </div>
            </div>
            <div class="h-80 w-full">
              <v-chart class="chart" :option="chart.option" autoresize />
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
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { 
  HomeIcon, 
  ArrowDownWideNarrow, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  XIcon
} from 'lucide-vue-next'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DataZoomComponent,
])

// State
const isComparisonMode = ref(false)
const selectedCharts = ref([])
const isLoading = ref(false)
const activeDropdown = ref(null)
const regions = ref(['北京', '上海', '四川', '云南', '湖北', '贵州'])

// Sample charts data
const charts = ref([
  {
    id: 1,
    title: '中国金融机构:各项贷款余额:人民币:同比',
    source: '中国人民银行',
    code: 'M0001381',
    option: generateChartOption()
  },
  {
    id: 2,
    title: '中国:金融机构:外汇贷款余额:同比',
    source: '中国人民银行',
    code: 'M0001382',
    option: generateChartOption()
  }
])

// Methods
function generateChartOption() {
  const { time, value } = generateData()
  return {
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
  }
}

function generateData() {
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

function toggleComparisonMode() {
  isComparisonMode.value = !isComparisonMode.value
  if (!isComparisonMode.value) {
    selectedCharts.value = []
  }
}

function closeComparisonMode() {
  isComparisonMode.value = false
  selectedCharts.value = []
}

function toggleChartSelection(chart) {
  const index = selectedCharts.value.findIndex(c => c.id === chart.id)
  if (index === -1) {
    selectedCharts.value.push(chart)
  } else {
    selectedCharts.value.splice(index, 1)
  }
}

function isChartSelected(chart) {
  return selectedCharts.value.some(c => c.id === chart.id)
}

function removeFromComparison(chart) {
  const index = selectedCharts.value.findIndex(c => c.id === chart.id)
  if (index !== -1) {
    selectedCharts.value.splice(index, 1)
  }
}

async function handleComparisonClick() {
  if (!isComparisonMode.value) {
    toggleComparisonMode()
    return
  }
  
  if (selectedCharts.value.length >= 2) {
    try {
      isLoading.value = true
      console.log('Loading started')
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 3000))
      console.log('API call completed')
    } catch (error) {
      console.error('对比失败:', error)
    } finally {
      console.log('Loading finished')
      isLoading.value = false
      closeComparisonMode()
    }
  }
}

const toggleDropdown = (dropdown) => {
  if (activeDropdown.value === dropdown) {
    activeDropdown.value = null
  } else {
    activeDropdown.value = dropdown
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.group')) {
      activeDropdown.value = null
    }
  })
})

onUnmounted(() => {
  // Removed: document.removeEventListener('click', closeDropdowns)
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
