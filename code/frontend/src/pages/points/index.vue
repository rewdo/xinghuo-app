<template>
	<view class="page">
		<view class="points-header">
			<view class="points-big">
				<text class="points-icon">⭐</text>
				<text class="points-num">{{ points.current_points || 1350 }}</text>
			</view>
			<text class="points-label">可用积分</text>
			<view class="points-stats">
				<view class="stat-item">
					<text class="stat-num">{{ points.total_points || 2800 }}</text>
					<text class="stat-label">累计获得</text>
				</view>
				<view class="stat-item">
					<text class="stat-num">{{ points.redeemed || 1450 }}</text>
					<text class="stat-label">已兑换</text>
				</view>
			</view>
		</view>

		<view class="tab-bar">
			<view class="tab-item" :class="{active: activeTab === 'shop'}" @tap="activeTab = 'shop'"><text>🏪 积分商城</text></view>
			<view class="tab-item" :class="{active: activeTab === 'history'}" @tap="activeTab = 'history'"><text>📋 积分流水</text></view>
		</view>

		<view class="shop-list" v-if="activeTab === 'shop'">
			<view class="shop-card" v-for="item in shopItems" :key="item.id" @tap="redeem(item)">
				<text class="shop-emoji">{{ item.emoji || '🎁' }}</text>
				<view class="shop-info">
					<text class="shop-name">{{ item.name }}</text>
					<text class="shop-desc">{{ item.description }}</text>
				</view>
				<view class="shop-action">
					<text class="shop-price">{{ item.points_required }}分</text>
					<text class="shop-exchange">兑换</text>
				</view>
			</view>
		</view>

		<view class="history-list" v-else>
			<view class="history-item" v-for="(t, idx) in transactions" :key="idx">
				<view class="history-left">
					<text class="history-title">{{ t.remark || '任务奖励' }}</text>
					<text class="history-time">{{ t.created_at || '今天' }}</text>
				</view>
				<text class="history-amount" :class="(t.type === 1 || t.type === undefined) ? 'income' : 'outcome'">
					{{ (t.type === 3 || t.type === 'exchange') ? '-' : '+' }}{{ t.amount || 0 }}
				</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			activeTab: 'shop',
			points: { current_points: 1350, total_points: 2800, redeemed: 1450 },
			shopItems: [
				{id:1, emoji:'🧣', name:'品牌运动毛巾', description:'超强吸水，运动必备', points_required:500},
				{id:2, emoji:'🧤', name:'健身手套', description:'防滑耐磨，保护手掌', points_required:1000},
				{id:3, emoji:'📱', name:'Keep 月卡', description:'虚拟商品，自动到账', points_required:800, is_virtual:1},
				{id:4, emoji:'💧', name:'运动水壶', description:'500ml大容量，便携', points_required:1500},
				{id:5, emoji:'⌚', name:'智能手环(基础款)', description:'计步/心率/睡眠监测', points_required:5000},
				{id:6, emoji:'💍', name:'定制纪念戒指', description:'坚持365天专属定制，刻字纪念', points_required:20000},
				{id:7, emoji:'👟', name:'品牌运动鞋', description:'经典款，舒适耐穿', points_required:20000}
			],
			transactions: [
				{type:1, amount:50, remark:'完成巡检任务', created_at:'今天 09:30'},
				{type:1, amount:50, remark:'完成配送任务', created_at:'昨天 15:20'},
				{type:1, amount:25, remark:'连续7天活跃加成', created_at:'昨天 15:20'},
				{type:3, amount:500, remark:'兑换运动毛巾', created_at:'3天前'},
				{type:1, amount:50, remark:'完成帮送文件', created_at:'4天前'},
				{type:1, amount:60, remark:'完成搬货任务', created_at:'5天前'}
			]
		}
	},
	onLoad() {
		Promise.all([
			uni.request({url:'https://xinghuo.yiouxiaozhan.top/api/v1/points/balance?user_id=1', timeout:3000}).catch(()=>{}),
			uni.request({url:'https://xinghuo.yiouxiaozhan.top/api/v1/points/shop/items', timeout:3000}).catch(()=>{})
		])
	},
	methods: {
		redeem(item) {
			uni.showModal({
				title:'确认兑换',
				content:`确定使用 ${item.points_required} 积分兑换「${item.name}」吗？`,
				success:(res) => { if(res.confirm) uni.showToast({title:'兑换成功！',icon:'success'}) }
			})
		}
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; padding-bottom: 30rpx; }
.points-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 60rpx 40rpx 40rpx; text-align: center; color: #fff; }
.points-big { display: flex; align-items: center; justify-content: center; margin-bottom: 10rpx; }
.points-icon { font-size: 48rpx; margin-right: 12rpx; }
.points-num { font-size: 64rpx; font-weight: bold; }
.points-label { font-size: 26rpx; opacity: 0.8; display: block; margin-bottom: 30rpx; }
.points-stats { display: flex; justify-content: center; gap: 60rpx; }
.stat-item { text-align: center; }
.stat-num { font-size: 32rpx; font-weight: bold; display: block; }
.stat-label { font-size: 22rpx; opacity: 0.7; display: block; }
.tab-bar { display: flex; background: #fff; margin: 20rpx 30rpx; border-radius: 16rpx; overflow: hidden; }
.tab-item { flex: 1; text-align: center; padding: 20rpx; font-size: 26rpx; color: #999; }
.tab-item.active { color: #667eea; font-weight: bold; border-bottom: 4rpx solid #667eea; }
.shop-list, .history-list { padding: 0 30rpx; }
.shop-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; display: flex; align-items: center; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.shop-emoji { font-size: 48rpx; margin-right: 20rpx; }
.shop-info { flex: 1; }
.shop-name { font-size: 28rpx; font-weight: bold; color: #333; display: block; }
.shop-desc { font-size: 22rpx; color: #999; display: block; margin-top: 4rpx; }
.shop-action { text-align: center; }
.shop-price { font-size: 24rpx; color: #667eea; font-weight: bold; display: block; }
.shop-exchange { font-size: 20rpx; color: #fff; background: #667eea; padding: 4rpx 16rpx; border-radius: 20rpx; display: inline-block; margin-top: 6rpx; }
.history-item { background: #fff; border-radius: 12rpx; padding: 20rpx; margin-bottom: 12rpx; display: flex; justify-content: space-between; align-items: center; }
.history-title { font-size: 26rpx; color: #333; display: block; }
.history-time { font-size: 20rpx; color: #ccc; display: block; margin-top: 4rpx; }
.history-amount { font-size: 28rpx; font-weight: bold; }
.income { color: #4caf50; }
.outcome { color: #f44336; }
</style>
