import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = 'http://120.48.150.254:8888'

// 添加响应拦截器处理错误
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

export default axios 