<script>
	export default {
		onLaunch: function() {
			console.log('星火 APP Launched');
		},
		globalData: {
			userInfo: null
		}
	}
</script>

<style>
	/* 全局样式 */
	page {
		background-color: #f5f5f5;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
		color: #333;
		font-size: 28rpx;
		line-height: 1.5;
		box-sizing: border-box;
	}
	view, text, scroll-view {
		box-sizing: border-box;
	}
	/* 品牌色 */
	:root {
		--primary: #ff6b35;
		--primary-light: #ff8c5a;
		--primary-bg: #fff3ed;
		--success: #34c759;
		--warning: #ff9500;
		--danger: #ff3b30;
		--gray-1: #f5f5f5;
		--gray-2: #e8e8e8;
		--gray-3: #999;
		--gray-4: #666;
		--gray-5: #333;
		--text-primary: #333;
		--text-secondary: #666;
		--text-hint: #999;
	}
</style>
