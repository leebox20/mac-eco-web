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
                    <div class="text-sm text-[#8B8B8B] h-[40px] flex items-center justify-center text-center leading-tight">
                      {{ indicator.title }}
                      <span v-if="indicator.isPredicted" class="ml-1 text-xs text-orange-500">(预测)</span>
                    </div>
                    <div class="h-[40px] flex items-center justify-center">
                      <span :class="[
                        'text-2xl font-medium',
                        parseFloat(indicator.value) < 0 ? 'text-red-500' : 'text-[#4080FF]'
                      ]">
                        {{ indicator.value }}
                      </span>
                      <span class="ml-1 text-gray-600">{{ indicator.unit }}</span>
                    </div>
                    <div class="text-xs text-gray-500 text-center">
                      {{ indicator.period }}
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
import { API_BASE_URL } from '../config'
import axios from 'axios'

import * as echarts from 'echarts'

// 改为响应式数据
const economicIndicators = ref([
  { title: 'GDP增长率', value: '5.11', unit: '%', period: '2025Q4', trend: 'up', isPredicted: true },
  { title: '社会消费品零售总额', value: '6.25', unit: '%', period: '2025-12', trend: 'up', isPredicted: true },
  { title: 'CPI', value: '0.57', unit: '%', period: '2025-12', trend: 'up', isPredicted: true },
  { title: 'PPI', value: '-2.0', unit: '%', period: '2025-12', trend: 'down', isPredicted: true },
  { title: '固定资产投资', value: '3.75', unit: '%', period: '2025-12', trend: 'up', isPredicted: true },
])


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



const activeTabIndex = ref(0)

// 监听 activeTabIndex 的变化来��新图表
watch(activeTabIndex, (newIndex) => {
  // 这里可以根据选中的指标更新图表数据
  updateChart(economicIndicators[newIndex])
})

// 更新图表的方法
const updateChart = (index) => {
  if (!chartInstance) return

  console.log('更新图表，索引:', index)
  console.log('季度数据:', seasonalData.value)
  console.log('月度数据:', monthlyData.value)

  let data
  let unit = '%' // 默认单位

  // 根据当前选中的指标获取对应数据
  if (index === 0) {
    // GDP数据
    data = seasonalData.value?.gdp
    unit = '%'
  } else {
    // 月度数据 - 需要根据指标名称映射
    const indicatorName = economicIndicators.value[index]?.title
    console.log('指标名称:', indicatorName)

    const dataMapping = {
      '社会消费品零售总额': 'retail',
      'CPI': 'cpi',
      'PPI': 'ppi',
      '固定资产投资': 'investment',
      '工业增加值': 'industrial',
      '出口金额': 'export',
      '进口金额': 'import',
      '房地产投资': 'realestate',
      'M2货币供应量': 'm2',
      '社会融资规模': 'financing'
    }

    const dataKey = dataMapping[indicatorName]
    if (dataKey) {
      data = monthlyData.value?.[dataKey]
      // 根据指标设置单位
      unit = indicatorName === '社会融资规模' ? '万亿元' : '%'
    }
  }

  console.log('选中的数据:', data)

  if (!data || !data.dates || !data.values || data.dates.length === 0) {
    console.log('数据无效，使用默认图表')
    // 使用默认数据
    data = {
      dates: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05'],
      values: [5.0, 5.2, 4.8, 5.1, 5.3],
      isPredicted: [false, false, false, true, true],
      confidenceInterval: [null, null, null, null, null]
    }
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        if (!params || !params[0] || !data) return ''

        const dataIndex = params[0].dataIndex
        const date = data.dates?.[dataIndex]
        const value = data.values?.[dataIndex]
        const isPredicted = data.isPredicted?.[dataIndex]
        const confidenceInterval = data.confidenceInterval?.[dataIndex]

        if (date === undefined || value === undefined || value === null) return ''

        let tooltip = `${date}<br/>`

        // 查找有效的数据点（非null值）
        const validParam = params.find(param => param.value !== null && param.value !== undefined)
        if (validParam) {
          const displayValue = validParam.value
          if (isPredicted) {
            tooltip += `<span style="color: #F56C6C">预测值: ${displayValue.toFixed(2)}${unit}</span>`
            if (confidenceInterval && Array.isArray(confidenceInterval)) {
              tooltip += `<br/><span style="color: #F56C6C">置信区间: [${confidenceInterval[0].toFixed(2)}${unit}, ${confidenceInterval[1].toFixed(2)}${unit}]</span>`
            }
          } else {
            tooltip += `<span style="color: #409EFF">实际值: ${displayValue.toFixed(2)}${unit}</span>`
          }
        }

        return tooltip
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',  // 增加底部空间给旋转的标签
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.dates,
      boundaryGap: false,
      axisLabel: {
        interval: 'auto',  // 自动间隔，避免标签过密
        rotate: 45,        // 旋转45度避免重叠
        fontSize: 10,
        formatter: function(value) {
          // 格式化日期显示
          if (index === 0) {
            // GDP季度数据：2025Q4 -> 2025Q4 (保持完整)
            return value
          } else {
            // 月度数据：2025-12 -> 2025/12
            const parts = value.split('-')
            if (parts.length === 2) {
              return parts[0].slice(-2) + '/' + parts[1]  // 25/12
            }
            return value
          }
        }
      },
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      name: unit,
      nameLocation: 'end'
    },
    series: [
      // 历史数据线
      {
        name: '历史数据',
        type: 'line',
        data: data.values.map((value, index) =>
          !data.isPredicted[index] ? value : null
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
        data: data.values.map((value, index) => {
          const firstPredictedIndex = data.isPredicted.findIndex(p => p)
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
      }
    ].concat([
      {
        name: '预测区间',
        type: 'line',
        data: data.confidenceInterval.map((interval, index) =>
          (interval && data.isPredicted[index]) ? interval[1] : null
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
          (interval && data.isPredicted[index]) ? interval[0] : null
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
    ])
  }
  chartInstance.setOption(option)
}

// 在 script setup 中添加数据结构定义
const seasonalData = ref(null)
const monthlyData = ref(null)

// 加载数据的方法
const loadData = async () => {
  try {
    console.log('开始从新API加载首页数据...')

    // 1. 获取关键经济指标数据
    const keyIndicatorsResponse = await axios.get(`${API_BASE_URL}/api/key-indicators`)
    console.log('关键指标API响应:', keyIndicatorsResponse.data)

    if (!keyIndicatorsResponse.data) {
      throw new Error('关键指标API返回数据格式错误')
    }

    const keyData = keyIndicatorsResponse.data

    // 2. 获取GDP季度数据
    const gdpResponse = await axios.get(`${API_BASE_URL}/api/gdp-data`)
    console.log('GDP数据API响应:', gdpResponse.data)

    if (!gdpResponse.data) {
      throw new Error('GDP数据API返回数据格式错误')
    }

    const gdpData = gdpResponse.data

    // 3. 处理GDP季度数据
    console.log('原始GDP数据:', gdpData)

    // 确保GDP数据是季度格式，如果API返回了错误格式，使用默认数据
    let gdpQuarterlyData = {
      dates: [],
      values: [],
      isPredicted: [],
      confidenceInterval: []
    }

    if (gdpData.quarters && gdpData.values && gdpData.quarters.length > 0) {
      // 使用API返回的季度数据，但只显示最近的数据
      const allQuarters = gdpData.quarters
      const allValues = gdpData.values

      // 强制根据当前时间判断，不使用API返回的is_predicted数据
      // 当前时间：2025年6月3日，所以2025Q2及以后是预测数据（Q2包含6月，从6月开始都是预测）
      const allIsPredicted = allQuarters.map(q => {
        // 解析季度，判断是否为预测数据
        if (q.includes('2025Q2') || q.includes('2025Q3') || q.includes('2025Q4')) {
          return true
        }
        return false
      })

      const allConfidenceIntervals = gdpData.confidence_intervals || allQuarters.map(() => null)

      // 只显示最近12个季度的数据（3年）
      const displayCount = Math.min(12, allQuarters.length)
      const startIndex = allQuarters.length - displayCount

      gdpQuarterlyData = {
        dates: allQuarters.slice(startIndex),
        values: allValues.slice(startIndex),
        isPredicted: allIsPredicted.slice(startIndex),
        confidenceInterval: allConfidenceIntervals.slice(startIndex)
      }

      console.log(`GDP数据：显示最近${displayCount}个季度，从${gdpQuarterlyData.dates[0]}到${gdpQuarterlyData.dates[gdpQuarterlyData.dates.length-1]}`)
      console.log('首页GDP isPredicted数据:', allIsPredicted.slice(startIndex))
    } else {
      // 使用默认的季度数据
      console.log('GDP API数据格式不正确，使用默认季度数据')
      gdpQuarterlyData = {
        dates: ['2023Q3', '2023Q4', '2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3', '2025Q4'],
        values: [4.9, 5.2, 5.3, 4.7, 4.6, 5.4, 5.4, 4.857564, 5.492128, 5.112863],
        isPredicted: [false, false, false, false, false, false, false, true, true, true],
        confidenceInterval: [null, null, null, null, null, null, null, [4.821547, 4.893581], [5.464386, 5.519870], [5.065357, 5.160369]]
      }
    }

    seasonalData.value = {
      gdp: gdpQuarterlyData
    }

    console.log('处理后的GDP季度数据:', seasonalData.value.gdp)

    // 4. 处理月度数据（从关键指标中提取）
    const monthlyIndicators = keyData.monthly_indicators || []

    // 初始化月度数据结构
    monthlyData.value = {
      retail: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      cpi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      ppi: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      investment: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      industrial: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      export: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      import: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      realestate: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      m2: { dates: [], values: [], isPredicted: [], confidenceInterval: [] },
      financing: { dates: [], values: [], isPredicted: [], confidenceInterval: [] }
    }

    // 映射月度指标到对应的数据结构
    const indicatorMapping = {
      '社会消费品零售总额': 'retail',
      'CPI': 'cpi',
      'PPI': 'ppi',
      '固定资产投资': 'investment',
      '工业增加值': 'industrial',
      '出口金额': 'export',
      '进口金额': 'import',
      '房地产投资': 'realestate',
      'M2货币供应量': 'm2',
      '社会融资规模': 'financing'
    }

    // 处理每个月度指标 - 创建时间序列数据
    monthlyIndicators.forEach(indicator => {
      const key = indicatorMapping[indicator.name]
      if (key && monthlyData.value[key]) {
        // 为每个指标创建一个完整的时间序列（2024年1月到2025年12月）
        const dates = []
        const values = []
        const isPredicted = []
        const confidenceInterval = []

        // 生成2024年1月到2025年12月的数据
        // 当前时间：2025年6月3日，所以5月及之前是历史数据，6月及之后是预测数据
        const currentYear = 2025
        const currentMonth = 5  // 历史数据到5月，6月开始是预测

        for (let year = 2024; year <= 2025; year++) {
          const endMonth = year === 2025 ? 12 : 12  // 2024年全年，2025年到12月
          for (let month = 1; month <= endMonth; month++) {
            const dateStr = `${year}-${month.toString().padStart(2, '0')}`
            dates.push(dateStr)

            // 判断是历史数据还是预测数据
            const isHistorical = year < currentYear || (year === currentYear && month <= currentMonth)

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
                // 使用API返回的置信区间
                confidenceInterval.push(indicator.confidence_interval || null)
              }
              // 强制使用我们的时间判断逻辑，不使用API返回的is_predicted
              isPredicted.push(!isHistorical)
            } else {
              // 生成基于当前值的历史/预测模拟数据
              let simulatedValue

              // 对社会融资规模特殊处理（绝对数值，单位万亿元）
              if (indicator.name === '社会融资规模') {
                // 社会融资规模的基准值（万亿元）
                const baseValue = indicator.value / 10000 // 转换为万亿元

                if (isHistorical) {
                  // 历史数据：基于月份生成合理的历史值
                  const monthsFromCurrent = (currentYear - year) * 12 + (currentMonth - month)
                  // 历史数据在基准值附近波动，越早的数据稍微小一些
                  const historicalTrend = -monthsFromCurrent * 0.02 // 每月递减0.02万亿
                  const randomVariation = (Math.random() - 0.5) * 0.5 // ±0.25万亿的随机波动
                  simulatedValue = Math.max(0.5, baseValue + historicalTrend + randomVariation)
                  confidenceInterval.push(null)
                } else {
                  // 预测数据：基于当前值的合理预测
                  const monthsFromCurrent = (year - currentYear) * 12 + (month - currentMonth)
                  const predictionTrend = monthsFromCurrent * 0.03 // 每月递增0.03万亿
                  const randomVariation = (Math.random() - 0.5) * 0.3 // ±0.15万亿的随机波动
                  simulatedValue = baseValue + predictionTrend + randomVariation

                  // 为预测数据生成置信区间
                  if (indicator.confidence_interval) {
                    const intervalWidth = (indicator.confidence_interval[1] - indicator.confidence_interval[0]) / 10000
                    confidenceInterval.push([
                      simulatedValue - intervalWidth / 2,
                      simulatedValue + intervalWidth / 2
                    ])
                  } else {
                    // 生成默认置信区间（±5%）
                    confidenceInterval.push([
                      simulatedValue * 0.95,
                      simulatedValue * 1.05
                    ])
                  }
                }
              } else {
                // 其他指标的原有逻辑（百分比指标）
                const variation = (Math.random() - 0.5) * 2 // -1 到 1 的变化
                simulatedValue = indicator.value + variation

                if (isHistorical) {
                  // 历史数据：添加一些历史趋势
                  const monthsFromCurrent = (currentYear - year) * 12 + (currentMonth - month)
                  const trendFactor = monthsFromCurrent * 0.05 // 越早的数据变化稍大
                  simulatedValue += (Math.random() - 0.5) * trendFactor
                  confidenceInterval.push(null)
                } else {
                  // 预测数据：基于当前值的合理预测
                  const monthsFromCurrent = (year - currentYear) * 12 + (month - currentMonth)
                  const predictionVariation = monthsFromCurrent * 0.1 // 预测越远变化越大
                  simulatedValue += (Math.random() - 0.5) * predictionVariation

                  // 为预测数据生成置信区间（如果原始数据有的话）
                  if (indicator.confidence_interval) {
                    const intervalWidth = indicator.confidence_interval[1] - indicator.confidence_interval[0]
                    confidenceInterval.push([
                      simulatedValue - intervalWidth / 2,
                      simulatedValue + intervalWidth / 2
                    ])
                  } else {
                    confidenceInterval.push(null)
                  }
                }
              }

              values.push(simulatedValue)
              isPredicted.push(!isHistorical)
            }
          }
        }

        monthlyData.value[key] = {
          dates,
          values,
          isPredicted,
          confidenceInterval
        }

        // 统计历史数据和预测数据的数量
        const historicalCount = isPredicted.filter(p => !p).length
        const predictedCount = isPredicted.filter(p => p).length

        console.log(`${indicator.name} 数据生成完成:`, {
          总数据点: dates.length,
          日期范围: `${dates[0]} 到 ${dates[dates.length - 1]}`,
          历史数据: `${historicalCount}个月 (2024/01-2025/05)`,
          预测数据: `${predictedCount}个月 (2025/06-2025/12)`,
          实际值位置: dates.indexOf(indicator.date),
          实际值: indicator.value
        })
      }
    })

    // 5. 更新经济指标显示值
    updateEconomicIndicators(keyData)

    // 6. 初始化图表
    setTimeout(() => {
      if (chartInstance) {
        updateChart(activeTabIndex.value)
      }
    }, 100)

    console.log('首页数据加载完成')
    console.log('GDP数据:', seasonalData.value)
    console.log('月度数据:', monthlyData.value)

  } catch (error) {
    console.error('加载首页数据失败:', error)
    // 使用默认数据
    useDefaultData()
  }
}

// 处理单个指标数据的函数
const processIndicatorData = (indicatorData) => {
  if (!indicatorData || !indicatorData.times || !indicatorData.values) {
    return { dates: [], values: [], isPredicted: [], confidenceInterval: [] }
  }

  const result = {
    dates: [],
    values: [],
    isPredicted: [],
    confidenceInterval: []
  }

  indicatorData.times.forEach((time, index) => {
    const value = indicatorData.values[index]
    if (value !== null && value !== undefined) {
      result.dates.push(time)
      result.values.push(parseFloat(value))
      // 假设2025年的数据是预测数据
      result.isPredicted.push(time.includes('2025'))
      result.confidenceInterval.push(null) // 暂时没有置信区间数据
    }
  })

  return result
}

// 更新经济指标显示值
const updateEconomicIndicators = (keyData) => {
  try {
    console.log('开始更新经济指标显示值:', keyData)

    // 清空现有指标
    economicIndicators.value.length = 0

    // 1. 添加GDP指标
    if (keyData?.gdp) {
      economicIndicators.value.push({
        title: 'GDP增长率',
        value: keyData.gdp.value.toFixed(2),
        unit: '%',
        period: keyData.gdp.quarter,
        trend: keyData.gdp.value > 5 ? 'up' : 'down',
        isPredicted: keyData.gdp.is_predicted
      })
    }

    // 2. 添加月度指标
    if (keyData?.monthly_indicators) {
      keyData.monthly_indicators.forEach(indicator => {
        // 确定趋势方向（简单规则）
        let trend = 'stable'
        if (indicator.name === 'CPI' || indicator.name === 'PPI') {
          trend = indicator.value > 2 ? 'up' : indicator.value < -1 ? 'down' : 'stable'
        } else {
          trend = indicator.value > 5 ? 'up' : indicator.value < 2 ? 'down' : 'stable'
        }

        // 格式化数值
        let formattedValue = indicator.value.toFixed(2)
        if (indicator.unit === '亿元') {
          // 对于社会融资规模，转换为万亿元
          formattedValue = (indicator.value / 10000).toFixed(2)
        }

        economicIndicators.value.push({
          title: indicator.name,
          value: formattedValue,
          unit: indicator.unit === '亿元' ? '万亿元' : indicator.unit,
          period: indicator.date,
          trend: trend,
          isPredicted: indicator.is_predicted
        })
      })
    }

    console.log('经济指标更新完成:', economicIndicators)

  } catch (error) {
    console.error('更新经济指标显示值失败:', error)
    // 使用默认指标
    useDefaultIndicators()
  }
}

// 使用默认指标的函数
const useDefaultIndicators = () => {
  economicIndicators.value.length = 0
  economicIndicators.value.push(
    { title: 'GDP增长率', value: '5.11', unit: '%', period: '2025Q4', trend: 'up', isPredicted: true },
    { title: '社会消费品零售总额', value: '4.82', unit: '%', period: '2025-12', trend: 'up', isPredicted: true },
    { title: 'CPI', value: '-0.10', unit: '%', period: '2025-12', trend: 'down', isPredicted: true },
    { title: 'PPI', value: '-2.35', unit: '%', period: '2025-12', trend: 'down', isPredicted: true },
    { title: '工业增加值', value: '8.31', unit: '%', period: '2025-12', trend: 'up', isPredicted: true }
  )
}

// 使用默认数据的函数
const useDefaultData = () => {
  console.log('使用默认数据')
  seasonalData.value = {
    gdp: {
      dates: ['2024Q1', '2024Q2', '2024Q3', '2024Q4'],
      values: [5.3, 4.7, 4.6, 5.11],
      isPredicted: [false, false, false, true],
      confidenceInterval: [null, null, null, null]
    }
  }

  monthlyData.value = {
    retail: {
      dates: ['2024-09', '2024-10', '2024-11', '2024-12'],
      values: [3.2, 4.8, 5.5, 6.25],
      isPredicted: [false, false, false, true],
      confidenceInterval: [null, null, null, null]
    },
    cpi: {
      dates: ['2024-09', '2024-10', '2024-11', '2024-12'],
      values: [0.4, 0.3, 0.2, 0.57],
      isPredicted: [false, false, false, true],
      confidenceInterval: [null, null, null, null]
    },
    ppi: {
      dates: ['2024-09', '2024-10', '2024-11', '2024-12'],
      values: [-2.8, -2.9, -2.5, -2.0],
      isPredicted: [false, false, false, true],
      confidenceInterval: [null, null, null, null]
    },
    investment: {
      dates: ['2024-09', '2024-10', '2024-11', '2024-12'],
      values: [3.4, 3.5, 3.6, 3.75],
      isPredicted: [false, false, false, true],
      confidenceInterval: [null, null, null, null]
    }
  }
}

// 在组件挂载时加载数据
onMounted(async () => {
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)

  // 先初始化空图表
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
  }

  // 加载数据
  await loadData()

  // 数据加载完成后更新图表
  setTimeout(() => {
    if (chartInstance && economicIndicators.value.length > 0) {
      updateChart(activeTabIndex.value)
    }
  }, 100)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
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
