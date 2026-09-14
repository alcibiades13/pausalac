<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Button, Card, Alert, EmptyState, Skeleton } from '@pausalac/ui'
import { listClients, type Client } from '@/services/clients'
import { ApiError } from '@/lib/api'

const clients = ref<Client[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    const page = await listClients()
    clients.value = page.results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo klijente.'
    status.value = 'error'
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">Klijenti</h1>
      <RouterLink :to="{ name: 'client-new' }">
        <Button>+ Novi klijent</Button>
      </RouterLink>
    </div>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="clients.length === 0">
      <EmptyState
        title="Još nemaš klijente."
        description="Prvi klijent može biti dodat za manje od minuta."
      >
        <template #action>
          <RouterLink :to="{ name: 'client-new' }">
            <Button>+ Novi klijent</Button>
          </RouterLink>
        </template>
      </EmptyState>
    </Card>

    <Card v-else>
      <ul class="flex flex-col divide-y divide-border">
        <li v-for="c in clients" :key="c.id" class="py-3">
          <RouterLink
            :to="{ name: 'client-edit', params: { id: c.id } }"
            class="-mx-2 flex flex-col gap-1 rounded-lg px-2 py-1 hover:bg-background sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p class="font-medium text-navy">{{ c.name }}</p>
              <p class="text-sm text-text-secondary">{{ c.email || c.phone || '—' }}</p>
            </div>
            <span class="text-sm text-text-secondary">
              {{ c.client_type === 'company' ? 'Pravno lice' : 'Fizičko lice' }}
            </span>
          </RouterLink>
        </li>
      </ul>
    </Card>
  </div>
</template>
