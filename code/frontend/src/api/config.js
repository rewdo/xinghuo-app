// API 基础配置
const ENV = 'production'

const API_CONFIG = {
  development: {
    baseURL: 'http://localhost:5000/api/v1',
    name: '开发环境（本地）'
  },
  production: {
    baseURL: 'http://xinghuo.yiouxiaozhan.top/api/v1',
    name: '生产环境（服务器）'
  }
}

const config = API_CONFIG[ENV]
const BASE_URL = config.baseURL

console.log(`[星火] 当前环境: ${config.name}`)

export default config
