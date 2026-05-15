<template>
	<view class="page">
		<!-- 余额卡片 -->
		<view class="balance-card">
			<text class="balance-label">账户余额（元）</text>
			<text class="balance-num">{{ balance }}</text>
			<view class="balance-actions">
				<view class="action-btn withdraw" @tap="withdraw">
					<text>提现</text>
				</view>
				<view class="action-btn recharge" @tap="recharge">
					<text>充值</text>
				</view>
			</view>
		</view>

		<!-- 累计统计 -->
		<view class="stats-row">
			<view class="stat">
				<text class="stat-num">{{ totalEarned }}</text>
				<text class="stat-label">累计收入(元)</text>
			</view>
			<view class="stat">
				<text class="stat-num">{{ totalWithdrawn }}</text>
				<text class="stat-label">已提现(元)</text>
			</view>
			<view class="stat">
				<text class="stat-num">{{ orders }}</text>
				<text class="stat-label">完成订单</text>
			</view>
		</view>

		<!-- 交易记录 -->
		<view class="section-title-row">
			<text class="st-title">📋 交易记录</text>
		</view>
		<view class="tx-list" v-if="txns.length > 0">
			<view class="tx-item" v-for="(t, i) in txns" :key="i">
				<view class="tx-left">
					<text class="tx-type">{{ t.remark || '任务收入' }}</text>
					<text class="tx-time">{{ t.created_at || '' }}</text>
				</view>
				<text class="tx-amount" :class="(t.type === 1 || t.type === 2) ? 'income' : 'outcome'">
					{{ (t.type === 1 || t.type === 2) ? '+' : '-' }}{{ t.amount || 0 }}
				</text>
			</view>
		</view>
		<view class="empty" v-else>
			<text class="empty-text">暂无交易记录</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			balance: '86.00',
			totalEarned: '126.00',
			totalWithdrawn: '40.00',
			orders: 12,
			txns: [
				{type:1, amount:5.00, remark:'帮王阿姨送菜', created_at:'2026-05-14 15:20'},
				{type:1, amount:4.00, remark:'送文件到5栋', created_at:'2026-05-13 10:15'},
				{type:1, amount:12.00, remark:'搬货到2楼仓库', created_at:'2026-05-12 16:00'},
				{type:2, amount:20.00, remark:'提现到微信零钱', created_at:'2026-05-10'},
				{type:1, amount:6.00, remark:'配送1箱饮料', created_at:'2026-05-09'},
				{type:2, amount:20.00, remark:'提现到微信零钱', created_at:'2026-05-05'}
			]
		}
	},
	methods: {
		withdraw() {
			uni.showToast({ title: '提现功能开发中', icon: 'none' })
		},
		recharge() {
			uni.showToast({ title: '商户充值请使用管理端', icon: 'none' })
		}
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; }
.balance-card {
	background: linear-gradient(135deg, #ff6b35, #ff8c42);
	margin: 30rpx;
	padding: 40rpx;
	border-radius: 20rpx;
	color: #fff;
	text-align: center;
}
.balance-label { font-size: 24rpx; opacity: 0.8; display: block; }
.balance-num { font-size: 72rpx; font-weight: bold; display: block; margin: 16rpx 0; }
.balance-actions { display: flex; justify-content: center; gap: 30rpx; margin-top: 20rpx; }
.action-btn { padding: 14rpx 48rpx; border-radius: 40rpx; font-size: 26rpx; }
.withdraw { background: #fff; color: #ff6b35; }
.recharge { background: rgba(255,255,255,0.2); color: #fff; }

.stats-row { display: flex; background: #fff; margin: 0 30rpx 20rpx; border-radius: 16rpx; padding: 20rpx 0; }
.stat { flex: 1; text-align: center; }
.stat-num { font-size: 32rpx; font-weight: bold; color: #333; display: block; }
.stat-label { font-size: 22rpx; color: #999; display: block; margin-top: 6rpx; }

.section-title-row { padding: 20rpx 30rpx 10rpx; }
.st-title { font-size: 28rpx; font-weight: bold; color: #333; }

.tx-list { padding: 0 30rpx; }
.tx-item { background: #fff; border-radius: 12rpx; padding: 20rpx; margin-bottom: 12rpx; display: flex; justify-content: space-between; align-items: center; }
.tx-type { font-size: 26rpx; color: #333; display: block; }
.tx-time { font-size: 20rpx; color: #ccc; display: block; margin-top: 4rpx; }
.tx-amount { font-size: 28rpx; font-weight: bold; }
.income { color: #4caf50; }
.outcome { color: #f44336; }
.empty { text-align: center; padding: 60rpx; }
.empty-text { font-size: 26rpx; color: #ccc; }
</style>
