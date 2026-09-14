<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { listNotifications } from '@/services/notifications'

const auth = useAuthStore()
const company = useCompanyStore()
const router = useRouter()
const route = useRoute()

const NAV_LINKS = [
  { name: 'home', label: 'Početna' },
  { name: 'clients', label: 'Klijenti' },
  { name: 'invoices', label: 'Fakture' },
  { name: 'limits', label: 'Limiti' },
  { name: 'kpo', label: 'KPO' },
  { name: 'obligations', label: 'Obaveze' },
  { name: 'documents', label: 'Dokumenti' },
]

const menuOpen = ref(false)
const unreadCount = ref(0)

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
    menuOpen.value = false
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
    <header class="border-b border-border bg-white">
      <div class="mx-auto flex max-w-4xl items-center justify-between gap-3 px-4 py-3">
        <span class="truncate font-semibold text-navy">
          {{ company.currentCompany?.name ?? 'Pausalac' }}
        </span>

        <!-- Desktop/tablet nav: hidden below sm, a plain row from sm up. -->
        <nav class="hidden items-center gap-5 sm:flex">
          <RouterLink
            v-for="link in NAV_LINKS"
            :key="link.name"
            :to="{ name: link.name }"
            class="text-sm text-text-secondary hover:text-navy"
            active-class="text-navy font-medium"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
        <div class="hidden items-center gap-4 sm:flex">
          <RouterLink
            :to="{ name: 'settings' }"
            class="text-sm text-text-secondary hover:text-navy"
            active-class="text-navy font-medium"
          >
            Podešavanja
          </RouterLink>
          <Button variant="ghost" @click="onLogout">Odjavi se</Button>
        </div>

        <!-- Bell: always visible regardless of viewport, not folded into
             the mobile menu — checking notifications is a primary action. -->
        <RouterLink
          :to="{ name: 'notifications' }"
          class="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-navy hover:bg-background"
          aria-label="Obaveštenja"
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
            class="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger px-1 text-[10px] font-medium text-white"
          >
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
        </RouterLink>

        <!-- Mobile: a single hamburger toggle instead of cramming every
             link into the header row (mobile-first — never let the nav
             force the header to grow or wrap). -->
        <button
          type="button"
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-navy hover:bg-background sm:hidden"
          :aria-expanded="menuOpen"
          aria-label="Meni"
          @click="menuOpen = !menuOpen"
        >
          <svg v-if="!menuOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <nav v-if="menuOpen" class="flex flex-col border-t border-border px-4 py-2 sm:hidden">
        <RouterLink
          v-for="link in NAV_LINKS"
          :key="link.name"
          :to="{ name: link.name }"
          class="rounded-lg px-2 py-2.5 text-sm text-text-secondary hover:bg-background hover:text-navy"
          active-class="text-navy font-medium"
        >
          {{ link.label }}
        </RouterLink>
        <RouterLink
          :to="{ name: 'settings' }"
          class="rounded-lg px-2 py-2.5 text-sm text-text-secondary hover:bg-background hover:text-navy"
          active-class="text-navy font-medium"
        >
          Podešavanja
        </RouterLink>
        <button
          type="button"
          class="rounded-lg px-2 py-2.5 text-left text-sm text-text-secondary hover:bg-background hover:text-navy"
          @click="onLogout"
        >
          Odjavi se
        </button>
      </nav>
    </header>
    <main class="mx-auto max-w-4xl px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
