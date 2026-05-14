<template>
	<view class="page-merchant">
		<view v-if="!merchant" class="register-section">
			<text class="reg-title">商户入驻</text>
			<text class="reg-desc">发布任务，让超能侠帮你完成</text>

			<input class="input-field" v-model="form.company_name" placeholder="公司/店铺名称" />
			<input class="input-field" v-model="form.contact_name" placeholder="联系人姓名" />
			<input class="input-field" v-model="form.contact_phone" placeholder="联系电话" type="phone" />
			<input class="input-field" v-model="form.address" placeholder="地址" />

			<button class="submit-btn" @tap="handleRegister" :loading="registering">提交入驻</button>
			<button class="skip-btn" @tap="loadDemoData">跳过（演示数据）</button>
		</view>

		<template v-else>
			<view class="merchant-header">
				<text class="merchant-name">{{ merchant.company_name }}</text>
				<text class="merchant-balance">余额 ¥{{ merchant.balance?.toFixed(2) || '0.00' }}</text>
			</view>

			<view class="action-card" @tap="goCreateTask">
				<text class="action-icon">➕</text>
				<text class="action-text">发布新任务</text>
				<text class="action-arrow">›</text>
			</view>

			<view class="section-title">已发布的任务</view>
			<view v-for="task in tasks" :key="task.id" class="task-item">
				<view class="task-top">
					<text class="task-title">{{ task.title }}</text>
					<text :class="'task-status status-' + task.status">
						{{ ['待接受','进行中','已完成','已取消'][task.status] }}
					</text>
				</view>
				<view class="task-bottom">
					<text class="task-count">{{ task.accepted_count }}/{{ task.quantity }}人</text>
					<text class="task-reward">¥{{ task.reward_amount }}</text>
				</view>

				<!-- 待确认订单的处理按钮 -->
				<button
					v-if="hasPendingOrder(task.id)"
					class="confirm-btn"
					@tap="handleConfirm(task.id)"
				>
					确认完成
				</button>
			</view>

			<view v-if="tasks.length === 0" class="empty-hint">暂无发布的任务</view>
		</template>
	</view>
</template>

<script>
	import { merchantRegister, getMerchantProfile, getMerchantTasks, confirmTaskComplete } from '@/api/index.js'

	export default {
		data() {
			return {
				merchant: null,
				merchantId: null,
				tasks: [],
				registering: false,
				form: { company_name: '', contact_name: '', contact_phone: '', address: '' }
			}
		},
		onShow() {
			const id = uni.getStorageSync('merchant_id')
			if (id) {
				this.merchantId = id
				this.loadMerchant(id)
			}
		},
		methods: {
			handleRegister() {
				if (!this.form.company_name || !this.form.contact_name || !this.form.contact_phone) {
					uni.showToast({ title: '请填写完整信息', icon: 'none' })
					return
				}
				this.registering = true
				merchantRegister(this.form)
					.then(data => {
						this.merchant = data
						this.merchantId = data.id
						uni.setStorageSync('merchant_id', data.id)
						uni.showToast({ title: '入驻成功！', icon: 'success' })
					})
					.catch(err => {
						uni.showToast({ title: err.message || '入驻失败', icon: 'none' })
					})
					.finally(() => { this.registering = false })
			},
			loadMerchant(id) {
				getMerchantProfile(id).then(data => { this.merchant = data })
				getMerchantTasks(id).then(data => { this.tasks = data.tasks || [] })
			},
			loadDemoData() {
				this.merchant = {
					id: 1, company_name: '测试商户', balance: 500,
					contact_name: '张三', contact_phone: '13800000000'
				}
				this.merchantId = 1
				uni.setStorageSync('merchant_id', 1)
			},
			goCreateTask() {
				uni.navigateTo({ url: '/pages/merchant/task-create' })
			},
			hasPendingOrder(taskId) {
				// Simplified: for MVP, show confirm button if task is not completed
				const task = this.tasks.find(t => t.id === taskId)
				return task && task.status === 1
			},
			handleConfirm(taskId) {
				confirmTaskComplete(taskId, this.merchantId)
					.then(data => {
						uni.showToast({
							title: `已完成，用户收入¥${data.user_income}`,
							icon: 'success'
						})
						this.loadMerchant(this.merchantId)
					})
					.catch(err => {
						uni.showToast({ title: err.message || '确认失败', icon: 'none' })
					})
			}
		}
	}
</script>

<style>
	.page-merchant { background: #f5f5f5; min-height: 100vh; padding: 30rpx; }

	/* 入驻表单 */
	.register-section { padding-top: 100rpx; }
	.reg-title { font-size: 40rpx; font-weight: 700; text-align: center; display: block; }
	.reg-desc { font-size: 26rpx; color: #999; text-align: center; display: block; margin: 16rpx 0 50rpx; }
	.input-field {
		width: 100%;
		height: 88rpx;
		background: #fff;
		border-radius: 12rpx;
		padding: 0 24rpx;
		font-size: 28rpx;
		margin-bottom: 20rpx;
	}
	.submit-btn {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 44rpx;
		font-size: 30rpx;
		border: none;
		margin-top: 30rpx;
	}
	.skip-btn {
		width: 100%;
		text-align: center;
		font-size: 26rpx;
		color: #999;
		margin-top: 20rpx;
		background: transparent;
		border: none;
	}

	/* 管理面板 */
	.merchant-header {
		background: #fff;
		border-radius: 16rpx;
		padding: 40rpx;
		margin-bottom: 20rpx;
	}
	.merchant-name { font-size: 36rpx; font-weight: 700; display: block; }
	.merchant-balance { font-size: 28rpx; color: var(--primary); margin-top: 10rpx; display: block; }

	.action-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		display: flex;
		align-items: center;
		margin-bottom: 20rpx;
	}
	.action-icon { font-size: 40rpx; margin-right: 16rpx; }
	.action-text { flex: 1; font-size: 30rpx; font-weight: 600; }
	.action-arrow { font-size: 36rpx; color: #ccc; }

	.section-title {
		font-size: 28rpx;
		font-weight: 600;
		margin: 20rpx 0;
	}
	.task-item {
		background: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 16rpx;
	}
	.task-top { display: flex; justify-content: space-between; margin-bottom: 12rpx; }
	.task-title { font-size: 28rpx; font-weight: 600; }
	.task-status { font-size: 22rpx; padding: 4rpx 12rpx; border-radius: 6rpx; }
	.task-status.status-0 { background: #e3f2fd; color: #1565c0; }
	.task-status.status-1 { background: #fff3e0; color: #e65100; }
	.task-status.status-2 { background: #e8f5e9; color: #2e7d32; }
	.task-bottom { display: flex; justify-content: space-between; }
	.task-count { font-size: 24rpx; color: #999; }
	.task-reward { font-size: 28rpx; font-weight: 600; color: var(--primary); }
	.confirm-btn {
		margin-top: 16rpx;
		height: 60rpx;
		line-height: 60rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 30rpx;
		font-size: 24rpx;
		border: none;
	}
	.empty-hint { text-align: center; padding: 60rpx; color: #999; }
</style>
