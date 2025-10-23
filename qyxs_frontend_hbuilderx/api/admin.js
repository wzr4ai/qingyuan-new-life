// api/admin.js
import { request } from './request.js';

/**
 * H5 管理员登录
 * @param {string} phone
 * @param {string} password
 */
export const adminLogin = (phone, password) => {
    return request({
        url: '/auth/admin-login',
        method: 'POST',
        data: {
            phone: phone,
            password: password
        }
    });
};

// --- 后续我们将在这里添加所有 /admin/... 的 API ---