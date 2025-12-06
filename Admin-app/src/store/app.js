import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarOpen: true,
    theme: 'dark',
    notifications: [],
    settings: {
      platformName: 'Digital Utopia',
      platformURL: 'https://digitalutopia.com',
      supportEmail: 'support@digitalutopia.com',
      timezone: 'UTC',
      defaultLanguage: 'en',
      maintenanceMode: false,
      allowRegistrations: true,
    },
  }),

  getters: {
    isSidebarOpen: (state) => state.sidebarOpen,
  },

  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },

    setSidebarOpen(open) {
      this.sidebarOpen = open;
    },

    setTheme(theme) {
      this.theme = theme;
    },

    async fetchSettings() {
      // TODO: Fetch from API
      // const response = await api.get('/api/admin/settings');
      // this.settings = response;
    },

    async updateSettings(settings) {
      // TODO: Update via API
      // const response = await api.put('/api/admin/settings', settings);
      this.settings = { ...this.settings, ...settings };
    },
  },
});

