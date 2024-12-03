<template>
  <div class="min-h-screen bg-[#f2f5f8]">
    <!-- 使用组件 -->
    <TheHeader />
    
    <!-- 主要内容 -->
    <main class="main-bg min-h-screen relative overflow-hidden mb-12">
      <!-- 地图背景 -->
      <div class="absolute right-0 top-0 w-1/2 h-full pointer-events-none" style="z-index: 1;">
        <img src="@/assets/map/img_0.png" alt="" class="w-full h-full object-contain opacity-50">
      </div>
      
      <!-- 内容区域 -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative pt-24" style="z-index: 2;">
        <div class="max-w-3xl">
          <!-- 欢迎区域 -->
          <div class="mb-16 text-left">
            <h1 class="text-2xl font-medium text-gray-900 leading-tight">
              欢迎使用<span class="text-primary">中国宏观经济大数据AI预测系统</span>！
            </h1>
            <p class="mt-8 text-base text-gray-600 leading-7">
              我们致力于为用户提供专业、高效的宏观经济趋势分析服务。通过强大的大数据处理能力，我们能够轻松找到特定年份某个行业的经济趋势，并与其他年份进行精准对比，从而帮助您清晰了解行业发展的脉络与变化。
            </p>
            <p class="mt-6 text-base text-gray-600 leading-7">
              不仅如此，基于对历史数据的深入分析和先进的预测算法，我们可以对未来的经济形势进行科学预测，为您的战略决策提供可靠依据，无论是投资、市场研究，还是政策制定，我们都能助您一臂之力。
            </p>
          </div>

          <!-- Economic Indicators -->
          <div class="mb-16">
            <h3 class="text-lg font-medium mb-4 text-left">次月/季数据预测：</h3>
            <div class="grid grid-cols-3 gap-6">
              <div v-for="(indicator, index) in economicIndicators" 
                  :key="index"
                  class="bg-white rounded-lg p-4 shadow-sm">
                <div class="text-sm text-gray-600">{{ indicator.label }}</div>
                <div class="mt-2 h-12 flex items-center justify-center">
                  <div class="number-container flex items-center justify-center">
                    <transition name="scroll" mode="out-in">
                      <div :key="scrollTrigger" class="flex items-center justify-center">
                        <CountTo
                          :startVal="0"
                          :endVal="parseFloat(indicator.value)"
                          :duration="2000"
                          :decimals="1"
                          @finished="triggerScroll"
                          class="text-[#4080FF] text-3xl font-medium"
                        />
                        <span class="ml-1 text-gray-600 text-xl">%</span>
                      </div>
                    </transition>
                  </div>
                </div>
              </div>
            </div>
          </div>



          <!-- Feature Section -->
          <h2 class="text-lg font-medium text-gray-900 mb-6 text-left">便捷功能入口</h2>
          <div class="grid grid-cols-2 gap-6">
            <div v-for="(feature, index) in features" 
                 :key="index"
                 class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
              <div class="w-full bg-gradient-to-br from-blue-50 to-white ">
                <img :src="feature.icon" :alt="feature.title" class="w-full h-full object-contain  rounded-t-lg" />
              </div>
              <div class="px-6 py-4">
                <h3 class="text-base font-medium text-gray-900 mb-1">{{ feature.title }}</h3>
                <p class="text-gray-600 text-sm">{{ feature.description }}</p>
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
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { ref, onMounted } from 'vue'
import { CountTo } from 'vue3-count-to'
import aiPredictionIcon from '@/assets/forecast.png'
import dataComparisonIcon from '@/assets/data-compare.png'

const economicIndicators = [
  { label: 'GDP:不变价当季同比', value: '12.5' },
  { label: '工业增加值:当月同比', value: '8.2' },
  { label: '固定资产投资:累计同比', value: '6.8' },
  { label: '社会消费品零售总额:当月同比', value: '7.6' },
  { label: '居民消费价格指数:当月同比', value: '2.3' },
]

const features = [
  {
    title: 'AI智能预测',
    description: '基于先进算法，快速从海量数据中找到关键信息，提供高可信度的未来经济形势预测。',
    icon: aiPredictionIcon
  },
  {
    title: '横向数据对比',
    description: '从海量数据库轻松锁定不同行业和年份的经济趋势进行对比，数据至简，结果直观。',
    icon: dataComparisonIcon
  }
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
</script>

<style scoped>
.number-container {
  height: 3rem;
  width: 100%;
  overflow: hidden;
}

.main-bg {
  background-color: #f2f5f8;
  background-image: url('/src/assets/home-body-bg.png');
  background-size: 60% 60%;
  background-position: -60% -20%;
  background-repeat: no-repeat;
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
</style>
