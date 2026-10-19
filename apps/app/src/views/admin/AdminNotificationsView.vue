<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import { listAdminNotifications, type AdminNotification } from '@/services/admin'
import { formatDate } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const columns = computed<DataTableColumn<AdminNotification>[]>(() => [
  { key: 'company_name', label: t('admin.adminNotificationsView.companyColumn') },
  { key: 'recipient_email', label: t('admin.adminNotificationsView.recipientColumn') },
  { key: 'event_type', label: t('admin.adminNotificationsView.eventColumn') },
  { key: 'channel', label: t('admin.adminNotificationsView.channelColumn') },
  {
    key: 'created_at',
    label: t('admin.adminNotificationsView.dateColumn'),
    format: (r) => formatDate(r.created_at),
    sortable: true,
  },
])

const {
  rows: notifications,
  status,
  errorMessage,
  page,
  totalPages,
  hasNext,
  hasPrevious,
  sort,
  onSort,
  nextPage,
  prevPage,
  load,
} = useTableQuery<AdminNotification>(
  (q) => listAdminNotifications({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminNotificationsView.loadError') },
)

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminNotificationsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="notifications"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminNotificationsView.emptyTitle')"
      @sort="onSort"
    >
      <template #actions="{ row }">
        <Badge :variant="row.status === 'failed' ? 'danger' : 'neutral'">{{ row.status }}</Badge>
      </template>
    </DataTable>

    <Pagination
      :has-next="hasNext"
      :has-previous="hasPrevious"
      :page="page"
      :total-pages="totalPages"
      @next="nextPage"
      @previous="prevPage"
    />
  </div>
</template>
