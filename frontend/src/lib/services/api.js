/**
 * Dịch vụ xử lý các request API đến backend
 */

const API_URL = 'http://localhost:8000';

/**
 * @typedef {'include' | 'same-origin' | 'omit'} RequestCredentials
 */

/**
 * Gửi request đến API
 * @param {string} endpoint - Đường dẫn API endpoint
 * @param {RequestInit} options - Các tùy chọn fetch
 * @returns {Promise<any>} Dữ liệu phản hồi đã được parse
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  
  /** @type {RequestInit} */
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  };

  /** @type {RequestInit} */
  const fetchOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {}),
    },
  };

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
}

/**
 * Interface cho response kết nối
 * @typedef {Object} ConnectionResponse
 * @property {string} message - Thông báo kết nối
 * @property {string} [status] - Trạng thái kết nối
 */

/**
 * Test kết nối đến backend
 * @returns {Promise<ConnectionResponse>} Thông tin kết nối
 */
export async function testConnection() {
  return await fetchApi('/api/test-connection');
}

export default {
  testConnection,
  // Thêm các hàm API khác ở đây
}; 