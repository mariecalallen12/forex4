import { createApp } from "vue";
import { createPinia } from "pinia";
import "./style.css";
import "./styles/trading.css";
import "./styles/market.css";
import "./styles/themes.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "remixicon/fonts/remixicon.css";
import "swiper/swiper-bundle.css";
import "aos/dist/aos.css";
import { i18n } from "./i18n";
import router from "./router";
import App from "./App.vue";
import { useWebSocketStore } from "./stores/websocket";

if ("serviceWorker" in navigator) {
  import("virtual:pwa-register").then(({ registerSW }) => {
    registerSW({ immediate: true });
  });
}

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(i18n);
app.use(router);

// Initialize WebSocket connection (only if store is available)
try {
  const wsStore = useWebSocketStore();
  wsStore.connect(import.meta.env.VITE_WS_URL || 'http://localhost:8000');
} catch (error) {
  console.warn('WebSocket initialization skipped:', error);
}

app.mount("#app");
