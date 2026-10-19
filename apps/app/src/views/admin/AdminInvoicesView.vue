<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, MoneyDisplay, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import { listAdminInvoices, type AdminInvoice } from '@/services/admin'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

// `due_date` wasn't shown as a column before — added here because it's
// the one field (besides `created_at`, which isn't otherwise interesting
// to an admin) the backend actually supports ordering by
// (AdminInvoiceListView.ordering_fields); without it this view would get
// zero sortable columns despite the backend being ready for them.
const columns = computed<DataTableColumn<AdminInvoice>[]>(() => [
  { key: 'company_name', label: t('admin.adminInvoicesView.companyColumn') },
  { key: 'client_name', label: t('admin.adminInvoicesView.clientColumn') },
  { key: 'invoice_number', label: t('admin.adminInvoicesView.numberColumn'), format: (r) => r.invoice_number ?? t('admin.adminInvoicesView.draftFallback') },
  { key: 'issue_date', label: t('admin.adminInvoicesView.issueDateColumn') },
  { key: 'due_date', label: t('admin.adminInvoicesView.dueDateColumn'), sortable: true },
])

const {
  rows: invoices,
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
} = useTableQuery<AdminInvoice>(
  (q) => listAdminInvoices({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminInvoicesView.loadError') },
)

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminInvoicesView.title') }}</h1>
    <p class="text-sm text-text-secondary">
      {{ t('admin.adminInvoicesView.description') }}
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="invoices"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminInvoicesView.emptyTitle')"
      @sort="onSort"
    >
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <InvoiceStatusBadge :status="row.status" />
          <MoneyDisplay :amount="row.total" :currency="row.currency" />
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
