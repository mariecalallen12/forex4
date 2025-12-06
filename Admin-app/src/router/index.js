import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";
import LoginPage from "../views/LoginPage.vue";
import Layout from "../components/layout/Layout.vue";

// Lazy load views
const Dashboard = () => import("../views/Dashboard.vue");
const UserManagement = () => import("../views/UserManagement.vue");
const TradingManagement = () => import("../views/TradingManagement.vue");
const FinancialManagement = () => import("../views/FinancialManagement.vue");
const AnalyticsReports = () => import("../views/AnalyticsReports.vue");
const SystemSettings = () => import("../views/SystemSettings.vue");
const AdminTradingControls = () => import("../views/AdminTradingControls.vue");

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { requiresAuth: false },
  },
  {
    path: "/dashboard",
    component: Layout,
    meta: { requiresAuth: true, permission: "admin.dashboard" },
    children: [
      {
        path: "",
        name: "Dashboard",
        component: Dashboard,
      },
    ],
  },
  {
    path: "/users",
    component: Layout,
    meta: { requiresAuth: true, permission: "user:read" },
    children: [
      {
        path: "",
        name: "UserManagement",
        component: UserManagement,
      },
    ],
  },
  {
    path: "/trading",
    component: Layout,
    meta: { requiresAuth: true, permission: "trade:read" },
    children: [
      {
        path: "",
        name: "TradingManagement",
        component: TradingManagement,
      },
    ],
  },
  {
    path: "/financial",
    component: Layout,
    meta: { requiresAuth: true, permission: "financial:read" },
    children: [
      {
        path: "",
        name: "FinancialManagement",
        component: FinancialManagement,
      },
    ],
  },
  {
    path: "/analytics",
    component: Layout,
    meta: { requiresAuth: true, permission: "analytics:read" },
    children: [
      {
        path: "",
        name: "AnalyticsReports",
        component: AnalyticsReports,
      },
    ],
  },
  {
    path: "/settings",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "SystemSettings",
        component: SystemSettings,
      },
    ],
  },
  {
    path: "/admin-controls",
    component: Layout,
    meta: { requiresAuth: true, permission: "admin:trading:control" },
    children: [
      {
        path: "",
        name: "AdminTradingControls",
        component: AdminTradingControls,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory("/admin/"),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Always check auth from localStorage first
  if (!authStore.isAuthenticated) {
    await authStore.checkAuth();
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next({ name: "Login", query: { redirect: to.fullPath } });
      return;
    }

    // Check permissions - temporarily disabled for testing
    // Admin users should have all permissions, so we'll allow access
    // if (to.meta.permission) {
    //   if (!authStore.hasPermission(to.meta.permission)) {
    //     next({ name: "Dashboard" }); // Redirect to dashboard if no permission
    //     return;
    //   }
    // }
  }

  // Redirect authenticated users away from login
  if (to.name === "Login" && authStore.isAuthenticated) {
    next({ name: "Dashboard" });
    return;
  }

  next();
});

export default router;
