import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
    /** Client-side UX only (hide/redirect) — the real gate is always the
     * backend's IsAdminUser/IsSuperUser (master prompt §67, Phase 6b). */
    requiresStaff?: boolean
    /**
     * TopHeader.vue's breadcrumb (desktop/tablet header, added alongside
     * the language-switcher relocation): `section` names the top-level
     * NAV_LINKS entry (AppShell.vue) or admin NAV_LINKS entry
     * (AdminShell.vue) this route belongs to, so a subroute can show
     * "Section / this page" with a working back button. Top-level list
     * pages themselves (clients, invoices, ...) don't set this — the
     * breadcrumb only appears one level below them. `breadcrumbKey`
     * is the i18n key suffix (under `authShell.breadcrumb.*`) for the
     * leaf segment. Detail pages (client-detail/invoice-detail) show a
     * generic leaf, not the entity's real name/number — a live page
     * title would need a small reactive title bus this pass didn't
     * build; flagged as a follow-up, not silently faked.
     */
    section?: string
    breadcrumbKey?: string
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // Without this, Vue Router keeps the outgoing page's scroll position on
  // the incoming one (the browser's default SPA behavior) — e.g. scrolling
  // down a long invoice list then opening a detail page lands mid-page
  // instead of at the top. Restore on back/forward, honor #hash targets,
  // otherwise always reset to top.
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash }
    return { top: 0 }
  },
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
          // Only the dashboard opts into the wider content column
          // (AppShell.vue) — cards/charts benefit from desktop width
          // (blueprint §4.7), unlike a form or a reading-width detail
          // page, which stay at the app's normal max-w-5xl.
          meta: { wideContent: true },
        },
        {
          path: 'klijenti',
          name: 'clients',
          component: () => import('@/views/ClientsListView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'klijenti/novi',
          name: 'client-new',
          component: () => import('@/views/ClientFormView.vue'),
          meta: { section: 'clients', breadcrumbKey: 'newClient' },
        },
        {
          path: 'klijenti/:id',
          name: 'client-detail',
          component: () => import('@/views/ClientDetailView.vue'),
          props: true,
          meta: { section: 'clients', breadcrumbKey: 'clientDetail' },
        },
        {
          path: 'klijenti/:id/izmeni',
          name: 'client-edit',
          component: () => import('@/views/ClientFormView.vue'),
          props: true,
          meta: { section: 'clients', breadcrumbKey: 'editClient' },
        },
        {
          path: 'fakture',
          name: 'invoices',
          component: () => import('@/views/InvoicesListView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'fakture/nova',
          name: 'invoice-new',
          component: () => import('@/views/InvoiceFormView.vue'),
          meta: { section: 'invoices', breadcrumbKey: 'newInvoice' },
        },
        {
          path: 'fakture/nova/profaktura',
          name: 'invoice-new-profaktura',
          component: () => import('@/views/InvoiceFormView.vue'),
          props: { documentType: 'profaktura' },
          meta: { section: 'invoices', breadcrumbKey: 'newProforma' },
        },
        {
          path: 'fakture/nova/avans',
          name: 'invoice-new-avans',
          component: () => import('@/views/InvoiceFormView.vue'),
          props: { documentType: 'avans' },
          meta: { section: 'invoices', breadcrumbKey: 'newAdvance' },
        },
        {
          path: 'fakture/:id/izmeni',
          name: 'invoice-edit',
          component: () => import('@/views/InvoiceFormView.vue'),
          props: true,
          meta: { section: 'invoices', breadcrumbKey: 'editInvoice' },
        },
        {
          path: 'fakture/:id',
          name: 'invoice-detail',
          component: () => import('@/views/InvoiceDetailView.vue'),
          props: true,
          meta: { section: 'invoices', breadcrumbKey: 'invoiceDetail' },
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
          meta: { wideContent: true },
        },
        {
          path: 'obaveze',
          name: 'obligations',
          component: () => import('@/views/ObligationsView.vue'),
          meta: { wideContent: true },
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
          meta: { wideContent: true },
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
          meta: { section: 'accounting', breadcrumbKey: 'organization', wideContent: true },
        },
        {
          path: 'pretplata',
          name: 'subscription',
          component: () => import('@/views/SubscriptionView.vue'),
          meta: { section: 'settings', breadcrumbKey: 'subscription' },
        },
        {
          path: 'finansije',
          name: 'finansije',
          component: () => import('@/views/FinansijeView.vue'),
        },
        {
          path: 'vise',
          name: 'vise',
          component: () => import('@/views/ViseView.vue'),
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
          meta: { wideContent: true },
        },
        {
          path: 'kompanije',
          name: 'admin-companies',
          component: () => import('@/views/admin/AdminCompaniesView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'pretplate',
          name: 'admin-subscriptions',
          component: () => import('@/views/admin/AdminSubscriptionsView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'planovi',
          name: 'admin-plans',
          component: () => import('@/views/admin/AdminPlansView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'fakture',
          name: 'admin-invoices',
          component: () => import('@/views/admin/AdminInvoicesView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'dokumenti',
          name: 'admin-documents',
          component: () => import('@/views/admin/AdminDocumentsView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'poreske-obaveze',
          name: 'admin-tax-obligations',
          component: () => import('@/views/admin/AdminTaxObligationsView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'pravila',
          name: 'admin-rules',
          component: () => import('@/views/admin/AdminRulesView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'obavestenja',
          name: 'admin-notifications',
          component: () => import('@/views/admin/AdminNotificationsView.vue'),
          meta: { wideContent: true },
        },
        {
          path: 'audit-log',
          name: 'admin-audit-log',
          component: () => import('@/views/admin/AdminAuditLogView.vue'),
          meta: { wideContent: true },
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
