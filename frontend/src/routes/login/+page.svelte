<script lang="ts" context="module">
  import type { Load } from '@sveltejs/kit';

  export const load: Load = async () => {
    return {
      title: 'Đăng nhập',
      description: 'Đăng nhập vào hệ thống Spotifood'
    };
  };
</script>

<script lang="ts">
  import { goto } from '$app/navigation';
  import { writable } from 'svelte/store';
  import { Mail, Lock } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  // Store lưu trữ trạng thái user
  export const user = writable<any>(null);
  export const isAuthenticated = writable<boolean>(false);
  export const token = writable<string | null>(null);

  // Thêm state kiểm tra xác thực để tránh flash UI
  let isCheckingAuth = true;
  let isLoading = false;
  let errorMessage = '';
  let showConnectionTest = false;
  let showPassword = false;

  // API URL
  const API_URL = 'http://localhost:8000';

  // Hàm fetch API
  async function fetchApi<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'include',
      mode: 'cors',
    };

    const fetchOptions: RequestInit = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers as Record<string, string>,
        ...(options.headers || {}) as Record<string, string>,
      },
    };

    try {
      const response = await fetch(url, fetchOptions);
      
      // Nếu response không OK, xử lý lỗi
      if (!response.ok) {
        // Cố gắng nhận lỗi từ API nếu có
        try {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Lỗi không xác định');
        } catch (error) {
          throw new Error(`Lỗi ${response.status}: ${response.statusText}`);
        }
      }
      
      // Kiểm tra nếu response rỗng
      const text = await response.text();
      return text ? JSON.parse(text) as T : {} as T;
    } catch (error) {
      console.error('Lỗi kết nối API:', error);
      throw error;
    }
  }
  
  // Kiểm tra từ localStorage nếu đã đăng nhập trước đó
  if (typeof window !== 'undefined') {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        user.set(userData);
        token.set(storedToken);
        isAuthenticated.set(true);
      } catch (error) {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
  }
  
  // Interface cho dữ liệu login và response
  interface LoginCredentials {
    email: string;
    password: string;
    rememberMe?: boolean;
  }
  
  interface AuthResponse {
    access_token: string;
    token_type: string;
  }
  
  // Kiểm tra token hợp lệ từ API
  async function validateToken(authToken: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/api/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        // Nếu API trả về user data thì token hợp lệ
        if (userData) {
          user.set(userData);
          isAuthenticated.set(true);
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('Lỗi xác thực token:', error);
      return false;
    }
  }
  
  // Hàm kiểm tra auth và chuyển hướng
  async function checkAndRedirect() {
    try {
      isCheckingAuth = true;
      
      // Lấy token từ localStorage
      const storedToken = localStorage.getItem('token');
      
      if (storedToken) {
        // Kiểm tra token với API
        const isValid = await validateToken(storedToken);
        
        if (isValid) {
          // Lưu token vào store
          token.set(storedToken);
          
          // Lưu token vào cookie cho server-side
          document.cookie = `auth_token=${storedToken}; max-age=${60*60*24*7}; path=/; SameSite=Lax`;
          
          // Redirect ngay lập tức
          goto('/dashboard');
          return; // Dừng hàm ở đây để không set isCheckingAuth = false
        } else {
          // Token không hợp lệ - xóa khỏi localStorage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          token.set(null);
          user.set(null);
          isAuthenticated.set(false);
        }
      }
    } catch (error) {
      console.error('Lỗi kiểm tra authentication:', error);
    } finally {
      isCheckingAuth = false; // Kết thúc kiểm tra, hiển thị UI
    }
  }
  
  /**
   * Đăng nhập người dùng
   */
  async function login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const { rememberMe, ...loginData } = credentials;
      
      const response = await fetchApi<AuthResponse>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(loginData)
      });
      
      if (response.access_token) {
        // Lưu token
        token.set(response.access_token);
        localStorage.setItem('token', response.access_token);
        
        // Thêm: Lưu vào cookie để server-side có thể đọc
        document.cookie = `auth_token=${response.access_token}; max-age=${60*60*24*7}; path=/; SameSite=Lax`;
        
        // Lấy thông tin user từ token
        try {
          const userResponse = await fetch('http://localhost:8000/api/users/me', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${response.access_token}`
            }
          });
          
          if (userResponse.ok) {
            const userInfo = await userResponse.json();
            if (userInfo) {
              user.set(userInfo);
              isAuthenticated.set(true);
              
              if (rememberMe && typeof window !== 'undefined') {
                localStorage.setItem('user', JSON.stringify(userInfo));
              }
            }
          } else {
            console.error('Lỗi lấy thông tin người dùng:', userResponse.statusText);
          }
        } catch (error) {
          console.error('Lỗi lấy thông tin người dùng:', error);
        }
      }
      
      return response;
    } catch (error) {
      console.error('Lỗi đăng nhập:', error);
      throw error;
    }
  }
  
  const loginData = writable<LoginCredentials>({
    email: '',
    password: '',
    rememberMe: false
  });

  // Kiểm tra nếu đã đăng nhập thì chuyển hướng - đã cải thiện để tránh flash UI
  onMount(() => {
    checkAndRedirect();
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

<!-- Hiển thị spinner khi đang kiểm tra auth -->
{#if isCheckingAuth}
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-dark">
    <div class="spinner-border text-accent" role="status" style="width: 3rem; height: 3rem;">
      <span class="visually-hidden">Đang tải...</span>
    </div>
  </div>
{:else}
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
{/if}

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