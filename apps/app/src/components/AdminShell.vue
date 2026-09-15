<script setup lang="ts">
/**
 * Parallel to AppShell.vue, its own nested route tree under /admin
 * (master prompt §67/§114, Phase 6b). Deliberately separate from the
 * main app shell — this is a System Admin surface almost no user will
 * ever see, not a mode of the regular product nav.
 */
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from './AppSidebar.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const NAV_LINKS = [
  { name: 'admin-users', label: 'Korisnici' },
  { name: 'admin-companies', label: 'Kompanije' },
  { name: 'admin-subscriptions', label: 'Pretplate' },
  { name: 'admin-plans', label: 'Planovi' },
  { name: 'admin-invoices', label: 'Fakture' },
  { name: 'admin-documents', label: 'Dokumenti' },
  { name: 'admin-tax-obligations', label: 'Poreske obaveze' },
  { name: 'admin-rules', label: 'Regulatorna pravila' },
  { name: 'admin-notifications', label: 'Obaveštenja' },
  { name: 'admin-audit-log', label: 'Audit log' },
  { name: 'admin-integrations', label: 'Integracije' },
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
          <span class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-navy to-text-secondary" aria-hidden="true" />
          <span class="font-display text-base font-semibold text-navy">System Admin</span>
        </span>
        <Button variant="ghost" @click="onExit">Nazad u aplikaciju</Button>
      </div>
      <nav class="flex items-center gap-1 overflow-x-auto px-4 pb-2" aria-label="Admin navigacija">
        <RouterLink
          v-for="link in NAV_LINKS"
          :key="link.name"
          :to="{ name: link.name }"
          :class="navLinkClass(link.name, true)"
        >
          {{ link.label }}
        </RouterLink>
      </nav>
    </header>

    <!-- Tablet/desktop: same AppSidebar chrome AppShell.vue uses, text-only
         (no icons — 11 hand-drawn, visually-unverified icons for a
         rarely-used internal tool isn't a good trade). -->
    <AppSidebar nav-label="Admin navigacija">
      <template #header>
        <span class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-navy to-text-secondary" aria-hidden="true" />
        <span class="font-display text-base font-semibold text-navy">System Admin</span>
      </template>

      <RouterLink
        v-for="link in NAV_LINKS"
        :key="link.name"
        :to="{ name: link.name }"
        :class="navLinkClass(link.name)"
      >
        {{ link.label }}
      </RouterLink>

      <template #footer>
        <p class="truncate px-3 py-1 text-xs text-text-secondary">{{ auth.user?.email }}</p>
        <button
          type="button"
          class="rounded-lg px-3 py-2 text-left text-sm text-text-secondary hover:bg-background hover:text-primary"
          @click="onExit"
        >
          Nazad u aplikaciju
        </button>
      </template>
    </AppSidebar>

    <div class="sm:pl-64">
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
