// store/user.js
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
    state: () => ({
        token: uni.getStorageSync('token') || null,
        isLoggedIn: !!uni.getStorageSync('token'),
        // userInfo: {} // 稍后用于存储 GET /auth/me 的信息
    }),
    actions: {
        /**
         * 核心：应用启动时的登录流程
         */
        async appLogin() {
            if (this.isLoggedIn) {
                console.log('用户已登录, Token:', this.token);
                // TODO: 在这里可以加一个 'check_token' 的 API 验证 Token 是否真的有效
                return;
            }

            console.log('用户未登录，开始自动登录...');
            
            // 1. uni.login() 会自动调用 wx.login()
            const [loginErr, loginRes] = await uni.login({
                provider: 'weixin'
            });

            if (loginErr) {
                console.error('uni.login 失败:', loginErr);
                return;
            }

            // 2. 调用后端 API
            try {
                const data = await wxLogin(loginRes.code);
                if (data && data.access_token) {
                    this.setToken(data.access_token);
                }
            } catch (error) {
                console.error('后端 wxLogin 失败:', error);
            }
        },

        /**
         * 设置 Token
         */
        setToken(newToken) {
            this.token = newToken;
            this.isLoggedIn = true;
            uni.setStorageSync('token', newToken);
        },

        /**
         * 退出登录
         */
        logout() {
            this.token = null;
            this.isLoggedIn = false;
            uni.removeStorageSync('token');
        }
    }
});