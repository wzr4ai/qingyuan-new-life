<template>
	<view class="login-container">
		<view class="login-form">
			<text class="title">青元新生 管理后台</text>
			
			<input class="input-field" v-model="form.phone" type="text" placeholder="请输入手机号" />
			<input class="input-field" v-model="form.password" type="password" placeholder="请输入密码" />
			
			<button class="login-button" @click="handleLogin" :disabled="isLoading">
				{{ isLoading ? '登录中...' : '登 录' }}
			</button>
			
			<text v-if="errorMsg" class="error-text">{{ errorMsg }}</text>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/store/user.js';
import { adminLogin } from '@/api/admin.js';

// 1. Vue 3 Composition API (setup 语法糖)
const userStore = useUserStore();

// 2. 表单数据
const form = ref({
	phone: '',
	password: ''
});
const isLoading = ref(false);
const errorMsg = ref('');

// 3. 登录方法
const handleLogin = async () => {
	isLoading.value = true;
	errorMsg.value = '';

	if (!form.value.phone || !form.value.password) {
		errorMsg.value = '手机号和密码不能为空';
		isLoading.value = false;
		return;
	}

	try {
		// 4. 调用 API
		const data = await adminLogin(form.value.phone, form.value.password);
		
		if (data && data.access_token) {
			// 5. 登录成功, 存储 Token 到 Pinia
			userStore.setToken(data.access_token);
			
			// 6. 显示成功提示
			uni.showToast({
				title: '登录成功',
				icon: 'success'
			});
			
			// 7. 跳转到管理后台首页
			uni.redirectTo({
				url: '/pages/admin/dashboard'
			});
			
		} else {
			throw new Error('未收到 Token');
		}
		
	} catch (error) {
		// 8. 登录失败 (request.js 会自动弹窗, 这里我们也设置错误信息)
		errorMsg.value = error.data?.detail || '登录失败，请重试';
	} finally {
		isLoading.value = false;
	}
};
</script>

<style scoped>
.login-container {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 100vh;
	background-color: #f4f4f4;
}
.login-form {
	width: 350px;
	padding: 30px;
	background-color: #fff;
	border-radius: 8px;
	box-shadow: 0 4px 12px rgba(0,0,0,0.05);
	display: flex;
	flex-direction: column;
}
.title {
	font-size: 24px;
	font-weight: bold;
	text-align: center;
	margin-bottom: 25px;
}
.input-field {
	height: 45px;
	border: 1px solid #dcdfe6;
	border-radius: 4px;
	padding: 0 15px;
	margin-bottom: 20px;
	font-size: 16px;
}
.login-button {
	height: 45px;
	line-height: 45px;
	font-size: 18px;
	background-color: #007aff;
	color: #fff;
}
.login-button[disabled] {
    background-color: #a0cfff;
}
.error-text {
	color: #f56c6c;
	font-size: 14px;
	text-align: center;
	margin-top: 15px;
}
</style>