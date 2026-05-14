<template>
	<view class="page-index">
		<!-- 顶部定位栏 -->
		<view class="header">
			<view class="location-bar" @tap="chooseLocation">
				<text class="icon-location">📍</text>
				<text class="location-text">{{ locationText }}</text>
				<text class="icon-arrow">▼</text>
			</view>
			<view class="header-right">
				<text class="badge-text" @tap="goWallet">¥{{ balance }}</text>
			</view>
		</view>

		<!-- 快捷筛选 -->
		<scroll-view class="filter-bar" scroll-x enable-flex>
			<view
				v-for="(item, idx) in taskFilters"
				:key="idx"
				class="filter-item"
				:class="{ active: currentFilter === item.value }"
				@tap="switchFilter(item.value)"
			>
				{{ item.label }}
			</view>
		</scroll-view>

		<!-- 任务列表 -->
		<scroll-view
			class="task-list"
			scroll-y
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<view v-if="loading && tasks.length === 0" class="loading-state">
				<text>加载中...</text>
			</view>

			<view v-else-if="tasks.length === 0" class="empty-state">
				<text class="empty-icon">📭</text>
				<text class="empty-text">附近暂无任务</text>
				<text class="empty-hint">稍后再来看看吧</text>
			</view>

			<view v-else class="task-cards">
				<view
					v-for="task in tasks"
					:key="task.id"
					class="task-card"
					@tap="goTaskDetail(task.id)"
				>
					<view class="card-header">
						<text class="task-type-tag" :class="'type-' + task.task_type">
							{{ typeLabels[task.task_type] }}
						</text>
						<text class="task-distance">{{ task.distance }}m</text>
					</view>
					<text class="task-title">{{ task.title }}</text>
					<view class="card-footer">
						<text class="task-reward">¥{{ task.reward_amount }}</text>
						<text class="task-merchant">{{ task.merchant_name }}</text>
					</view>
				</view>
			</view>

			<view v-if="loadingMore" class="load-more">
				<text>加载更多...</text>
			</view>
		</scroll-view>

		<!-- 商户入口 -->
		<view class="merchant-entry" @tap="goMerchant">
			<text class="entry-icon">🏪</text>
			<text class="entry-text">我是商户，发布任务</text>
			<text class="entry-arrow">›</text>
		</view>

		<!-- 登录授权弹窗 -->
		<view v-if="showLogin" class="login-overlay">
			<view class="login-box">
				<text class="login-title">欢迎来到星火</text>
				<text class="login-desc">动起来，就有价值</text>
				<button class="login-btn" type="primary" open-type="getUserInfo" @getuserinfo="handleLogin">
					微信一键登录
				</button>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		getNearbyTasks,
		getWalletBalance,
		wxLogin,
		getUserProfile
	} from '@/api/index.js'

	export default {
		data() {
			return {
				tasks: [],
				page: 1,
				loading: false,
				loadingMore: false,
				refreshing: false,
				hasMore: true,
				locationText: '获取位置中...',
				lat: null,
				lng: null,
				balance: '0.00',
				currentFilter: 0,
				showLogin: false,
				taskFilters: [
					{ label: '全部', value: 0 },
					{ label: '配送', value: 1 },
					{ label: '搬运', value: 2 },
					{ label: '巡检', value: 3 },
					{ label: '其他', value: 4 }
				],
				typeLabels: { 1: '配送', 2: '搬运', 3: '巡检', 4: '其他' }
			}
		},

		onLoad() {
			this.checkLogin()
		},

		onShow() {
			if (this.lat && this.lng) {
				this.loadTasks(true)
				this.loadBalance()
			}
		},

		methods: {
			// 检查登录状态
			checkLogin() {
				const token = uni.getStorageSync('token')
				if (!token) {
					this.showLogin = true
					return
				}
				this.initLocation()
				this.loadBalance()
			},

			// 微信登录
			handleLogin(e) {
				uni.login({
					provider: 'weixin',
					success: (res) => {
						wxLogin(res.code)
							.then(data => {
								uni.setStorageSync('token', data.token)
								uni.setStorageSync('userInfo', data.user)
								this.showLogin = false
								this.initLocation()
								this.loadBalance()
							})
							.catch(err => {
								uni.showToast({ title: '登录失败', icon: 'none' })
							})
					},
					fail: () => {
						uni.showToast({ title: '授权失败', icon: 'none' })
					}
				})
			},

			// 初始化位置
			initLocation() {
				uni.getLocation({
					type: 'gcj02',
					success: (res) => {
						this.lat = res.latitude
						this.lng = res.longitude
						this.locationText = '附近位置'
						this.loadTasks(true)
					},
					fail: () => {
						this.locationText = '定位失败'
						uni.showToast({ title: '请开启位置权限', icon: 'none' })
					}
				})
			},

			// 加载任务列表
			loadTasks(reset = false) {
				if (reset) {
					this.page = 1
					this.hasMore = true
					this.loading = true
				}

				if (!this.hasMore || !this.lat) return

				const params = { page: this.page, per_page: 20 }
				if (this.currentFilter > 0) params.task_type = this.currentFilter

				getNearbyTasks(this.lat, this.lng, 3000, params)
					.then(data => {
						if (reset) {
							this.tasks = data.tasks || []
						} else {
							this.tasks = this.tasks.concat(data.tasks || [])
						}
						this.hasMore = this.tasks.length < data.total
						this.page++
					})
					.catch(err => {
						if (reset) this.tasks = []
					})
					.finally(() => {
						this.loading = false
						this.loadingMore = false
						this.refreshing = false
					})
			},

			// 加载更多
			loadMore() {
				if (!this.loadingMore && this.hasMore) {
					this.loadingMore = true
					this.loadTasks()
				}
			},

			// 下拉刷新
			onRefresh() {
				this.refreshing = true
				this.loadTasks(true)
			},

			// 切换筛选
			switchFilter(value) {
				this.currentFilter = value
				this.loadTasks(true)
			},

			// 加载余额
			loadBalance() {
				getWalletBalance()
					.then(data => {
						this.balance = data.balance.toFixed(2)
					})
					.catch(() => {})
			},

			// 选择位置
			chooseLocation() {
				uni.chooseLocation({
					success: (res) => {
						this.lat = res.latitude
						this.lng = res.longitude
						this.locationText = res.name || '已选位置'
						this.loadTasks(true)
					}
				})
			},

			// 跳转
			goTaskDetail(id) {
				uni.navigateTo({ url: `/pages/task/detail?id=${id}` })
			},
			goWallet() {
				uni.navigateTo({ url: '/pages/wallet/index' })
			},
			goMerchant() {
				uni.navigateTo({ url: '/pages/merchant/index' })
			}
		}
	}
</script>

<style>
	.page-index {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background: #f5f5f5;
		position: relative;
	}

	/* 头部 */
	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 20rpx 30rpx;
		background: #fff;
		border-bottom: 2rpx solid #f0f0f0;
	}
	.location-bar {
		display: flex;
		align-items: center;
		gap: 8rpx;
	}
	.icon-location { font-size: 32rpx; }
	.location-text { font-size: 30rpx; font-weight: 600; color: #333; }
	.icon-arrow { font-size: 20rpx; color: #999; }
	.badge-text {
		font-size: 28rpx;
		color: var(--primary);
		font-weight: 600;
		padding: 8rpx 20rpx;
		background: var(--primary-bg);
		border-radius: 30rpx;
	}

	/* 筛选栏 */
	.filter-bar {
		white-space: nowrap;
		padding: 20rpx 30rpx;
		background: #fff;
	}
	.filter-item {
		display: inline-block;
		padding: 12rpx 28rpx;
		margin-right: 16rpx;
		border-radius: 30rpx;
		font-size: 26rpx;
		color: #666;
		background: #f5f5f5;
	}
	.filter-item.active {
		color: #fff;
		background: var(--primary);
	}

	/* 任务列表 */
	.task-list {
		flex: 1;
		padding: 0 30rpx;
	}
	.task-cards {
		padding: 20rpx 0;
	}
	.task-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
	}
	.card-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 16rpx;
	}
	.task-type-tag {
		padding: 6rpx 16rpx;
		border-radius: 8rpx;
		font-size: 22rpx;
		background: #f0f0f0;
		color: #666;
	}
	.task-type-tag.type-1 { background: #e8f5e9; color: #2e7d32; }
	.task-type-tag.type-2 { background: #fff3e0; color: #e65100; }
	.task-type-tag.type-3 { background: #e3f2fd; color: #1565c0; }
	.task-distance { font-size: 24rpx; color: #999; }
	.task-title {
		font-size: 30rpx;
		font-weight: 600;
		color: #333;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		margin-bottom: 16rpx;
	}
	.card-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.task-reward {
		font-size: 36rpx;
		font-weight: 700;
		color: var(--primary);
	}
	.task-merchant {
		font-size: 24rpx;
		color: #999;
	}

	/* 空状态 */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 200rpx;
	}
	.empty-icon { font-size: 80rpx; margin-bottom: 20rpx; }
	.empty-text { font-size: 30rpx; color: #666; }
	.empty-hint { font-size: 24rpx; color: #999; margin-top: 10rpx; }
	.loading-state { text-align: center; padding-top: 300rpx; color: #999; }
	.load-more { text-align: center; padding: 30rpx; color: #999; font-size: 24rpx; }

	/* 商户入口 */
	.merchant-entry {
		position: fixed;
		right: 30rpx;
		bottom: 140rpx;
		background: var(--primary);
		color: #fff;
		padding: 20rpx 30rpx;
		border-radius: 40rpx;
		display: flex;
		align-items: center;
		gap: 10rpx;
		box-shadow: 0 4rpx 20rpx rgba(255,107,53,0.4);
		z-index: 100;
	}
	.entry-icon { font-size: 28rpx; }
	.entry-text { font-size: 24rpx; font-weight: 500; }
	.entry-arrow { font-size: 28rpx; }

	/* 登录弹窗 */
	.login-overlay {
		position: fixed;
		top: 0; left: 0; right: 0; bottom: 0;
		background: rgba(0,0,0,0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 999;
	}
	.login-box {
		background: #fff;
		border-radius: 24rpx;
		padding: 60rpx 50rpx;
		width: 560rpx;
		text-align: center;
	}
	.login-title {
		font-size: 40rpx;
		font-weight: 700;
		color: #333;
		margin-bottom: 12rpx;
	}
	.login-desc {
		font-size: 28rpx;
		color: #999;
		margin-bottom: 50rpx;
	}
	.login-btn {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 44rpx;
		font-size: 30rpx;
		border: none;
	}
</style>
