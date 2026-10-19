<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { listNotifications } from '@/services/notifications'
import MobileBottomNav from './MobileBottomNav.vue'
import AppSidebar from './AppSidebar.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'
import NotificationBell from './NotificationBell.vue'
import DropdownMenu from './DropdownMenu.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'

const { t } = useI18n()
const auth = useAuthStore()
const company = useCompanyStore()
const router = useRouter()
const route = useRoute()

// Each entry's `icon` is one <path>'s `d` attribute (all icons share the
// same 24x24/stroke-2/round-cap convention MobileBottomNav.vue already
// established) — Početna/Fakture reuse that file's exact paths. `name`
// doubles as the i18n key under authShell.appShell.navLinks.* (see
// template) since it's already a unique per-entry identifier, and as a
// valid `route.meta.section` value for Breadcrumb (see below).
const NAV_LINKS = [
  {
    name: 'home',
    icon: 'M4 10.5 12 4l8 6.5;M6 9.5V20a1 1 0 0 0 1 1h3v-6h4v6h3a1 1 0 0 0 1-1V9.5',
  },
  { name: 'clients', icon: 'M5 20a7 7 0 0 1 14 0' },
  {
    name: 'invoices',
    icon: 'M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z;M14 3v5h5;M9 13h6M9 17h6',
  },
  { name: 'limits', icon: 'M4 20V11M12 20V4M20 20v-6' },
  {
    name: 'kpo',
    icon: 'M4 6.5A1.5 1.5 0 0 1 5.5 5H11v14H5.5A1.5 1.5 0 0 1 4 17.5v-11Z;M20 6.5A1.5 1.5 0 0 0 18.5 5H13v14h5.5a1.5 1.5 0 0 0 1.5-1.5v-11Z',
  },
  { name: 'obligations', icon: 'M4 10h16M8 3v4M16 3v4' },
  {
    name: 'documents',
    icon: 'M4 7.5A1.5 1.5 0 0 1 5.5 6H10l2 2h6.5A1.5 1.5 0 0 1 20 9.5v8A1.5 1.5 0 0 1 18.5 19h-13A1.5 1.5 0 0 1 4 17.5v-10Z',
  },
  {
    name: 'accounting',
    icon: 'M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2;M3 13h18',
  },
]

// Desktop equivalent of MobileBottomNav.vue's FAB — same 4 real
// destinations, same i18n keys (authShell.mobileBottomNav.fab.*), on
// purpose: one action model on both platforms, not two lists that can
// drift apart. Fiskalni račun/Novi trošak are excluded there for real
// reasons (fiscalization integration undefined, Novi trošak is a V2
// item — see that file's docstring), not an oversight to "fix" here by
// inventing a longer desktop-only list.
const QUICK_CREATE_ITEMS = [
  { labelKey: 'newInvoice', to: { name: 'invoice-new' } },
  { labelKey: 'proforma', to: { name: 'invoice-new-profaktura' } },
  { labelKey: 'advance', to: { name: 'invoice-new-avans' } },
  { labelKey: 'newClient', to: { name: 'client-new' } },
]

const unreadCount = ref(0)

// Deliberately not `class="..." active-class="..."`: RouterLink appends
// active-class alongside the base class rather than replacing it, and
// `text-text-secondary`/`text-primary-dark` are equal-specificity utilities —
// Tailwind happens to emit `.text-text-secondary` after `.text-primary-dark`
// in the compiled stylesheet, so the "active" color silently lost the
// cascade and only font-weight ever visibly changed. A background pill
// (mutually exclusive classes, never both colors on the element at once)
// both fixes that and reads as a much clearer active indicator.
function navLinkClass(routeName: string): string {
  const isActive = route.name === routeName
  if (isActive) {
    return 'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium bg-primary/10 text-primary-dark'
  }
  return 'flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary-dark'
}

// A user who belongs to more than one company (typically an accounting
// org's staff member — Phase 4a) needs a way to change which one is
// active; a typical single-company paušalac never sees this at all.
async function onSwitchCompany(event: Event) {
  const id = Number((event.target as HTMLSelectElement).value)
  company.setCurrentCompany(id)
  // Views don't individually react to a company switch — send the user
  // back to a known-good screen rather than plumbing reactivity through
  // every view's own data-loading code.
  await router.push({ name: 'home' })
}

async function refreshUnreadCount() {
  try {
    unreadCount.value = (await listNotifications({ isRead: false })).count
  } catch {
    // A failed badge fetch shouldn't block navigation — just leave the
    // count as-is.
  }
}

onMounted(refreshUnreadCount)
watch(
  () => route.fullPath,
  () => {
    refreshUnreadCount()
  },
)

const notificationsAriaLabel = computed(() =>
  unreadCount.value > 0
    ? t('authShell.appShell.notificationsAriaCount', { count: unreadCount.value })
    : t('authShell.appShell.notificationsAriaLabel'),
)

// Breadcrumb (TopHeader, desktop/tablet only): only shows on routes one
// level *below* a NAV_LINKS entry (route.meta.section set — router/
// index.ts), e.g. client-detail/invoice-new. Top-level pages themselves
// (Clients, Invoices, ...) show nothing here — the sidebar already
// marks the active section, and each of those views has its own bare
// page-level heading; a breadcrumb repeating that same name a third
// time was real, reported redundancy, not orientation. Genuinely
// nested routes are where a breadcrumb (plus a working back button)
// earns its place, since the sidebar can't show that depth.
const breadcrumbSection = computed(() => {
  const section = route.meta.section as string | undefined
  return section ? t('authShell.breadcrumb.sections.' + section) : undefined
})
const breadcrumbLeaf = computed(() => {
  const key = route.meta.breadcrumbKey as string | undefined
  return key ? t('authShell.breadcrumb.leaves.' + key) : undefined
})

// First name/last name initials, falling back to the email's first
// letter — no avatar photo upload exists anywhere in this product, an
// initials circle is the honest option rather than a placeholder image.
const userInitials = computed(() => {
  const user = auth.user
  if (!user) return '?'
  const first = user.first_name?.trim()?.[0]
  const last = user.last_name?.trim()?.[0]
  if (first || last) return `${first ?? ''}${last ?? ''}`.toUpperCase()
  return (user.email?.[0] ?? '?').toUpperCase()
})

async function onLogout() {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-white"
    >
      {{ t('authShell.appShell.skipToContent') }}
    </a>

    <!-- Mobile-only top bar: logo/company-switcher + notification bell.
         Nav lives in MobileBottomNav.vue; sidebar (below) takes over
         from sm: up, so this whole header disappears there. -->
    <header class="sticky top-0 z-10 bg-surface shadow-[0_1px_2px_rgba(23,32,51,0.04),0_4px_16px_-8px_rgba(23,32,51,0.10)] sm:hidden">
      <div class="flex items-center justify-between gap-3 px-4 py-3">
        <span class="flex min-w-0 items-center gap-2">
          <span
            class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-primary to-primary-dark"
            aria-hidden="true"
          />
          <select
            v-if="company.companies.length > 1"
            :value="company.currentCompanyId ?? undefined"
            :aria-label="t('authShell.appShell.activeCompanyLabel')"
            class="max-w-[9rem] truncate rounded-lg border border-transparent bg-transparent py-0.5 font-display text-base font-semibold text-navy hover:border-border focus:border-primary focus:outline-none"
            @change="onSwitchCompany"
          >
            <option v-for="c in company.companies" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <span v-else class="truncate font-display text-base font-semibold text-navy">
            {{ company.currentCompany?.name ?? 'Pausalac' }}
          </span>
        </span>

        <NotificationBell :unread-count="unreadCount" :label="notificationsAriaLabel" />
      </div>
    </header>

    <!-- Tablet/desktop: persistent left sidebar (hidden below sm:, see
         AppSidebar.vue). Logo/switcher up top, nav in the middle,
         Settings pinned to the footer as before — an empty footer read
         as sparse (user feedback), so only language/notifications/
         logout moved into TopHeader below, not Settings. -->
    <AppSidebar :nav-label="t('authShell.appShell.navLabel')">
      <template #header>
        <span
          class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-primary to-primary-dark"
          aria-hidden="true"
        />
        <select
          v-if="company.companies.length > 1"
          :value="company.currentCompanyId ?? undefined"
          :aria-label="t('authShell.appShell.activeCompanyLabel')"
          class="min-w-0 flex-1 truncate rounded-lg border border-transparent bg-transparent py-0.5 font-display text-base font-semibold text-navy hover:border-border focus:border-primary focus:outline-none"
          @change="onSwitchCompany"
        >
          <option v-for="c in company.companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <span v-else class="min-w-0 flex-1 truncate font-display text-base font-semibold text-navy">
          {{ company.currentCompany?.name ?? 'Pausalac' }}
        </span>
      </template>

      <RouterLink
        v-for="link in NAV_LINKS"
        :key="link.name"
        :to="{ name: link.name }"
        :class="navLinkClass(link.name)"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0" aria-hidden="true">
          <path
            v-for="(d, i) in link.icon.split(';')"
            :key="i"
            stroke-linecap="round"
            stroke-linejoin="round"
            :d="d"
          />
        </svg>
        {{ t('authShell.appShell.navLinks.' + link.name) }}
      </RouterLink>

      <template #footer>
        <RouterLink :to="{ name: 'settings' }" :class="navLinkClass('settings')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h12M20 18h0" />
            <circle cx="15" cy="6" r="2" />
            <circle cx="7" cy="12" r="2" />
            <circle cx="16" cy="18" r="2" />
          </svg>
          {{ t('authShell.appShell.settingsLink') }}
        </RouterLink>
      </template>
    </AppSidebar>

    <div class="sm:pl-64">
      <!-- Desktop/tablet-only top header: breadcrumb + back button on the
           left, search (placeholder — no global search exists yet, a
           real one is a separate later phase)/notifications/language/
           user menu on the right. Language moving here (out of the
           sidebar footer, where it read as an awkward extra row wedged
           between Settings and Odjavi se) was the whole reason this
           exists — Settings stayed in the sidebar footer (user
           feedback: moving it out left the footer looking sparse), and
           the user menu here is just the logout action, per the
           original ask. -->
      <header class="sticky top-0 z-10 hidden h-16 items-center justify-between gap-4 border-b border-border bg-surface px-6 sm:flex">
        <AppBreadcrumb
          :section-label="breadcrumbSection"
          :leaf-label="breadcrumbLeaf"
          :show-back="!!breadcrumbLeaf"
          :back-label="t('authShell.topHeader.backButtonLabel')"
          @back="router.back()"
        />

        <div class="flex shrink-0 items-center gap-2">
          <!-- Desktop equivalent of the mobile FAB (MobileBottomNav.vue) —
               same 4 destinations, so a user who's anywhere in the app
               (not just on /fakture) can start the most common actions
               without losing their place. -->
          <DropdownMenu
            :label="t('authShell.topHeader.quickCreateLabel')"
            menu-width-class="w-56"
            trigger-class="flex items-center gap-1.5 rounded-lg bg-gradient-to-br from-primary to-primary-dark px-3 py-2 text-sm font-medium text-white hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            <template #trigger>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <line x1="12" y1="5" x2="12" y2="19" stroke-linecap="round" />
                <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" />
              </svg>
              {{ t('authShell.topHeader.quickCreateButton') }}
            </template>
            <RouterLink
              v-for="item in QUICK_CREATE_ITEMS"
              :key="item.labelKey"
              :to="item.to"
              class="flex w-full items-center px-4 py-2 text-left text-sm text-text-secondary hover:bg-background hover:text-primary-dark"
            >
              {{ t('authShell.mobileBottomNav.fab.' + item.labelKey) }}
            </RouterLink>
          </DropdownMenu>

          <div class="relative hidden lg:block">
            <svg
              class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" stroke-linecap="round" />
            </svg>
            <input
              type="search"
              disabled
              :placeholder="t('authShell.topHeader.searchPlaceholder')"
              :aria-label="t('authShell.topHeader.searchAriaLabel')"
              class="w-56 rounded-lg border border-border bg-background py-2 pl-9 pr-3 text-sm text-navy placeholder:text-text-secondary disabled:cursor-not-allowed"
            />
          </div>

          <NotificationBell :unread-count="unreadCount" :label="notificationsAriaLabel" />
          <LanguageSwitcher />

          <DropdownMenu
            :label="t('authShell.topHeader.userMenuLabel')"
            trigger-class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-dark text-sm font-semibold text-white hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            <template #trigger>{{ userInitials }}</template>
            <button
              type="button"
              class="flex w-full items-center px-4 py-2 text-left text-sm text-text-secondary hover:bg-background hover:text-primary-dark"
              @click="onLogout"
            >
              {{ t('authShell.appShell.logoutButton') }}
            </button>
          </DropdownMenu>
        </div>
      </header>

      <main
        id="main-content"
        class="mx-auto px-4 py-8 pb-24 sm:pb-8"
        :class="route.meta.wideContent ? 'max-w-[1600px]' : 'max-w-5xl'"
      >
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
    <MobileBottomNav />
  </div>
</template>
