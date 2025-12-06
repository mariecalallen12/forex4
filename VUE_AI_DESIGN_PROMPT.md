# AI Design Prompt - Digital Utopia Platform Client App Vue.js

**Phiên Bản:** 2.0.0  
**Ngày Tạo:** 2025-12-05  
**Tác Giả:** MiniMax Agent  
**Mục Đích:** Hướng dẫn AI thiết kế giao diện Vue.js 3 hoàn chỉnh cho Client App

---

## 🎯 MISSION STATEMENT

Bạn là một AI Design Expert chuyên về Vue.js 3 và Fintech/Trading applications. Nhiệm vụ của bạn là thiết kế toàn bộ giao diện người dùng (UI/UX) cho **Digital Utopia Platform Client App** - một ứng dụng web enterprise-grade dành cho khách hàng người dùng. Ứng dụng này cung cấp các dịch vụ công nghệ và trading platforms với yêu cầu thiết kế professional, secure, và user-friendly.

---

## 🏗️ TECHNICAL FOUNDATION

### Core Technology Stack
```javascript
// Frontend Architecture
Vue.js 3 (Composition API)
TypeScript
Tailwind CSS + DaisyUI
Pinia State Management
Vue Router 4
Vite Build Tool
PWA Ready
WebSocket Integration
```

### Backend Integration Requirements
```javascript
// API Integration
72 FastAPI endpoints đã được verify
OAuth 2.0 / JWT Authentication
Real-time data feeds
File upload system
RESTful API design patterns
```

---

## 🎨 DESIGN SYSTEM FOUNDATION

### Color Palette System (Based on Research)
```css
/* Primary Colors - Trust & Professional */
--primary-blue: #0066cc;          /* Main brand color */
--primary-blue-light: #3385d6;    /* Hover states */
--primary-blue-dark: #004499;     /* Active states */

/* Secondary Colors - Success & Growth */
--success-green: #00cc66;         /* Positive actions */
--success-green-light: #33d685;   /* Success backgrounds */
--warning-orange: #ff6600;        /* Call-to-action */
--warning-orange-light: #ff8833;  /* Warning states */

/* Neutral Colors - Base */
--neutral-50: #f8f9fa;            /* Light backgrounds */
--neutral-100: #e9ecef;           /* Card backgrounds */
--neutral-200: #dee2e6;           /* Borders */
--neutral-300: #ced4da;           /* Disabled states */
--neutral-400: #adb5bd;           /* Placeholder text */
--neutral-500: #6c757d;           /* Secondary text */
--neutral-600: #495057;           /* Primary text */
--neutral-700: #343a40;           /* Headings */
--neutral-800: #212529;           /* Dark text */

/* Semantic Colors */
--error-red: #dc3545;             /* Error states */
--error-red-light: #f8d7da;       /* Error backgrounds */
--info-blue: #0dcaf0;             /* Information */
--info-blue-light: #cff4fc;       /* Info backgrounds */
```

### Typography System
```css
/* Font Stack */
--font-primary: 'Inter', 'Roboto', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Typography Scale */
--text-xs: 0.75rem;      /* 12px - Labels */
--text-sm: 0.875rem;     /* 14px - Body small */
--text-base: 1rem;       /* 16px - Body regular */
--text-lg: 1.125rem;     /* 18px - Body large */
--text-xl: 1.25rem;      /* 20px - Heading 6 */
--text-2xl: 1.5rem;      /* 24px - Heading 5 */
--text-3xl: 1.875rem;    /* 30px - Heading 4 */
--text-4xl: 2.25rem;     /* 36px - Heading 3 */
--text-5xl: 3rem;        /* 48px - Heading 2 */
--text-6xl: 3.75rem;     /* 60px - Heading 1 */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Spacing System
```css
/* Spacing Scale (4px base) */
--space-1: 0.25rem;      /* 4px */
--space-2: 0.5rem;       /* 8px */
--space-3: 0.75rem;      /* 12px */
--space-4: 1rem;         /* 16px */
--space-5: 1.25rem;      /* 20px */
--space-6: 1.5rem;       /* 24px */
--space-8: 2rem;         /* 32px */
--space-10: 2.5rem;      /* 40px */
--space-12: 3rem;        /* 48px */
--space-16: 4rem;        /* 64px */
--space-20: 5rem;        /* 80px */
--space-24: 6rem;        /* 96px */
```

### Component Dimensions
```css
/* Button Sizes */
--btn-sm: 2rem;          /* 32px height */
--btn-md: 2.5rem;        /* 40px height */
--btn-lg: 3rem;          /* 48px height */
--btn-xl: 3.5rem;        /* 56px height */

/* Input Heights */
--input-sm: 2rem;        /* 32px */
--input-md: 2.5rem;      /* 40px */
--input-lg: 3rem;        /* 48px */

/* Border Radius */
--radius-sm: 0.25rem;    /* 4px */
--radius-md: 0.5rem;     /* 8px */
--radius-lg: 0.75rem;    /* 12px */
--radius-xl: 1rem;       /* 16px */
--radius-2xl: 1.5rem;    /* 24px */
--radius-full: 9999px;   /* Full rounded */
```

---

## 🏗️ APPLICATION STRUCTURE

### Page Hierarchy & Routing
```javascript
// Main Application Routes
const routes = [
  // Public Routes
  { path: '/', name: 'home', component: () => import('@/views/HomePage.vue') },
  { path: '/auth/selection', name: 'auth-selection', component: () => import('@/views/auth/AuthSelection.vue') },
  { path: '/auth/google', name: 'google-auth', component: () => import('@/views/auth/GoogleAuth.vue') },
  { path: '/auth/microsoft', name: 'microsoft-auth', component: () => import('@/views/auth/MicrosoftAuth.vue') },
  { path: '/auth/success', name: 'auth-success', component: () => import('@/views/auth/AuthSuccess.vue') },
  { path: '/auth/error', name: 'auth-error', component: () => import('@/views/auth/AuthError.vue') },
  
  // Service Registration
  { path: '/service/registration', name: 'service-registration', component: () => import('@/views/service/ServiceRegistration.vue') },
  { path: '/service/selection', name: 'service-selection', component: () => import('@/views/service/ServiceSelection.vue') },
  { path: '/service/configuration', name: 'service-configuration', component: () => import('@/views/service/ServiceConfiguration.vue') },
  { path: '/service/compliance', name: 'service-compliance', component: () => import('@/views/service/ServiceCompliance.vue') },
  { path: '/service/payment', name: 'service-payment', component: () => import('@/views/service/ServicePayment.vue') },
  { path: '/service/success', name: 'service-success', component: () => import('@/views/service/ServiceSuccess.vue') },
  
  // Protected Routes (Require Authentication)
  { path: '/dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: () => import('@/views/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/settings', name: 'settings', component: () => import('@/views/Settings.vue'), meta: { requiresAuth: true } },
  { path: '/legal/terms', name: 'terms', component: () => import('@/views/legal/Terms.vue') },
  { path: '/legal/privacy', name: 'privacy', component: () => import('@/views/legal/Privacy.vue') },
  { path: '/legal/cookie-policy', name: 'cookie-policy', component: () => import('@/views/legal/CookiePolicy.vue') },
  { path: '/support', name: 'support', component: () => import('@/views/Support.vue') },
  { path: '/documentation', name: 'documentation', component: () => import('@/views/Documentation.vue') },
  
  // Trading/Financial Routes
  { path: '/trading', name: 'trading', component: () => import('@/views/trading/TradingDashboard.vue'), meta: { requiresAuth: true } },
  { path: '/portfolio', name: 'portfolio', component: () => import('@/views/portfolio/Portfolio.vue'), meta: { requiresAuth: true } },
  { path: '/wallet', name: 'wallet', component: () => import('@/views/wallet/Wallet.vue'), meta: { requiresAuth: true } },
  { path: '/analytics', name: 'analytics', component: () => import('@/views/analytics/Analytics.vue'), meta: { requiresAuth: true } },
  
  // Error Routes
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFound.vue') }
];
```

### Component Architecture
```javascript
// Component Structure
components/
├── layout/
│   ├── AppHeader.vue           // Main navigation header
│   ├── AppFooter.vue           // Footer with legal links
│   ├── AppSidebar.vue          // Side navigation (desktop)
│   ├── AppMobileMenu.vue       // Mobile menu overlay
│   └── AppBreadcrumbs.vue      // Breadcrumb navigation
│
├── auth/
│   ├── AuthLayout.vue          // Auth page wrapper
│   ├── GoogleLoginButton.vue   // Google OAuth button
│   ├── MicrosoftLoginButton.vue// Microsoft OAuth button
│   ├── EmailLoginForm.vue      // Email/OTP login form
│   ├── AuthSuccessModal.vue    // Success modal
│   └── AuthErrorAlert.vue      // Error alert component
│
├── service/
│   ├── ServiceCard.vue         // Service selection card
│   ├── ServiceFeature.vue      // Feature highlight component
│   ├── ComplianceForm.vue      // Legal compliance form
│   ├── PaymentMethod.vue       // Payment method selection
│   └── ServiceStepper.vue      // Multi-step progress
│
├── dashboard/
│   ├── DashboardOverview.vue   // Main dashboard view
│   ├── ServiceStatus.vue       // Service status indicator
│   ├── QuickActions.vue        // Quick action buttons
│   ├── RecentActivity.vue      // Activity feed
│   └── MetricsCard.vue         // Metrics display card
│
├── trading/
│   ├── TradingChart.vue        // Price chart component
│   ├── OrderBook.vue           // Order book display
│   ├── TradeHistory.vue        // Trade history table
│   ├── PortfolioChart.vue      // Portfolio allocation chart
│   ├── MarketTicker.vue        // Real-time ticker
│   └── TradingPanel.vue        // Order placement panel
│
├── ui/
│   ├── BaseButton.vue          // Reusable button component
│   ├── BaseInput.vue           // Reusable input component
│   ├── BaseModal.vue           // Modal wrapper
│   ├── BaseDropdown.vue        // Dropdown component
│   ├── BaseTooltip.vue         // Tooltip component
│   ├── LoadingSpinner.vue      // Loading indicator
│   ├── AlertMessage.vue        // Alert component
│   ├── ProgressBar.vue         // Progress indicator
│   └── DataTable.vue           // Data table component
│
└── common/
    ├── UserAvatar.vue          // User avatar component
    ├── NotificationBell.vue    // Notification indicator
    ├── SearchBox.vue           // Global search
    ├── ThemeToggle.vue         // Dark/light mode toggle
    └── LanguageSelector.vue    // Language switcher
```

---

## 📱 PAGE DESIGN SPECIFICATIONS

### 1. HomePage (index.html)
**Purpose:** Landing page with service overview and clear CTAs

**Layout Structure:**
```vue
<template>
  <div class="homepage">
    <!-- Header Navigation -->
    <AppHeader />
    
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">
            Nền Tảng Công Nghệ Số<br>
            <span class="text-primary">Digital Utopia</span>
          </h1>
          <p class="hero-description">
            Giải pháp công nghệ toàn diện cho doanh nghiệp hiện đại.
            Tích hợp API, ứng dụng web, và hệ thống trading tiên tiến.
          </p>
          <div class="hero-actions">
            <router-link to="/auth/selection" class="btn-primary btn-lg">
              Bắt Đầu Ngay
            </router-link>
            <router-link to="/documentation" class="btn-secondary btn-lg">
              Tìm Hiểu Thêm
            </router-link>
          </div>
        </div>
        <div class="hero-visual">
          <!-- Hero image/animation -->
          <img src="/images/hero-illustration.svg" alt="Digital Utopia Platform">
        </div>
      </div>
    </section>
    
    <!-- Services Overview -->
    <section class="services-section">
      <div class="container">
        <h2 class="section-title">Dịch Vụ Của Chúng Tôi</h2>
        <div class="services-grid">
          <ServiceCard 
            v-for="service in services" 
            :key="service.id"
            :service="service"
          />
        </div>
      </div>
    </section>
    
    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">Tại Sao Chọn Digital Utopia?</h2>
        <div class="features-grid">
          <div class="feature-item" v-for="feature in features" :key="feature.id">
            <div class="feature-icon">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Trust Indicators -->
    <section class="trust-section">
      <div class="container">
        <div class="trust-stats">
          <div class="stat-item">
            <span class="stat-number">10,000+</span>
            <span class="stat-label">Khách Hàng</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">99.9%</span>
            <span class="stat-label">Uptime</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">24/7</span>
            <span class="stat-label">Hỗ Trợ</span>
          </div>
        </div>
      </div>
    </section>
    
    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <h2>Sẵn Sàng Bắt Đầu?</h2>
        <p>Tham gia cùng hàng nghìn doanh nghiệp tin tưởng Digital Utopia</p>
        <router-link to="/auth/selection" class="btn-primary btn-xl">
          Đăng Nhập Ngay
        </router-link>
      </div>
    </section>
    
    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<style scoped>
.hero-section {
  @apply bg-gradient-to-br from-primary-50 to-primary-100 py-20;
}

.hero-content {
  @apply max-w-4xl mx-auto text-center;
}

.hero-title {
  @apply text-5xl md:text-6xl font-bold text-neutral-800 mb-6;
}

.hero-description {
  @apply text-xl text-neutral-600 mb-8 max-w-3xl mx-auto;
}

.hero-actions {
  @apply flex flex-col sm:flex-row gap-4 justify-center;
}

.services-section {
  @apply py-20 bg-white;
}

.section-title {
  @apply text-4xl font-bold text-center text-neutral-800 mb-16;
}

.services-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8;
}

.features-section {
  @apply py-20 bg-neutral-50;
}

.features-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8;
}

.feature-item {
  @apply bg-white p-8 rounded-xl shadow-sm text-center;
}

.feature-icon {
  @apply w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-full flex items-center justify-center;
  @apply text-primary-600 text-2xl;
}

.trust-section {
  @apply py-16 bg-primary-600 text-white;
}

.trust-stats {
  @apply flex flex-wrap justify-center gap-8 md:gap-16;
}

.stat-item {
  @apply text-center;
}

.stat-number {
  @apply block text-3xl md:text-4xl font-bold;
}

.stat-label {
  @apply block text-primary-100 mt-2;
}

.cta-section {
  @apply py-20 bg-gradient-to-r from-primary-600 to-primary-700 text-center;
}

.cta-section h2 {
  @apply text-4xl font-bold mb-4;
}

.cta-section p {
  @apply text-xl text-primary-100 mb-8;
}
</style>
```

### 2. AuthSelection Page
**Purpose:** Allow users to choose authentication method

**Layout Structure:**
```vue
<template>
  <div class="auth-selection">
    <div class="auth-container">
      <div class="auth-header">
        <h1>Chọn Phương Thức Đăng Nhập</h1>
        <p>Chọn cách đăng nhập phù hợp với bạn</p>
      </div>
      
      <div class="auth-methods">
        <!-- Google OAuth -->
        <div class="auth-method-card" @click="signInWithGoogle">
          <div class="method-icon">
            <i class="fab fa-google"></i>
          </div>
          <div class="method-info">
            <h3>Đăng nhập với Google</h3>
            <p>Sử dụng tài khoản Google để đăng nhập nhanh chóng và an toàn</p>
          </div>
          <div class="method-arrow">
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>
        
        <!-- Microsoft OAuth -->
        <div class="auth-method-card" @click="signInWithMicrosoft">
          <div class="method-icon">
            <i class="fab fa-microsoft"></i>
          </div>
          <div class="method-info">
            <h3>Đăng nhập với Microsoft</h3>
            <p>Sử dụng tài khoản Microsoft/Office 365 để truy cập</p>
          </div>
          <div class="method-arrow">
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>
        
        <!-- Email/OTP -->
        <div class="auth-method-card" @click="showEmailLogin = true">
          <div class="method-icon">
            <i class="fas fa-envelope"></i>
          </div>
          <div class="method-info">
            <h3>Đăng nhập bằng Email</h3>
            <p>Nhập email và mã OTP để xác thực tài khoản</p>
          </div>
          <div class="method-arrow">
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>
      </div>
      
      <!-- Back to Home -->
      <div class="auth-footer">
        <router-link to="/" class="back-link">
          <i class="fas fa-arrow-left"></i>
          Quay về trang chủ
        </router-link>
      </div>
    </div>
    
    <!-- Email Login Modal -->
    <EmailLoginForm 
      v-if="showEmailLogin"
      @close="showEmailLogin = false"
      @success="handleEmailLoginSuccess"
    />
  </div>
</template>

<style scoped>
.auth-selection {
  @apply min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4;
}

.auth-container {
  @apply max-w-md w-full bg-white rounded-2xl shadow-xl p-8;
}

.auth-header {
  @apply text-center mb-8;
}

.auth-header h1 {
  @apply text-2xl font-bold text-neutral-800 mb-2;
}

.auth-header p {
  @apply text-neutral-600;
}

.auth-methods {
  @apply space-y-4;
}

.auth-method-card {
  @apply flex items-center p-4 border border-neutral-200 rounded-xl cursor-pointer;
  @apply hover:border-primary-300 hover:bg-primary-50 transition-all duration-200;
}

.method-icon {
  @apply w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center text-neutral-600 text-xl;
  @apply mr-4 flex-shrink-0;
}

.method-info {
  @apply flex-1;
}

.method-info h3 {
  @apply font-semibold text-neutral-800 mb-1;
}

.method-info p {
  @apply text-sm text-neutral-600;
}

.method-arrow {
  @apply text-neutral-400 text-lg;
}

.auth-footer {
  @apply text-center mt-8;
}

.back-link {
  @apply text-primary-600 hover:text-primary-700 font-medium;
  @apply flex items-center justify-center;
}
</style>
```

### 3. ServiceRegistration Page
**Purpose:** Multi-step service registration with compliance

**Layout Structure:**
```vue
<template>
  <div class="service-registration">
    <div class="registration-container">
      <!-- Progress Steps -->
      <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="step.id"
          :class="[
            'progress-step',
            { 'active': currentStep === index },
            { 'completed': index < currentStep }
          ]"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-label">{{ step.label }}</div>
        </div>
      </div>
      
      <!-- Step Content -->
      <div class="step-content">
        <component 
          :is="currentStepComponent" 
          @next="nextStep"
          @previous="previousStep"
          @submit="handleSubmit"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.service-registration {
  @apply min-h-screen bg-neutral-50 py-8;
}

.registration-container {
  @apply max-w-4xl mx-auto bg-white rounded-2xl shadow-sm p-8;
}

.progress-steps {
  @apply flex justify-between mb-12;
}

.progress-step {
  @apply flex-1 flex flex-col items-center text-center;
}

.step-number {
  @apply w-10 h-10 rounded-full flex items-center justify-center font-semibold;
  @apply bg-neutral-200 text-neutral-600 mb-2;
}

.progress-step.active .step-number {
  @apply bg-primary-600 text-white;
}

.progress-step.completed .step-number {
  @apply bg-success-green text-white;
}

.step-label {
  @apply text-sm font-medium text-neutral-600;
}

.progress-step.active .step-label {
  @apply text-primary-600;
}

.progress-step.completed .step-label {
  @apply text-success-green;
}

.step-content {
  @apply min-h-[500px];
}
</style>
```

### 4. Dashboard Page
**Purpose:** Main authenticated user dashboard

**Layout Structure:**
```vue
<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="container">
        <h1>Xin chào, {{ user.name }}!</h1>
        <p>Dưới đây là tổng quan về tài khoản và dịch vụ của bạn</p>
      </div>
    </div>
    
    <!-- Dashboard Content -->
    <div class="dashboard-content">
      <div class="container">
        <!-- Quick Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-server"></i>
            </div>
            <div class="stat-info">
              <span class="stat-number">{{ servicesActive }}</span>
              <span class="stat-label">Dịch vụ đang hoạt động</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-info">
              <span class="stat-number">{{ apiCallsThisMonth }}</span>
              <span class="stat-label">API calls tháng này</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="stat-info">
              <span class="stat-number">99.9%</span>
              <span class="stat-label">Uptime</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="stat-info">
              <span class="stat-number">{{ teamMembers }}</span>
              <span class="stat-label">Thành viên team</span>
            </div>
          </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="content-grid">
          <!-- Service Status -->
          <div class="content-card">
            <h2>Trạng Thái Dịch Vụ</h2>
            <div class="service-list">
              <div 
                v-for="service in userServices" 
                :key="service.id"
                class="service-item"
              >
                <div class="service-info">
                  <h3>{{ service.name }}</h3>
                  <p>{{ service.description }}</p>
                </div>
                <div class="service-status">
                  <span :class="['status-badge', service.status]">
                    {{ getStatusText(service.status) }}
                  </span>
                  <button class="btn-sm btn-outline">Quản lý</button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Recent Activity -->
          <div class="content-card">
            <h2>Hoạt Động Gần Đây</h2>
            <div class="activity-list">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-icon" :class="activity.type">
                  <i :class="getActivityIcon(activity.type)"></i>
                </div>
                <div class="activity-info">
                  <p class="activity-description">{{ activity.description }}</p>
                  <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Quick Actions -->
          <div class="content-card">
            <h2>Thao Tác Nhanh</h2>
            <div class="quick-actions">
              <router-link to="/service/registration" class="quick-action">
                <i class="fas fa-plus"></i>
                <span>Đăng ký dịch vụ mới</span>
              </router-link>
              
              <router-link to="/documentation" class="quick-action">
                <i class="fas fa-book"></i>
                <span>Xem tài liệu API</span>
              </router-link>
              
              <router-link to="/support" class="quick-action">
                <i class="fas fa-headset"></i>
                <span>Liên hệ hỗ trợ</span>
              </router-link>
              
              <router-link to="/settings" class="quick-action">
                <i class="fas fa-cog"></i>
                <span>Cài đặt tài khoản</span>
              </router-link>
            </div>
          </div>
          
          <!-- Usage Chart -->
          <div class="content-card">
            <h2>Sử Dụng API (30 ngày qua)</h2>
            <div class="chart-container">
              <!-- Chart component would go here -->
              <canvas ref="usageChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  @apply min-h-screen bg-neutral-50;
}

.dashboard-header {
  @apply bg-white border-b border-neutral-200 py-8;
}

.dashboard-header h1 {
  @apply text-3xl font-bold text-neutral-800 mb-2;
}

.dashboard-header p {
  @apply text-neutral-600;
}

.dashboard-content {
  @apply py-8;
}

.stats-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8;
}

.stat-card {
  @apply bg-white p-6 rounded-xl shadow-sm;
  @apply flex items-center space-x-4;
}

.stat-icon {
  @apply w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center;
  @apply text-primary-600 text-xl;
}

.stat-number {
  @apply block text-2xl font-bold text-neutral-800;
}

.stat-label {
  @apply block text-sm text-neutral-600;
}

.content-grid {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-8;
}

.content-card {
  @apply bg-white p-6 rounded-xl shadow-sm;
}

.content-card h2 {
  @apply text-xl font-semibold text-neutral-800 mb-4;
}

.service-list {
  @apply space-y-4;
}

.service-item {
  @apply flex items-center justify-between p-4 border border-neutral-200 rounded-lg;
}

.service-info h3 {
  @apply font-semibold text-neutral-800 mb-1;
}

.service-info p {
  @apply text-sm text-neutral-600;
}

.service-status {
  @apply flex items-center space-x-3;
}

.status-badge {
  @apply px-3 py-1 rounded-full text-xs font-medium;
}

.status-badge.active {
  @apply bg-success-green-100 text-success-green-800;
}

.status-badge.pending {
  @apply bg-warning-orange-100 text-warning-orange-800;
}

.status-badge.error {
  @apply bg-error-red-100 text-error-red-800;
}

.activity-list {
  @apply space-y-3;
}

.activity-item {
  @apply flex items-center space-x-3;
}

.activity-icon {
  @apply w-8 h-8 rounded-full flex items-center justify-center text-sm;
}

.activity-icon.success {
  @apply bg-success-green-100 text-success-green-600;
}

.activity-icon.info {
  @apply bg-info-blue-100 text-info-blue-600;
}

.activity-icon.warning {
  @apply bg-warning-orange-100 text-warning-orange-600;
}

.activity-description {
  @apply text-sm text-neutral-800;
}

.activity-time {
  @apply text-xs text-neutral-500;
}

.quick-actions {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-3;
}

.quick-action {
  @apply flex items-center space-x-3 p-3 border border-neutral-200 rounded-lg;
  @apply hover:border-primary-300 hover:bg-primary-50 transition-colors;
}

.quick-action i {
  @apply text-primary-600 text-lg;
}

.chart-container {
  @apply h-64 flex items-center justify-center bg-neutral-50 rounded-lg;
}
</style>
```

---

## 🎛️ STATE MANAGEMENT (PINIA)

### User Store
```javascript
// /stores/user.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref(null);
  const token = ref(localStorage.getItem('auth_token'));
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  
  // Actions
  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      user.value = response.data.user;
      token.value = response.data.token;
      localStorage.setItem('auth_token', token.value);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
  
  const loginWithOAuth = async (provider, authData) => {
    try {
      const response = await api.post(`/auth/${provider}/callback`, authData);
      user.value = response.data.user;
      token.value = response.data.token;
      localStorage.setItem('auth_token', token.value);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
  
  const logout = async () => {
    try {
      await api.post('/auth/logout');
      user.value = null;
      token.value = null;
      localStorage.removeItem('auth_token');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };
  
  const updateProfile = async (profileData) => {
    try {
      const response = await api.put('/user/profile', profileData);
      user.value = { ...user.value, ...response.data };
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
  
  return {
    // State
    user,
    token,
    isAuthenticated,
    
    // Actions
    login,
    loginWithOAuth,
    logout,
    updateProfile
  };
});
```

### Service Store
```javascript
// /stores/services.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useServiceStore = defineStore('services', () => {
  // State
  const services = ref([]);
  const activeServices = computed(() => services.value.filter(s => s.status === 'active'));
  const pendingServices = computed(() => services.value.filter(s => s.status === 'pending'));
  
  // Actions
  const fetchServices = async () => {
    try {
      const response = await api.get('/services');
      services.value = response.data;
    } catch (error) {
      console.error('Failed to fetch services:', error);
    }
  };
  
  const registerService = async (serviceData) => {
    try {
      const response = await api.post('/services', serviceData);
      services.value.push(response.data);
      return { success: true, service: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
  
  const updateService = async (serviceId, updateData) => {
    try {
      const response = await api.put(`/services/${serviceId}`, updateData);
      const index = services.value.findIndex(s => s.id === serviceId);
      if (index !== -1) {
        services.value[index] = response.data;
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
  
  const deleteService = async (serviceId) => {
    try {
      await api.delete(`/services/${serviceId}`);
      services.value = services.value.filter(s => s.id !== serviceId);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
  
  return {
    // State
    services,
    activeServices,
    pendingServices,
    
    // Actions
    fetchServices,
    registerService,
    updateService,
    deleteService
  };
});
```

---

## 🔧 COMPOSABLES & UTILITIES

### useAuth Composable
```javascript
// /composables/useAuth.js
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

export function useAuth() {
  const userStore = useUserStore();
  const router = useRouter();
  
  const login = async (credentials) => {
    const result = await userStore.login(credentials);
    if (result.success) {
      router.push('/dashboard');
    }
    return result;
  };
  
  const loginWithGoogle = async () => {
    // Redirect to Google OAuth
    window.location.href = '/auth/google/redirect';
  };
  
  const loginWithMicrosoft = async () => {
    // Redirect to Microsoft OAuth
    window.location.href = '/auth/microsoft/redirect';
  };
  
  const logout = async () => {
    await userStore.logout();
    router.push('/');
  };
  
  const requireAuth = (to, from, next) => {
    if (userStore.isAuthenticated) {
      next();
    } else {
      router.push('/auth/selection');
    }
  };
  
  return {
    user: userStore.user,
    isAuthenticated: userStore.isAuthenticated,
    login,
    loginWithGoogle,
    loginWithMicrosoft,
    logout,
    requireAuth
  };
}
```

### useApi Composable
```javascript
// /composables/useApi.js
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';

export function useApi() {
  const loading = ref(false);
  const error = ref(null);
  const userStore = useUserStore();
  
  const apiCall = async (endpoint, options = {}) => {
    loading.value = true;
    error.value = null;
    
    try {
      const config = {
        baseURL: import.meta.env.VITE_API_URL,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      };
      
      // Add auth token if available
      if (userStore.token) {
        config.headers.Authorization = `Bearer ${userStore.token}`;
      }
      
      const response = await fetch(endpoint, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      return { success: true, data };
      
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      loading.value = false;
    }
  };
  
  const get = (endpoint, options = {}) => 
    apiCall(endpoint, { ...options, method: 'GET' });
  
  const post = (endpoint, data, options = {}) => 
    apiCall(endpoint, { 
      ...options, 
      method: 'POST',
      body: JSON.stringify(data)
    });
  
  const put = (endpoint, data, options = {}) => 
    apiCall(endpoint, { 
      ...options, 
      method: 'PUT',
      body: JSON.stringify(data)
    });
  
  const del = (endpoint, options = {}) => 
    apiCall(endpoint, { ...options, method: 'DELETE' });
  
  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del
  };
}
```

---

## 🎨 RESPONSIVE DESIGN GUIDELINES

### Breakpoint System
```css
/* Responsive Breakpoints */
/* Mobile First Approach */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

### Grid System
```css
/* Container Classes */
.container {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.container-narrow {
  @apply max-w-4xl mx-auto px-4 sm:px-6 lg:px-8;
}

.container-wide {
  @apply max-w-full mx-auto px-4 sm:px-6 lg:px-8;
}
```

### Mobile-First Component Design
```vue
<!-- Example Responsive Component -->
<template>
  <div class="responsive-card">
    <!-- Mobile: Stack vertically -->
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <p class="card-subtitle">{{ subtitle }}</p>
    </div>
    
    <!-- Desktop: Horizontal layout -->
    <div class="card-content">
      <img :src="image" :alt="title" class="card-image">
      <div class="card-body">
        <p>{{ description }}</p>
        <button class="card-action">{{ actionText }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.responsive-card {
  @apply bg-white rounded-xl shadow-sm overflow-hidden;
  @apply transition-all duration-200 hover:shadow-md;
}

/* Mobile First */
.card-header {
  @apply p-6 border-b border-neutral-200;
}

.card-title {
  @apply text-xl font-semibold text-neutral-800 mb-2;
}

.card-subtitle {
  @apply text-sm text-neutral-600;
}

.card-content {
  @apply flex flex-col;
}

.card-image {
  @apply w-full h-48 object-cover;
}

.card-body {
  @apply p-6;
}

.card-action {
  @apply mt-4 w-full btn-primary;
}

/* Desktop: md breakpoint */
@media (min-width: 768px) {
  .card-content {
    @apply flex-row;
  }
  
  .card-image {
    @apply w-48 h-auto;
  }
  
  .card-action {
    @apply w-auto mt-0;
  }
}
</style>
```

---

## 🔒 SECURITY & COMPLIANCE

### Content Security Policy
```html
<!-- CSP Meta Tag -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.digitalutopia.vn wss://api.digitalutopia.vn;
">
```

### Authentication Security
```javascript
// Secure token handling
const secureStorage = {
  setToken(token) {
    // Use httpOnly cookies in production
    if (import.meta.env.PROD) {
      document.cookie = `auth_token=${token}; HttpOnly; Secure; SameSite=Strict; Path=/`;
    } else {
      localStorage.setItem('auth_token', token);
    }
  },
  
  getToken() {
    if (import.meta.env.PROD) {
      const cookies = document.cookie.split(';');
      const tokenCookie = cookies.find(c => c.trim().startsWith('auth_token='));
      return tokenCookie ? tokenCookie.split('=')[1] : null;
    }
    return localStorage.getItem('auth_token');
  },
  
  clearToken() {
    if (import.meta.env.PROD) {
      document.cookie = 'auth_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0';
    } else {
      localStorage.removeItem('auth_token');
    }
  }
};
```

### GDPR Compliance Components
```vue
<template>
  <div class="gdpr-compliance">
    <!-- Cookie Consent Banner -->
    <CookieConsentBanner v-if="!cookiesAccepted" />
    
    <!-- Privacy Settings Modal -->
    <PrivacySettingsModal />
    
    <!-- Data Export/Deletion Requests -->
    <DataRightsSection />
  </div>
</template>

<script>
export default {
  name: 'GDPRCompliance',
  setup() {
    const { cookiesAccepted } = useCookieConsent();
    
    return {
      cookiesAccepted
    };
  }
};
</script>
```

---

## 📊 ANALYTICS & TRACKING

### User Interaction Tracking
```javascript
// Analytics Service
class AnalyticsService {
  trackEvent(eventName, properties = {}) {
    const eventData = {
      event: eventName,
      properties: {
        ...properties,
        timestamp: new Date().toISOString(),
        userId: this.getCurrentUserId(),
        sessionId: this.getSessionId(),
        page: window.location.pathname
      }
    };
    
    // Send to analytics service
    this.sendToAnalytics(eventData);
  }
  
  trackPageView(page) {
    this.trackEvent('page_view', { page });
  }
  
  trackButtonClick(buttonName, location) {
    this.trackEvent('button_click', { buttonName, location });
  }
  
  trackFormSubmission(formName, success = true) {
    this.trackEvent('form_submission', { formName, success });
  }
}
```

### Performance Monitoring
```javascript
// Performance Observer
const performanceObserver = new PerformanceObserver((list) => {
  list.getEntries().forEach((entry) => {
    // Track Core Web Vitals
    if (entry.entryType === 'largest-contentful-paint') {
      this.trackMetric('LCP', entry.startTime);
    }
    
    if (entry.entryType === 'first-input') {
      this.trackMetric('FID', entry.processingStart - entry.startTime);
    }
    
    if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
      this.trackMetric('CLS', entry.value);
    }
  });
});

performanceObserver.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
```

---

## 🚀 PERFORMANCE OPTIMIZATION

### Lazy Loading Strategy
```javascript
// Route-based code splitting
const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('@/views/trading/TradingDashboard.vue'),
    meta: { requiresAuth: true }
  }
];

// Component lazy loading
const HeavyComponent = defineAsyncComponent({
  loader: () => import('@/components/HeavyComponent.vue'),
  loading: LoadingSpinner,
  error: ErrorComponent,
  delay: 200,
  timeout: 3000
});
```

### Image Optimization
```vue
<template>
  <picture>
    <!-- WebP format with fallback -->
    <source :srcset="imageWebP" type="image/webp">
    <img 
      :src="imageFallback" 
      :alt="altText"
      :loading="loading"
      class="optimized-image"
      @load="onImageLoad"
      @error="onImageError"
    >
  </picture>
</template>

<style scoped>
.optimized-image {
  @apply w-full h-auto object-cover;
  /* Prevent layout shift */
  aspect-ratio: 16 / 9;
}

.optimized-image[loading="lazy"] {
  /* Add fade-in effect for lazy loaded images */
  @apply opacity-0 transition-opacity duration-300;
}

.optimized-image[loading="lazy"].loaded {
  @apply opacity-100;
}
</style>
```

---

## 🛠️ TESTING STRATEGY

### Unit Testing Example
```javascript
// /tests/components/Button.test.js
import { mount } from '@vue/test-utils';
import BaseButton from '@/components/ui/BaseButton.vue';

describe('BaseButton', () => {
  it('renders correctly with text', () => {
    const wrapper = mount(BaseButton, {
      props: {
        text: 'Click me',
        variant: 'primary'
      }
    });
    
    expect(wrapper.text()).toBe('Click me');
    expect(wrapper.classes()).toContain('btn-primary');
  });
  
  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        text: 'Click me'
      }
    });
    
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('click')).toHaveLength(1);
  });
  
  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: {
        text: 'Click me',
        disabled: true
      }
    });
    
    expect(wrapper.find('button').attributes('disabled')).toBeDefined();
  });
});
```

### E2E Testing Example
```javascript
// /tests/e2e/auth-flow.spec.js
describe('Authentication Flow', () => {
  it('completes Google OAuth flow', () => {
    cy.visit('/auth/selection');
    cy.get('[data-testid="google-login-button"]').click();
    
    // Mock Google OAuth response
    cy.window().then((win) => {
      win.postMessage({
        type: 'oauth-success',
        data: { token: 'mock-jwt-token', user: { id: 1, name: 'Test User' } }
      }, '*');
    });
    
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-welcome"]').should('contain', 'Test User');
  });
  
  it('handles login errors gracefully', () => {
    cy.visit('/auth/selection');
    cy.get('[data-testid="email-login"]').click();
    cy.get('[data-testid="email-input"]').type('invalid@email.com');
    cy.get('[data-testid="login-button"]').click();
    
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'Invalid credentials');
  });
});
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Core Setup (Week 1-2)
- [ ] Project initialization with Vue 3 + Vite
- [ ] Tailwind CSS + DaisyUI configuration
- [ ] TypeScript setup and configuration
- [ ] Pinia store setup and routing
- [ ] API service layer implementation
- [ ] Authentication system (OAuth + Email)
- [ ] Basic layout components (Header, Footer, Layout)

### Phase 2: Main Pages (Week 3-4)
- [ ] HomePage with hero section and service overview
- [ ] AuthSelection page with all authentication methods
- [ ] Service registration multi-step flow
- [ ] Dashboard with user overview and statistics
- [ ] Profile and Settings pages
- [ ] Legal pages (Terms, Privacy, Cookie Policy)

### Phase 3: Advanced Features (Week 5-6)
- [ ] Trading dashboard with real-time data
- [ ] Portfolio management with charts
- [ ] Wallet functionality (deposit, withdraw)
- [ ] Analytics and reporting features
- [ ] Notification system
- [ ] Search functionality

### Phase 4: Polish & Optimization (Week 7-8)
- [ ] Responsive design optimization
- [ ] Performance optimization (lazy loading, code splitting)
- [ ] Accessibility improvements (WCAG 2.1 AA)
- [ ] SEO optimization
- [ ] Security audit and enhancements
- [ ] Testing (unit, integration, e2e)
- [ ] Documentation completion

### Phase 5: Production Ready (Week 9-10)
- [ ] PWA implementation with service worker
- [ ] Offline functionality
- [ ] Error handling and recovery
- [ ] Monitoring and analytics integration
- [ ] Deployment configuration
- [ ] Production environment setup

---

## 🎯 SUCCESS METRICS

### Technical Metrics
- **Performance**: Core Web Vitals scores (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- **Accessibility**: WCAG 2.1 AA compliance score > 95%
- **SEO**: Lighthouse score > 90 for all categories
- **Code Quality**: ESLint score 0 errors, TypeScript strict mode compliance
- **Testing**: > 80% unit test coverage, 100% critical path e2e coverage

### User Experience Metrics
- **Task Completion**: > 95% success rate for key user flows
- **Error Rate**: < 5% error rate across all interactions
- **User Satisfaction**: > 4.5/5 average user satisfaction score
- **Time to Complete**: < 2 minutes for service registration flow
- **Mobile Usability**: > 98% mobile usability score

### Business Metrics
- **Conversion Rate**: > 15% conversion from visitor to registered user
- **User Retention**: > 80% week-1 retention rate
- **Support Tickets**: < 10% of users need support for basic tasks
- **API Adoption**: > 70% of registered users integrate API within 30 days

---

## 🔄 CONTINUOUS IMPROVEMENT

### Design Iteration Process
1. **User Research**: Monthly user interviews and usability testing
2. **Analytics Review**: Weekly review of user behavior and pain points
3. **A/B Testing**: Continuous testing of key conversion elements
4. **Performance Monitoring**: Real-time monitoring of Core Web Vitals
5. **Feedback Integration**: Monthly review of user feedback and feature requests

### Update Schedule
- **Weekly**: Bug fixes and small UI improvements
- **Monthly**: New features and major improvements
- **Quarterly**: Design system updates and major refactoring
- **Annually**: Complete design system review and modernization

---

**END OF PROMPT**

Đây là prompt thiết kế giao diện Vue.js 3 hoàn chỉnh cho Digital Utopia Platform Client App. Prompt này cung cấp tất cả thông tin cần thiết để AI có thể thiết kế và phát triển một ứng dụng web enterprise-grade với:

1. **Design System Hoàn Chỉnh**: Color palette, typography, spacing, components
2. **Technical Architecture**: Vue 3, TypeScript, Tailwind CSS, Pinia stores
3. **Page Specifications**: Chi tiết cho từng trang với layout và styling
4. **Security & Compliance**: GDPR, security measures, accessibility
5. **Performance Optimization**: Lazy loading, code splitting, optimization
6. **Testing Strategy**: Unit testing, e2e testing, quality assurance
7. **Implementation Roadmap**: Timeline 10 tuần với checklist rõ ràng
8. **Success Metrics**: KPIs để đo lường thành công

Prompt này đảm bảo AI có thể tạo ra một ứng dụng client app professional, user-friendly, và enterprise-ready cho Digital Utopia Platform.