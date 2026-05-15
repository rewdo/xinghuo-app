<template>
	<view class="page">
		<!-- 顶部训练计划卡片 -->
		<view class="header-card">
			<view class="header-top">
				<text class="greeting">🏃 今日训练</text>
				<text class="setup-btn" @tap="goToPlan">设定计划 ›</text>
			</view>
			<view class="plan-badges">
				<view class="badge" v-for="tag in plan.tags" :key="tag">{{ TAG_LABELS[tag] }}</view>
			</view>
			<view class="plan-stats">
				<text class="stat">目标：{{ GOAL_LABELS[plan.goal] }}</text>
				<text class="stat">频率：{{ plan.frequency }}次/周</text>
			</view>
		</view>

		<!-- 今日推荐标题 -->
		<view class="section-title">
			<text class="title-text">🔥 为你匹配的任务</text>
			<text class="switch-link" @tap="showAll = !showAll">
				{{ showAll ? '推荐' : '全部' }}
			</text>
		</view>

		<!-- 任务列表 -->
		<view class="task-list" v-if="tasks.length > 0">
			<view class="task-card" v-for="(task, idx) in displayTasks" :key="task.id || idx" @tap="goDetail(task.id)">
				<view class="task-left">
					<view class="task-icon">{{ FITNESS_ICONS[task.fitness_tag] || '📋' }}</view>
				</view>
				<view class="task-body">
					<view class="task-title-row">
						<text class="task-title">{{ task.title }}</text>
						<view class="task-tag">{{ TAG_LABELS[task.fitness_tag] || '综合' }}</view>
					</view>
					<view class="task-fitness">
						<text class="fitness-item">🔥 消耗{{ task.estimated_calories || 0 }}大卡</text>
						<text class="fitness-item">💪 {{ task.exercise_benefit || '全身' }}</text>
						<text class="fitness-item">⏱ {{ task.estimated_min || 0 }}min</text>
					</view>
					<view class="task-rewards">
						<text class="reward commission">💰 {{ task.commission_amount || task.reward_amount || 0 }}元</text>
						<text class="reward coupon" v-if="task.coupon_desc">🎫 {{ task.coupon_desc }}</text>
						<text class="reward points">⭐ +{{ task.platform_points || 10 }}</text>
					</view>
					<view class="task-meta">
						<text class="meta-distance">📍 {{ task.distance_meters || 0 }}m</text>
						<text class="meta-merchant">{{ task.merchant_name || '附近商户' }}</text>
					</view>
				</view>
				<view class="task-action">
					<view class="accept-btn">接单</view>
				</view>
			</view>
		</view>
		<view class="empty-state" v-else>
			<text class="empty-icon">📭</text>
			<text class="empty-text">附近暂无匹配任务</text>
			<text class="empty-sub">试试其他训练类型</text>
		</view>

		<!-- 底部假数据提示 -->
		<view class="demo-hint" v-if="isDemo">
			<text class="hint-text">⚡ 演示模式 — 数据为静态示例，连接后端后自动切换</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			showAll: false,
			isDemo: true,
			plan: {
				goal: 'fat_loss',
				frequency: 3,
				tags: ['run', 'walk'],
				daily_minutes: 30
			},
			tasks: [],
			TAG_LABELS: {
				run: '跑步', walk: '步行', lift: '力量',
				climb: '爬楼', carry: '负重'
			},
			GOAL_LABELS: {
				fat_loss: '减脂', muscle: '增肌',
				endurance: '耐力', general: '综合'
			},
			FITNESS_ICONS: {
				run: '🏃', walk: '🚶', lift: '💪',
				climb: '🧗', carry: '🚴'
			},
			demoTasks: [
				{
					id: 1, title: '帮王阿姨送菜', fitness_tag: 'walk',
					estimated_calories: 180, exercise_benefit: '有氧+腿部',
					estimated_min: 30, distance_meters: 800,
					commission_amount: '5.00', coupon_desc: '满20减5',
					platform_points: 50, merchant_name: '老王水果店'
				},
				{
					id: 2, title: '巡检3家便利店', fitness_tag: 'walk',
					estimated_calories: 220, exercise_benefit: '有氧+腿部',
					estimated_min: 40, distance_meters: 1200,
					commission_amount: '8.00', coupon_desc: '全场9折',
					platform_points: 50, merchant_name: '小李超市'
				},
				{
					id: 3, title: '搬货到2楼仓库', fitness_tag: 'lift',
					estimated_calories: 150, exercise_benefit: '核心+上肢',
					estimated_min: 20, distance_meters: 50,
					commission_amount: '12.00', coupon_desc: null,
					platform_points: 60, merchant_name: '大鹏五金'
				},
				{
					id: 4, title: '送文件到5栋', fitness_tag: 'run',
					estimated_calories: 145, exercise_benefit: '耐力+腿部',
					estimated_min: 15, distance_meters: 2000,
					commission_amount: '4.00', coupon_desc: '满10减3',
					platform_points: 50, merchant_name: '社区服务站'
				},
				{
					id: 5, title: '配送1箱饮料', fitness_tag: 'carry',
					estimated_calories: 175, exercise_benefit: '全身+爆发力',
					estimated_min: 25, distance_meters: 1500,
					commission_amount: '6.00', coupon_desc: null,
					platform_points: 55, merchant_name: '鑫鑫超市'
				}
			]
		}
	},
	computed: {
		displayTasks() {
			return this.showAll ? this.demoTasks :
				this.demoTasks.filter(t => this.plan.tags.includes(t.fitness_tag))
		}
	},
	onLoad() {
		this.loadTasks()
	},
	methods: {
		async loadTasks() {
			try {
				const res = await uni.request({
					url: 'https://xinghuo.yiouxiaozhan.top/api/v1/tasks/recommended?user_id=1',
					method: 'GET',
					timeout: 2000
				})
				if (res.data && res.data.code === 0 && res.data.data.length > 0) {
					this.tasks = res.data.data
					this.isDemo = false
				}
			} catch (e) {
				this.tasks = this.demoTasks
				this.isDemo = true
			}
		},
		goDetail(id) {
			uni.navigateTo({ url: `/pages/task/detail?id=${id}` })
		},
		goToPlan() {
			uni.switchTab({ url: '/pages/profile/index' })
		}
	}
}
</script>

<style>
.page {
	min-height: 100vh;
	background: #f5f5f5;
	padding-bottom: 30rpx;
}
.header-card {
	background: linear-gradient(135deg, #ff6b35, #ff8c42);
	padding: 80rpx 40rpx 40rpx;
	color: #fff;
}
.header-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}
.greeting {
	font-size: 36rpx;
	font-weight: bold;
}
.setup-btn {
	font-size: 26rpx;
	opacity: 0.9;
	padding: 8rpx 16rpx;
	background: rgba(255,255,255,0.2);
	border-radius: 30rpx;
}
.plan-badges {
	display: flex;
	gap: 12rpx;
	margin-bottom: 16rpx;
}
.badge {
	background: rgba(255,255,255,0.25);
	padding: 6rpx 20rpx;
	border-radius: 20rpx;
	font-size: 24rpx;
}
.plan-stats {
	display: flex;
	gap: 30rpx;
	font-size: 24rpx;
	opacity: 0.9;
}
.section-title {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx 30rpx 20rpx;
}
.title-text {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
}
.switch-link {
	font-size: 26rpx;
	color: #ff6b35;
}
.task-list {
	padding: 0 30rpx;
}
.task-card {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
	display: flex;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}
.task-left {
	width: 80rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}
.task-icon {
	font-size: 48rpx;
}
.task-body {
	flex: 1;
	padding: 0 16rpx;
}
.task-title-row {
	display: flex;
	align-items: center;
	margin-bottom: 10rpx;
}
.task-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	flex: 1;
}
.task-tag {
	font-size: 20rpx;
	background: #fff3ed;
	color: #ff6b35;
	padding: 4rpx 14rpx;
	border-radius: 20rpx;
}
.task-fitness {
	display: flex;
	gap: 16rpx;
	margin-bottom: 10rpx;
}
.fitness-item {
	font-size: 22rpx;
	color: #666;
}
.task-rewards {
	display: flex;
	gap: 12rpx;
	margin-bottom: 10rpx;
	flex-wrap: wrap;
}
.reward {
	font-size: 22rpx;
	padding: 4rpx 14rpx;
	border-radius: 20rpx;
}
.commission {
	background: #fff7e6;
	color: #e6a817;
}
.coupon {
	background: #e8f5e9;
	color: #4caf50;
}
.points {
	background: #e3f2fd;
	color: #2196f3;
}
.task-meta {
	display: flex;
	justify-content: space-between;
	font-size: 22rpx;
	color: #999;
}
.task-action {
	display: flex;
	align-items: center;
}
.accept-btn {
	background: #ff6b35;
	color: #fff;
	padding: 12rpx 24rpx;
	border-radius: 30rpx;
	font-size: 24rpx;
}
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 100rpx 0;
}
.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
}
.empty-text {
	font-size: 28rpx;
	color: #999;
}
.empty-sub {
	font-size: 24rpx;
	color: #ccc;
	margin-top: 10rpx;
}
.demo-hint {
	text-align: center;
	padding: 20rpx;
}
.hint-text {
	font-size: 20rpx;
	color: #ccc;
}
</style>
