<template>
	<view class="page-detail">
		<view v-if="!task" class="loading-state">加载中...</view>

		<template v-else>
			<!-- 任务信息卡片 -->
			<view class="info-card">
				<view class="header-row">
					<text class="type-tag" :class="'type-' + task.task_type">
						{{ typeLabels[task.task_type] }}
					</text>
					<text class="difficulty-tag" :class="'diff-' + task.difficulty">
						{{ diffLabels[task.difficulty] }}
					</text>
				</view>
				<text class="task-title">{{ task.title }}</text>
				<text class="task-reward">¥{{ task.reward_amount }}</text>
				<text v-if="task.description" class="task-desc">{{ task.description }}</text>
			</view>

			<!-- 商户信息 -->
			<view class="info-card">
				<view class="info-row">
					<text class="info-label">发布方</text>
					<text class="info-value">{{ task.merchant_name }}</text>
				</view>
				<view class="info-row">
					<text class="info-label">地址</text>
					<text class="info-value">{{ task.address || '未指定' }}</text>
				</view>
				<view class="info-row">
					<text class="info-label">预计耗时</text>
					<text class="info-value">{{ task.estimated_min }}分钟</text>
				</view>
				<view class="info-row">
					<text class="info-label">距你</text>
					<text class="info-value">{{ distance }}米</text>
				</view>
			</view>

			<!-- 底部操作按钮 -->
			<view class="bottom-bar">
				<button
					v-if="task.status === 0 && task.accepted_count < task.quantity"
					class="accept-btn"
					@tap="handleAccept"
					:loading="accepting"
					:disabled="accepting"
				>
					立即接单 - 赚 ¥{{ task.reward_amount }}
				</button>
				<text v-else class="full-tag">已满员 / 已结束</text>
			</view>
		</template>
	</view>
</template>

<script>
	import { getTaskDetail, acceptTask } from '@/api/index.js'

	export default {
		data() {
			return {
				task: null,
				accepting: false,
				distance: 0,
				typeLabels: { 1: '配送', 2: '搬运', 3: '巡检', 4: '其他' },
				diffLabels: { 1: '轻松', 2: '适中', 3: '挑战' }
			}
		},
		onLoad(options) {
			const id = options.id
			if (id) {
				this.loadTask(id)
			}
		},
		methods: {
			loadTask(id) {
				getTaskDetail(id)
					.then(data => {
						this.task = data
						this.distance = data.distance || 0
					})
					.catch(err => {
						uni.showToast({ title: '任务不存在', icon: 'none' })
						setTimeout(() => uni.navigateBack(), 1000)
					})
			},
			handleAccept() {
				const token = uni.getStorageSync('token')
				if (!token) {
					uni.showToast({ title: '请先登录', icon: 'none' })
					return
				}
				this.accepting = true
				acceptTask(this.task.id)
					.then(data => {
						uni.showToast({ title: '接单成功！', icon: 'success' })
						setTimeout(() => {
							uni.switchTab({ url: '/pages/order/list' })
						}, 1000)
					})
					.catch(err => {
						uni.showToast({ title: err.message || '接单失败', icon: 'none' })
					})
					.finally(() => {
						this.accepting = false
					})
			}
		}
	}
</script>

<style>
	.page-detail {
		padding: 30rpx;
		background: #f5f5f5;
		min-height: 100vh;
	}
	.loading-state { text-align: center; padding-top: 300rpx; color: #999; }

	.info-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
	}
	.header-row {
		display: flex;
		align-items: center;
		gap: 16rpx;
		margin-bottom: 16rpx;
	}
	.type-tag {
		padding: 6rpx 16rpx;
		border-radius: 8rpx;
		font-size: 22rpx;
	}
	.type-tag.type-1 { background: #e8f5e9; color: #2e7d32; }
	.type-tag.type-2 { background: #fff3e0; color: #e65100; }
	.type-tag.type-3 { background: #e3f2fd; color: #1565c0; }
	.difficulty-tag {
		padding: 6rpx 16rpx;
		border-radius: 8rpx;
		font-size: 22rpx;
		background: #f5f5f5;
		color: #999;
	}
	.task-title {
		font-size: 36rpx;
		font-weight: 700;
		color: #333;
		display: block;
		margin-bottom: 16rpx;
	}
	.task-reward {
		font-size: 48rpx;
		font-weight: 700;
		color: var(--primary);
		display: block;
		margin-bottom: 16rpx;
	}
	.task-desc {
		font-size: 28rpx;
		color: #666;
		line-height: 1.6;
		display: block;
	}
	.info-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16rpx 0;
		border-bottom: 2rpx solid #f5f5f5;
	}
	.info-row:last-child { border-bottom: none; }
	.info-label { font-size: 28rpx; color: #999; }
	.info-value { font-size: 28rpx; color: #333; }

	.bottom-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		padding: 20rpx 30rpx;
		padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
		background: #fff;
		border-top: 2rpx solid #f0f0f0;
	}
	.accept-btn {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 44rpx;
		font-size: 32rpx;
		font-weight: 600;
		border: none;
	}
	.full-tag {
		display: block;
		text-align: center;
		font-size: 28rpx;
		color: #999;
		padding: 20rpx;
	}
</style>
