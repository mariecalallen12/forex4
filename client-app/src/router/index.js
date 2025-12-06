import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import LoginPage from '../views/LoginPage.vue';
import ForgotPasswordPage from '../views/ForgotPasswordPage.vue';
import TradingDashboard from '../views/TradingDashboard.vue';
import MarketView from '../views/MarketView.vue';
import TestPage from '../views/TestPage.vue';
import PersonalAreaLayout from '../layouts/PersonalAreaLayout.vue';

// Lazy load personal area views
const DashboardView = () => import('../views/personal/DashboardView.vue');
const DepositView = () => import('../views/personal/DepositView.vue');
const WithdrawView = () => import('../views/personal/WithdrawView.vue');
const ProfileView = () => import('../views/personal/ProfileView.vue');
const WalletView = () => import('../views/personal/WalletView.vue');
const ExchangeRatesView = () => import('../views/personal/ExchangeRatesView.vue');
const TransactionHistoryView = () => import('../views/personal/TransactionHistoryView.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/test',
    name: 'Test',
    component: TestPage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordPage,
    meta: { requiresGuest: true },
  },
  {
    path: '/trading',
    name: 'TradingDashboard',
    component: TradingDashboard,
  },
  {
    path: '/market',
    name: 'Market',
    component: MarketView,
  },
  {
    path: '/education',
    name: 'Education',
    component: HomePage,
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: HomePage,
  },
  // Personal Area Routes
  {
    path: '/personal',
    component: PersonalAreaLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/personal/dashboard',
      },
      {
        path: 'dashboard',
        name: 'PersonalDashboard',
        component: DashboardView,
        meta: { title: 'Tổng Quan' },
      },
      {
        path: 'deposit',
        name: 'Deposit',
        component: DepositView,
        meta: { title: 'Nạp Tiền' },
      },
      {
        path: 'withdraw',
        name: 'Withdraw',
        component: WithdrawView,
        meta: { title: 'Rút Tiền' },
      },
      {
        path: 'wallet',
        name: 'Wallet',
        component: WalletView,
        meta: { title: 'Ví Điện Tử' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: ProfileView,
        meta: { title: 'Thông Tin Cá Nhân' },
      },
      {
        path: 'rates',
        name: 'ExchangeRates',
        component: ExchangeRatesView,
        meta: { title: 'Tỷ Giá Hối Đoái' },
      },
      {
        path: 'transactions',
        name: 'TransactionHistory',
        component: TransactionHistoryView,
        meta: { title: 'Lịch Sử Giao Dịch' },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Route guard for authentication
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);
  const token = localStorage.getItem('auth_token');
  
  // Redirect to home if already logged in and trying to access guest routes
  if (requiresGuest && token) {
    next({ name: 'PersonalDashboard' });
    return;
  }
  
  // Redirect to login if requires auth but no token
  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
    return;
  }
  
  next();
});

export default router;

