<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, MoneyDisplay, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import { listAdminTaxObligations, type AdminTaxObligation } from '@/services/admin'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const STATUS_LABELS = computed<Record<string, string>>(() => ({
  pending: t('admin.adminTaxObligationsView.statusPending'),
  paid: t('admin.adminTaxObligationsView.statusPaid'),
  overdue: t('admin.adminTaxObligationsView.statusOverdue'),
}))
const STATUS_VARIANTS: Record<string, 'success' | 'warning' | 'danger' | 'neutral'> = {
  pending: 'neutral',
  paid: 'success',
  overdue: 'danger',
}

const columns = computed<DataTableColumn<AdminTaxObligation>[]>(() => [
  { key: 'company_name', label: t('admin.adminTaxObligationsView.companyColumn') },
  { key: 'period_start', label: t('admin.adminTaxObligationsView.periodColumn'), sortable: true },
  { key: 'due_date', label: t('admin.adminTaxObligationsView.dueDateColumn'), sortable: true },
])

const {
  rows: obligations,
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
} = useTableQuery<AdminTaxObligation>(
  (q) => listAdminTaxObligations({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminTaxObligationsView.loadError') },
)

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminTaxObligationsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="obligations"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminTaxObligationsView.emptyTitle')"
      @sort="onSort"
    >
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="STATUS_VARIANTS[row.status] ?? 'neutral'">
            {{ STATUS_LABELS[row.status] ?? row.status }}
          </Badge>
          <MoneyDisplay :amount="row.total_amount" currency="RSD" />
        </div>
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
