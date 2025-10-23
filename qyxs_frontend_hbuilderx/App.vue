<script>
    import { useUserStore } from '@/store/user.js';
    
	export default {
		onLaunch: function() {
			console.log('App Launch');
            
            // 启动时自动执行登录流程
            const userStore = useUserStore();
            userStore.appLogin();
		},
		onShow: function() {
			console.log('App Show');
		},
		onHide: function() {
			console.log('App Hide');
		}
	}
</script>

<style>
	/* uni.css - App 全局样式 */
    @import '@/static/css/common.css';
</style>