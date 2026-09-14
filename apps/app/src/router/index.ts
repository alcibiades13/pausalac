import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/prijava',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/registracija',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/zaboravljena-lozinka',
      name: 'forgot-password',
      component: () => import('@/views/ForgotPasswordView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/nova-lozinka',
      name: 'reset-password',
      component: () => import('@/views/ResetPasswordView.vue'),
    },
    {
      path: '/verifikacija-emaila',
      name: 'verify-email',
      component: () => import('@/views/VerifyEmailView.vue'),
    },
    {
      path: '/',
      component: () => import('@/components/AppShell.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'home' } },
        {
          path: 'pocetna',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
        },
        {
          path: 'klijenti',
          name: 'clients',
          component: () => import('@/views/ClientsListView.vue'),
        },
        {
          path: 'klijenti/novi',
          name: 'client-new',
          component: () => import('@/views/ClientFormView.vue'),
        },
        {
          path: 'klijenti/:id',
          name: 'client-edit',
          component: () => import('@/views/ClientFormView.vue'),
          props: true,
        },
        {
          path: 'fakture',
          name: 'invoices',
          component: () => import('@/views/InvoicesListView.vue'),
        },
        {
          path: 'fakture/nova',
          name: 'invoice-new',
          component: () => import('@/views/InvoiceFormView.vue'),
        },
        {
          path: 'fakture/:id/izmeni',
          name: 'invoice-edit',
          component: () => import('@/views/InvoiceFormView.vue'),
          props: true,
        },
        {
          path: 'fakture/:id',
          name: 'invoice-detail',
          component: () => import('@/views/InvoiceDetailView.vue'),
          props: true,
        },
        {
          path: 'podesavanja',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
        {
          path: 'limiti',
          name: 'limits',
          component: () => import('@/views/LimitsView.vue'),
        },
        {
          path: 'kpo',
          name: 'kpo',
          component: () => import('@/views/KPOListView.vue'),
        },
        {
          path: 'obaveze',
          name: 'obligations',
          component: () => import('@/views/ObligationsView.vue'),
        },
        {
          path: 'obavestenja',
          name: 'notifications',
          component: () => import('@/views/NotificationsView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.status === 'idle') {
    await auth.bootstrap()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'home' }
  }
  return true
})

export default router
