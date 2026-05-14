<template>
	<view class="page-orders">
		<!-- 状态筛选 -->
		<view class="tabs">
			<view
				v-for="tab in tabs"
				:key="tab.value"
				class="tab-item"
				:class="{ active: currentTab === tab.value }"
				@tap="switchTab(tab.value)"
			>
				{{ tab.label }}
			</view>
		</view>

		<scroll-view scroll-y class="order-list" @scrolltolower="loadMore">
			<view v-if="loading && orders.length === 0" class="loading-state">加载中...</view>

			<view v-else-if="orders.length === 0" class="empty-state">
				<text class="empty-icon">📋</text>
				<text class="empty-text">暂无订单</text>
			</view>

			<view v-else class="order-cards">
				<view
					v-for="order in orders"
					:key="order.id"
					class="order-card"
					@tap="goDetail(order.id)"
				>
					<view class="order-header">
						<text class="order-title">{{ order.task_title }}</text>
						<text class="order-status" :class="'status-' + order.status">
							{{ statusLabels[order.status] }}
						</text>
					</view>
					<view class="order-footer">
						<text class="order-reward">¥{{ order.reward_amount }}</text>
						<text class="order-time">{{ formatTime(order.accepted_at) }}</text>
					</view>
				</view>
			</view>

			<view v-if="loadingMore" class="load-more">加载更多...</view>
		</scroll-view>
	</view>
</template>

<script>
	import { getMyOrders } from '@/api/index.js'

	export default {
		data() {
			return {
				orders: [],
				currentTab: 0,
				page: 1,
				loading: false,
				loadingMore: false,
				hasMore: true,
				tabs: [
					{ label: '全部', value: 0 },
					{ label: '进行中', value: 1 },
					{ label: '待确认', value: 2 },
					{ label: '已完成', value: 3 }
				],
				statusLabels: {
					0: '已接单', 1: '进行中', 2: '待确认', 3: '已完成', 4: '已取消'
				}
			}
		},
		onShow() {
			this.loadOrders(true)
		},
		methods: {
			loadOrders(reset) {
				if (reset) { this.page = 1; this.hasMore = true; this.loading = true }
				if (!this.hasMore) return

				const params = { page: this.page, per_page: 20 }
				if (this.currentTab > 0) params.status = this.currentTab

				getMyOrders(params)
					.then(data => {
						if (reset) this.orders = data.orders || []
						else this.orders = this.orders.concat(data.orders || [])
						this.hasMore = this.orders.length < data.total
						this.page++
					})
					.catch(() => {})
					.finally(() => {
						this.loading = false
						this.loadingMore = false
					})
			},
			switchTab(value) {
				this.currentTab = value
				this.loadOrders(true)
			},
			loadMore() {
				if (!this.loadingMore && this.hasMore) {
					this.loadingMore = true
					this.loadOrders()
				}
			},
			goDetail(id) {
				uni.navigateTo({ url: `/pages/order/detail?id=${id}` })
			},
			formatTime(t) {
				if (!t) return ''
				return t.split('T')[0]
			}
		}
	}
</script>

<style>
	.page-orders { background: #f5f5f5; min-height: 100vh; }

	.tabs {
		display: flex;
		background: #fff;
		padding: 20rpx 30rpx;
		gap: 20rpx;
	}
	.tab-item {
		padding: 12rpx 24rpx;
		font-size: 26rpx;
		color: #666;
		border-radius: 8rpx;
	}
	.tab-item.active {
		color: var(--primary);
		background: var(--primary-bg);
		font-weight: 600;
	}

	.order-list { padding: 20rpx 30rpx; height: calc(100vh - 100rpx); }
	.order-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
	}
	.order-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}
	.order-title { font-size: 30rpx; font-weight: 600; flex: 1; }
	.order-status { font-size: 24rpx; padding: 6rpx 16rpx; border-radius: 8rpx; }
	.order-status.status-1 { background: #e3f2fd; color: #1565c0; }
	.order-status.status-2 { background: #fff3e0; color: #e65100; }
	.order-status.status-3 { background: #e8f5e9; color: #2e7d32; }

	.order-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.order-reward { font-size: 32rpx; font-weight: 700; color: var(--primary); }
	.order-time { font-size: 24rpx; color: #999; }

	.empty-state { text-align: center; padding-top: 200rpx; }
	.empty-icon { font-size: 80rpx; }
	.empty-text { font-size: 28rpx; color: #999; margin-top: 16rpx; }
	.loading-state { text-align: center; padding-top: 300rpx; color: #999; }
	.load-more { text-align: center; padding: 30rpx; color: #999; }
</style>
