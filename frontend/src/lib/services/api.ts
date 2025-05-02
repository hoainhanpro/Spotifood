/**
 * Dịch vụ xử lý các request API đến backend
 */

const API_URL = 'http://localhost:8000';

/**
 * Gửi request đến API
 * @param endpoint - Đường dẫn API endpoint
 * @param options - Các tùy chọn fetch
 * @returns Dữ liệu phản hồi đã được parse
 */
export async function fetchApi<T = any>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
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
    return text ? JSON.parse(text) : {};
  } catch (error) {
    console.error('Lỗi kết nối API:', error);
    throw error;
  }
}

/**
 * Interface cho response kết nối
 */
export interface ConnectionResponse {
  message: string;
  status?: string;
}

/**
 * Test kết nối đến backend
 * @returns Thông tin kết nối
 */
export async function testConnection(): Promise<ConnectionResponse> {
  return await fetchApi<ConnectionResponse>('/api/test-connection');
}

export default {
  fetchApi,
  testConnection,
  // Thêm các hàm API khác ở đây
}; 