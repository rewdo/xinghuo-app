<template>
	<view class="page">
		<view class="merchant-header">
			<view class="avatar">🏪</view>
			<view class="info">
				<text class="name">{{ merchant.name || '未入驻' }}</text>
				<text class="status" :class="{active: merchant.status === 1}">
					{{ merchant.status === 1 ? '已认证' : '待认证' }}
				</text>
			</view>
			<view class="balance-badge">
				<text class="bb-label">余额</text>
				<text class="bb-num">{{ merchant.balance || 0 }}元</text>
			</view>
		</view>

		<!-- 快捷操作 -->
		<view class="quick-actions">
			<view class="qa-item" @tap="createTask">
				<text class="qa-icon">➕</text>
				<text class="qa-label">发布任务</text>
			</view>
			<view class="qa-item" @tap="createCoupon">
				<text class="qa-icon">🎫</text>
				<text class="qa-label">创建优惠券</text>
			</view>
			<view class="qa-item" @tap="recharge">
				<text class="qa-icon">💰</text>
				<text class="qa-label">账户充值</text>
			</view>
		</view>

		<!-- 任务管理 -->
		<view class="section-title">📋 我的任务</view>
		<view class="task-list" v-if="tasks.length > 0">
			<view class="task-item" v-for="t in tasks" :key="t.id">
				<view class="task-top">
					<text class="task-title">{{ t.title }}</text>
					<text class="task-status" :class="'s' + (t.status || 0)">
						{{ STATUS[t.status || 0] }}
					</text>
				</view>
				<view class="task-meta">
					<text>🏷 {{ TAG[t.fitness_tag] || '综合' }}</text>
					<text>💰 {{ t.commission_amount || 0 }}元</text>
				</view>
				<view class="task-bottom">
					<text>已接 {{ t.accepted_count || 0 }}/{{ t.quantity || 1 }} 单</text>
				</view>
			</view>
		</view>
		<view class="empty" v-else>
			<text class="empty-text">暂无发布的任务</text>
			<text class="empty-sub" @tap="createTask">去发布第一个任务 →</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			merchant: {name:'老王水果店', status:1, balance:200},
			STATUS: {0:'待接单',1:'进行中',2:'已完成',3:'已取消'},
			TAG: {run:'跑步',walk:'步行',lift:'力量',climb:'爬楼',carry:'负重'},
			tasks: [
				{id:1, title:'帮王阿姨送菜', fitness_tag:'walk', commission_amount:5, quantity:1, accepted_count:0, status:0},
				{id:2, title:'送货到3号楼', fitness_tag:'run', commission_amount:4, quantity:2, accepted_count:1, status:1}
			]
		}
	},
	methods: {
		createTask() {
			uni.navigateTo({ url: '/pages/merchant/task-create' })
		},
		createCoupon() {
			uni.showToast({ title: '优惠券功能开发中', icon: 'none' })
		},
		recharge() {
			uni.showToast({ title: '充值功能开发中', icon: 'none' })
		}
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; padding-bottom: 30rpx; }
.merchant-header {
	background: linear-gradient(135deg, #667eea, #764ba2);
	padding: 80rpx 40rpx 40rpx;
	display: flex;
	align-items: center;
	color: #fff;
}
.avatar { font-size: 60rpx; margin-right: 20rpx; }
.info { flex: 1; }
.name { font-size: 32rpx; font-weight: bold; display: block; }
.status { font-size: 22rpx; opacity: 0.7; display: inline-block; background: rgba(255,255,255,0.2); padding: 4rpx 16rpx; border-radius: 20rpx; margin-top: 6rpx; }
.status.active { background: rgba(76,175,80,0.3); }
.balance-badge { text-align: center; background: rgba(255,255,255,0.15); padding: 16rpx 24rpx; border-radius: 16rpx; }
.bb-label { font-size: 20rpx; opacity: 0.7; display: block; }
.bb-num { font-size: 28rpx; font-weight: bold; display: block; }

.quick-actions {
	display: flex;
	background: #fff;
	margin: 20rpx 30rpx;
	border-radius: 16rpx;
	padding: 20rpx 0;
}
.qa-item { flex: 1; text-align: center; }
.qa-icon { font-size: 40rpx; display: block; margin-bottom: 6rpx; }
.qa-label { font-size: 24rpx; color: #666; }

.section-title { font-size: 28rpx; font-weight: bold; color: #333; padding: 20rpx 30rpx 10rpx; }
.task-list { padding: 0 30rpx; }
.task-item { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.task-top { display: flex; justify-content: space-between; margin-bottom: 12rpx; }
.task-title { font-size: 28rpx; font-weight: bold; color: #333; }
.task-status { font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 20rpx; }
.s0 { background: #e3f2fd; color: #1565c0; }
.s1 { background: #fff3e0; color: #e65100; }
.s2 { background: #e8f5e9; color: #2e7d32; }
.task-meta { display: flex; gap: 20rpx; font-size: 24rpx; color: #666; margin-bottom: 8rpx; }
.task-bottom { font-size: 22rpx; color: #999; }
.empty { text-align: center; padding: 80rpx; }
.empty-text { font-size: 26rpx; color: #999; display: block; }
.empty-sub { font-size: 24rpx; color: #667eea; display: block; margin-top: 12rpx; }
</style>
