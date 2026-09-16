<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { listNotifications } from '@/services/notifications'
import MobileBottomNav from './MobileBottomNav.vue'
import AppSidebar from './AppSidebar.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'

const auth = useAuthStore()
const company = useCompanyStore()
const router = useRouter()
const route = useRoute()

// Each entry's `icon` is one <path>'s `d` attribute (all icons share the
// same 24x24/stroke-2/round-cap convention MobileBottomNav.vue already
// established) — Početna/Fakture reuse that file's exact paths.
const NAV_LINKS = [
  {
    name: 'home',
    label: 'Početna',
    icon: 'M4 10.5 12 4l8 6.5;M6 9.5V20a1 1 0 0 0 1 1h3v-6h4v6h3a1 1 0 0 0 1-1V9.5',
  },
  { name: 'clients', label: 'Klijenti', icon: 'M5 20a7 7 0 0 1 14 0' },
  {
    name: 'invoices',
    label: 'Fakture',
    icon: 'M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z;M14 3v5h5;M9 13h6M9 17h6',
  },
  { name: 'limits', label: 'Limiti', icon: 'M4 20V11M12 20V4M20 20v-6' },
  {
    name: 'kpo',
    label: 'KPO',
    icon: 'M4 6.5A1.5 1.5 0 0 1 5.5 5H11v14H5.5A1.5 1.5 0 0 1 4 17.5v-11Z;M20 6.5A1.5 1.5 0 0 0 18.5 5H13v14h5.5a1.5 1.5 0 0 0 1.5-1.5v-11Z',
  },
  { name: 'obligations', label: 'Obaveze', icon: 'M4 10h16M8 3v4M16 3v4' },
  {
    name: 'documents',
    label: 'Dokumenti',
    icon: 'M4 7.5A1.5 1.5 0 0 1 5.5 6H10l2 2h6.5A1.5 1.5 0 0 1 20 9.5v8A1.5 1.5 0 0 1 18.5 19h-13A1.5 1.5 0 0 1 4 17.5v-10Z',
  },
  {
    name: 'accounting',
    label: 'Računovođa',
    icon: 'M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2;M3 13h18',
  },
]

const unreadCount = ref(0)

// Deliberately not `class="..." active-class="..."`: RouterLink appends
// active-class alongside the base class rather than replacing it, and
// `text-text-secondary`/`text-primary` are equal-specificity utilities —
// Tailwind happens to emit `.text-text-secondary` after `.text-primary`
// in the compiled stylesheet, so the "active" color silently lost the
// cascade and only font-weight ever visibly changed. A background pill
// (mutually exclusive classes, never both colors on the element at once)
// both fixes that and reads as a much clearer active indicator.
function navLinkClass(routeName: string): string {
  const isActive = route.name === routeName
  if (isActive) {
    return 'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium bg-primary/10 text-primary'
  }
  return 'flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary'
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
      Preskoči na sadržaj
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
            aria-label="Aktivna kompanija"
            class="max-w-[9rem] truncate rounded-lg border border-transparent bg-transparent py-0.5 font-display text-base font-semibold text-navy hover:border-border focus:border-primary focus:outline-none"
            @change="onSwitchCompany"
          >
            <option v-for="c in company.companies" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <span v-else class="truncate font-display text-base font-semibold text-navy">
            {{ company.currentCompany?.name ?? 'Pausalac' }}
          </span>
        </span>

        <RouterLink
          :to="{ name: 'notifications' }"
          class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-navy hover:bg-background"
          :aria-label="unreadCount > 0 ? `Obaveštenja (${unreadCount} nepročitanih)` : 'Obaveštenja'"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5m6 0v1a3 3 0 1 1-6 0v-1m6 0H9"
            />
          </svg>
          <span
            v-if="unreadCount > 0"
            class="absolute right-1 top-1 flex h-4 min-w-4 animate-pulse items-center justify-center rounded-full bg-danger px-1 text-[10px] font-medium text-white"
            aria-hidden="true"
          >
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
        </RouterLink>
      </div>
    </header>

    <!-- Tablet/desktop: persistent left sidebar (hidden below sm:, see
         AppSidebar.vue). Logo/switcher up top, nav in the middle,
         notifications/settings/logout pinned to the bottom. -->
    <AppSidebar>
      <template #header>
        <span
          class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-primary to-primary-dark"
          aria-hidden="true"
        />
        <select
          v-if="company.companies.length > 1"
          :value="company.currentCompanyId ?? undefined"
          aria-label="Aktivna kompanija"
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
        {{ link.label }}
      </RouterLink>

      <template #footer>
        <RouterLink
          :to="{ name: 'notifications' }"
          :class="navLinkClass('notifications')"
          :aria-label="unreadCount > 0 ? `Obaveštenja (${unreadCount} nepročitanih)` : 'Obaveštenja'"
        >
          <span class="relative flex shrink-0 items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5m6 0v1a3 3 0 1 1-6 0v-1m6 0H9"
              />
            </svg>
            <span
              v-if="unreadCount > 0"
              class="absolute -right-1 -top-1 flex h-4 min-w-4 animate-pulse items-center justify-center rounded-full bg-danger px-1 text-[10px] font-medium text-white"
              aria-hidden="true"
            >
              {{ unreadCount > 9 ? '9+' : unreadCount }}
            </span>
          </span>
          Obaveštenja
        </RouterLink>
        <RouterLink :to="{ name: 'settings' }" :class="navLinkClass('settings')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h12M20 18h0" />
            <circle cx="15" cy="6" r="2" />
            <circle cx="7" cy="12" r="2" />
            <circle cx="16" cy="18" r="2" />
          </svg>
          Podešavanja
        </RouterLink>
        <div class="px-3 py-2">
          <LanguageSwitcher />
        </div>
        <button
          type="button"
          class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary"
          @click="onLogout"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 16l5-4-5-4" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12H3" />
          </svg>
          Odjavi se
        </button>
      </template>
    </AppSidebar>

    <div class="sm:pl-64">
      <main id="main-content" class="mx-auto max-w-5xl px-4 py-8 pb-24 sm:pb-8">
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
