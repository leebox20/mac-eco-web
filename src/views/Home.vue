<template>
  <div class="min-h-screen bg-[#f2f5f8]">
    <!-- 使用组件 -->
    <TheHeader />
    
    <!-- 主要内容 -->
    <main class="main-bg min-h-screen relative overflow-hidden">
      
      <!-- 内容区域 -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative pt-12" style="z-index: 2;">
        <div class="w-full">
          <!-- 欢迎区域 -->
          <Transition name="fade-up" appear>
            <div class="max-w-3xl mb-16 text-left">
              <h1 class="text-2xl font-medium text-gray-900 leading-tight">
                欢迎使用<span class="text-[#348FEF]">中国宏观经济大数据AI预测系统!</span>
              </h1>
              <p class="mt-4 text-base text-gray-600 leading-1">
                我们致力于为用户提供专业、高效的宏观经济趋势分析服务。通过强大的大数据处理能力，我们能够轻松找到特定年份某个行业的经济趋势，并与其他年份进行精准对比，从而帮助您清晰了解行业发展的脉络与变化。
              </p>
              <p class="mt-2 text-base text-gray-600 leading-1">
                不仅如此，基于对历史数据的深入分析和先进的预测算法，我们可以对未来的经济形势进行科学预测，为您的战略决策提供可靠依据，无论是投资、市场研究，还是政策制定，我们都能助您一臂之力。
              </p>
            </div>
          </Transition>

          <!-- Economic Indicators -->
          <Transition name="fade-up" appear :duration="{ enter: 500 }" :style="{ transitionDelay: '300ms' }">
            <div class="bg-white rounded-lg shadow-sm mb-16 pb-6">
              <!-- Card Header -->
              <h3 class="text-base font-medium mb-6 text-center border-b border-gray-200 p-3">次月/季数据预测:</h3>
              
              <!-- Tabs/Indicators -->
              <div class="flex flex-wrap gap-4 justify-center">
                <template v-for="(indicator, index) in economicIndicators" :key="index">
                  <button
                    @click="activeTabIndex = index"
                    :class="[
                      'px-3 py-2 rounded-lg transition-all duration-200',
                      'min-w-[160px] max-w-[200px] h-[90px]',
                      'flex-grow',
                      activeTabIndex === index 
                        ? 'bg-[#EFF5FF] border border-[#EFF5FF]' 
                        : 'bg-white'
                    ]"
                  >
                    <div class="text-sm text-[#8B8B8B] h-[40px] flex items-center justify-center">
                      {{ indicator.label }}
                    </div>
                    <div class="h-[40px] flex items-center justify-center">
                      <span :class="[
                        'text-2xl font-medium',
                        indicator.value < 0 ? 'text-red-500' : 'text-[#4080FF]'
                      ]">
                        {{ indicator.value }}
                      </span>
                      <span class="ml-1 text-gray-600">%</span>
                    </div>
                  </button>
                </template>
              </div>

              <!-- Chart Area -->
              <div class="h-[400px]" ref="chartRef"></div>
            </div>
          </Transition>

        </div>
        
     
      </div>
    </main>

    <TheFooter />
  </div>
</template>

<script setup>
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { CountTo } from 'vue3-count-to' 
import aiPredictionIcon from '@/assets/forecast.png'
import dataComparisonIcon from '@/assets/data-compare.png'

import * as echarts from 'echarts'

const economicIndicators = [
  { label: 'GDP:不变价-当季同比', value: '5.11' },
  { label: '社会消费品零售总额:当月同比', value: '6.25' },
  { label: 'CPI:当月同比', value: '0.57' },
  { label: 'PPI:全部工业品-当月同比', value: '-2.0' },
  { label: '固定资产投资完成额:累计同比', value: '3.75' },
] 


const scrollTrigger = ref(0)
const isAnimating = ref(false)

const triggerScroll = () => {
  if (!isAnimating.value) {
    isAnimating.value = true
    scrollTrigger.value += 1
    
    // Reset animation state after transition completes
    setTimeout(() => {
      isAnimating.value = false
    }, 500) // Match this with your CSS transition duration
  }
}

// Start periodic animation
onMounted(() => {
  setInterval(() => {
    triggerScroll()
  }, 3000) // Trigger every 3 seconds after count finishes
})


// 图表相关
const chartRef = ref(null)
let chartInstance = null


// 添加图表组件和数据
const LineChart = {
  props: ['chartData'],
  mounted() {
    const chart = echarts.init(this.$el)
    const option = {
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: this.chartData.dates,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        scale: true
      },
      series: [{
        data: this.chartData.values,
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
            offset: 0,
            color: 'rgba(64, 128, 255, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(64, 128, 255, 0.1)'
          }])
        },
        lineStyle: {
          color: '#4080FF'
        },
        itemStyle: {
          color: '#4080FF'
        }
      }]
    }
    chart.setOption(option)
  }
}

// 模拟图表数据
const chartDataSets = [
  {
    dates: ['1970/3/13', '1970/4/3', '1970/4/24', '1970/5/15', '1970/6/5', '1970/6/26', 
            '1970/7/17', '1970/8/7', '1970/8/28', '1970/9/18', '1970/10/9', '1970/10/30'],
    values: [20, 15, -10, 5, 20, 45, 40, 50, 65, 90, 100, 95]
  },
  {
    dates: ['1970/3/13', '1970/4/3', '1970/4/24', '1970/5/15', '1970/6/5', '1970/6/26', 
            '1970/7/17', '1970/8/7', '1970/8/28', '1970/9/18', '1970/10/9', '1970/10/30'],
    values: [30, 25, 0, 10, 30, 55, 50, 60, 75, 100, 110, 105]
  },
  {
    dates: ['1970/3/13', '1970/4/3', '1970/4/24', '1970/5/15', '1970/6/5', '1970/6/26', 
            '1970/7/17', '1970/8/7', '1970/8/28', '1970/9/18', '1970/10/9', '1970/10/30'],
    values: [10, 5, -20, -5, 10, 35, 30, 40, 55, 80, 90, 85]
  },
  {
    dates: ['1970/3/13', '1970/4/3', '1970/4/24', '1970/5/15', '1970/6/5', '1970/6/26', 
            '1970/7/17', '1970/8/7', '1970/8/28', '1970/9/18', '1970/10/9', '1970/10/30'],
    values: [40, 35, 10, 15, 40, 65, 60, 70, 85, 110, 120, 115]
  },
  {
    dates: ['1970/3/13', '1970/4/3', '1970/4/24', '1970/5/15', '1970/6/5', '1970/6/26', 
            '1970/7/17', '1970/8/7', '1970/8/28', '1970/9/18', '1970/10/9', '1970/10/30'],
    values: [-5, -10, -30, -15, -5, 20, 15, 25, 40, 65, 75, 70]
  }
]

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    const option = {
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartDataSets[activeTabIndex.value].dates,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        scale: true
      },
      series: [{
        data: chartDataSets[activeTabIndex.value].values,
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
            offset: 0,
            color: 'rgba(64, 128, 255, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(64, 128, 255, 0.1)'
          }])
        },
        lineStyle: {
          color: '#4080FF'
        },
        itemStyle: {
          color: '#4080FF'
        }
      }]
    }
    chartInstance.setOption(option)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

const activeTabIndex = ref(0)

// 监听 activeTabIndex 的变化来��新图表
watch(activeTabIndex, (newIndex) => {
  // 这里可以根据选中的指标更新图表数据
  updateChart(economicIndicators[newIndex])
})

// 更新图表的方法
const updateChart = (index) => {
  if (!chartInstance) return
  
  let data
  switch(index) {
    case 0: // GDP
      data = seasonalData.value?.gdp
      break
    case 1: // 社会消费品零售总额
      data = monthlyData.value?.retail
      break
    case 2: // CPI
      data = monthlyData.value?.cpi
      break
    case 3: // PPI
      data = monthlyData.value?.ppi
      break
    case 4: // 固定资产投资
      data = monthlyData.value?.investment
      break
  }

  if (!data) return

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const date = data.dates[dataIndex]
        const value = data.values[dataIndex]
        const isPredicted = data.isPredicted[dataIndex]
        const confidenceInterval = data.confidenceInterval[dataIndex]
        
        let tooltip = `${date}<br/>`
        if (isPredicted) {
          tooltip += `<span style="color: #F56C6C">预测值: ${value.toFixed(2)}%</span>`
          if (confidenceInterval) {
            tooltip += `<br/><span style="color: #F56C6C">置信区间: [${confidenceInterval[0].toFixed(2)}%, ${confidenceInterval[1].toFixed(2)}%]</span>`
          }
        } else {
          tooltip += `<span style="color: #409EFF">实际值: ${value.toFixed(2)}%</span>`
        }
        return tooltip
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.dates,
      boundaryGap: false,
      axisLabel: {
        interval: index === 0 ? 3 : 11,  // GDP是季度数据，其他是月度数据
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      name: '%',
      nameLocation: 'end'
    },
    series: [
      {
        name: '历史数据',
        type: 'line',
        data: data.values.map((value, index) => 
          data.isPredicted[index] ? null : value
        ),
        itemStyle: {
          color: '#409EFF'
        },
        symbol: 'emptyCircle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        z: 3
      },
      {
        name: '预测数据',
        type: 'line',
        data: data.values.map((value, index) => 
          data.isPredicted[index] ? value : null
        ),
        itemStyle: {
          color: '#F56C6C'
        },
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 2,
          color: '#F56C6C'
        },
        z: 4
      },
      {
        name: '预测区间',
        type: 'line',
        data: data.confidenceInterval.map((interval, index) => 
          interval ? interval[1] : null
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
        type: 'line',
        data: data.confidenceInterval.map((interval, index) => 
          interval ? interval[0] : null
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
    ]
  }
  chartInstance.setOption(option)
}

// 在 script setup 中添加数据结构定义
const seasonalData = ref(null)
const monthlyData = ref(null)

// 加载数据的方法
const loadData = async () => {
  try {
    // 加载季度GDP数据
    const gdpResponse = await fetch(new URL('/data/seasonal_gdp.csv', window.location.origin))
    const gdpText = await gdpResponse.text()
    const gdpRows = gdpText.replace(/^\\ufeff/, '').split('\n').slice(1)
    seasonalData.value = {
      gdp: {
        dates: [],
        values: [],
        isPredicted: [],
        confidenceInterval: []
      }
    }
    
    gdpRows.forEach(row => {
      if (!row.trim()) return
      const [date, valueStr] = row.split(',')
      if (!valueStr) return
      
      if (valueStr.trim().includes('±')) {
        const [baseValue, interval] = valueStr.trim().split('±')
        const value = parseFloat(baseValue)
        const intervalValue = parseFloat(interval)
        seasonalData.value.gdp.dates.push(date.trim())
        seasonalData.value.gdp.values.push(value)
        seasonalData.value.gdp.isPredicted.push(true)
        seasonalData.value.gdp.confidenceInterval.push([
          value - intervalValue,
          value + intervalValue
        ])
      } else {
        seasonalData.value.gdp.dates.push(date.trim())
        seasonalData.value.gdp.values.push(parseFloat(valueStr))
        seasonalData.value.gdp.isPredicted.push(false)
        seasonalData.value.gdp.confidenceInterval.push(null)
      }
    })

    // 加载月度数据
    const monthlyResponse = await fetch(new URL('/data/monthly_data.csv', window.location.origin))
    const monthlyText = await monthlyResponse.text()
    const monthlyRows = monthlyText.replace(/^\\ufeff/, '').split('\n').slice(1)
    
    monthlyData.value = {
      retail: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      cpi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      ppi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      investment: { dates: [], values: [], isPredicted: [], confidenceInterval: [] }
    }

    monthlyRows.forEach(row => {
      if (!row.trim()) return
      const [date, retail, cpi, ppi, investment] = row.split(',')
      
      const processIndicator = (valueStr, indicator) => {
        if (!valueStr) return
        
        if (valueStr.trim().includes('±')) {
          const [baseValue, interval] = valueStr.trim().split('±')
          const value = parseFloat(baseValue)
          const intervalValue = parseFloat(interval)
          monthlyData.value[indicator].dates.push(date.trim())
          monthlyData.value[indicator].values.push(value)
          monthlyData.value[indicator].isPredicted.push(true)
          monthlyData.value[indicator].confidenceInterval.push([
            value - intervalValue,
            value + intervalValue
          ])
        } else {
          monthlyData.value[indicator].dates.push(date.trim())
          monthlyData.value[indicator].values.push(parseFloat(valueStr))
          monthlyData.value[indicator].isPredicted.push(false)
          monthlyData.value[indicator].confidenceInterval.push(null)
        }
      }

      processIndicator(retail, 'retail')
      processIndicator(cpi, 'cpi')
      processIndicator(ppi, 'ppi')
      processIndicator(investment, 'investment')
    })
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

// 在组件挂载时加载数据
onMounted(() => {
  loadData().then(() => {
    initChart()
    updateChart(activeTabIndex.value)
  })
})

// 监听标签切换
watch(activeTabIndex, (newIndex) => {
  updateChart(newIndex)
})

</script>

<style scoped>
.number-container {
  height: 3rem;
  width: 100%;
  overflow: hidden;
}

.main-bg {
  background-color: #f2f5f8;
  background-image: 
    url('/src/assets/home-body-bg2-left.png'),
    url('/src/assets/home-body-bg2-right.png');
  background-size: 60% 60%, 60% 60%;
  background-position: 0 0, 100% 0;
  background-repeat: no-repeat, no-repeat;
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
}

.scroll-enter-active,
.scroll-leave-active {
  transition: all 0.5s ease;
}

.scroll-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.scroll-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

.scroll-enter-to,
.scroll-leave-from {
  transform: translateY(0);
  opacity: 1;
}

.bg-background {
  background-color: rgb(249, 250, 251);
}

.custom-italic {
  font-style: italic;
  transform: skew(-15deg);
}

/* 从右侧滑入动画 */
.slide-from-right-enter-active,
.slide-from-right-leave-active {
  transition: all 0.8s ease;
}

.slide-from-right-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-from-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 从下方淡入动画 */
.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.5s ease;
  transition-delay: var(--delay, 0ms);
}

.fade-up-enter-from {
  transform: translateY(30px);
  opacity: 0;
}

.fade-up-leave-to {
  transform: translateY(-30px);
  opacity: 0;
}

/* 波纹动画样式 */
.ripple-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1000px;
  height: 600px;
  transform-origin: center;
  transform: translate(-50%, -50%) rotate(-15deg);
}

.ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 60px;
  border: 3px solid rgba(64, 128, 255, 0.25);
  border-radius: 50%;
  animation: ripple 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  z-index: 0;
}

.ripple:nth-child(2) {
  animation-delay: 1.3s;
}

.ripple:nth-child(3) {
  animation-delay: 2.6s;
}

@keyframes ripple {
  0% {
    width: 100px;
    height: 60px;
    opacity: 1;
  }
  100% {
    width: 1000px;
    height: 600px;
    opacity: 0;
  }
}

/* 添加新的图表相关样式 */
.grid-cols-5 {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}
</style>
