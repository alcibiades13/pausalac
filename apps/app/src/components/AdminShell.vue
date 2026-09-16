<script setup lang="ts">
/**
 * Parallel to AppShell.vue, its own nested route tree under /admin
 * (master prompt §67/§114, Phase 6b). Deliberately separate from the
 * main app shell — this is a System Admin surface almost no user will
 * ever see, not a mode of the regular product nav.
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from './AppSidebar.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'
import UserMenu from './UserMenu.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'

const { t } = useI18n()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

// `name` doubles as the i18n key under authShell.adminShell.navLinks.*
// (see template) since it's already a unique per-entry identifier.
const NAV_LINKS = [
  { name: 'admin-users' },
  { name: 'admin-companies' },
  { name: 'admin-subscriptions' },
  { name: 'admin-plans' },
  { name: 'admin-invoices' },
  { name: 'admin-documents' },
  { name: 'admin-tax-obligations' },
  { name: 'admin-rules' },
  { name: 'admin-notifications' },
  { name: 'admin-audit-log' },
  { name: 'admin-integrations' },
]

function navLinkClass(routeName: string, mobile = false): string {
  const isActive = route.name === routeName
  const base = mobile
    ? 'rounded-lg px-3 py-1.5 text-sm whitespace-nowrap'
    : 'rounded-lg px-3 py-2 text-sm'
  return isActive
    ? `${base} font-medium bg-primary/10 text-primary`
    : `${base} text-text-secondary hover:bg-background hover:text-primary`
}

// Admin's nav is flat (no nested detail pages under a section the way
// the main app has invoice-detail/client-detail etc.), so the
// breadcrumb never needs a back button — every page IS the leaf, always
// one level under the fixed "System Admin" root.
const breadcrumbLeaf = computed(() => t('authShell.adminShell.navLinks.' + (route.name as string)))

const userInitials = computed(() => {
  const user = auth.user
  if (!user) return '?'
  const first = user.first_name?.trim()?.[0]
  const last = user.last_name?.trim()?.[0]
  if (first || last) return `${first ?? ''}${last ?? ''}`.toUpperCase()
  return (user.email?.[0] ?? '?').toUpperCase()
})

async function onExit() {
  await router.push({ name: 'home' })
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Mobile-only: admin has no separate bottom-nav component (unlike
         AppShell/MobileBottomNav.vue), so this header — nav row
         included — stays the only nav below sm:; the sidebar (below)
         takes over from sm: up. -->
    <header class="sticky top-0 z-10 bg-surface shadow-[0_1px_2px_rgba(23,32,51,0.04),0_4px_16px_-8px_rgba(23,32,51,0.10)] sm:hidden">
      <div class="flex items-center justify-between gap-3 px-4 py-3">
        <span class="flex items-center gap-2">
          <span class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-navy to-secondary" aria-hidden="true" />
          <span class="font-display text-base font-semibold text-navy">{{ t('authShell.adminShell.title') }}</span>
        </span>
        <button
          type="button"
          class="rounded-lg px-3 py-1.5 text-sm text-text-secondary hover:bg-background hover:text-primary"
          @click="onExit"
        >
          {{ t('authShell.adminShell.backToAppButton') }}
        </button>
      </div>
      <nav class="flex items-center gap-1 overflow-x-auto px-4 pb-2" :aria-label="t('authShell.adminShell.navLabel')">
        <RouterLink
          v-for="link in NAV_LINKS"
          :key="link.name"
          :to="{ name: link.name }"
          :class="navLinkClass(link.name, true)"
        >
          {{ t('authShell.adminShell.navLinks.' + link.name) }}
        </RouterLink>
      </nav>
    </header>

    <!-- Tablet/desktop: same AppSidebar chrome AppShell.vue uses, text-only
         (no icons — 11 hand-drawn, visually-unverified icons for a
         rarely-used internal tool isn't a good trade). No footer slot
         content anymore — language/account moved into the top header,
         same reasoning as AppShell.vue. -->
    <AppSidebar :nav-label="t('authShell.adminShell.navLabel')">
      <template #header>
        <span class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-navy to-secondary" aria-hidden="true" />
        <span class="font-display text-base font-semibold text-navy">{{ t('authShell.adminShell.title') }}</span>
      </template>

      <RouterLink
        v-for="link in NAV_LINKS"
        :key="link.name"
        :to="{ name: link.name }"
        :class="navLinkClass(link.name)"
      >
        {{ t('authShell.adminShell.navLinks.' + link.name) }}
      </RouterLink>
    </AppSidebar>

    <div class="sm:pl-64">
      <header class="sticky top-0 z-10 hidden h-16 items-center justify-between gap-4 border-b border-border bg-surface px-6 sm:flex">
        <AppBreadcrumb
          :section-label="t('authShell.adminShell.title')"
          :leaf-label="breadcrumbLeaf"
          :show-back="false"
          :back-label="t('authShell.topHeader.backButtonLabel')"
        />

        <div class="flex shrink-0 items-center gap-2">
          <LanguageSwitcher />
          <UserMenu :initials="userInitials" :label="t('authShell.topHeader.userMenuLabel')">
            <p class="truncate border-b border-border px-4 py-2 text-xs text-text-secondary">{{ auth.user?.email }}</p>
            <button
              type="button"
              class="flex w-full items-center px-4 py-2 text-left text-sm text-text-secondary hover:bg-background hover:text-primary"
              @click="onExit"
            >
              {{ t('authShell.adminShell.backToAppButton') }}
            </button>
          </UserMenu>
        </div>
      </header>

      <main class="mx-auto max-w-5xl px-4 py-8">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>
