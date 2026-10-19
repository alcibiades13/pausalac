<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import { listAdminDocuments, type AdminDocument } from '@/services/admin'
import { formatDate } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const columns = computed<DataTableColumn<AdminDocument>[]>(() => [
  { key: 'company_name', label: t('admin.adminDocumentsView.companyColumn') },
  { key: 'title', label: t('admin.adminDocumentsView.nameColumn') },
  { key: 'category', label: t('admin.adminDocumentsView.categoryColumn') },
  { key: 'uploaded_by_email', label: t('admin.adminDocumentsView.uploadedByColumn'), format: (r) => r.uploaded_by_email ?? '—' },
  {
    key: 'created_at',
    label: t('admin.adminDocumentsView.dateColumn'),
    format: (r) => formatDate(r.created_at),
    sortable: true,
  },
])

const {
  rows: documents,
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
} = useTableQuery<AdminDocument>(
  (q) => listAdminDocuments({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminDocumentsView.loadError') },
)

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminDocumentsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="documents"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminDocumentsView.emptyTitle')"
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
