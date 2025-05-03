<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { goto } from '$app/navigation';
  import { fly, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  
  // Định nghĩa interface cho address
  interface Address {
    id: number;
    user_id: number;
    address_name?: string;
    address: string;
    latitude?: number;
    longitude?: number;
    is_default: boolean;
    created_at: string;
    updated_at: string;
  }
  
  // Định nghĩa interface cho user
  interface User {
    id: number;
    email: string;
    full_name?: string;
    is_admin: boolean;
    is_active: boolean;
    created_at: string;
    addresses?: Address[];
  }
  
  // Store để lưu trữ dữ liệu
  const users = writable<User[]>([]);
  const isLoading = writable<boolean>(true);
  const error = writable<string | null>(null);
  const sortDirection = writable<'asc' | 'desc'>('asc');
  const searchQuery = writable<string>('');
  
  // Modal và form state
  const editingUser = writable<User | null>(null);
  const isEditModalOpen = writable<boolean>(false);
  const isUpdating = writable<boolean>(false);
  const updateError = writable<string | null>(null);
  const updateSuccess = writable<boolean>(false);
  
  // Form data
  let formData = {
    full_name: '',
    is_admin: false,
    is_active: true
  };
  
  // API URL
  const API_URL = 'http://localhost:8000';
  
  /**
   * Lấy token từ localStorage
   */
  function getToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }
  
  /**
   * Sắp xếp danh sách người dùng theo ID
   */
  function sortUsersById(direction: 'asc' | 'desc' = 'asc') {
    users.update(currentUsers => {
      return [...currentUsers].sort((a, b) => {
        return direction === 'asc' 
          ? a.id - b.id 
          : b.id - a.id;
      });
    });
    sortDirection.set(direction);
  }
  
  /**
   * Đảo chiều sắp xếp
   */
  function toggleSort() {
    const newDirection = $sortDirection === 'asc' ? 'desc' : 'asc';
    sortUsersById(newDirection);
  }
  
  /**
   * Lọc user theo thanh tìm kiếm
   */
  $: filteredUsers = $users.filter(user => {
    const query = $searchQuery.toLowerCase();
    return user.email.toLowerCase().includes(query) || 
           (user.full_name?.toLowerCase().includes(query) || false);
  });
  
  /**
   * Lấy danh sách tất cả người dùng
   */
  async function fetchUsers() {
    try {
      isLoading.set(true);
      error.set(null);
      
      const token = getToken();
      
      if (!token) {
        // Chuyển hướng đến trang login nếu chưa đăng nhập
        goto('/login');
        return;
      }
      
      const response = await fetch(`${API_URL}/api/users/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token hết hạn hoặc không hợp lệ
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          goto('/login');
          return;
        }
        
        if (response.status === 403) {
          error.set('Bạn không có quyền xem danh sách người dùng');
          return;
        }
        
        throw new Error(`Lỗi: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json() as User[];
      users.set(data);
      
      // Sắp xếp theo ID sau khi lấy dữ liệu
      sortUsersById($sortDirection);
    } catch (err: any) {
      console.error('Lỗi khi tải danh sách người dùng:', err);
      error.set(err.message || 'Không thể tải danh sách người dùng');
    } finally {
      isLoading.set(false);
    }
  }

  /**
   * Mở modal chỉnh sửa thông tin người dùng
   */
  function openEditModal(user: User) {
    editingUser.set(user);
    formData = {
      full_name: user.full_name || '',
      is_admin: user.is_admin,
      is_active: user.is_active
    };
    updateError.set(null);
    updateSuccess.set(false);
    isEditModalOpen.set(true);
  }

  /**
   * Đóng modal chỉnh sửa thông tin
   */
  function closeEditModal() {
    isEditModalOpen.set(false);
    setTimeout(() => {
      editingUser.set(null);
      updateError.set(null);
      updateSuccess.set(false);
    }, 300);
  }

  /**
   * Cập nhật thông tin người dùng
   */
  async function updateUserInfo() {
    if (!$editingUser) return;
    
    try {
      isUpdating.set(true);
      updateError.set(null);
      updateSuccess.set(false);
      
      const token = getToken();
      
      if (!token) {
        goto('/login');
        return;
      }
      
      // Đảm bảo gửi đúng schema dựa trên backend
      const updateData = {
        full_name: formData.full_name,
        is_admin: formData.is_admin,
        is_active: formData.is_active
      };
      
      const response = await fetch(`${API_URL}/api/users/${$editingUser.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          goto('/login');
          return;
        }
        
        if (response.status === 403) {
          updateError.set('Bạn không có quyền cập nhật thông tin người dùng');
          return;
        }
        
        throw new Error(`Lỗi: ${response.status} ${response.statusText}`);
      }
      
      const updatedUser = await response.json();
      
      // Cập nhật danh sách users
      users.update(currentUsers => {
        return currentUsers.map(user => 
          user.id === updatedUser.id ? updatedUser : user
        );
      });
      
      updateSuccess.set(true);
      setTimeout(() => {
        closeEditModal();
        // Làm mới danh sách sau khi cập nhật thành công
        fetchUsers();
      }, 1500);
      
    } catch (err: any) {
      console.error('Lỗi khi cập nhật thông tin người dùng:', err);
      updateError.set(err.message || 'Không thể cập nhật thông tin người dùng');
    } finally {
      isUpdating.set(false);
    }
  }
  
  // Tạo avatar từ email
  function getInitials(email: string, fullName?: string): string {
    if (fullName && fullName.trim().length > 0) {
      return fullName
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase();
    }
    return email.substring(0, 2).toUpperCase();
  }
  
  // Tạo màu ngẫu nhiên cho avatar
  function getAvatarColor(id: number): string {
    const colors = [
      '#8a7dfd', // Màu chính
      '#7D4CDB', // Tím
      '#00C781', // Xanh lá
      '#FFCA58', // Vàng
      '#FF4040', // Đỏ
      '#00739D', // Xanh dương
      '#6FFFB0', // Xanh mint
      '#FD6FFF', // Hồng
      '#81FCED', // Xanh cyan
    ];
    
    return colors[id % colors.length];
  }
  
  // Format ngày 
  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric'
    });
  }
  
  onMount(() => {
    fetchUsers();
  });
</script>

<svelte:head>
  <title>Quản lý người dùng | Spotifood</title>
</svelte:head>

<div class="min-vh-100 bg-dark">
  <div class="container py-5">
    <div class="row">
      <div class="col-12">
        <div in:fly={{ y: -20, duration: 500, delay: 200 }} out:fade>
          <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-5">
            <h2 class="text-gradient mb-3 mb-md-0 text-center text-md-start">Quản lý người dùng</h2>
            
            <div class="d-flex flex-column flex-sm-row gap-3 w-100 w-md-auto">
              <!-- Tìm kiếm -->
              <div class="search-box">
                <i class="bi bi-search search-icon" aria-hidden="true"></i>
                <input 
                  type="text" 
                  class="search-input" 
                  placeholder="Tìm kiếm..."
                  bind:value={$searchQuery}
                />
              </div>
              
              <!-- Nút sắp xếp -->
              <button class="btn btn-primary-soft" on:click={toggleSort}>
                <i class="bi bi-arrow-up-down me-2" aria-hidden="true"></i>
                Sắp xếp theo ID
                {#if $sortDirection === 'asc'}
                  <i class="bi bi-arrow-up-short ms-1" aria-hidden="true"></i>
                {:else}
                  <i class="bi bi-arrow-down-short ms-1" aria-hidden="true"></i>
                {/if}
              </button>
              
              <!-- Nút làm mới -->
              <button class="btn btn-outline-light" on:click={() => fetchUsers()}>
                <i class="bi bi-arrow-clockwise me-2" aria-hidden="true"></i>
                Làm mới
              </button>
            </div>
          </div>
          
          {#if $isLoading}
            <div class="d-flex justify-content-center my-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
              </div>
            </div>
          {:else if $error}
            <div class="alert alert-danger bg-dark-subtle">
              <i class="bi bi-exclamation-triangle-fill me-2" aria-hidden="true"></i>
              {$error}
            </div>
          {:else if filteredUsers.length === 0}
            <div class="alert alert-info bg-dark-subtle">
              <i class="bi bi-info-circle-fill me-2" aria-hidden="true"></i>
              {$searchQuery ? 'Không tìm thấy người dùng phù hợp' : 'Không có người dùng nào'}
            </div>
          {:else}
            <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
              {#each filteredUsers as user, i}
                <div 
                  class="col" 
                  in:fly={{ y: 20, duration: 400, delay: i * 100 }} 
                  out:fade
                >
                  <div class="user-card">
                    <div class="card-content">
                      <div class="avatar-container">
                        <div class="avatar" style="background-color: {getAvatarColor(user.id)}">
                          <span>{getInitials(user.email, user.full_name)}</span>
                        </div>
                      </div>
                      
                      <div class="user-info">
                        <h3 class="user-name">{user.full_name || 'Chưa cập nhật tên'}</h3>
                        <p class="user-email">{user.email}</p>
                      </div>
                      
                      <div class="user-meta">
                        <div class="user-id">ID: {user.id}</div>
                        <div class="user-badge" class:admin={user.is_admin}>
                          {user.is_admin ? 'Admin' : 'Người dùng'}
                        </div>
                      </div>
                      
                      <div class="user-date">
                        <i class="bi bi-calendar3 me-2" aria-hidden="true"></i>
                        {formatDate(user.created_at)}
                      </div>
                      
                      <!-- Hiển thị địa chỉ người dùng -->
                      {#if user.addresses && user.addresses.length > 0}
                        <div class="user-address">
                          <div class="address-header">
                            <i class="bi bi-geo-alt me-2" aria-hidden="true"></i>
                            <span>Địa chỉ ({user.addresses.length})</span>
                          </div>
                          {#if user.addresses.length === 1}
                            <div class="address-item">
                              <div class="address-name">{user.addresses[0].address_name || 'Địa chỉ mặc định'}</div>
                              <div class="address-text">{user.addresses[0].address}</div>
                              {#if user.addresses[0].is_default}
                                <span class="default-badge">Mặc định</span>
                              {/if}
                            </div>
                          {:else}
                            <div class="address-default">
                              {#each user.addresses.filter(addr => addr.is_default) as defaultAddress}
                                <div class="address-item">
                                  <div class="address-name">{defaultAddress.address_name || 'Địa chỉ mặc định'}</div>
                                  <div class="address-text">{defaultAddress.address}</div>
                                  <span class="default-badge">Mặc định</span>
                                </div>
                              {/each}
                              <button class="btn-expand" type="button" on:click={() => alert('Tính năng đang phát triển')} aria-label="Xem thêm địa chỉ">
                                <i class="bi bi-three-dots" aria-hidden="true"></i>
                              </button>
                            </div>
                          {/if}
                        </div>
                      {/if}
                      
                      <div class="user-status" class:active={user.is_active}>
                        <span class="status-dot" aria-hidden="true"></span>
                        <span class="status-text">Hoạt động</span>
                      </div>

                      <!-- Nút chỉnh sửa -->
                      <button 
                        class="btn-edit" 
                        on:click={() => openEditModal(user)}
                        type="button"
                        aria-label="Chỉnh sửa thông tin người dùng"
                      >
                        <i class="bi bi-pencil-square" aria-hidden="true"></i>
                        Chỉnh sửa
                      </button>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Modal chỉnh sửa thông tin người dùng -->
{#if $isEditModalOpen}
  <div 
    class="modal-backdrop" 
    in:fade={{ duration: 200 }} 
    on:click={closeEditModal}
    on:keydown={(e) => e.key === 'Escape' && closeEditModal()}
    tabindex="0"
    role="button"
    aria-label="Đóng modal"
  ></div>
  <div class="modal-container" in:fly={{ y: 20, duration: 300 }}>
    <div 
      class="modal-content" 
      on:click|stopPropagation 
      on:keydown|stopPropagation
      tabindex="-1"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div class="modal-header">
        <h4 class="modal-title" id="modal-title">Chỉnh sửa thông tin người dùng</h4>
        <button 
          type="button" 
          class="btn-close" 
          on:click={closeEditModal}
          aria-label="Đóng hộp thoại"
        >
          <i class="bi bi-x-lg" aria-hidden="true"></i>
        </button>
      </div>
      
      <div class="modal-body">
        {#if $editingUser}
          {#if $updateSuccess}
            <div class="alert alert-success">
              <i class="bi bi-check-circle-fill me-2" aria-hidden="true"></i>
              Cập nhật thông tin người dùng thành công!
            </div>
          {:else if $updateError}
            <div class="alert alert-danger">
              <i class="bi bi-exclamation-triangle-fill me-2" aria-hidden="true"></i>
              {$updateError}
            </div>
          {/if}
          
          <form on:submit|preventDefault={updateUserInfo}>
            <div class="form-group mb-3">
              <label for="email" class="form-label">Email</label>
              <input 
                type="email" 
                id="email" 
                class="form-control" 
                value={$editingUser.email} 
                disabled 
              />
              <small class="form-text text-muted">Email không thể thay đổi</small>
            </div>
            
            <div class="form-group mb-3">
              <label for="fullName" class="form-label">Họ và tên</label>
              <input 
                type="text" 
                id="fullName" 
                class="form-control" 
                bind:value={formData.full_name} 
                placeholder="Nhập họ và tên" 
                required
              />
            </div>
            
            <div class="form-check form-switch mb-3">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isAdmin" 
                bind:checked={formData.is_admin}
              />
              <label class="form-check-label" for="isAdmin">
                Quyền admin
              </label>
            </div>
            
            <div class="form-check form-switch mb-4">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isActive" 
                bind:checked={formData.is_active}
              />
              <label class="form-check-label" for="isActive">
                Trạng thái hoạt động
              </label>
            </div>
            
            <div class="d-grid gap-2">
              <button 
                type="submit" 
                class="btn btn-primary" 
                disabled={$isUpdating}
              >
                {#if $isUpdating}
                  <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Đang cập nhật...
                {:else}
                  <i class="bi bi-check-lg me-2" aria-hidden="true"></i>
                  Lưu thay đổi
                {/if}
              </button>
              <button 
                type="button" 
                class="btn btn-outline-secondary" 
                on:click={closeEditModal}
                disabled={$isUpdating}
              >
                Hủy
              </button>
            </div>
          </form>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  /* Biến màu */
  :root {
    --dark-bg: #0c0c13;
    --card-bg: #15151e;
    --primary-color: #8a7dfd;
    --primary-light: rgba(138, 125, 253, 0.1);
    --text-light: #ffffff;
    --text-muted: #8c8c9e;
    --admin-color: #ff7c7c;
    --active-color: #00cc66;
    --border-color: #252536;
  }

  /* Global styles */
  :global(body) {
    background-color: var(--dark-bg);
    color: var(--text-light);
  }
  
  .bg-dark {
    background-color: var(--dark-bg) !important;
  }
  
  .text-gradient {
    background: linear-gradient(to right, #8a7dfd, #c7a0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2rem;
    letter-spacing: -0.5px;
  }
  
  /* Search box */
  .search-box {
    position: relative;
    width: 100%;
    max-width: 300px;
  }
  
  .search-input {
    width: 100%;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-light);
    padding: 10px 15px 10px 40px;
    border-radius: 8px;
    transition: all 0.3s;
  }
  
  .search-input:focus {
    outline: none;
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(138, 125, 253, 0.3);
    box-shadow: 0 0 0 2px rgba(138, 125, 253, 0.1);
  }
  
  .search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    font-size: 14px;
  }
  
  /* Buttons */
  .btn-primary-soft {
    background-color: rgba(138, 125, 253, 0.15);
    color: var(--primary-color);
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 500;
    transition: all 0.3s;
  }
  
  .btn-primary-soft:hover {
    background-color: rgba(138, 125, 253, 0.25);
    transform: translateY(-1px);
  }
  
  .btn-outline-light {
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--text-light);
    background: transparent;
    border-radius: 8px;
    padding: 10px 16px;
    transition: all 0.3s;
  }
  
  .btn-outline-light:hover {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
  
  /* User card */
  .user-card {
    background-color: var(--card-bg);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    height: 100%;
  }
  
  .user-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
  
  .card-content {
    padding: 1.5rem;
    position: relative;
  }
  
  /* Avatar */
  .avatar-container {
    margin-bottom: 1rem;
  }
  
  .avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    color: white;
  }
  
  /* User info */
  .user-name {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0;
    color: var(--text-light);
  }
  
  .user-email {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin: 0.2rem 0 1rem;
  }
  
  /* User meta */
  .user-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .user-id {
    background-color: rgba(255, 255, 255, 0.1);
    color: var(--text-muted);
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
  }
  
  .user-badge {
    background-color: rgba(138, 125, 253, 0.15);
    color: var(--primary-color);
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-weight: 500;
  }
  
  .user-badge.admin {
    background-color: rgba(255, 124, 124, 0.15);
    color: var(--admin-color);
  }
  
  /* User date */
  .user-date {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
  }
  
  /* User status */
  .user-status {
    display: flex;
    align-items: center;
    font-size: 0.85rem;
    color: var(--text-muted);
    opacity: 0.6;
  }
  
  .user-status.active {
    color: var(--active-color);
    opacity: 1;
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--text-muted);
    margin-right: 6px;
    display: inline-block;
  }
  
  .user-status.active .status-dot {
    background-color: var(--active-color);
    box-shadow: 0 0 0 2px rgba(0, 204, 102, 0.2);
  }
  
  /* User address */
  .user-address {
    margin-bottom: 1rem;
    padding: 0.5rem;
    background-color: rgba(255, 255, 255, 0.02);
    border-radius: 8px;
  }
  
  .address-header {
    display: flex;
    align-items: center;
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
  }
  
  .address-item {
    font-size: 0.85rem;
    margin-top: 0.5rem;
    position: relative;
  }
  
  .address-name {
    font-weight: 500;
    color: var(--text-light);
    margin-bottom: 0.25rem;
  }
  
  .address-text {
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 90%;
  }
  
  .default-badge {
    position: absolute;
    top: 0;
    right: 0;
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    background-color: rgba(138, 125, 253, 0.1);
    color: var(--primary-color);
  }
  
  .address-default {
    position: relative;
  }
  
  .btn-expand {
    background: none;
    border: none;
    color: var(--text-muted);
    padding: 0.25rem;
    position: absolute;
    right: 0;
    bottom: 0;
    font-size: 0.9rem;
    cursor: pointer;
  }
  
  .btn-expand:hover {
    color: var(--text-light);
  }

  /* Nút chỉnh sửa */
  .btn-edit {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background-color: rgba(138, 125, 253, 0.15);
    color: var(--primary-color);
    border: none;
    border-radius: 6px;
    padding: 0.3rem 0.8rem;
    font-size: 0.85rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    transition: all 0.2s;
  }

  .btn-edit:hover {
    background-color: rgba(138, 125, 253, 0.25);
    transform: translateY(-1px);
  }

  /* Modal styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    z-index: 1000;
  }

  .modal-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 500px;
    z-index: 1010;
  }

  .modal-content {
    background-color: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    overflow: hidden;
  }

  .modal-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-light);
  }

  .btn-close {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0.25rem;
    transition: color 0.2s;
  }

  .btn-close:hover {
    color: var(--text-light);
  }

  .modal-body {
    padding: 1.5rem;
  }

  /* Form styles */
  .form-control {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-light);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    transition: all 0.3s;
  }

  .form-control:focus {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(138, 125, 253, 0.3);
    box-shadow: 0 0 0 2px rgba(138, 125, 253, 0.1);
    outline: none;
  }

  .form-label {
    color: var(--text-light);
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .form-text {
    color: var(--text-muted);
    font-size: 0.8rem;
  }

  .form-check-input {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    width: 2.5rem;
    height: 1.25rem;
  }

  .form-check-input:checked {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
  }

  .form-check-label {
    color: var(--text-light);
    font-size: 0.95rem;
    padding-left: 0.5rem;
  }

  /* Alert styles */
  .alert {
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
  }

  .alert-success {
    background-color: rgba(0, 204, 102, 0.15);
    color: #00cc66;
    border: 1px solid rgba(0, 204, 102, 0.2);
  }

  .alert-danger {
    background-color: rgba(255, 76, 76, 0.15);
    color: #ff4c4c;
    border: 1px solid rgba(255, 76, 76, 0.2);
  }

  /* Button styles */
  .btn {
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-weight: 500;
    transition: all 0.3s;
  }

  .btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #7a6fe4;
    border-color: #7a6fe4;
    transform: translateY(-2px);
  }

  .btn-outline-secondary {
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--text-light);
    background: transparent;
  }

  .btn-outline-secondary:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .btn:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
  
  /* Responsive */
  @media (max-width: 767.98px) {
    .text-gradient {
      font-size: 1.75rem;
    }
  }
</style> 