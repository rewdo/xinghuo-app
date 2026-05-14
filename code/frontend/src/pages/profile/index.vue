<template>
	<view class="page">
		<!-- 顶部用户卡片 -->
		<view class="user-card">
			<view class="user-avatar">
				<text class="avatar-text">⚡</text>
			</view>
			<view class="user-info">
				<text class="user-name">{{ user.nickname || '星火行者' }}</text>
				<text class="user-level">Lv.{{ user.level || 1 }} · 已完成 {{ user.total_tasks || 12 }} 单</text>
			</view>
		</view>

		<!-- 累计数据 -->
		<view class="stats-row">
			<view class="stats-item" @tap="goPoints">
				<text class="stats-icon">⭐</text>
				<text class="stats-num">{{ user.points || 1350 }}</text>
				<text class="stats-label">积分</text>
			</view>
			<view class="stats-item">
				<text class="stats-icon">🔥</text>
				<text class="stats-num">{{ user.total_calories || 8600 }}</text>
				<text class="stats-label">消耗大卡</text>
			</view>
			<view class="stats-item">
				<text class="stats-icon">💰</text>
				<text class="stats-num">{{ user.balance || '86.00' }}</text>
				<text class="stats-label">收益(元)</text>
			</view>
		</view>

		<!-- 训练计划设置 -->
		<view class="section-card">
			<view class="section-title">
				<text>🏃 训练计划</text>
				<text class="edit-hint">点击修改</text>
			</view>

			<view class="setting-row" @tap="showGoalPicker = true">
				<text class="setting-label">训练目标</text>
				<text class="setting-value">{{ GOAL_LABELS[user.fitness_goal || 'fat_loss'] }}</text>
				<text class="arrow">›</text>
			</view>
			<view class="setting-row" @tap="showFreqPicker = true">
				<text class="setting-label">每周频率</text>
				<text class="setting-value">{{ user.fitness_frequency || 3 }}次/周</text>
				<text class="arrow">›</text>
			</view>
			<view class="setting-row" @tap="showTagPicker = true">
				<text class="setting-label">锻炼类型</text>
				<text class="setting-value">{{ tagNames.join(' / ') }}</text>
				<text class="arrow">›</text>
			</view>
			<view class="setting-row" @tap="showMinutesPicker = true">
				<text class="setting-label">每日时长</text>
				<text class="setting-value">{{ user.daily_minutes || 30 }}分钟</text>
				<text class="arrow">›</text>
			</view>
		</view>

		<!-- 功能入口 -->
		<view class="section-card">
			<view class="section-title"><text>📋 功能</text></view>
			<view class="menu-row" @tap="goPoints">
				<text class="menu-icon">⭐</text>
				<text class="menu-label">积分中心</text>
				<text class="arrow">›</text>
			</view>
			<view class="menu-row" @tap="goWallet">
				<text class="menu-icon">💰</text>
				<text class="menu-label">我的钱包</text>
				<text class="arrow">›</text>
			</view>
			<view class="menu-row" @tap="goOrders">
				<text class="menu-icon">📋</text>
				<text class="menu-label">历史订单</text>
				<text class="arrow">›</text>
			</view>
		</view>

		<!-- 演示提示 -->
		<view class="demo-hint">
			<text class="hint-text">⚡ 演示数据，连接后端后自动同步</text>
		</view>

		<!-- 选择器弹窗 -->
		<view class="picker-overlay" v-if="showGoalPicker || showFreqPicker || showTagPicker || showMinutesPicker" @tap="closePickers">
			<view class="picker-modal" @tap.stop>
				<view class="picker-title">{{ pickerTitle }}</view>
				<view class="picker-options">
					<view class="picker-option"
						v-for="opt in pickerOptions" :key="opt.value"
						:class="{selected: opt.selected}"
						@tap="selectPicker(opt)">
						<text>{{ opt.label }}</text>
						<text class="check" v-if="opt.selected">✓</text>
					</view>
				</view>
				<view class="picker-close" @tap="closePickers">关闭</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			user: {
				nickname: '星火行者',
				level: 2,
				total_tasks: 12,
				total_calories: 8600,
				balance: '86.00',
				points: 1350,
				fitness_goal: 'fat_loss',
				fitness_frequency: 3,
				fitness_tags: ['run', 'walk'],
				daily_minutes: 30,
				weight_kg: 70
			},
			GOAL_LABELS: { fat_loss: '减脂', muscle: '增肌', endurance: '耐力', general: '综合' },
			TAG_LABELS: { run: '跑步', walk: '步行', lift: '力量', climb: '爬楼', carry: '负重' },
			showGoalPicker: false, showFreqPicker: false, showTagPicker: false, showMinutesPicker: false,
			activePicker: null,
			pickers: {
				goal: { title: '选择训练目标', options: [
					{ value: 'fat_loss', label: '减脂' },
					{ value: 'muscle', label: '增肌' },
					{ value: 'endurance', label: '耐力' },
					{ value: 'general', label: '综合' }
				]},
				freq: { title: '每周训练次数', options: [
					{ value: 2, label: '每周2次' },
					{ value: 3, label: '每周3次' },
					{ value: 5, label: '每周5次' },
					{ value: 7, label: '每天' }
				]},
				tag: { title: '选择锻炼类型', options: [
					{ value: 'run', label: '🏃 跑步' },
					{ value: 'walk', label: '🚶 步行' },
					{ value: 'lift', label: '💪 力量' },
					{ value: 'climb', label: '🧗 爬楼' },
					{ value: 'carry', label: '🚴 负重' }
				]},
				minutes: { title: '每日训练时长', options: [
					{ value: 15, label: '15分钟' },
					{ value: 30, label: '30分钟' },
					{ value: 45, label: '45分钟' },
					{ value: 60, label: '1小时+' }
				]}
			}
		}
	},
	computed: {
		tagNames() {
			const tags = this.user.fitness_tags || []
			return tags.map(t => this.TAG_LABELS[t] || t)
		},
		pickerTitle() {
			if (this.showGoalPicker) return this.pickers.goal.title
			if (this.showFreqPicker) return this.pickers.freq.title
			if (this.showTagPicker) return this.pickers.tag.title
			if (this.showMinutesPicker) return this.pickers.minutes.title
			return ''
		},
		pickerOptions() {
			if (this.showGoalPicker) return this.pickers.goal.options.map(o => ({
				...o, selected: o.value === this.user.fitness_goal
			}))
			if (this.showFreqPicker) return this.pickers.freq.options.map(o => ({
				...o, selected: o.value === this.user.fitness_frequency
			}))
			if (this.showTagPicker) return this.pickers.tag.options.map(o => ({
				...o, selected: (this.user.fitness_tags || []).includes(o.value)
			}))
			if (this.showMinutesPicker) return this.pickers.minutes.options.map(o => ({
				...o, selected: o.value === this.user.daily_minutes
			}))
			return []
		}
	},
	onLoad() {
		this.loadUser()
	},
	methods: {
		async loadUser() {
			// Try to load from API
		},
		selectPicker(opt) {
			if (this.showGoalPicker) {
				this.user.fitness_goal = opt.value
				this.showGoalPicker = false
			} else if (this.showFreqPicker) {
				this.user.fitness_frequency = opt.value
				this.showFreqPicker = false
			} else if (this.showTagPicker) {
				const tags = this.user.fitness_tags || []
				const idx = tags.indexOf(opt.value)
				if (idx >= 0) {
					tags.splice(idx, 1)
				} else if (tags.length < 3) {
					tags.push(opt.value)
				}
				this.user.fitness_tags = tags
			} else if (this.showMinutesPicker) {
				this.user.daily_minutes = opt.value
				this.showMinutesPicker = false
			}
			uni.showToast({ title: '已更新', icon: 'none' })
		},
		closePickers() {
			this.showGoalPicker = false
			this.showFreqPicker = false
			this.showTagPicker = false
			this.showMinutesPicker = false
		},
		goPoints() {
			uni.switchTab({ url: '/pages/points/index' })
		},
		goWallet() {
			uni.navigateTo({ url: '/pages/wallet/index' })
		},
		goOrders() {
			uni.switchTab({ url: '/pages/order/list' })
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
.user-card {
	background: linear-gradient(135deg, #ff6b35, #ff8c42);
	padding: 80rpx 40rpx 40rpx;
	display: flex;
	align-items: center;
	color: #fff;
}
.user-avatar {
	width: 100rpx;
	height: 100rpx;
	background: rgba(255,255,255,0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}
.avatar-text { font-size: 48rpx; }
.user-name { font-size: 32rpx; font-weight: bold; display: block; }
.user-level { font-size: 24rpx; opacity: 0.8; display: block; margin-top: 6rpx; }

.stats-row {
	display: flex;
	background: #fff;
	margin: 20rpx 30rpx;
	border-radius: 16rpx;
	padding: 20rpx 0;
}
.stats-item {
	flex: 1;
	text-align: center;
}
.stats-icon { font-size: 28rpx; display: block; }
.stats-num { font-size: 32rpx; font-weight: bold; color: #333; display: block; margin: 6rpx 0; }
.stats-label { font-size: 22rpx; color: #999; display: block; }

.section-card {
	background: #fff;
	margin: 20rpx 30rpx;
	border-radius: 16rpx;
	overflow: hidden;
}
.section-title {
	display: flex;
	justify-content: space-between;
	padding: 24rpx 30rpx;
	border-bottom: 1rpx solid #f5f5f5;
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}
.edit-hint { font-size: 22rpx; color: #ccc; font-weight: normal; }

.setting-row, .menu-row {
	display: flex;
	align-items: center;
	padding: 24rpx 30rpx;
	border-bottom: 1rpx solid #f5f5f5;
}
.setting-row:last-child, .menu-row:last-child { border-bottom: none; }
.setting-label { font-size: 26rpx; color: #666; flex: 1; }
.setting-value { font-size: 26rpx; color: #333; }
.menu-icon { font-size: 28rpx; margin-right: 16rpx; }
.menu-label { font-size: 26rpx; color: #333; flex: 1; }
.arrow { font-size: 28rpx; color: #ccc; }

.demo-hint { text-align: center; padding: 20rpx; }
.hint-text { font-size: 20rpx; color: #ccc; }

/* Picker overlay */
.picker-overlay {
	position: fixed;
	top: 0; left: 0; right: 0; bottom: 0;
	background: rgba(0,0,0,0.4);
	display: flex;
	align-items: flex-end;
	z-index: 100;
}
.picker-modal {
	background: #fff;
	border-radius: 20rpx 20rpx 0 0;
	width: 100%;
	max-height: 60vh;
	overflow-y: auto;
}
.picker-title { font-size: 28rpx; font-weight: bold; padding: 30rpx; text-align: center; border-bottom: 1rpx solid #f0f0f0; }
.picker-option {
	padding: 24rpx 40rpx;
	display: flex;
	justify-content: space-between;
	font-size: 28rpx;
	border-bottom: 1rpx solid #f5f5f5;
}
.picker-option.selected { color: #ff6b35; font-weight: bold; }
.check { color: #ff6b35; }
.picker-close {
	padding: 24rpx;
	text-align: center;
	color: #999;
	font-size: 26rpx;
}
</style>
