<script setup lang="ts">
/**
 * Mobile "More" tab (master prompt §7/blueprint §5 name the tab but never
 * enumerate its contents) — the direct replacement for the mobile
 * hamburger dropdown removed from AppShell.vue in Phase 6d: everything
 * that dropdown used to reach (including logout) lives here now, as a
 * real page instead of an in-flow toggle.
 */
import { useRouter } from 'vue-router'
import { Card } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const LINKS = [
  { name: 'clients', label: 'Klijenti' },
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
            class="-mx-2 flex items-center justify-between rounded-lg px-2 py-3 text-sm text-navy hover:bg-background"
          >
            {{ link.label }}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
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
