import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "LuxeTrade",
        short_name: "LuxeTrade",
        theme_color: "#0b0b15",
        background_color: "#0b0b15",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "/vite.svg", sizes: "192x192", type: "image/svg+xml" },
          { src: "/vite.svg", sizes: "512x512", type: "image/svg+xml" },
        ],
      },
    }),
  ],
  server: {
    port: 3002,
  },
});
