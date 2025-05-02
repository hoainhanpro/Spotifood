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