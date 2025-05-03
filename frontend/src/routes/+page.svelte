<script lang="ts" context="module">
    import { redirect } from '@sveltejs/kit';
    import type { Load } from '@sveltejs/kit';

    export const load: Load = async ({ url, fetch }) => {
        // Đoạn này có thể được sử dụng để kiểm tra đăng nhập và chuyển hướng
        // Ví dụ: nếu đã đăng nhập thì chuyển hướng đến dashboard, chưa đăng nhập thì ở login
        
        // Trả về dữ liệu cần thiết cho trang
        return {
            title: 'Spotifood - Trang chủ'
        };
    };
</script>

<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    onMount(() => {
        // Chuyển hướng đến trang login khi trang được tải
        goto('/login');
    });
</script>

<div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div class="text-center">
        <h1>Spotifood</h1>
        <p>Đang chuyển hướng đến trang đăng nhập...</p>
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Đang tải...</span>
        </div>
    </div>
</div> 