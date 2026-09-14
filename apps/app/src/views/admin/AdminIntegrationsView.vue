<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Card, Skeleton } from '@pausalac/ui'
import { getAdminIntegrationsStatus, type AdminIntegrationsStatus } from '@/services/admin'
import { ApiError } from '@/lib/api'

const status = ref<AdminIntegrationsStatus | null>(null)
const loading = ref(true)
const errorMessage = ref('')

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    status.value = await getAdminIntegrationsStatus()
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo status integracija.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Integracije</h1>
    <p class="text-sm text-text-secondary">
      Stvarno stanje konfiguracije, ne lažna lista integracija koje ne postoje — SEF/fiskalizacija
      nema izabranog provajdera (master prompt §39), Sentry i produkt-analitika su ožičeni ali
      neaktivni seamovi dok se ne postavi provajder (Faza 6a).
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <Card v-if="loading">
      <Skeleton :count="4" />
    </Card>

    <Card v-else-if="status">
      <ul class="flex flex-col divide-y divide-border">
        <li class="flex items-center justify-between py-3">
          <span class="text-sm text-navy">Sentry (greške)</span>
          <Badge :variant="status.sentry.configured ? 'success' : 'neutral'">
            {{ status.sentry.configured ? 'Podešeno' : 'Nije podešeno' }}
          </Badge>
        </li>
        <li class="flex items-center justify-between py-3">
          <span class="text-sm text-navy">Skladište fajlova</span>
          <Badge :variant="status.storage.configured ? 'success' : 'danger'">
            {{ status.storage.configured ? 'Dostupno' : 'Nedostupno' }}
          </Badge>
        </li>
        <li class="flex items-center justify-between py-3">
          <span class="text-sm text-navy">Email server</span>
          <Badge :variant="status.email.configured ? 'success' : 'neutral'">
            {{ status.email.configured ? 'Podešeno' : 'Nije podešeno' }}
          </Badge>
        </li>
        <li class="flex flex-col gap-1 py-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-navy">SEF / fiskalizacija</span>
            <Badge variant="neutral">Nije podešeno</Badge>
          </div>
          <p class="text-xs text-text-secondary">{{ status.sef.note }}</p>
        </li>
      </ul>
    </Card>
  </div>
</template>
