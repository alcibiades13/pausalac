<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { Button, Card, Input, Alert, EmptyState, Skeleton } from '@pausalac/ui'
import { listClients, type Client } from '@/services/clients'
import { ApiError } from '@/lib/api'

const clients = ref<Client[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
const searchTerm = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

async function load() {
  status.value = 'loading'
  try {
    const result = await listClients({ page: page.value, search: searchTerm.value || undefined })
    clients.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo klijente.'
    status.value = 'error'
  }
}

onMounted(load)
watch(searchTerm, () => {
  page.value = 1
  load()
})

function goNext() {
  page.value += 1
  load()
}
function goPrevious() {
  page.value = Math.max(1, page.value - 1)
  load()
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">Klijenti</h1>
      <RouterLink :to="{ name: 'client-new' }">
        <Button>+ Novi klijent</Button>
      </RouterLink>
    </div>

    <Input v-model="searchTerm" label="Pretraga" placeholder="Naziv, PIB, email..." class="max-w-xs" />

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

    <template v-else>
      <Card>
        <ul class="flex flex-col divide-y divide-border">
          <li v-for="c in clients" :key="c.id" class="py-3">
            <RouterLink
              :to="{ name: 'client-detail', params: { id: c.id } }"
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

      <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
        <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
        <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
      </div>
    </template>
  </div>
</template>
