<template>
	<view class="page-create">
		<view class="form-group">
			<text class="form-label">任务标题 *</text>
			<input class="form-input" v-model="form.title" placeholder="例：送3份外卖到2栋" />
		</view>

		<view class="form-group">
			<text class="form-label">任务描述</text>
			<textarea class="form-textarea" v-model="form.description" placeholder="详细描述任务内容和要求" />
		</view>

		<view class="form-group">
			<text class="form-label">任务类型 *</text>
			<view class="radio-group">
				<view
					v-for="type in taskTypes"
					:key="type.value"
					class="radio-item"
					:class="{ active: form.task_type === type.value }"
					@tap="form.task_type = type.value"
				>
					{{ type.label }}
				</view>
			</view>
		</view>

		<view class="form-row">
			<view class="form-group flex-1">
				<text class="form-label">酬金（元）*</text>
				<input class="form-input" type="digit" v-model="form.reward_amount" placeholder="0.00" />
			</view>
			<view class="form-group flex-1">
				<text class="form-label">需要人数</text>
				<input class="form-input" type="number" v-model="form.quantity" placeholder="1" />
			</view>
		</view>

		<view class="form-row">
			<view class="form-group flex-1">
				<text class="form-label">难度</text>
				<view class="radio-group">
					<view
						v-for="d in difficulties"
						:key="d.value"
						class="radio-item small"
						:class="{ active: form.difficulty === d.value }"
						@tap="form.difficulty = d.value"
					>
						{{ d.label }}
					</view>
				</view>
			</view>
			<view class="form-group flex-1">
				<text class="form-label">预计耗时（分钟）</text>
				<input class="form-input" type="number" v-model="form.estimated_min" placeholder="15" />
			</view>
		</view>

		<view class="form-group">
			<text class="form-label">地址</text>
			<input class="form-input" v-model="form.address" placeholder="任务执行地点" @tap="chooseLocation" />
		</view>

		<button class="publish-btn" @tap="handlePublish" :loading="publishing">发布任务</button>
	</view>
</template>

<script>
	import { createTask } from '@/api/index.js'

	export default {
		data() {
			return {
				form: {
					title: '',
					description: '',
					task_type: 1,
					reward_amount: '',
					quantity: 1,
					difficulty: 1,
					estimated_min: 15,
					address: '',
					lat: null,
					lng: null,
				},
				publishing: false,
				taskTypes: [
					{ label: '配送', value: 1 },
					{ label: '搬运', value: 2 },
					{ label: '巡检', value: 3 },
					{ label: '其他', value: 4 }
				],
				difficulties: [
					{ label: '轻松', value: 1 },
					{ label: '适中', value: 2 },
					{ label: '挑战', value: 3 }
				]
			}
		},
		methods: {
			chooseLocation() {
				uni.chooseLocation({
					success: (res) => {
						this.form.address = res.address || res.name
						this.form.lat = res.latitude
						this.form.lng = res.longitude
					}
				})
			},
			handlePublish() {
				if (!this.form.title || !this.form.reward_amount) {
					uni.showToast({ title: '请填写必填项', icon: 'none' })
					return
				}
				const merchantId = uni.getStorageSync('merchant_id')
				if (!merchantId) {
					uni.showToast({ title: '请先入驻商户', icon: 'none' })
					return
				}

				this.publishing = true
				const data = {
					...this.form,
					merchant_id: merchantId,
					reward_amount: parseFloat(this.form.reward_amount),
					quantity: parseInt(this.form.quantity) || 1,
					estimated_min: parseInt(this.form.estimated_min) || 15,
				}

				createTask(data)
					.then(() => {
						uni.showToast({ title: '发布成功！', icon: 'success' })
						setTimeout(() => uni.navigateBack(), 1000)
					})
					.catch(err => {
						uni.showToast({ title: err.message || '发布失败', icon: 'none' })
					})
					.finally(() => { this.publishing = false })
			}
		}
	}
</script>

<style>
	.page-create { background: #f5f5f5; min-height: 100vh; padding: 30rpx; }

	.form-group { margin-bottom: 30rpx; }
	.form-label { font-size: 28rpx; color: #666; margin-bottom: 12rpx; display: block; }
	.form-input {
		width: 100%;
		height: 80rpx;
		background: #fff;
		border-radius: 12rpx;
		padding: 0 24rpx;
		font-size: 28rpx;
	}
	.form-textarea {
		width: 100%;
		height: 160rpx;
		background: #fff;
		border-radius: 12rpx;
		padding: 20rpx 24rpx;
		font-size: 28rpx;
	}
	.form-row { display: flex; gap: 20rpx; }
	.flex-1 { flex: 1; }

	.radio-group { display: flex; gap: 16rpx; flex-wrap: wrap; }
	.radio-item {
		padding: 12rpx 24rpx;
		background: #fff;
		border-radius: 12rpx;
		font-size: 26rpx;
		color: #666;
	}
	.radio-item.active {
		background: var(--primary-bg);
		color: var(--primary);
		font-weight: 600;
	}
	.radio-item.small { padding: 8rpx 20rpx; font-size: 24rpx; }

	.publish-btn {
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		background: var(--primary);
		color: #fff;
		border-radius: 44rpx;
		font-size: 32rpx;
		font-weight: 600;
		border: none;
		margin-top: 40rpx;
	}
</style>
