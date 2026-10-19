<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert, EmptyState, DataTable, Pagination, Skeleton, type DataTableColumn } from '@pausalac/ui'
import { listClients, type Client } from '@/services/clients'
import { useTableQuery } from '@/composables/useTableQuery'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()
const router = useRouter()

const columns: DataTableColumn<Client>[] = [
  { key: 'name', label: t('dashboardInvoicesClients.clientsListView.columnName'), sortable: true },
  { key: 'tax_id', label: t('dashboardInvoicesClients.clientsListView.columnTaxId') },
  { key: 'email', label: t('dashboardInvoicesClients.clientsListView.columnEmail') },
  { key: 'client_type', label: t('dashboardInvoicesClients.clientsListView.columnType') },
  { key: 'created_at', label: t('dashboardInvoicesClients.clientsListView.columnCreatedAt'), sortable: true },
]

const {
  rows: clients,
  status,
  errorMessage,
  page,
  totalPages,
  hasNext,
  hasPrevious,
  search,
  sort,
  onSort,
  nextPage,
  prevPage,
  load,
  reload,
} = useTableQuery<Client>(
  (q) =>
    listClients({
      page: q.page,
      pageSize: q.pageSize,
      search: q.search,
      ordering: q.ordering,
    }),
  { genericErrorMessage: t('dashboardInvoicesClients.clientsListView.loadError') },
)

onMounted(load)

function onRowClick(client: Client) {
  router.push({ name: 'client-detail', params: { id: client.id } })
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

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="reload">{{ t('dashboardInvoicesClients.clientsListView.retryButton') }}</button>
    </Alert>

    <Card v-else>
      <div class="border-b border-border pb-4">
        <Input
          v-model="search"
          label-sr-only
          :label="t('dashboardInvoicesClients.clientsListView.searchLabel')"
          :placeholder="t('dashboardInvoicesClients.clientsListView.searchPlaceholder')"
          class="max-w-xs"
        />
      </div>

      <Skeleton v-if="status === 'loading' && clients.length === 0" class="mt-4" :count="3" />

      <EmptyState
        v-else-if="clients.length === 0"
        class="mt-4"
        :title="t('dashboardInvoicesClients.clientsListView.emptyTitle')"
        :description="t('dashboardInvoicesClients.clientsListView.emptyDescription')"
      >
        <template #action>
          <RouterLink :to="{ name: 'client-new' }">
            <Button>{{ t('dashboardInvoicesClients.clientsListView.newClientButton') }}</Button>
          </RouterLink>
        </template>
      </EmptyState>

      <template v-else>
        <DataTable
          class="mt-4"
          :columns="columns"
          :rows="clients"
          :loading="status === 'loading'"
          :sort="sort"
          row-clickable
          @sort="onSort"
          @row-click="onRowClick"
        >
          <template #cell-name="{ row }">
            <span class="font-medium text-navy">{{ row.name }}</span>
          </template>
          <template #cell-email="{ row }">
            {{ row.email || row.phone || '—' }}
          </template>
          <template #cell-client_type="{ row }">
            {{ t(`dashboardInvoicesClients.clientsListView.clientTypeLabels.${row.client_type}`) }}
          </template>
          <template #cell-created_at="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </DataTable>

        <Pagination
          class="mt-4"
          :has-next="hasNext"
          :has-previous="hasPrevious"
          :page="page"
          :total-pages="totalPages"
          @next="nextPage"
          @previous="prevPage"
        />
      </template>
    </Card>
  </div>
</template>
