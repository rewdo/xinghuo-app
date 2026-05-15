<template>
	<view class="page">
		<view class="nav-bar">
			<text class="back-btn" @tap="goBack">‹ 返回</text>
			<text class="nav-title">发布任务</text>
			<text class="nav-placeholder"></text>
		</view>

		<view class="form">
			<!-- 基本信息 -->
			<view class="form-group">
				<text class="form-label">任务标题 *</text>
				<input class="form-input" v-model="form.title" placeholder="例：帮王阿姨送菜到3号楼" />
			</view>
			<view class="form-group">
				<text class="form-label">任务描述</text>
				<textarea class="form-textarea" v-model="form.desc" placeholder="详细描述任务内容..." />
			</view>

			<!-- 锻炼类型 -->
			<view class="form-group">
				<text class="form-label">锻炼类型 *</text>
				<view class="tag-select">
					<view class="tag-option" v-for="t in fitnessTypes" :key="t.value"
						:class="{active: form.fitness_tag === t.value}" @tap="form.fitness_tag = t.value">
						<text>{{ t.icon }} {{ t.label }}</text>
					</view>
				</view>
				<text class="form-hint">选择后系统自动计算消耗🔥</text>
			</view>

			<!-- 距离/时长 -->
			<view class="form-row">
				<view class="form-group half">
					<text class="form-label">距离（米）</text>
					<input class="form-input" v-model="form.distance" type="number" placeholder="800" />
				</view>
				<view class="form-group half">
					<text class="form-label">预计时长（分钟）</text>
					<input class="form-input" v-model="form.minutes" type="number" placeholder="30" />
				</view>
			</view>
			<view class="calc-preview" v-if="calories > 0">
				<text>🔥 AI计算：约消耗 <text class="calc-num">{{ calories }}</text> 大卡</text>
			</view>

			<!-- 佣金 -->
			<view class="form-group">
				<text class="form-label">佣金金额（元）*</text>
				<input class="form-input" v-model="form.commission" type="digit" placeholder="5.00" />
				<text class="form-hint">用户完成此单后可提现的金额</text>
			</view>

			<!-- 优惠券（可选） -->
			<view class="form-group">
				<text class="form-label">优惠券（可选）</text>
				<view class="coupon-toggle">
					<text class="toggle-text" @tap="form.hasCoupon = !form.hasCoupon">
						{{ form.hasCoupon ? '✓ 提供优惠券' : '不提供优惠券' }}
					</text>
				</view>
				<view v-if="form.hasCoupon" class="coupon-form">
					<view class="tag-select small">
						<view class="tag-option mini" v-for="c in couponTypes" :key="c.value"
							:class="{active: form.couponType === c.value}" @tap="form.couponType = c.value">
							<text>{{ c.label }}</text>
						</view>
					</view>
					<input class="form-input" v-model="form.couponDesc" placeholder="例：满20减5" />
				</view>
			</view>

			<!-- 需要人数 -->
			<view class="form-group">
				<text class="form-label">需要人数</text>
				<input class="form-input" v-model="form.quantity" type="number" placeholder="1" />
			</view>

			<button class="submit-btn" @tap="publish" :disabled="!canSubmit">
				<text>发 布</text>
			</button>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			fitnessTypes: [
				{value:'walk', icon:'🚶', label:'步行'},
				{value:'run', icon:'🏃', label:'跑步'},
				{value:'lift', icon:'💪', label:'力量'},
				{value:'climb', icon:'🧗', label:'爬楼'},
				{value:'carry', icon:'🚴', label:'负重'}
			],
			couponTypes: [
				{value:'满减', label:'满减券'},
				{value:'折扣', label:'折扣券'},
				{value:'实物', label:'实物券'}
			],
			form: {
				title: '', desc: '',
				fitness_tag: 'walk',
				distance: 800, minutes: 30,
				commission: 5, hasCoupon: false,
				couponType: '满减', couponDesc: '',
				quantity: 1
			}
		}
	},
	computed: {
		calories() {
			const formulas = {
				walk: (w,d,m) => Math.floor(d * 0.04),
				run: (w,d,m) => Math.floor(70 * (d/1000) * 1.036),
				lift: (w,d,m) => Math.floor(m * 5),
				climb: (w,d,m) => Math.floor((d/4) * 5),
				carry: (w,d,m) => Math.floor(d * 70 * 0.5 / 1000)
			}
			const f = formulas[this.form.fitness_tag]
			return f ? f(70, Number(this.form.distance) || 0, Number(this.form.minutes) || 0) : 0
		},
		canSubmit() {
			return this.form.title.trim() && this.form.commission > 0
		}
	},
	methods: {
		publish() {
			uni.showToast({ title: '发布成功！', icon: 'success' })
			setTimeout(() => uni.navigateBack(), 1500)
		},
		goBack() { uni.navigateBack() }
	}
}
</script>

<style>
.page { min-height: 100vh; background: #f5f5f5; }
.nav-bar { display: flex; align-items: center; padding: 60rpx 30rpx 20rpx; background: #fff; justify-content: space-between; }
.back-btn { font-size: 28rpx; color: #ff6b35; }
.nav-title { font-size: 28rpx; font-weight: bold; color: #333; }
.nav-placeholder { width: 80rpx; }

.form { padding: 30rpx; }
.form-group { margin-bottom: 28rpx; background: #fff; border-radius: 16rpx; padding: 24rpx; }
.form-label { font-size: 26rpx; font-weight: bold; color: #333; display: block; margin-bottom: 12rpx; }
.form-input { width: 100%; padding: 16rpx; border: 2rpx solid #eee; border-radius: 12rpx; font-size: 26rpx; }
.form-input:focus { border-color: #ff6b35; }
.form-textarea { width: 100%; padding: 16rpx; border: 2rpx solid #eee; border-radius: 12rpx; font-size: 26rpx; min-height: 120rpx; }
.form-hint { font-size: 22rpx; color: #999; display: block; margin-top: 8rpx; }
.form-row { display: flex; gap: 20rpx; }
.half { flex: 1; }

.tag-select { display: flex; flex-wrap: wrap; gap: 12rpx; }
.tag-option { padding: 12rpx 24rpx; border: 2rpx solid #eee; border-radius: 30rpx; font-size: 24rpx; color: #666; }
.tag-option.active { background: #fff3ed; border-color: #ff6b35; color: #ff6b35; font-weight: bold; }
.tag-option.mini { padding: 8rpx 18rpx; font-size: 22rpx; }

.calc-preview { background: #fff8f0; padding: 20rpx; border-radius: 12rpx; font-size: 24rpx; color: #e6a817; margin-top: -16rpx; margin-bottom: 28rpx; }
.calc-num { font-size: 32rpx; font-weight: bold; color: #ff6b35; }

.coupon-toggle { background: #f5f5f5; border-radius: 12rpx; padding: 16rpx; }
.toggle-text { font-size: 24rpx; color: #666; }
.coupon-form { margin-top: 12rpx; }

.submit-btn { width: 100%; background: linear-gradient(135deg, #ff6b35, #ff8c42); color: #fff; border: none; border-radius: 50rpx; padding: 24rpx; font-size: 30rpx; font-weight: bold; margin-top: 20rpx; }
.submit-btn[disabled] { opacity: 0.5; }
</style>
