import { defineStore } from 'pinia';
import authService from '../services/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
  }),

  getters: {
    currentUser: (state) => state.user,
    hasPermission: (state) => (permission) => {
      if (!state.user) return false;
      // Admin role has all permissions, owner role also has all
      if (state.user.role === 'admin' || state.user.role === 'owner' || state.user.role === 'SUPER_ADMIN') {
        return true;
      }
      return state.user.permissions?.includes(permission) || false;
    },
    hasRole: (state) => (role) => {
      if (!state.user) return false;
      return state.user.role === role || state.user.role === 'SUPER_ADMIN';
    },
  },

  actions: {
    async login(credentials) {
      this.loading = true;
      try {
        const response = await authService.login(credentials);
        this.user = response.user || authService.getCurrentUser();
        this.isAuthenticated = true;
        return response;
      } catch (error) {
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await authService.logout();
      } finally {
        this.user = null;
        this.isAuthenticated = false;
      }
    },

    async checkAuth() {
      try {
        // Wrap in try-catch to ensure it never throws and blocks render
        if (authService.isAuthenticated()) {
          const user = authService.getCurrentUser();
          if (user) {
            this.user = user;
            this.isAuthenticated = true;
          } else {
            // Token exists but no user data, clear auth state
            this.user = null;
            this.isAuthenticated = false;
          }
        } else {
          this.user = null;
          this.isAuthenticated = false;
        }
      } catch (error) {
        console.error('Check auth error:', error);
        // Ensure state is set even on error to prevent blocking
        this.user = null;
        this.isAuthenticated = false;
      }
    },

    setUser(user) {
      this.user = user;
      this.isAuthenticated = !!user;
    },
  },
});

