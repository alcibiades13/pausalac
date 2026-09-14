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

function navLinkClass(routeName: string): string {
  const isActive = route.name === routeName
  return isActive
    ? 'rounded-lg px-3 py-1.5 text-sm font-medium bg-primary/10 text-primary whitespace-nowrap'
    : 'rounded-lg px-3 py-1.5 text-sm text-text-secondary hover:bg-background hover:text-primary whitespace-nowrap'
}

async function onExit() {
  await router.push({ name: 'home' })
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="sticky top-0 z-10 bg-surface shadow-[0_1px_2px_rgba(23,32,51,0.04),0_4px_16px_-8px_rgba(23,32,51,0.10)]">
      <div class="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-3">
        <span class="flex items-center gap-2">
          <span class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-navy to-text-secondary" aria-hidden="true" />
          <span class="font-display text-base font-semibold text-navy">System Admin</span>
        </span>
        <div class="flex items-center gap-2">
          <span class="hidden text-sm text-text-secondary sm:inline">{{ auth.user?.email }}</span>
          <Button variant="ghost" @click="onExit">Nazad u aplikaciju</Button>
        </div>
      </div>
      <nav class="mx-auto flex max-w-5xl items-center gap-1 overflow-x-auto px-4 pb-2">
        <RouterLink
          v-for="link in NAV_LINKS"
          :key="link.name"
          :to="{ name: link.name }"
          :class="navLinkClass(link.name)"
        >
          {{ link.label }}
        </RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-5xl px-4 py-8">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>
