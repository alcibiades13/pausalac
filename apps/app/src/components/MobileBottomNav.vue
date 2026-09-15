<script setup lang="ts">
/**
 * Mobile bottom nav + global "+" quick-action button (master prompt §7,
 * blueprint §5, Phase 6d) — mobile-only (sm:hidden), replaces the old
 * hamburger dropdown in AppShell.vue (this + the "Više" page cover
 * everything the hamburger used to). §7's FAB menu lists 6 items; Fiskalni
 * račun (§40, fiscalization undefined) and Novi trošak (§76/78, V2) are
 * already-established Phase 6 exclusions, so only 4 real destinations ship.
 */
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const fabOpen = ref(false)

// Which AppShell-child route names count as "on" each tab — lets a
// sub-page (e.g. limits) still highlight its parent tab (Finansije)
// instead of showing no active tab at all.
const TAB_ROUTES: Record<string, string[]> = {
  home: ['home'],
  invoices: [
    'invoices',
    'invoice-new',
    'invoice-new-profaktura',
    'invoice-new-avans',
    'invoice-edit',
    'invoice-detail',
  ],
  finansije: ['finansije', 'limits', 'kpo', 'obligations'],
  vise: [
    'vise',
    'clients',
    'client-new',
    'client-edit',
    'documents',
    'accounting',
    'accounting-organization',
    'settings',
    'notifications',
    'subscription',
  ],
}

function tabClass(key: string): string {
  const name = route.name as string | undefined
  const isActive = !!name && TAB_ROUTES[key]!.includes(name)
  return isActive ? 'text-primary' : 'text-text-secondary'
}

// §7's FAB order minus the two already-excluded items (Fiskalni račun,
// Novi trošak — see file docstring).
const FAB_ITEMS = [
  { label: 'Nova faktura', to: { name: 'invoice-new' } },
  { label: 'Profaktura', to: { name: 'invoice-new-profaktura' } },
  { label: 'Avans', to: { name: 'invoice-new-avans' } },
  { label: 'Novi klijent', to: { name: 'client-new' } },
]

watch(
  () => route.fullPath,
  () => {
    fabOpen.value = false
  },
)
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-0 z-20 flex items-stretch justify-around border-t border-border bg-surface sm:hidden"
    aria-label="Glavna navigacija"
  >
    <RouterLink :to="{ name: 'home' }" class="flex flex-1 flex-col items-center justify-center gap-0.5 py-2 text-[11px]" :class="tabClass('home')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 10.5 12 4l8 6.5" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 9.5V20a1 1 0 0 0 1 1h3v-6h4v6h3a1 1 0 0 0 1-1V9.5" />
      </svg>
      <span>Početna</span>
    </RouterLink>

    <RouterLink :to="{ name: 'invoices' }" class="flex flex-1 flex-col items-center justify-center gap-0.5 py-2 text-[11px]" :class="tabClass('invoices')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M14 3v5h5" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 13h6M9 17h6" />
      </svg>
      <span>Fakture</span>
    </RouterLink>

    <div class="flex flex-1 items-center justify-center">
      <button
        type="button"
        class="relative -mt-6 flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-dark text-white shadow-lg shadow-primary/30"
        :aria-expanded="fabOpen"
        aria-label="Brza akcija"
        @click="fabOpen = !fabOpen"
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" d="M12 5v14M5 12h14" />
        </svg>
      </button>
    </div>

    <RouterLink :to="{ name: 'finansije' }" class="flex flex-1 flex-col items-center justify-center gap-0.5 py-2 text-[11px]" :class="tabClass('finansije')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 7a2 2 0 0 1 2-2h13a1 1 0 0 1 1 1v3" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 0 0 2 2h14a1 1 0 0 0 1-1v-4" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12h4a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-4a2 2 0 0 1 0-4Z" />
      </svg>
      <span>Finansije</span>
    </RouterLink>

    <RouterLink :to="{ name: 'vise' }" class="flex flex-1 flex-col items-center justify-center gap-0.5 py-2 text-[11px]" :class="tabClass('vise')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <circle cx="5" cy="12" r="1.6" />
        <circle cx="12" cy="12" r="1.6" />
        <circle cx="19" cy="12" r="1.6" />
      </svg>
      <span>Više</span>
    </RouterLink>
  </nav>

  <Teleport to="body">
    <div v-if="fabOpen" class="fixed inset-0 z-30 sm:hidden">
      <div class="absolute inset-0 bg-navy/40" @click="fabOpen = false" />
      <div class="absolute inset-x-0 bottom-0 flex flex-col gap-1 rounded-t-2xl bg-surface p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-[0_-4px_24px_rgba(23,32,51,0.12)]">
        <RouterLink
          v-for="item in FAB_ITEMS"
          :key="item.label"
          :to="item.to"
          class="rounded-lg px-4 py-3 text-sm font-medium text-navy hover:bg-background"
        >
          {{ item.label }}
        </RouterLink>
      </div>
    </div>
  </Teleport>
</template>
