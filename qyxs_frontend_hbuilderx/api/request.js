// api/request.js
import { useUserStore } from '@/store/user.js';

const BASE_URL = 'http://qyxs.online/dev/'; // 替换为您的后端 URL

export const request = (options) => {
    return new Promise((resolve, reject) => {
        
        const userStore = useUserStore();
        const token = userStore.token;

        // 1. 自动附加 Token
        let header = options.header || {};
        if (token) {
            header['Authorization'] = 'Bearer ' + token;
        }

        uni.request({
            url: BASE_URL + options.url,
            method: options.method || 'GET',
            data: options.data || {},
            header: header,
            success: (res) => {
                // 2. 状态码 2xx (成功)
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(res.data);
                } 
                // 3. 401 未认证 (Token 失效)
                else if (res.statusCode === 401) {
                    console.error('Token失效, 需要重新登录');
                    userStore.logout(); // 清除本地 Token 和状态
                    uni.showToast({
                        title: '登录已失效',
                        icon: 'error',
                    });
                    // 可选：强制跳转到登录页
                    // uni.navigateTo({ url: '/pages/login/login' }); 
                    reject(res);
                }
                // 4. 其他错误 (4xx, 5xx)
                else {
                    uni.showToast({
                        title: res.data.detail || '请求失败',
                        icon: 'none',
                    });
                    reject(res);
                }
            },
            fail: (err) => {
                // 5. 网络错误
                uni.showToast({
                    title: '网络连接失败',
                    icon: 'none',
                });
                reject(err);
            }
        });
    });
};