import api from './api';

class AuthService {
  async login(credentials) {
    try {
      // API client returns data directly (not response.data)
      const responseData = await api.post('/api/auth/login', credentials);
      
      // Handle nested response structure from backend: {success, message, data: {...}}
      const data = responseData.data || responseData;
      
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
        }
      }
      
      return {
        ...data,
        success: responseData.success !== undefined ? responseData.success : true,
        message: responseData.message || 'Đăng nhập thành công'
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout() {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) throw new Error('No refresh token');
      
      // Use Authorization header instead of body
      const response = await api.post('/api/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      });
      
      // Handle nested response structure
      const data = response.data.data || response.data;
      
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      
      return {
        ...data,
        success: response.data.success,
        message: response.data.message
      };
    } catch (error) {
      console.error('Refresh token error:', error);
      this.logout();
      throw error;
    }
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user');
      if (!userStr) return null;
      return JSON.parse(userStr);
    } catch (error) {
      console.error('Error parsing user from localStorage:', error);
      // Clear invalid user data
      localStorage.removeItem('user');
      return null;
    }
  }

  getToken() {
    return localStorage.getItem('access_token');
  }

  hasPermission(permission) {
    const user = this.getCurrentUser();
    if (!user || !user.permissions) return false;
    return user.permissions.includes(permission) || user.role === 'SUPER_ADMIN';
  }

  hasRole(role) {
    const user = this.getCurrentUser();
    return user?.role === role || user?.role === 'SUPER_ADMIN';
  }
}

export default new AuthService();

