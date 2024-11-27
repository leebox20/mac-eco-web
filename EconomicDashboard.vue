<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <TheHeader />


    <!-- Subheader -->
    <div class="bg-[#4479e7] text-white px-4 py-2">
      <div class="container mx-auto flex items-center space-x-2">
        <DatabaseIcon class="h-5 w-5" />
        <span>数据筛选</span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto p-4">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <!-- Tabs and Search -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex space-x-4">
            <button class="text-blue-600 font-medium border-b-2 border-blue-600 px-4 py-2">全部</button>
            <button class="text-gray-600 hover:text-blue-600 px-4 py-2">
              区域
              <ChevronDownIcon class="h-4 w-4 inline-block ml-1" />
            </button>
            <button class="text-gray-600 hover:text-blue-600 px-4 py-2">
              政策
              <ChevronDownIcon class="h-4 w-4 inline-block ml-1" />
            </button>
          </div>
          <div class="flex items-center space-x-4">
            <div class="relative">
              <SearchIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="搜索"
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button class="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 flex items-center space-x-1">
              <BarChartIcon class="h-5 w-5" />
              <span>对比</span>
            </button>
          </div>
        </div>

        <!-- Chart Section -->
        <div class="space-y-6">
          <div v-for="i in 2" :key="i" class="border rounded-lg p-4">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium">中国金融机构:各项贷款余额:人民币:同比</h2>
              <div class="text-gray-500 text-sm">
                <span>来源：中国人民银行</span>
                <span class="ml-4">M0001381</span>
              </div>
            </div>
            <!-- Placeholder for Chart -->
            <div class="h-64 bg-gray-100 rounded flex items-center justify-center">
              Chart Component Would Go Here
            </div>
          </div>
        </div>
      </div>
    </main>

    <TheFooter />

    
  </div>
</template>

<script setup>
import { 
  HomeIcon, 
  DatabaseIcon, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  BrainCircuitIcon
} from 'lucide-vue-next'
</script>