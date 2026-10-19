<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import { listAdminAuditLog, type AdminAuditLogEntry } from '@/services/admin'
import { formatDateTime } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const columns = computed<DataTableColumn<AdminAuditLogEntry>[]>(() => [
  {
    key: 'created_at',
    label: t('admin.adminAuditLogView.createdAtColumn'),
    format: (r) => formatDateTime(r.created_at),
    sortable: true,
  },
  {
    key: 'actor_email',
    label: t('admin.adminAuditLogView.actorColumn'),
    format: (r) => r.actor_email ?? t('admin.adminAuditLogView.systemFallback'),
  },
  { key: 'company_name', label: t('admin.adminAuditLogView.companyColumn'), format: (r) => r.company_name ?? '—' },
  { key: 'entity_type', label: t('admin.adminAuditLogView.entityColumn') },
  { key: 'action', label: t('admin.adminAuditLogView.actionColumn') },
])

const {
  rows: entries,
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
} = useTableQuery<AdminAuditLogEntry>(
  (q) => listAdminAuditLog({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminAuditLogView.loadError') },
)

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminAuditLogView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="entries"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminAuditLogView.emptyTitle')"
      @sort="onSort"
    />

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
