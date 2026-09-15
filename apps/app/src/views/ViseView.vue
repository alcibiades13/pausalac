<script setup lang="ts">
/**
 * Mobile "More" tab (master prompt §7/blueprint §5 name the tab but never
 * enumerate its contents) — the direct replacement for the mobile
 * hamburger dropdown removed from AppShell.vue in Phase 6d: everything
 * that dropdown used to reach (including logout) lives here now, as a
 * real page instead of an in-flow toggle. Deliberately lists every
 * secondary destination (including Limiti/KPO/Obaveze, which are also
 * reachable one tap sooner via the Finansije tab) rather than assuming a
 * user will discover the Finansije hub on their own — a "more" menu that
 * doesn't actually have everything defeats its own purpose.
 */
import { useRouter } from 'vue-router'
import { Card } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

// One or more <path> `d` strings per item — same hand-rolled inline-SVG
// convention as MobileBottomNav.vue/AppShell.vue (no icon library exists
// anywhere in the app).
const ICON_PATHS: Record<string, string[]> = {
  clients: ['M5 20c0-3.5 3-6 7-6s7 2.5 7 6', 'M12 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z'],
  limits: ['M4 20h16', 'M7 20v-6', 'M12 20V6', 'M17 20v-10'],
  kpo: [
    'M4 4.5A2.5 2.5 0 0 1 6.5 2H20v16H6.5A2.5 2.5 0 0 0 4 20.5V4.5Z',
    'M4 19.5A2.5 2.5 0 0 1 6.5 17H20',
  ],
  obligations: ['M3 5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5Z', 'M16 3v4M8 3v4M3 10h18'],
  documents: ['M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z'],
  accounting: [
    'M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z',
    'M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2',
  ],
  subscription: ['M2 6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6Z', 'M2 10h20'],
  settings: [
    'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1Z',
  ],
  notifications: [
    'M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5m6 0v1a3 3 0 1 1-6 0v-1m6 0H9',
  ],
}

const LINKS = [
  { name: 'clients', label: 'Klijenti' },
  { name: 'limits', label: 'Limiti' },
  { name: 'kpo', label: 'KPO' },
  { name: 'obligations', label: 'Obaveze' },
  { name: 'documents', label: 'Dokumenti' },
  { name: 'accounting', label: 'Računovođa' },
  { name: 'subscription', label: 'Pretplata' },
  { name: 'settings', label: 'Podešavanja' },
  { name: 'notifications', label: 'Obaveštenja' },
]

async function onLogout() {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Više</h1>

    <Card>
      <ul class="flex flex-col divide-y divide-border">
        <li v-for="link in LINKS" :key="link.name">
          <RouterLink
            :to="{ name: link.name }"
            class="-mx-2 flex items-center gap-3 rounded-lg px-2 py-3 text-sm text-navy hover:bg-background"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0 text-text-secondary" aria-hidden="true">
              <path v-for="d in ICON_PATHS[link.name]" :key="d" stroke-linecap="round" stroke-linejoin="round" :d="d" />
            </svg>
            <span class="flex-1">{{ link.label }}</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shrink-0 text-text-secondary" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="m9 6 6 6-6 6" />
            </svg>
          </RouterLink>
        </li>
      </ul>
    </Card>

    <Card>
      <button
        type="button"
        class="w-full rounded-lg px-2 py-2 text-left text-sm text-danger hover:bg-background"
        @click="onLogout"
      >
        Odjavi se
      </button>
    </Card>
  </div>
</template>
