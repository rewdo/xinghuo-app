// API 基础配置
import config from './config.js'
const BASE_URL = config.baseURL

// 获取存储的 token
function getToken() {
	try {
		return uni.getStorageSync('token')
	} catch (e) {
		return null
	}
}

// 通用请求方法
function request(method, path, data = {}, options = {}) {
	const token = getToken()
	const url = `${BASE_URL}${path}`

	return new Promise((resolve, reject) => {
		uni.request({
			url,
			method,
			data,
			header: {
				'Content-Type': 'application/json',
				'Authorization': token ? `Bearer ${token}` : '',
				...options.headers
			},
			timeout: options.timeout || 15000,
			success: (res) => {
				if (res.statusCode === 200) {
					const body = res.data
					if (body.code === 0) {
						resolve(body.data)
					} else if (body.code === 401) {
						// Token expired, redirect to login
						uni.removeStorageSync('token')
						uni.navigateTo({ url: '/pages/login/index' })
						reject(new Error(body.msg || '登录已过期'))
					} else {
						reject(new Error(body.msg || '请求失败'))
					}
				} else if (res.statusCode === 401) {
					uni.removeStorageSync('token')
					uni.navigateTo({ url: '/pages/login/index' })
					reject(new Error('登录已过期'))
				} else {
					reject(new Error(`请求失败 (${res.statusCode})`))
				}
			},
			fail: (err) => {
				reject(new Error('网络异常，请检查网络连接'))
			}
		})
	})
}

// ============= 用户相关 =============

export function wxLogin(code) {
	return request('POST', '/user/wxlogin', { code })
}

export function getUserProfile() {
	return request('GET', '/user/profile')
}

export function updateUserProfile(data) {
	return request('PUT', '/user/profile', data)
}

// ============= 任务相关 =============

export function getNearbyTasks(lat, lng, radius = 3000, params = {}) {
	return request('GET', '/tasks/nearby', { lat, lng, radius, ...params })
}

export function getTaskDetail(taskId) {
	return request('GET', `/tasks/${taskId}`)
}

export function acceptTask(taskId) {
	return request('POST', '/orders/accept', { task_id: taskId })
}

// ============= 订单相关 =============

export function getMyOrders(params = {}) {
	return request('GET', '/orders', params)
}

export function getOrderDetail(orderId) {
	return request('GET', `/orders/${orderId}`)
}

export function completeOrder(orderId) {
	return request('POST', `/orders/${orderId}/complete`)
}

export function cancelOrder(orderId) {
	return request('POST', `/orders/${orderId}/cancel`)
}

// ============= 钱包相关 =============

export function getWalletBalance() {
	return request('GET', '/wallet/balance')
}

export function getTransactions(params = {}) {
	return request('GET', '/wallet/transactions', params)
}

export function withdraw(amount) {
	return request('POST', '/wallet/withdraw', { amount })
}

// ============= 评价相关 =============

export function submitReview(data) {
	return request('POST', '/reviews', data)
}

export function getOrderReview(orderId) {
	return request('GET', `/reviews/order/${orderId}`)
}

// ============= 商户相关 =============

export function merchantRegister(data) {
	return request('POST', '/merchant/register', data)
}

export function getMerchantProfile(merchantId) {
	return request('GET', '/merchant/profile', { merchant_id: merchantId })
}

export function createTask(data) {
	return request('POST', '/tasks/create', data)
}

export function getMerchantTasks(merchantId, params = {}) {
	return request('GET', '/tasks/manage', { merchant_id: merchantId, ...params })
}

export function confirmTaskComplete(taskId, merchantId) {
	return request('POST', `/merchant/tasks/${taskId}/confirm`, { merchant_id: merchantId })
}
