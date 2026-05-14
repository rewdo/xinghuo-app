<template>
	<view class="page-profile">
		<!-- 用户信息 -->
		<view class="user-card" @tap="editProfile">
			<image class="avatar" :src="user.avatar_url || '/static/default-avatar.png'" mode="aspectFill" />
			<view class="user-info">
				<text class="user-name">{{ user.nickname || '微信用户' }}</text>
				<text class="user-level">Lv.{{ user.level }} · 信用分 {{ user.credit_score }}</text>
			</view>
			<text class="arrow">›</text>
		</view>

		<!-- 收益概览 -->
		<view class="stats-card">
			<view class="stat-item" @tap="goWallet">
				<text class="stat-value">¥{{ user.balance?.toFixed(2) || '0.00' }}</text>
				<text class="stat-label">账户余额</text>
			</view>
			<view class="stat-item">
				<text class="stat-value">¥{{ user.total_earnings?.toFixed(2) || '0.00' }}</text>
				<text class="stat-label">累计收益</text>
			</view>
		</view>

		<!-- 菜单列表 -->
		<view class="menu-group">
			<view class="menu-item" @tap="goWallet">
				<text class="menu-icon">💰</text>
				<text class="menu-text">我的钱包</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" @tap="goOrders">
				<text class="menu-icon">📋</text>
				<text class="menu-text">我的任务</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item" @tap="goMerchant">
				<text class="menu-icon">🏪</text>
				<text class="menu-text">商户中心</text>
				<text class="menu-arrow">›</text>
			</view>
		</view>

		<view class="menu-group">
			<view class="menu-item" @tap="editProfile">
				<text class="menu-icon">⚙️</text>
				<text class="menu-text">设置</text>
				<text class="menu-arrow">›</text>
			</view>
		</view>

		<!-- 退出登录 -->
		<view class="logout" @tap="handleLogout">退出登录</view>
	</view>
</template>

<script>
	import { getUserProfile } from '@/api/index.js'

	export default {
		data() {
			return {
				user: {}
			}
		},
		onShow() {
			this.loadProfile()
		},
		methods: {
			loadProfile() {
				const local = uni.getStorageSync('userInfo')
				if (local) this.user = local

				getUserProfile()
					.then(data => {
						this.user = data
						uni.setStorageSync('userInfo', data)
					})
					.catch(() => {})
			},
			goWallet() { uni.navigateTo({ url: '/pages/wallet/index' }) },
			goOrders() { uni.switchTab({ url: '/pages/order/list' }) },
			goMerchant() { uni.navigateTo({ url: '/pages/merchant/index' }) },
			editProfile() { uni.showToast({ title: '功能开发中', icon: 'none' }) },
			handleLogout() {
				uni.showModal({
					title: '提示',
					content: '确定退出登录吗？',
					success: (res) => {
						if (res.confirm) {
							uni.removeStorageSync('token')
							uni.removeStorageSync('userInfo')
							uni.reLaunch({ url: '/pages/index/index' })
						}
					}
				})
			}
		}
	}
</script>

<style>
	.page-profile { background: #f5f5f5; min-height: 100vh; padding: 30rpx; }

	.user-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 40rpx 30rpx;
		display: flex;
		align-items: center;
		margin-bottom: 20rpx;
	}
	.avatar {
		width: 100rpx;
		height: 100rpx;
		border-radius: 50%;
		margin-right: 24rpx;
		background: #f0f0f0;
	}
	.user-info { flex: 1; }
	.user-name { font-size: 34rpx; font-weight: 700; display: block; margin-bottom: 6rpx; }
	.user-level { font-size: 24rpx; color: #999; }
	.arrow { font-size: 36rpx; color: #ccc; }

	.stats-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		display: flex;
		margin-bottom: 20rpx;
	}
	.stat-item {
		flex: 1;
		text-align: center;
		border-right: 2rpx solid #f0f0f0;
	}
	.stat-item:last-child { border-right: none; }
	.stat-value { font-size: 40rpx; font-weight: 700; color: var(--primary); display: block; }
	.stat-label { font-size: 24rpx; color: #999; margin-top: 8rpx; display: block; }

	.menu-group {
		background: #fff;
		border-radius: 16rpx;
		margin-bottom: 20rpx;
		overflow: hidden;
	}
	.menu-item {
		display: flex;
		align-items: center;
		padding: 28rpx 30rpx;
		border-bottom: 2rpx solid #f5f5f5;
	}
	.menu-item:last-child { border-bottom: none; }
	.menu-icon { font-size: 36rpx; margin-right: 20rpx; }
	.menu-text { flex: 1; font-size: 28rpx; color: #333; }
	.menu-arrow { font-size: 32rpx; color: #ccc; }

	.logout {
		text-align: center;
		padding: 30rpx;
		color: var(--danger);
		font-size: 28rpx;
		margin-top: 40rpx;
	}
</style>
