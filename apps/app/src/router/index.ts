import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
    /** Client-side UX only (hide/redirect) — the real gate is always the
     * backend's IsAdminUser/IsSuperUser (master prompt §67, Phase 6b). */
    requiresStaff?: boolean
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
          path: 'fakture/nova/profaktura',
          name: 'invoice-new-profaktura',
          component: () => import('@/views/InvoiceFormView.vue'),
          props: { documentType: 'profaktura' },
        },
        {
          path: 'fakture/nova/avans',
          name: 'invoice-new-avans',
          component: () => import('@/views/InvoiceFormView.vue'),
          props: { documentType: 'avans' },
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
        {
          path: 'dokumenti',
          name: 'documents',
          component: () => import('@/views/DocumentsView.vue'),
        },
        {
          path: 'racunovodja',
          name: 'accounting',
          component: () => import('@/views/AccountingView.vue'),
        },
        {
          path: 'organizacija',
          name: 'accounting-organization',
          component: () => import('@/views/AccountingOrganizationView.vue'),
        },
        {
          path: 'pretplata',
          name: 'subscription',
          component: () => import('@/views/SubscriptionView.vue'),
        },
      ],
    },
    {
      path: '/admin',
      component: () => import('@/components/AdminShell.vue'),
      meta: { requiresAuth: true, requiresStaff: true },
      children: [
        { path: '', redirect: { name: 'admin-users' } },
        {
          path: 'korisnici',
          name: 'admin-users',
          component: () => import('@/views/admin/AdminUsersView.vue'),
        },
        {
          path: 'kompanije',
          name: 'admin-companies',
          component: () => import('@/views/admin/AdminCompaniesView.vue'),
        },
        {
          path: 'pretplate',
          name: 'admin-subscriptions',
          component: () => import('@/views/admin/AdminSubscriptionsView.vue'),
        },
        {
          path: 'planovi',
          name: 'admin-plans',
          component: () => import('@/views/admin/AdminPlansView.vue'),
        },
        {
          path: 'fakture',
          name: 'admin-invoices',
          component: () => import('@/views/admin/AdminInvoicesView.vue'),
        },
        {
          path: 'dokumenti',
          name: 'admin-documents',
          component: () => import('@/views/admin/AdminDocumentsView.vue'),
        },
        {
          path: 'poreske-obaveze',
          name: 'admin-tax-obligations',
          component: () => import('@/views/admin/AdminTaxObligationsView.vue'),
        },
        {
          path: 'pravila',
          name: 'admin-rules',
          component: () => import('@/views/admin/AdminRulesView.vue'),
        },
        {
          path: 'obavestenja',
          name: 'admin-notifications',
          component: () => import('@/views/admin/AdminNotificationsView.vue'),
        },
        {
          path: 'audit-log',
          name: 'admin-audit-log',
          component: () => import('@/views/admin/AdminAuditLogView.vue'),
        },
        {
          path: 'integracije',
          name: 'admin-integrations',
          component: () => import('@/views/admin/AdminIntegrationsView.vue'),
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
  if (to.meta.requiresStaff && !auth.user?.is_staff) {
    return { name: 'home' }
  }
  return true
})

export default router
