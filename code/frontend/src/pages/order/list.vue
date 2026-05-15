<template>
	<view class="page">
		<!-- 状态筛选 -->
		<view class="tabs">
			<view class="tab" v-for="t in filters" :key="t.key"
				:class="{active: activeTab === t.key}" @tap="activeTab = t.key">
				<text>{{ t.label }}</text>
			</view>
		</view>

		<!-- 订单列表 -->
		<view class="list" v-if="orders.length > 0">
			<view class="order-card" v-for="o in filteredOrders" :key="o.id" @tap="goDetail(o.id)">
				<view class="order-top">
					<text class="order-title">{{ o.title || o.task_title }}</text>
					<text class="order-status" :class="'s' + (o.status || 0)">{{ STATUS_LABELS[o.status || 0] }}</text>
				</view>
				<view class="order-fitness">
					<text class="fit">🔥 {{ o.estimated_calories || 0 }}大卡</text>
					<text class="fit">⏱ {{ o.estimated_min || 0 }}min</text>
				</view>
				<view class="order-rewards">
					<text class="rw cm">💰 {{ o.commission_received || o.reward_amount || 0 }}元</text>
					<text class="rw pt">⭐ +{{ o.points_received || 0 }}</text>
				</view>
				<text class="order-time">{{ o.created_at || '' }}</text>
			</view>
		</view>
		<view class="empty" v-else>
			<text class="empty-icon">📋</text>
			<text class="empty-text">暂无{{ activeTabText }}订单</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			activeTab: 'all',
			filters: [
				{key:'all', label:'全部'},
				{key:'0', label:'进行中'},
				{key:'3', label:'已完成'},
				{key:'4', label:'已取消'}
			],
			STATUS_LABELS: {0:'进行中',1:'执行中',2:'待确认',3:'已完成',4:'已取消'},
			orders: [],
			demoOrders: [
				{id:1, title:'巡检3家便利店', status:0, estimated_calories:220, estimated_min:40, commission_received:0, points_received:0, created_at:'2026-05-15 09:30'},
				{id:2, title:'帮王阿姨送菜', status:3, estimated_calories:180, estimated_min:30, commission_received:5.00, points_received:60, created_at:'2026-05-14 15:20'},
				{id:3, title:'送文件到5栋', status:3, estimated_calories:145, estimated_min:15, commission_received:4.00, points_received:50, created_at:'2026-05-13 10:15'},
				{id:4, title:'搬货到2楼仓库', status:3, estimated_calories:150, estimated_min:20, commission_received:12.00, points_received:55, created_at:'2026-05-12 16:00'},
				{id:5, title:'配送1箱饮料', status:4, estimated_calories:175, estimated_min:25, commission_received:0, points_received:0, created_at:'2026-05-11 11:30'}
			]
		}
	},
	computed: {
		activeTabText() {
			const t = this.filters.find(f => f.key === this.activeTab)
			return t ? t.label : ''
		},
		filteredOrders() {
			if (this.activeTab === 'all') return this.orders
			return this.orders.filter(o => String(o.status) === this.activeTab)
		}
	},
	onLoad() {
		this.loadOrders()
	},
	onPullDownRefresh() {
		this.loadOrders()
		setTimeout(() => uni.stopPullDownRefresh(), 500)
	},
	methods: {
		async loadOrders() {
			try {
				const res = await uni.request({
					url: 'https://xinghuo.yiouxiaozhan.top/api/v1/tasks/nearby?user_id=1',
					timeout: 3000
				})
			} catch (e) {}
			this.orders = this.demoOrders
		},
		goDetail(id) {
			uni.navigateTo({ url: '/pages/order/detail?id=' + id })
		}
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; }
.tabs { display: flex; background: #fff; padding: 20rpx 30rpx; position: sticky; top: 0; z-index: 10; }
.tab { padding: 12rpx 24rpx; font-size: 26rpx; color: #999; margin-right: 12rpx; border-radius: 30rpx; }
.tab.active { background: #ff6b35; color: #fff; font-weight: bold; }
.list { padding: 20rpx 30rpx; }
.order-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.order-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx; }
.order-title { font-size: 28rpx; font-weight: bold; color: #333; flex: 1; }
.order-status { font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 20rpx; }
.s0 { background: #fff3e0; color: #e65100; }
.s3 { background: #e8f5e9; color: #2e7d32; }
.s4 { background: #f5f5f5; color: #999; }
.order-fitness { display: flex; gap: 20rpx; margin-bottom: 10rpx; }
.fit { font-size: 22rpx; color: #666; }
.order-rewards { display: flex; gap: 16rpx; margin-bottom: 10rpx; }
.rw { font-size: 22rpx; padding: 4rpx 14rpx; border-radius: 20rpx; }
.cm { background: #fff7e6; color: #e6a817; }
.pt { background: #e3f2fd; color: #2196f3; }
.order-time { font-size: 20rpx; color: #ccc; }
.empty { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.empty-icon { font-size: 80rpx; margin-bottom: 20rpx; }
.empty-text { font-size: 28rpx; color: #999; }
</style>
