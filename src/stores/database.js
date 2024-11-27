import { defineStore } from 'pinia'

export const useDatabaseStore = defineStore('database', {
  state: () => ({
    filters: {
      timeRange: '最近一年',
      indicators: ['GDP'],
      region: '全球'
    },
    data: [
      {
        indicator: 'GDP',
        region: '中国',
        time: '2023 Q4',
        value: '121.02万亿',
        yoy: '+5.2%'
      },
      // 可以添加更多示例数据
    ],
    loading: false,
    currentPage: 1,
    totalPages: 10,
    itemsPerPage: 5
  }),
  
  actions: {
    async fetchData() {
      this.loading = true
      try {
        // TODO: 实现实际的API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        // 模拟数据
        this.data = Array(5).fill(null).map((_, index) => ({
          indicator: 'GDP',
          region: '中国',
          time: '2023 Q4',
          value: '121.02万亿',
          yoy: '+5.2%'
        }))
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        this.loading = false
      }
    },

    updateFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
      this.fetchData()
    },

    setPage(page) {
      this.currentPage = page
      this.fetchData()
    }
  }
})
