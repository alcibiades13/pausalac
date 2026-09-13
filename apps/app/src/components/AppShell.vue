<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'

const auth = useAuthStore()
const company = useCompanyStore()
const router = useRouter()

async function onLogout() {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="border-b border-border bg-white">
      <div class="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <nav class="flex items-center gap-6">
          <span class="font-semibold text-navy">
            {{ company.currentCompany?.name ?? 'Pausalac' }}
          </span>
          <RouterLink
            :to="{ name: 'home' }"
            class="text-sm text-text-secondary hover:text-navy"
            active-class="text-navy font-medium"
          >
            Početna
          </RouterLink>
          <RouterLink
            :to="{ name: 'clients' }"
            class="text-sm text-text-secondary hover:text-navy"
            active-class="text-navy font-medium"
          >
            Klijenti
          </RouterLink>
          <RouterLink
            :to="{ name: 'invoices' }"
            class="text-sm text-text-secondary hover:text-navy"
            active-class="text-navy font-medium"
          >
            Fakture
          </RouterLink>
        </nav>
        <Button variant="ghost" @click="onLogout">Odjavi se</Button>
      </div>
    </header>
    <main class="mx-auto max-w-4xl px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
