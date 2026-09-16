<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert, EmptyState, Skeleton, Pagination } from '@pausalac/ui'
import { listClients, type Client } from '@/services/clients'
import { ApiError } from '@/lib/api'

const { t } = useI18n()
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
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.clientsListView.loadError')
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
      <h1 class="text-xl font-semibold text-navy">{{ t('dashboardInvoicesClients.clientsListView.title') }}</h1>
      <RouterLink :to="{ name: 'client-new' }">
        <Button>{{ t('dashboardInvoicesClients.clientsListView.newClientButton') }}</Button>
      </RouterLink>
    </div>

    <Input
      v-model="searchTerm"
      :label="t('dashboardInvoicesClients.clientsListView.searchLabel')"
      :placeholder="t('dashboardInvoicesClients.clientsListView.searchPlaceholder')"
      class="max-w-xs"
    />

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">{{ t('dashboardInvoicesClients.clientsListView.retryButton') }}</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="clients.length === 0">
      <EmptyState
        :title="t('dashboardInvoicesClients.clientsListView.emptyTitle')"
        :description="t('dashboardInvoicesClients.clientsListView.emptyDescription')"
      >
        <template #action>
          <RouterLink :to="{ name: 'client-new' }">
            <Button>{{ t('dashboardInvoicesClients.clientsListView.newClientButton') }}</Button>
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
                {{ t(`dashboardInvoicesClients.clientsListView.clientTypeLabels.${c.client_type}`) }}
              </span>
            </RouterLink>
          </li>
        </ul>
      </Card>

      <Pagination :has-next="hasNext" :has-previous="hasPrevious" @next="goNext" @previous="goPrevious" />
    </template>
  </div>
</template>
