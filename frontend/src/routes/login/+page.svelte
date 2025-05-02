<script lang="ts">
  import { goto } from '$app/navigation';
  import { writable } from 'svelte/store';
  import { Mail, Lock } from 'lucide-svelte';
  import { login, isAuthenticated } from '$lib/services/auth';
  import { onMount } from 'svelte';
  
  let isLoading = false;
  let errorMessage = '';
  let showConnectionTest = false;
  let showPassword = false;
  
  const loginData = writable({
    email: '',
    password: '',
    rememberMe: false
  });

  // Kiểm tra nếu đã đăng nhập thì chuyển hướng
  onMount(() => {
    const checkLoginStatus = async () => {
      if ($isAuthenticated) {
        goto('/dashboard');
      }
    };
    
    checkLoginStatus();
  });

  // Hiện/ẩn mật khẩu
  const togglePassword = () => {
    showPassword = !showPassword;
  };

  const handleLogin = async () => {
    try {
      isLoading = true;
      errorMessage = '';
      
      // Validate form
      if (!$loginData.email || !$loginData.password) {
        errorMessage = 'Vui lòng nhập đầy đủ email và mật khẩu';
        return;
      }
      
      // Thực hiện gọi service đăng nhập
      const response = await login($loginData);
      
      if (response.access_token) {
        // Chờ một chút để đảm bảo store được cập nhật
        setTimeout(() => {
          // Sau khi đăng nhập thành công, chuyển hướng người dùng
          goto('/dashboard');
        }, 500);
      } else {
        errorMessage = 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin';
        showConnectionTest = true;
      }
    } catch (error: any) {
      console.error('Lỗi đăng nhập:', error);
      
      // Hiển thị thông báo lỗi chi tiết nếu có
      if (error?.message) {
        errorMessage = error.message;
      } else {
        errorMessage = 'Không thể kết nối tới máy chủ. Vui lòng thử lại sau.';
      }
      
      // Hiển thị kiểm tra kết nối
      showConnectionTest = true;
    } finally {
      isLoading = false;
    }
  };
</script>

<div class="min-vh-100 d-flex align-items-center justify-content-center bg-dark">
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-5 col-xl-4">
        <div class="card bg-dark text-white border-0 shadow-lg rounded-4 animate__animated animate__fadeIn">
          <!-- Header -->
          <div class="card-header bg-transparent border-0 text-center py-4">
            <h3 class="fw-bold mb-2 text-gradient">SPOTIFOOD</h3>
            <p class="text-light opacity-75 small">Đăng nhập để trải nghiệm</p>
          </div>
          
          <div class="card-body px-4 px-md-5">
            {#if errorMessage}
              <div class="alert alert-danger bg-dark-subtle border-danger text-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <span>{errorMessage}</span>
              </div>
            {/if}

            <form on:submit|preventDefault={handleLogin} class="needs-validation">
              <!-- Email input -->
              <div class="form-floating mb-4">
                <input
                  type="email"
                  class="form-control bg-dark-subtle text-white border-0"
                  id="email"
                  placeholder="name@example.com"
                  bind:value={$loginData.email}
                  required
                  disabled={isLoading}
                />
                <label for="email" class="text-light-purple">Email</label>
              </div>

              <!-- Password input -->
              <div class="form-floating mb-4 position-relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  class="form-control bg-dark-subtle text-white border-0"
                  id="password"
                  placeholder="Mật khẩu"
                  bind:value={$loginData.password}
                  required
                  disabled={isLoading}
                />
                <label for="password" class="text-light-purple">Mật khẩu</label>
                <button 
                  type="button"
                  class="btn btn-link text-light position-absolute end-0 top-50 translate-middle-y border-0 bg-transparent"
                  style="z-index: 5"
                  on:click={togglePassword}
                  aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}>
                  <i class={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`}></i>
                </button>
              </div>

              <!-- Remember me & Forgot password -->
              <div class="d-flex justify-content-between mb-4">
                <div class="form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="rememberMe"
                    bind:checked={$loginData.rememberMe}
                    disabled={isLoading}
                  />
                  <label class="form-check-label text-light opacity-75 small" for="rememberMe">Nhớ mật khẩu</label>
                </div>
                <a href="/forgot-password" class="text-decoration-none small text-accent">Quên mật khẩu?</a>
              </div>

              <!-- Submit button -->
              <div class="d-grid gap-2 mb-4">
                <button 
                  type="submit" 
                  class="btn btn-gradient btn-lg border-0 rounded-3"
                  disabled={isLoading}
                >
                  {#if isLoading}
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Đang xử lý...
                  {:else}
                    Đăng nhập
                  {/if}
                </button>
              </div>
            </form>
          </div>
          
          <!-- Footer -->
          <div class="card-footer bg-transparent border-0 text-center py-4">
            <p class="mb-0 text-light opacity-75 small">
              Chưa có tài khoản? 
              <a href="/register" class="text-decoration-none text-accent fw-medium">Đăng ký ngay</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  :global(body) {
    background-color: #121212;
  }
  
  .bg-dark {
    background-color: #121212 !important;
  }
  
  .bg-dark-subtle {
    background-color: #1e1e1e !important;
  }
  
  .form-control:focus {
    border-color: #8a7dfd;
    box-shadow: 0 0 0 0.25rem rgba(138, 125, 253, 0.25);
    background-color: #252525 !important;
  }
  
  .btn-gradient {
    background: linear-gradient(45deg, #8a7dfd, #c7a0ff);
    border: none;
    transition: all 0.3s ease;
    color: #fff;
    font-weight: 500;
  }
  
  .btn-gradient:hover, .btn-gradient:focus {
    background: linear-gradient(45deg, #7a6dfd, #b596ff);
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(138, 125, 253, 0.3);
  }
  
  .text-accent {
    color: #c7a0ff !important;
  }
  
  .text-light-purple {
    color: rgba(255, 255, 255, 0.8) !important;
  }
  
  .text-gradient {
    background: linear-gradient(to right, #8a7dfd, #c7a0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .form-check-input:checked {
    background-color: #8a7dfd;
    border-color: #8a7dfd;
  }
  
  .form-floating > .form-control:focus ~ label::after,
  .form-floating > .form-control:not(:placeholder-shown) ~ label::after {
    background-color: transparent !important;
  }
  
  .form-floating > .form-control:focus ~ label,
  .form-floating > .form-control:not(:placeholder-shown) ~ label {
    color: #c7a0ff !important;
    opacity: 1;
  }
  
  .card {
    overflow: hidden;
    transition: all 0.3s ease;
    background-color: #181818 !important;
  }
  
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .animate__fadeIn {
    animation: fadeIn 0.6s ease-out;
  }
  
  .shadow-lg {
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2) !important;
  }
  
  .text-light {
    color: #ffffff !important;
  }
</style> 