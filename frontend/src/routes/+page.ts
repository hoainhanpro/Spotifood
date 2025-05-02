import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
    // Đoạn này có thể được sử dụng để kiểm tra đăng nhập và chuyển hướng
    // Ví dụ: nếu đã đăng nhập thì chuyển hướng đến dashboard, chưa đăng nhập thì ở login
    
    // Trả về dữ liệu cần thiết cho trang
    return {
        title: 'Spotifood - Trang chủ'
    };
}; 