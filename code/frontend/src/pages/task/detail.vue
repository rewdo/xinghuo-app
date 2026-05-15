<template>
	<view class="page">
		<view class="nav-bar">
			<text class="back-btn" @tap="goBack">‹ 返回</text>
			<text class="nav-title">任务详情</text>
			<text class="nav-placeholder"></text>
		</view>

		<view class="task-header">
			<view class="task-emojis"><text class="big-emoji">{{ ICONS[task.fitness_tag] || '📋' }}</text></view>
			<text class="task-title">{{ task.title }}</text>
			<text class="task-merchant">{{ task.merchant_name || '附近商户' }}</text>
		</view>

		<view class="fitness-card">
			<view class="card-title">🏋️ 训练价值</view>
			<view class="fitness-grid">
				<view class="fitness-item">
					<text class="fitness-value">{{ task.estimated_calories || 0 }}</text>
					<text class="fitness-label">🔥 消耗大卡</text>
				</view>
				<view class="fitness-item">
					<text class="fitness-value">{{ task.exercise_benefit || '全身' }}</text>
					<text class="fitness-label">💪 锻炼效果</text>
				</view>
				<view class="fitness-item">
					<text class="fitness-value">{{ task.estimated_min || 0 }}</text>
					<text class="fitness-label">⏱ 用时(分钟)</text>
				</view>
				<view class="fitness-item">
					<text class="fitness-value">{{ task.distance_meters || 0 }}</text>
					<text class="fitness-label">📍 距离(米)</text>
				</view>
			</view>
			<view class="ai-calc">
				<text class="ai-label">🔥 AI帮你算：完成此单 = {{ TYPES[task.fitness_tag] || '有氧运动' }} {{ task.estimated_min || 0 }}分钟</text>
			</view>
		</view>

		<view class="rewards-card">
			<view class="card-title">🎁 任务奖励</view>
			<view class="reward-row">
				<text class="rw-icon">💰</text>
				<view class="rw-info">
					<text class="rw-label">佣金</text>
					<text class="rw-value highlight">{{ task.commission_amount || task.reward_amount || 0 }} 元</text>
				</view>
				<text class="rw-hint">可提现</text>
			</view>
			<view class="reward-row" v-if="task.coupon_desc">
				<text class="rw-icon">🎫</text>
				<view class="rw-info">
					<text class="rw-label">优惠券</text>
					<text class="rw-value green">{{ task.coupon_desc }}</text>
				</view>
				<text class="rw-hint">商户券</text>
			</view>
			<view class="reward-row">
				<text class="rw-icon">⭐</text>
				<view class="rw-info">
					<text class="rw-label">平台积分</text>
					<text class="rw-value blue">+{{ task.platform_points || 10 }}</text>
				</view>
				<text class="rw-hint">可兑实物</text>
			</view>
		</view>

		<view class="desc-card" v-if="task.description">
			<view class="card-title">📝 任务描述</view>
			<text class="desc-text">{{ task.description }}</text>
		</view>

		<view class="action-bar">
			<view class="accept-btn" @tap="acceptTask">
				<text class="btn-text">🔥 接单 · 完成训练</text>
				<text class="btn-sub">燃烧{{ task.estimated_calories || 0 }}大卡 · 赚取{{ task.commission_amount || task.reward_amount || 0 }}元</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			task: {},
			ICONS: { run:'🏃', walk:'🚶', lift:'💪', climb:'🧗', carry:'🚴' },
			TYPES: { run:'跑步', walk:'步行', lift:'力量训练', climb:'爬楼', carry:'负重运输' },
			demo: {
				id:1, title:'帮王阿姨送菜', fitness_tag:'walk',
				description:'从菜市场西门取菜送到小区3号楼501室',
				estimated_calories:180, exercise_benefit:'有氧+腿部',
				estimated_min:30, distance_meters:800,
				commission_amount:'5.00', coupon_desc:'满20减5', platform_points:50,
				merchant_name:'老王水果店'
			}
		}
	},
	onLoad(options) {
		this.loadTask(options.id)
	},
	methods: {
		async loadTask(id) {
			try {
				const res = await uni.request({
					url: 'https://xinghuo.yiouxiaozhan.top/api/v1/tasks/' + id,
					method: 'GET', timeout: 3000
				})
				if (res.data && res.data.code === 0) { this.task = res.data.data; return }
			} catch (e) {}
			this.task = this.demo
		},
		acceptTask() {
			uni.showToast({ title: '已接单！', icon: 'success' })
		},
		goBack() { uni.navigateBack() }
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; padding-bottom: 140rpx; }
.nav-bar { display: flex; align-items: center; padding: 60rpx 30rpx 20rpx; background: #fff; justify-content: space-between; }
.back-btn { font-size: 28rpx; color: #ff6b35; }
.nav-title { font-size: 28rpx; font-weight: bold; color: #333; }
.nav-placeholder { width: 80rpx; }
.task-header { background: #fff; padding: 30rpx; text-align: center; }
.big-emoji { font-size: 72rpx; }
.task-title { font-size: 32rpx; font-weight: bold; color: #333; display: block; margin-top: 12rpx; }
.task-merchant { font-size: 24rpx; color: #999; display: block; margin-top: 6rpx; }
.card-title { font-size: 26rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
.fitness-card, .rewards-card, .desc-card { background: #fff; margin: 20rpx 30rpx; padding: 30rpx; border-radius: 16rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }
.fitness-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20rpx; }
.fitness-item { text-align: center; }
.fitness-value { font-size: 32rpx; font-weight: bold; color: #ff6b35; display: block; }
.fitness-label { font-size: 22rpx; color: #999; display: block; margin-top: 4rpx; }
.ai-calc { margin-top: 20rpx; padding: 16rpx; background: #fff8f0; border-radius: 12rpx; }
.ai-label { font-size: 22rpx; color: #e6a817; }
.reward-row { display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.reward-row:last-child { border-bottom: none; }
.rw-icon { font-size: 36rpx; margin-right: 16rpx; }
.rw-info { flex: 1; }
.rw-label { font-size: 24rpx; color: #999; display: block; }
.rw-value { font-size: 28rpx; font-weight: bold; }
.highlight { color: #e6a817; }
.green { color: #4caf50; }
.blue { color: #2196f3; }
.rw-hint { font-size: 20rpx; color: #ccc; }
.desc-text { font-size: 26rpx; color: #666; line-height: 1.6; white-space: pre-wrap; }
.action-bar { position: fixed; bottom: 0; left: 0; right: 0; padding: 20rpx 30rpx; padding-bottom: calc(20rpx + env(safe-area-inset-bottom)); background: #fff; box-shadow: 0 -2rpx 12rpx rgba(0,0,0,0.06); }
.accept-btn { background: linear-gradient(135deg, #ff6b35, #ff8c42); border-radius: 50rpx; padding: 24rpx; text-align: center; }
.btn-text { color: #fff; font-size: 30rpx; font-weight: bold; display: block; }
.btn-sub { color: rgba(255,255,255,0.8); font-size: 22rpx; display: block; margin-top: 6rpx; }
</style>
