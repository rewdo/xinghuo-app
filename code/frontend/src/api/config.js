// API 基础配置 - 可切换开发/生产环境
// 开发环境：连接本地 Flask 后端
// 生产环境：连接正式服务器

const ENV = 'development' // 切换为 'production' 时使用正式地址

const API_CONFIG = {
  development: {
    baseURL: 'http://localhost:5000/api/v1',
    name: '开发环境（本地）'
  },
  production: {
    baseURL: 'https://xinghuo.tongshengwangluo.com/api/v1',
    name: '生产环境（正式）'
  }
}

const config = API_CONFIG[ENV]
const BASE_URL = config.baseURL

console.log(`[星火] 当前环境: ${config.name}`)

export default config
