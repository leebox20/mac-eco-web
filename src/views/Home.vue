<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 使用组件 -->
    <TheHeader />
    
    <!-- 主要内容 -->
    <main class="bg-background min-h-screen relative overflow-hidden pt-12 pb-12">
      <!-- 地图背景 -->
      <div class="absolute right-0 top-0 w-1/2 h-full pointer-events-none" style="z-index: 1;">
        <img src="@/assets/map/img_0.png" alt="" class="w-full h-full object-contain opacity-50">
      </div>
      
      <!-- 内容区域 -->
      <div class="max-w-7xl mx-auto pt-16 px-4 sm:px-6 lg:px-8 relative" style="z-index: 2;">
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

          <!-- 数据统计 -->
          <div class="grid grid-cols-3 gap-6 mb-16">
            <div class="bg-white rounded-lg p-6 shadow">
              <div class="text-[#666666] text-sm">今日已生成</div>
              <div class="mt-2">
                <span class="text-[32px] font-medium text-[#4080FF]">8323</span>
                <span class="text-base text-[#666666] ml-2">字</span>
              </div>
            </div>
            <div class="bg-white rounded-lg p-6 shadow">
              <div class="text-[#666666] text-sm">数据库已收录</div>
              <div class="mt-2">
                <span class="text-[32px] font-medium text-[#4080FF]">12353</span>
                <span class="text-base text-[#666666] ml-2">条</span>
              </div>
            </div>
            <div class="bg-white rounded-lg p-6 shadow">
              <div class="text-[#666666] text-sm">已使用该系统</div>
              <div class="mt-2">
                <span class="text-[32px] font-medium text-[#4080FF]">79</span>
                <span class="text-base text-[#666666] ml-2">天</span>
              </div>
            </div>
          </div>

          <!-- 功能入口 -->
          <h2 class="text-[18px] font-medium text-[#333333] mb-6">便捷功能入口</h2>
          <div class="grid grid-cols-2 gap-6">
            <!-- AI智能预测 -->
            <div class="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <div class="text-[#4080FF] mb-4">
                <i class="fas fa-robot text-3xl"></i>
              </div>
              <h3 class="text-[16px] font-medium text-[#1B2559] mb-2">AI智能预测</h3>
              <p class="text-[#64748B] text-sm leading-relaxed">
                基于先进算法，快速从海量数据中找到关键信息，提供高可信度的未来经济形势预测。
              </p>
            </div>

            <!-- 横向数据对比 -->
            <div class="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <div class="text-[#4080FF] mb-4">
                <i class="fas fa-chart-line text-3xl"></i>
              </div>
              <h3 class="text-[16px] font-medium text-[#1B2559] mb-2">横向数据对比</h3>
              <p class="text-[#64748B] text-sm leading-relaxed">
                从海量数据库轻松锁定不同行业和年份的经济趋势进行对比，数据至简，结果直观。
              </p>
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
</script>

<style scoped>
.custom-italic {
  font-style: italic;
  transform: skew(-15deg);
}
</style>
