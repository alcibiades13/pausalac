<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Select, Alert, EmptyState, MoneyDisplay, Metric, DataTable, Pagination, Skeleton, type DataTableColumn } from '@pausalac/ui'
import {
  listInvoices,
  getInvoiceStatusBreakdown,
  type Invoice,
  type InvoiceDocumentType,
  type InvoiceStatus,
  type InvoiceStatusBreakdown as InvoiceStatusBreakdownData,
} from '@/services/invoices'
import { STATUS_LABELS } from '@/lib/invoiceStatus'
import { DOCUMENT_TYPE_LABELS } from '@/lib/documentType'
import { useTableQuery } from '@/composables/useTableQuery'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import DocumentTypeBadge from '@/components/DocumentTypeBadge.vue'
import InvoiceStatusBreakdownChart from '@/components/charts/InvoiceStatusBreakdown.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

// Seeded from ?status=/?document_type= on first load (master prompt
// §115 deep links — e.g. the invoice_overdue notification's "Pogledaj →").
const statusFilter = ref<InvoiceStatus | ''>((route.query.status as InvoiceStatus | undefined) ?? '')
const documentTypeFilter = ref<InvoiceDocumentType | ''>(
  (route.query.document_type as InvoiceDocumentType | undefined) ?? '',
)

// Only the backend status/document-type identifiers (the Record keys) are
// used here — the Serbian label VALUES in these lib files are bypassed in
// favor of t() lookups below, so the dropdown options are translatable.
const STATUS_OPTIONS = Object.keys(STATUS_LABELS) as InvoiceStatus[]
const DOCUMENT_TYPE_OPTIONS = Object.keys(DOCUMENT_TYPE_LABELS) as InvoiceDocumentType[]

const statusSelectOptions = [
  { value: '', label: t('dashboardInvoicesClients.invoicesListView.allStatusesOption') },
  ...STATUS_OPTIONS.map((value) => ({ value, label: t(`dashboardInvoicesClients.invoiceStatusBadge.${value}`) })),
]
const documentTypeSelectOptions = [
  { value: '', label: t('dashboardInvoicesClients.invoicesListView.allTypesOption') },
  ...DOCUMENT_TYPE_OPTIONS.map((value) => ({ value, label: t(`dashboardInvoicesClients.documentTypeBadge.${value}`) })),
]

const columns: DataTableColumn<Invoice>[] = [
  { key: 'invoice_number', label: t('dashboardInvoicesClients.invoicesListView.columnNumber') },
  { key: 'client_name', label: t('dashboardInvoicesClients.invoicesListView.columnClient') },
  { key: 'issue_date', label: t('dashboardInvoicesClients.invoicesListView.columnIssueDate'), sortable: true },
  { key: 'due_date', label: t('dashboardInvoicesClients.invoicesListView.columnDueDate'), sortable: true },
  { key: 'total', label: t('dashboardInvoicesClients.invoicesListView.columnAmount') },
  { key: 'status', label: t('dashboardInvoicesClients.invoicesListView.columnStatus') },
]

const {
  rows: invoices,
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
} = useTableQuery<Invoice>(
  (q) =>
    listInvoices({
      status: statusFilter.value || undefined,
      documentType: documentTypeFilter.value || undefined,
      page: q.page,
      pageSize: q.pageSize,
      search: q.search,
      ordering: q.ordering,
    }),
  { genericErrorMessage: t('dashboardInvoicesClients.invoicesListView.loadError') },
)

onMounted(load)
watch([statusFilter, documentTypeFilter], reload)

function onRowClick(invoice: Invoice) {
  router.push({ name: 'invoice-detail', params: { id: invoice.id } })
}

// --- status breakdown (independent of the filters/table above) ----------

const breakdown = ref<InvoiceStatusBreakdownData | null>(null)
const breakdownStatus = ref<'loading' | 'ready' | 'error'>('loading')
const breakdownError = ref('')

async function loadBreakdown() {
  breakdownStatus.value = 'loading'
  try {
    breakdown.value = await getInvoiceStatusBreakdown()
    breakdownStatus.value = 'ready'
  } catch {
    breakdownError.value = t('dashboardInvoicesClients.invoicesListView.loadError')
    breakdownStatus.value = 'error'
  }
}

onMounted(loadBreakdown)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('dashboardInvoicesClients.invoicesListView.title') }}</h1>

    <!-- Stat row — the same status-breakdown data already fetched for the
         chart below, surfaced as quick numbers instead of only a donut. -->
    <div v-if="breakdownStatus === 'ready' && breakdown" class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <Card>
        <Metric :label="t('dashboardInvoicesClients.invoicesListView.statTotalLabel')">
          <MoneyDisplay :amount="breakdown.total" :currency="breakdown.currency" />
        </Metric>
      </Card>
      <Card>
        <Metric :label="t('dashboardInvoicesClients.invoicesListView.statCountLabel')">{{ breakdown.count }}</Metric>
      </Card>
      <Card>
        <Metric :label="t('dashboardInvoicesClients.invoicesListView.statOverdueLabel')">
          <span class="text-danger">{{ breakdown.overdue_count }}</span>
        </Metric>
      </Card>
      <Card>
        <Metric :label="t('dashboardInvoicesClients.invoicesListView.statPaidYtdLabel')">
          <MoneyDisplay :amount="breakdown.paid_ytd" :currency="breakdown.currency" />
        </Metric>
      </Card>
    </div>

    <Card>
      <h2 class="mb-3 text-sm font-medium text-navy">{{ t('dashboardInvoicesClients.charts.invoiceStatusBreakdown.title') }}</h2>
      <Alert v-if="breakdownStatus === 'error'" variant="danger">
        {{ breakdownError }}
        <button class="ml-2 underline" @click="loadBreakdown">{{ t('dashboardInvoicesClients.invoicesListView.retryButton') }}</button>
      </Alert>
      <Skeleton v-else-if="breakdownStatus === 'loading'" :count="1" height="240px" />
      <InvoiceStatusBreakdownChart v-else-if="breakdown" :breakdown="breakdown" />
    </Card>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="reload">{{ t('dashboardInvoicesClients.invoicesListView.retryButton') }}</button>
    </Alert>

    <Card v-else>
      <div class="flex flex-wrap items-end gap-4 border-b border-border pb-4">
        <Input
          v-model="search"
          :label="t('dashboardInvoicesClients.invoicesListView.searchLabel')"
          :placeholder="t('dashboardInvoicesClients.invoicesListView.searchPlaceholder')"
          class="min-w-[220px] flex-1"
        />
        <Select
          v-model="statusFilter"
          :label="t('dashboardInvoicesClients.invoicesListView.statusFilterLabel')"
          :options="statusSelectOptions"
        />
        <Select
          v-model="documentTypeFilter"
          :label="t('dashboardInvoicesClients.invoicesListView.typeFilterLabel')"
          :options="documentTypeSelectOptions"
        />
      </div>

      <Skeleton v-if="status === 'loading' && invoices.length === 0" class="mt-4" :count="3" />

      <EmptyState
        v-else-if="invoices.length === 0"
        class="mt-4"
        :title="t('dashboardInvoicesClients.invoicesListView.emptyTitle')"
        :description="t('dashboardInvoicesClients.invoicesListView.emptyDescription')"
      >
        <template #action>
          <RouterLink :to="{ name: 'invoice-new' }">
            <Button>{{ t('dashboardInvoicesClients.invoicesListView.newInvoiceCta') }}</Button>
          </RouterLink>
        </template>
      </EmptyState>

      <template v-else>
        <DataTable
          class="mt-4"
          :columns="columns"
          :rows="invoices"
          :loading="status === 'loading'"
          :sort="sort"
          row-clickable
          @sort="onSort"
          @row-click="onRowClick"
        >
          <template #cell-invoice_number="{ row }">
            <span class="font-mono font-medium text-navy">
              {{ row.invoice_number ?? t('dashboardInvoicesClients.invoicesListView.draftNumberFallback', { id: row.id }) }}
            </span>
          </template>
          <template #cell-total="{ row }">
            <MoneyDisplay :amount="row.total" :currency="row.currency" />
          </template>
          <template #cell-status="{ row }">
            <div class="flex items-center gap-2">
              <DocumentTypeBadge v-if="row.document_type !== 'invoice'" :type="row.document_type" />
              <InvoiceStatusBadge :status="row.status" />
            </div>
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
