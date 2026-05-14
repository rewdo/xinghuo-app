<template>
	<view class="page-order-detail">
		<view v-if="!order" class="loading-state">加载中...</view>

		<template v-else>
			<!-- 订单状态 -->
			<view class="status-bar" :class="'status-' + order.status">
				<text class="status-text">{{ statusLabels[order.status] }}</text>
				<text class="status-hint">{{ statusHint }}</text>
			</view>

			<!-- 任务信息 -->
			<view class="info-card">
				<text class="info-title">{{ order.task_title }}</text>
				<text class="info-reward">¥{{ order.reward_amount }}</text>
			</view>

			<!-- 时间线 -->
			<view class="timeline-card">
				<view class="timeline-item">
					<view class="dot"></view>
					<view class="content">
						<text class="content-title">接单</text>
						<text class="content-time">{{ order.accepted_at }}</text>
					</view>
				</view>
				<view class="timeline-item" v-if="order.completed_at">
					<view class="dot done"></view>
					<view class="content">
						<text class="content-title">完成</text>
						<text class="content-time">{{ order.completed_at }}</text>
					</view>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="buttons">
				<button
					v-if="order.status === 1"
					class="btn-primary"
					@tap="handleComplete"
				>
					标记已完成
				</button>
				<button
					v-if="order.status === 0 || order.status === 1"
					class="btn-danger"
					@tap="handleCancel"
				>
					取消订单
				</button>
			</view>
		</template>
	</view>
</template>

<script>
	import { getOrderDetail, completeOrder, cancelOrder } from '@/api/index.js'

	export default {
		data() {
			return {
				order: null,
				statusLabels: { 0: '已接单', 1: '进行中', 2: '待确认', 3: '已完成', 4: '已取消' },
				statusHint: ''
			}
		},
		onLoad(options) {
			if (options.id) this.loadOrder(options.id)
		},
		methods: {
			loadOrder(id) {
				getOrderDetail(id)
					.then(data => {
						this.order = data
						this.statusHint = {
							0: '前往任务地点开始执行', 1: '执行完成后等待商户确认',
							2: '商户确认后将结算收益', 3: '收益已入账', 4: '任务已被取消'
						}[data.status] || ''
					})
					.catch(() => {
						uni.showToast({ title: '订单不存在', icon: 'none' })
						setTimeout(() => uni.navigateBack(), 1000)
					})
			},
			handleComplete() {
				completeOrder(this.order.id)
					.then(() => {
						uni.showToast({ title: '已标记完成，等待商户确认', icon: 'success' })
						this.loadOrder(this.order.id)
					})
					.catch(err => uni.showToast({ title: err.message, icon: 'none' }))
			},
			handleCancel() {
				uni.showModal({
					title: '提示',
					content: '确定取消这个订单吗？',
					success: (res) => {
						if (res.confirm) {
							cancelOrder(this.order.id)
								.then(() => {
									uni.showToast({ title: '已取消', icon: 'success' })
									this.loadOrder(this.order.id)
								})
								.catch(err => uni.showToast({ title: err.message, icon: 'none' }))
						}
					}
				})
			}
		}
	}
</script>

<style>
	.page-order-detail { background: #f5f5f5; min-height: 100vh; }

	.loading-state { text-align: center; padding-top: 300rpx; color: #999; }

	.status-bar {
		padding: 40rpx 30rpx;
		color: #fff;
	}
	.status-bar.status-0 { background: #1565c0; }
	.status-bar.status-1 { background: var(--primary); }
	.status-bar.status-2 { background: var(--warning); }
	.status-bar.status-3 { background: var(--success); }
	.status-bar.status-4 { background: #999; }
	.status-text { font-size: 40rpx; font-weight: 700; display: block; }
	.status-hint { font-size: 24rpx; opacity: 0.8; margin-top: 8rpx; display: block; }

	.info-card {
		background: #fff;
		margin: 30rpx;
		padding: 30rpx;
		border-radius: 16rpx;
	}
	.info-title { font-size: 32rpx; font-weight: 600; display: block; margin-bottom: 16rpx; }
	.info-reward { font-size: 48rpx; font-weight: 700; color: var(--primary); }

	.timeline-card {
		background: #fff;
		margin: 0 30rpx 30rpx;
		padding: 30rpx;
		border-radius: 16rpx;
	}
	.timeline-item {
		display: flex;
		align-items: flex-start;
		padding: 16rpx 0;
		position: relative;
	}
	.dot {
		width: 20rpx;
		height: 20rpx;
		border-radius: 50%;
		background: var(--primary);
		margin-right: 16rpx;
		margin-top: 8rpx;
		flex-shrink: 0;
	}
	.dot.done { background: var(--success); }
	.content-title { font-size: 28rpx; color: #333; display: block; }
	.content-time { font-size: 22rpx; color: #999; display: block; margin-top: 4rpx; }

	.buttons { padding: 0 30rpx; }
	.btn-primary {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 44rpx;
		font-size: 30rpx;
		border: none;
		margin-bottom: 16rpx;
	}
	.btn-danger {
		width: 100%;
		height: 80rpx;
		line-height: 80rpx;
		background: #fff;
		color: var(--danger);
		border-radius: 40rpx;
		font-size: 28rpx;
		border: 2rpx solid var(--danger);
	}
</style>
