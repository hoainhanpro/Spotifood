/**
 * Service xử lý xác thực đăng nhập
 */
import { fetchApi } from './api';
import { writable, type Writable } from 'svelte/store';

// Interfaces
interface User {
  id: string;
  email: string;
  name?: string;
  role?: string;
  [key: string]: any;
}

interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

// Store lưu trữ trạng thái user
export const user: Writable<User | null> = writable(null);
export const isAuthenticated: Writable<boolean> = writable(false);
export const token: Writable<string | null> = writable(null);

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

/**
 * Đăng nhập người dùng
 * @param credentials - Thông tin đăng nhập
 * @returns Thông tin xác thực
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  try {
    const { rememberMe, ...loginData } = credentials;
    
    const response = await fetchApi<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(loginData)
    });
    
    if (response.access_token) {
      // Lưu token
      token.set(response.access_token);
      
      // Lấy thông tin user từ token nếu cần
      try {
        const userInfo = await fetchApi<User>('/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${response.access_token}`
          }
        });
        
        if (userInfo) {
          user.set(userInfo);
          isAuthenticated.set(true);
          
          if (rememberMe && typeof window !== 'undefined') {
            localStorage.setItem('user', JSON.stringify(userInfo));
            localStorage.setItem('token', response.access_token);
          }
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

/**
 * Đăng xuất người dùng
 */
export async function logout(): Promise<void> {
  try {
    const currentToken = token;
    if (currentToken) {
      await fetchApi('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${currentToken}`
        }
      });
    }
  } catch (error) {
    console.error('Lỗi đăng xuất:', error);
  } finally {
    // Xóa thông tin người dùng khỏi store và localStorage
    user.set(null);
    token.set(null);
    isAuthenticated.set(false);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
  }
}

/**
 * Kiểm tra phiên đăng nhập hiện tại
 * @returns Trạng thái đăng nhập
 */
export async function checkAuth(): Promise<boolean> {
  try {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) return false;
    
    const response = await fetchApi('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${currentToken}`
      }
    });
    
    if (response) {
      user.set(response);
      token.set(currentToken);
      isAuthenticated.set(true);
      return true;
    }
    
    return false;
  } catch (error) {
    user.set(null);
    token.set(null);
    isAuthenticated.set(false);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
    return false;
  }
}

export default {
  login,
  logout,
  checkAuth,
  user,
  isAuthenticated,
  token
}; 