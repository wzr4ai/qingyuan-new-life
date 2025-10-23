// api/auth.js
import { request } from './request.js';

/**
 * 微信登录 (V6)
 * @param {string} code - uni.login() 获取的 code
 */
export const wxLogin = (code) => {
    return request({
        url: '/auth/wx-login',
        method: 'POST',
        data: {
            code: code
        }
    });
};