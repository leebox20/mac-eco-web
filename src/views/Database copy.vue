<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />
    
    <main class="bg-background min-h-screen pt-12 pb-12">
      <!-- 主体内容区域 -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 顶部筛选栏 -->
        <div class="flex items-center justify-between mb-6 bg-white rounded-lg shadow-md p-4">
          <div class="flex items-center space-x-4">
            <button class="px-4 py-2 text-blue-600 bg-white rounded-md hover:bg-blue-50 border border-blue-200">全部</button>
            <button class="px-4 py-2 text-gray-600 hover:bg-blue-50 rounded-md flex items-center">
              区域
              <i class="fas fa-chevron-down text-xs ml-2"></i>
            </button>
            <button class="px-4 py-2 text-gray-600 hover:bg-blue-50 rounded-md flex items-center">
              政策
              <i class="fas fa-chevron-down text-xs ml-2"></i>
            </button>
          </div>
          
          <div class="flex items-center space-x-4">
            <div class="relative">
              <input
                type="text"
                placeholder="搜索"
                class="pl-10 pr-4 py-2 rounded-md w-64 bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              >
              <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
            </div>
            <button class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
              对比
            </button>
          </div>
        </div>

        <!-- 图表卡片 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <!-- 卡片标题区域 -->
          <div class="flex items-center justify-between p-4  bg-gray-50 shadow">
            <div>
              <h2 class="text-lg font-medium">中国金融机构:各项贷款余额:人民币:同比</h2>
              <p class="text-sm text-gray-500">M0001381 · 来源：中国人民银行</p>
            </div>
          </div>
          
          <!-- 图表内容区域 -->
          <div class="p-6">
            <div ref="chartRef" class="h-[400px]"></div>
          </div>
        </div>
      </div>
    </main>

    <TheFooter />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'

const chartRef = ref(null)
let chart = null

// 图表配置
const option = {
  tooltip: {
    trigger: 'axis'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['1990', '1992', '1994', '1996', '1998']
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value}'
    }
  },
  series: [
    {
      name: '贷款余额同比',
      type: 'line',
      areaStyle: {
        opacity: 0.3
      },
      data: [200, 0, 100, 0, -200],
      lineStyle: {
        color: '#4B96FF'
      },
      itemStyle: {
        color: '#4B96FF'
      },
      areaStyle: {
        color: '#4B96FF',
        opacity: 0.2
      }
    }
  ]
}

// 初始化图表
onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.setOption(option)
    
    // 响应式处理
    window.addEventListener('resize', () => {
      chart?.resize()
    })
  }
})

// 组件销毁时清理
onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', chart?.resize)
})
</script>
