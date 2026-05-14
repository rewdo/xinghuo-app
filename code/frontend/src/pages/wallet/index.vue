<template>
	<view class="page-wallet">
		<!-- 余额卡片 -->
		<view class="balance-card">
			<text class="balance-label">账户余额（元）</text>
			<text class="balance-amount">¥{{ balance }}</text>
			<text class="total-earnings">累计收益 ¥{{ totalEarnings }}</text>
		</view>

		<!-- 操作按钮 -->
		<view class="actions">
			<button class="action-btn withdraw-btn" @tap="showWithdraw = true">提现</button>
		</view>

		<!-- 交易记录 -->
		<view class="section-title">交易记录</view>
		<scroll-view scroll-y class="tx-list" @scrolltolower="loadMore">
			<view v-if="transactions.length === 0" class="empty-state">
				<text>暂无交易记录</text>
			</view>
			<view v-for="tx in transactions" :key="tx.id" class="tx-item">
				<view class="tx-left">
					<text class="tx-remark">{{ tx.remark || tx.typeLabel }}</text>
					<text class="tx-time">{{ formatTime(tx.created_at) }}</text>
				</view>
				<text class="tx-amount" :class="tx.transaction_type === 1 ? 'income' : 'expense'">
					{{ tx.transaction_type === 1 ? '+' : '' }}{{ tx.amount }}
				</text>
			</view>
			<view v-if="loadingMore" class="load-more">加载更多...</view>
		</scroll-view>

		<!-- 提现弹窗 -->
		<view v-if="showWithdraw" class="overlay" @tap="showWithdraw = false">
			<view class="withdraw-box" @tap.stop>
				<text class="withdraw-title">提现</text>
				<view class="input-group">
					<text class="unit">¥</text>
					<input class="amount-input" type="digit" v-model="withdrawAmount" placeholder="输入提现金额" />
				</view>
				<text class="withdraw-tip">可提现 ¥{{ balance }}，满1元可提</text>
				<button class="confirm-btn" @tap="handleWithdraw" :loading="withdrawing">确认提现</button>
				<button class="cancel-btn" @tap="showWithdraw = false">取消</button>
			</view>
		</view>
	</view>
</template>

<script>
	import { getWalletBalance, getTransactions, withdraw } from '@/api/index.js'

	export default {
		data() {
			return {
				balance: '0.00',
				totalEarnings: '0.00',
				transactions: [],
				page: 1,
				hasMore: true,
				loadingMore: false,
				showWithdraw: false,
				withdrawAmount: '',
				withdrawing: false,
				typeLabels: { 1: '任务收入', 2: '提现', 3: '充值', 4: '平台佣金' }
			}
		},
		onShow() {
			this.loadData()
			this.loadTransactions(true)
		},
		methods: {
			loadData() {
				getWalletBalance().then(data => {
					this.balance = data.balance.toFixed(2)
					this.totalEarnings = data.total_earnings.toFixed(2)
				})
			},
			loadTransactions(reset) {
				if (reset) { this.page = 1; this.hasMore = true }
				if (!this.hasMore) return

				getTransactions({ page: this.page, per_page: 20 })
					.then(data => {
						const items = (data.transactions || []).map(t => ({
							...t,
							typeLabel: this.typeLabels[t.transaction_type] || '其他'
						}))
						if (reset) this.transactions = items
						else this.transactions = this.transactions.concat(items)
						this.hasMore = this.transactions.length < data.total
						this.page++
					})
					.finally(() => { this.loadingMore = false })
			},
			loadMore() {
				if (!this.loadingMore && this.hasMore) {
					this.loadingMore = true
					this.loadTransactions()
				}
			},
			handleWithdraw() {
				const amount = parseFloat(this.withdrawAmount)
				if (!amount || amount <= 0) {
					uni.showToast({ title: '请输入有效金额', icon: 'none' })
					return
				}
				if (amount > parseFloat(this.balance)) {
					uni.showToast({ title: '余额不足', icon: 'none' })
					return
				}
				this.withdrawing = true
				withdraw(amount)
					.then(() => {
						this.showWithdraw = false
						this.withdrawAmount = ''
						uni.showToast({ title: '提现申请已提交', icon: 'success' })
						this.loadData()
					})
					.catch(err => {
						uni.showToast({ title: err.message, icon: 'none' })
					})
					.finally(() => { this.withdrawing = false })
			},
			formatTime(t) {
				if (!t) return ''
				return t.split('T')[0] + ' ' + (t.split('T')[1] || '').substring(0, 5)
			}
		}
	}
</script>

<style>
	.page-wallet { background: #f5f5f5; min-height: 100vh; }

	.balance-card {
		background: linear-gradient(135deg, var(--primary), #ff8c5a);
		margin: 30rpx;
		padding: 50rpx;
		border-radius: 20rpx;
		color: #fff;
		text-align: center;
	}
	.balance-label { font-size: 26rpx; opacity: 0.9; }
	.balance-amount { font-size: 80rpx; font-weight: 700; display: block; margin: 16rpx 0; }
	.total-earnings { font-size: 24rpx; opacity: 0.8; }

	.actions { padding: 0 30rpx; margin-bottom: 30rpx; }
	.withdraw-btn {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: #fff;
		color: var(--primary);
		border-radius: 44rpx;
		font-size: 30rpx;
		font-weight: 600;
		border: 2rpx solid var(--primary);
	}

	.section-title {
		font-size: 30rpx;
		font-weight: 600;
		padding: 0 30rpx;
		margin-bottom: 16rpx;
		color: #333;
	}
	.tx-list { padding: 0 30rpx; height: 500rpx; }
	.tx-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24rpx 0;
		border-bottom: 2rpx solid #f0f0f0;
	}
	.tx-remark { font-size: 28rpx; color: #333; display: block; }
	.tx-time { font-size: 22rpx; color: #999; margin-top: 6rpx; display: block; }
	.tx-amount { font-size: 32rpx; font-weight: 600; }
	.tx-amount.income { color: var(--success); }
	.tx-amount.expense { color: #333; }

	.empty-state { text-align: center; padding: 100rpx 0; color: #999; }
	.load-more { text-align: center; padding: 20rpx; color: #999; font-size: 24rpx; }

	/* 提现弹窗 */
	.overlay {
		position: fixed; top: 0; left: 0; right: 0; bottom: 0;
		background: rgba(0,0,0,0.5);
		display: flex; align-items: center; justify-content: center;
		z-index: 999;
	}
	.withdraw-box {
		background: #fff;
		border-radius: 24rpx;
		padding: 50rpx;
		width: 600rpx;
	}
	.withdraw-title {
		font-size: 36rpx;
		font-weight: 700;
		text-align: center;
		margin-bottom: 40rpx;
	}
	.input-group {
		display: flex;
		align-items: center;
		border-bottom: 2rpx solid #e8e8e8;
		padding: 20rpx 0;
		margin-bottom: 16rpx;
	}
	.unit { font-size: 40rpx; font-weight: 700; color: #333; margin-right: 10rpx; }
	.amount-input { flex: 1; font-size: 48rpx; height: 60rpx; }
	.withdraw-tip { font-size: 24rpx; color: #999; display: block; margin-bottom: 40rpx; }
	.confirm-btn {
		width: 100%;
		height: 80rpx;
		line-height: 80rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 40rpx;
		font-size: 30rpx;
		border: none;
		margin-bottom: 16rpx;
	}
	.cancel-btn {
		width: 100%;
		height: 80rpx;
		line-height: 80rpx;
		background: #f5f5f5;
		color: #666;
		border-radius: 40rpx;
		font-size: 30rpx;
		border: none;
	}
</style>
