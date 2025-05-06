<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { fly, fade, slide } from 'svelte/transition';
  
  // Store cho trạng thái admin
  const user = writable<any>(null);
  const isSidebarOpen = writable<boolean>(true);
  const isMobile = writable<boolean>(false);
  
  // Toggle sidebar
  function toggleSidebar() {
    isSidebarOpen.update(open => !open);
  }
  
  // Kiểm tra nếu đang ở mobile view
  function checkMobile() {
    isMobile.set(window.innerWidth < 992);
    if (window.innerWidth < 992) {
      isSidebarOpen.set(false);
    } else {
      isSidebarOpen.set(true);
    }
  }
  
  // Cài đặt menu items
  const menuItems = [
    { id: 'dashboard', name: 'Dashboard', url: '/admin', icon: 'bi-grid-1x2-fill' },
    { id: 'restaurants', name: 'Quản lý nhà hàng', url: '/admin/restaurants', icon: 'bi-shop' },
    { id: 'menus', name: 'Quản lý menu', url: '/admin/menus', icon: 'bi-card-list' },
    { id: 'orders', name: 'Quản lý đơn hàng', url: '/admin/orders', icon: 'bi-bag-check-fill' },
    { id: 'promotions', name: 'Quản lý khuyến mãi', url: '/admin/promotions', icon: 'bi-tag-fill' },
    { id: 'addons', name: 'Quản lý món gọi kèm', url: '/admin/addons', icon: 'bi-plus-circle-fill' },
    { id: 'users', name: 'Quản lý người dùng', url: '/admin/users', icon: 'bi-people-fill' },
    { id: 'delivery', name: 'Quản lý giao hàng', url: '/admin/delivery', icon: 'bi-truck' }
  ];
  
  // Active menu item
  let activeMenuItem = menuItems[0]; // Gán giá trị mặc định
  
  $: {
    console.log('Current path:', $page.url.pathname);
    activeMenuItem = menuItems.find(item => {
      const isActive = $page.url.pathname === item.url || 
                      ($page.url.pathname.startsWith(item.url) && item.url !== '/admin');
      console.log(`Checking ${item.url}: ${isActive}`);
      return isActive;
    }) || menuItems[0];
  }
  
  // Đăng xuất
  function logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      goto('/login');
    }
  }
  
  // Lấy thông tin user từ localStorage
  onMount(() => {
    const init = async () => {
      checkMobile();
      window.addEventListener('resize', checkMobile);
      
      // Kiểm tra nếu đã đăng nhập và có quyền admin
      const storedUser = localStorage.getItem('user');
      const storedToken = localStorage.getItem('token');
      
      if (!storedToken) {
        goto('/login');
        return;
      }
      
      try {
        let userData;
        
        // Nếu có token nhưng không có dữ liệu user, gọi API để lấy thông tin
        if (!storedUser) {
          console.log('Có token nhưng không có dữ liệu user, gọi API lấy thông tin');
          
          try {
            const response = await fetch('http://localhost:8000/api/users/me', {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${storedToken}`
              }
            });
            
            if (response.ok) {
              userData = await response.json();
              
              // Lưu user vào localStorage để lần sau không cần gọi API nữa
              localStorage.setItem('user', JSON.stringify(userData));
            } else {
              console.error('Không thể lấy thông tin user từ API');
              goto('/login');
              return;
            }
          } catch (error) {
            console.error('Lỗi khi gọi API lấy thông tin user:', error);
            goto('/login');
            return;
          }
        } else {
          // Parse dữ liệu user từ localStorage
          userData = JSON.parse(storedUser);
        }
        
        // Lưu vào store để sử dụng trong các component
        user.set(userData);
        console.log('User Data:', userData);
        
        // Bây giờ đã có userData, kiểm tra role nếu cần
        if (userData.role !== 'admin') {
          console.log('Không có quyền admin, chuyển hướng về trang chủ');
          goto('/');
          return;
        }
        
      } catch (error) {
        console.error('Lỗi khi xử lý dữ liệu user:', error);
        goto('/login');
        return;
      }
    };
    
    init();
    
    // Cleanup listener khi component unmount
    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  });
</script>

<div class="admin-layout">
  <!-- Sidebar -->
  <aside 
    class="sidebar {$isSidebarOpen ? 'open' : 'closed'}" 
    transition:slide|local={{ duration: 300, axis: 'x' }}
  >
    <div class="sidebar-header">
      <div class="logo-container">
        <h2 class="logo">SPOTIFOOD</h2>
        <span class="admin-badge">ADMIN</span>
      </div>
      
      {#if $isMobile}
        <button class="toggle-button" on:click={toggleSidebar} aria-label="Đóng menu">
          <i class="bi bi-x-lg"></i>
        </button>
      {/if}
    </div>
    
    <div class="sidebar-content">
      <nav class="sidebar-nav">
        <ul class="nav-list">
          {#each menuItems as menuItem}
            <li 
              class="nav-item {activeMenuItem.id === menuItem.id ? 'active' : ''}"
              in:fly|local={{ y: 5, duration: 200, delay: 100 * menuItems.indexOf(menuItem) }}
            >
              <a 
                href={menuItem.url} 
                class="nav-link"
                aria-current={activeMenuItem.id === menuItem.id ? "page" : undefined}
              >
                <i class="bi {menuItem.icon} menu-icon"></i>
                <span class="menu-text">{menuItem.name}</span>
                {#if activeMenuItem.id === menuItem.id}
                  <span class="active-indicator" transition:fade|local></span>
                {/if}
              </a>
            </li>
          {/each}
        </ul>
      </nav>
    </div>
    
    <div class="sidebar-footer">
      <div class="user-info">
        {#if $user}
          <div class="avatar">
            <span>{$user.full_name ? $user.full_name.substring(0, 2).toUpperCase() : ($user.email.substring(0, 2).toUpperCase())}</span>
          </div>
          <div class="user-details" class:hidden={!$isSidebarOpen}>
            <p class="user-name">{$user.full_name || 'Admin'}</p>
            <p class="user-email">{$user.email}</p>
          </div>
        {/if}
      </div>
      
      <button class="logout-button" on:click={logout}>
        <i class="bi bi-box-arrow-right"></i>
        <span class="logout-text" class:hidden={!$isSidebarOpen}>Đăng xuất</span>
      </button>
    </div>
  </aside>
  
  <!-- Main content -->
  <main class="main-content {$isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}">
    <header class="content-header">
      {#if $isMobile && !$isSidebarOpen}
        <button class="toggle-button" on:click={toggleSidebar} aria-label="Mở menu">
          <i class="bi bi-list"></i>
        </button>
      {/if}
      
      <h1 class="page-title">{activeMenuItem.name}</h1>
      
      {#if !$isMobile}
        <button class="collapse-button" on:click={toggleSidebar} aria-label={$isSidebarOpen ? 'Thu gọn sidebar' : 'Mở rộng sidebar'}>
          <i class="bi {$isSidebarOpen ? 'bi-arrow-left-square-fill' : 'bi-arrow-right-square-fill'}"></i>
        </button>
      {/if}
    </header>
    
    <div class="content">
      <slot></slot>
    </div>
  </main>
  
  <!-- Backdrop overlay cho mobile -->
  {#if $isMobile && $isSidebarOpen}
    <button
      type="button"
      class="backdrop"
      aria-label="Đóng menu"
      on:click={toggleSidebar}
      transition:fade|local={{ duration: 200 }}
    ></button>
  {/if}
</div>

<style>
  /* Biến CSS */
  :root {
    --primary-gradient: linear-gradient(to right, #8a7dfd, #c7a0ff);
    --primary-color: #8a7dfd;
    --primary-light: rgba(138, 125, 253, 0.15);
    --primary-dark: #6a5fed;
    --dark-bg: #121212;
    --darker-bg: #0c0c13;
    --sidebar-bg: #15151e;
    --sidebar-width: 260px;
    --sidebar-collapsed-width: 80px;
    --header-height: 70px;
    --text-light: #ffffff;
    --text-muted: #8c8c9e;
    --border-color: #252536;
    --hover-bg: rgba(255, 255, 255, 0.05);
    --transition-duration: 300ms;
  }
  
  /* Layout styles */
  .admin-layout {
    display: flex;
    width: 100%;
    min-height: 100vh;
    background-color: var(--dark-bg);
    color: var(--text-light);
    position: relative;
  }
  
  /* Sidebar styles */
  .sidebar {
    background-color: var(--sidebar-bg);
    width: var(--sidebar-width);
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    transition: width var(--transition-duration) ease, transform var(--transition-duration) ease;
    box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
  }
  
  .sidebar.closed {
    width: var(--sidebar-collapsed-width);
  }
  
  /* Logo styles */
  .sidebar-header {
    padding: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);
  }
  
  .logo-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .logo {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
  }
  
  .admin-badge {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    margin-top: -5px;
    letter-spacing: 2px;
  }
  
  /* Navigation styles */
  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1rem 0;
  }
  
  .nav-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .nav-item {
    position: relative;
    margin: 0.25rem 0.75rem;
    border-radius: 10px;
    transition: background-color 0.3s;
  }
  
  .nav-item:hover {
    background-color: var(--hover-bg);
  }
  
  .nav-item.active {
    background-color: var(--primary-light);
  }
  
  .nav-link {
    display: flex;
    align-items: center;
    padding: 0.875rem 1.2rem;
    color: var(--text-muted);
    transition: color 0.3s;
    text-decoration: none;
    white-space: nowrap;
    border-radius: 10px;
    position: relative;
  }
  
  .nav-item.active .nav-link {
    color: var(--primary-color);
    font-weight: 500;
  }
  
  .menu-icon {
    font-size: 1.2rem;
    margin-right: 1rem;
    min-width: 24px;
    text-align: center;
  }
  
  .active-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    height: 70%;
    width: 4px;
    background: var(--primary-gradient);
    border-radius: 0 4px 4px 0;
  }
  
  /* Sidebar footer styles */
  .sidebar-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 0.875rem;
  }
  
  .avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: var(--primary-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: white;
    font-size: 1rem;
    flex-shrink: 0;
  }
  
  .user-details {
    overflow: hidden;
    transition: opacity var(--transition-duration);
  }
  
  .user-name {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .user-email {
    margin: 0;
    font-size: 0.8rem;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .logout-button {
    display: flex;
    align-items: center;
    gap: 0.875rem;
    padding: 0.6rem 1rem;
    background-color: rgba(255, 76, 76, 0.1);
    color: #ff4c4c;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .logout-button:hover {
    background-color: rgba(255, 76, 76, 0.2);
  }
  
  /* Main content styles */
  .main-content {
    flex: 1;
    margin-left: var(--sidebar-width);
    transition: margin-left var(--transition-duration) ease;
    width: calc(100% - var(--sidebar-width));
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  .main-content.sidebar-closed {
    margin-left: var(--sidebar-collapsed-width);
    width: calc(100% - var(--sidebar-collapsed-width));
  }
  
  .content-header {
    height: var(--header-height);
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);
  }
  
  .page-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
  }
  
  /* Buttons */
  .toggle-button, .collapse-button {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 1.25rem;
    cursor: pointer;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    transition: background-color 0.3s, color 0.3s;
  }
  
  .toggle-button:hover, .collapse-button:hover {
    background-color: var(--hover-bg);
    color: var(--text-light);
  }
  
  /* Backdrop overlay */
  .backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    z-index: 999;
    backdrop-filter: blur(4px);
  }
  
  /* Utility classes */
  .hidden {
    opacity: 0;
    visibility: hidden;
  }
  
  /* Collapsed sidebar styles */
  .sidebar.closed .menu-text,
  .sidebar.closed .user-details,
  .sidebar.closed .logout-text,
  .sidebar.closed .admin-badge {
    display: none;
  }
  
  .sidebar.closed .logo {
    font-size: 1.2rem;
  }
  
  .sidebar.closed .sidebar-header,
  .sidebar.closed .sidebar-footer {
    justify-content: center;
    padding: 1.5rem 0.75rem;
  }
  
  .sidebar.closed .nav-link {
    justify-content: center;
    padding: 0.875rem;
  }
  
  .sidebar.closed .menu-icon {
    margin-right: 0;
  }
  
  .sidebar.closed .user-info {
    justify-content: center;
  }
  
  .sidebar.closed .logout-button {
    width: 42px;
    height: 42px;
    justify-content: center;
    padding: 0;
  }
  
  /* Responsive styles */
  @media (max-width: 991.98px) {
    .sidebar {
      transform: translateX(-100%);
      box-shadow: none;
    }
    
    .sidebar.open {
      transform: translateX(0);
      box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
    }
    
    .main-content {
      margin-left: 0;
      width: 100%;
    }
    
    .main-content.sidebar-open {
      margin-left: 0;
    }
    
    .main-content.sidebar-closed {
      margin-left: 0;
      width: 100%;
    }
    
    .sidebar-header {
      justify-content: space-between;
    }
    
    .content-header {
      padding: 0 1.5rem;
    }
    
    .page-title {
      font-size: 1.25rem;
    }
  }
</style> 