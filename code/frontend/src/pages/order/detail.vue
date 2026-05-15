<template>
	<view class="page">
		<view class="nav-bar">
			<text class="back-btn" @tap="goBack">‹ 返回</text>
			<text class="nav-title">订单详情</text>
			<text class="nav-placeholder"></text>
		</view>

		<view class="status-banner" :class="'s' + (order.status || 0)">
			<text class="status-icon">{{ STATUS_ICONS[order.status || 0] }}</text>
			<text class="status-text">{{ STATUS_LABELS[order.status || 0] }}</text>
		</view>

		<!-- 任务信息 -->
		<view class="section">
			<view class="section-title">📋 任务信息</view>
			<text class="task-title">{{ order.title || '' }}</text>
			<view class="task-tags">
				<text class="tag">🔥 消耗{{ order.estimated_calories || 0 }}大卡</text>
				<text class="tag">⏱ {{ order.estimated_min || 0 }}分钟</text>
			</view>
		</view>

		<!-- 奖励明细 -->
		<view class="section">
			<view class="section-title">🎁 奖励明细</view>
			<view class="reward-row" v-if="order.commission_received > 0">
				<text class="rw-icon">💰</text>
				<text class="rw-label">佣金到账</text>
				<text class="rw-amount">+{{ order.commission_received }}元</text>
			</view>
			<view class="reward-row" v-if="order.points_received > 0">
				<text class="rw-icon">⭐</text>
				<text class="rw-label">平台积分</text>
				<text class="rw-amount blue">+{{ order.points_received }}</text>
			</view>
			<view class="reward-row" v-if="order.coupon_desc">
				<text class="rw-icon">🎫</text>
				<text class="rw-label">商户优惠券</text>
				<text class="rw-amount green">{{ order.coupon_desc }}</text>
			</view>
			<view v-else class="no-reward">
				<text>暂无其他奖励</text>
			</view>
		</view>

		<!-- 时间线 -->
		<view class="section">
			<view class="section-title">🕐 时间线</view>
			<view class="timeline-item">
				<text class="tl-time">{{ order.created_at || '-' }}</text>
				<text class="tl-dot">●</text>
				<text class="tl-text">接单</text>
			</view>
			<view class="timeline-item" v-if="order.completed_at">
				<text class="tl-time">{{ order.completed_at }}</text>
				<text class="tl-dot">●</text>
				<text class="tl-text">完成</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			order: {},
			STATUS_LABELS: {0:'进行中',1:'执行中',2:'待确认',3:'已完成',4:'已取消'},
			STATUS_ICONS: {0:'⏳',1:'🏃',2:'✅',3:'🎉',4:'🚫'},
			demo: {
				id:2, title:'帮王阿姨送菜', status:3,
				estimated_calories:180, estimated_min:30,
				commission_received:5.00, points_received:60,
				coupon_desc:'满20减5',
				created_at:'2026-05-14 15:20', completed_at:'2026-05-14 16:15'
			}
		}
	},
	onLoad(options) {
		this.loadOrder(options.id)
	},
	methods: {
		loadOrder(id) {
			this.order = this.demo
		},
		goBack() { uni.navigateBack() }
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; }
.nav-bar { display: flex; align-items: center; padding: 60rpx 30rpx 20rpx; background: #fff; justify-content: space-between; }
.back-btn { font-size: 28rpx; color: #ff6b35; }
.nav-title { font-size: 28rpx; font-weight: bold; color: #333; }
.nav-placeholder { width: 80rpx; }

.status-banner { margin: 20rpx 30rpx; padding: 24rpx; border-radius: 16rpx; display: flex; align-items: center; }
.s3 { background: #e8f5e9; }
.status-icon { font-size: 40rpx; margin-right: 16rpx; }
.status-text { font-size: 28rpx; font-weight: bold; color: #2e7d32; }

.section { background: #fff; margin: 20rpx 30rpx; padding: 30rpx; border-radius: 16rpx; }
.section-title { font-size: 26rpx; font-weight: bold; color: #333; margin-bottom: 16rpx; }
.task-title { font-size: 32rpx; font-weight: bold; color: #333; display: block; margin-bottom: 12rpx; }
.task-tags { display: flex; gap: 12rpx; }
.tag { font-size: 22rpx; color: #ff6b35; background: #fff8f0; padding: 6rpx 16rpx; border-radius: 20rpx; }

.reward-row { display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.reward-row:last-child { border-bottom: none; }
.rw-icon { font-size: 32rpx; margin-right: 16rpx; }
.rw-label { flex: 1; font-size: 26rpx; color: #333; }
.rw-amount { font-size: 28rpx; font-weight: bold; color: #e6a817; }
.blue { color: #2196f3; }
.green { color: #4caf50; }
.no-reward { font-size: 24rpx; color: #ccc; padding: 10rpx 0; }

.timeline-item { display: flex; align-items: center; padding: 12rpx 0; }
.tl-time { width: 160rpx; font-size: 22rpx; color: #999; }
.tl-dot { font-size: 18rpx; color: #ff6b35; margin: 0 16rpx; }
.tl-text { font-size: 24rpx; color: #333; }
</style>
