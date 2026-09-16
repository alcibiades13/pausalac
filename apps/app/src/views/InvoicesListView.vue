<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Alert, EmptyState, MoneyDisplay, Skeleton } from '@pausalac/ui'
import { listInvoices, type Invoice, type InvoiceDocumentType, type InvoiceStatus } from '@/services/invoices'
import { STATUS_LABELS } from '@/lib/invoiceStatus'
import { DOCUMENT_TYPE_LABELS } from '@/lib/documentType'
import { ApiError } from '@/lib/api'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import DocumentTypeBadge from '@/components/DocumentTypeBadge.vue'

const { t } = useI18n()
const route = useRoute()
const invoices = ref<Invoice[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
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

async function load() {
  status.value = 'loading'
  try {
    const page = await listInvoices({
      status: statusFilter.value || undefined,
      documentType: documentTypeFilter.value || undefined,
    })
    invoices.value = page.results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoicesListView.loadError')
    status.value = 'error'
  }
}

onMounted(load)
watch([statusFilter, documentTypeFilter], load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-xl font-semibold text-navy">{{ t('dashboardInvoicesClients.invoicesListView.title') }}</h1>
      <!-- Desktop-only: on mobile these three actions are covered by the
           global FAB (Phase 6d, MobileBottomNav.vue) — this row was
           originally a temporary stand-in for it (docs/decisions-log.md). -->
      <div class="hidden flex-wrap gap-2 sm:flex">
        <RouterLink :to="{ name: 'invoice-new' }">
          <Button>{{ t('dashboardInvoicesClients.invoicesListView.newInvoiceButton') }}</Button>
        </RouterLink>
        <RouterLink :to="{ name: 'invoice-new-profaktura' }">
          <Button variant="secondary">{{ t('dashboardInvoicesClients.invoicesListView.newProfakturaButton') }}</Button>
        </RouterLink>
        <RouterLink :to="{ name: 'invoice-new-avans' }">
          <Button variant="secondary">{{ t('dashboardInvoicesClients.invoicesListView.newAvansButton') }}</Button>
        </RouterLink>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-4">
      <div class="flex items-center gap-2">
        <label for="status-filter" class="text-sm text-text-secondary">{{ t('dashboardInvoicesClients.invoicesListView.statusFilterLabel') }}</label>
        <select
          id="status-filter"
          v-model="statusFilter"
          class="rounded-lg border border-border bg-white px-3 py-1.5 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
        >
          <option value="">{{ t('dashboardInvoicesClients.invoicesListView.allStatusesOption') }}</option>
          <option v-for="value in STATUS_OPTIONS" :key="value" :value="value">
            {{ t(`dashboardInvoicesClients.invoiceStatusBadge.${value}`) }}
          </option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label for="document-type-filter" class="text-sm text-text-secondary">{{ t('dashboardInvoicesClients.invoicesListView.typeFilterLabel') }}</label>
        <select
          id="document-type-filter"
          v-model="documentTypeFilter"
          class="rounded-lg border border-border bg-white px-3 py-1.5 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
        >
          <option value="">{{ t('dashboardInvoicesClients.invoicesListView.allTypesOption') }}</option>
          <option v-for="value in DOCUMENT_TYPE_OPTIONS" :key="value" :value="value">
            {{ t(`dashboardInvoicesClients.documentTypeBadge.${value}`) }}
          </option>
        </select>
      </div>
    </div>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">{{ t('dashboardInvoicesClients.invoicesListView.retryButton') }}</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="invoices.length === 0">
      <EmptyState
        :title="t('dashboardInvoicesClients.invoicesListView.emptyTitle')"
        :description="t('dashboardInvoicesClients.invoicesListView.emptyDescription')"
      >
        <template #action>
          <RouterLink :to="{ name: 'invoice-new' }">
            <Button>{{ t('dashboardInvoicesClients.invoicesListView.newInvoiceCta') }}</Button>
          </RouterLink>
        </template>
      </EmptyState>
    </Card>

    <Card v-else>
      <ul class="flex flex-col divide-y divide-border">
        <li v-for="invoice in invoices" :key="invoice.id" class="py-3">
          <RouterLink
            :to="{ name: 'invoice-detail', params: { id: invoice.id } }"
            class="-mx-2 flex flex-col gap-1 rounded-lg px-2 py-1 hover:bg-background sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p class="font-mono font-medium text-navy">
                {{ invoice.invoice_number ?? t('dashboardInvoicesClients.invoicesListView.draftNumberFallback', { id: invoice.id }) }}
              </p>
              <p class="text-sm text-text-secondary">{{ invoice.client_name }}</p>
            </div>
            <div class="flex items-center gap-3">
              <MoneyDisplay :amount="invoice.total" :currency="invoice.currency" />
              <DocumentTypeBadge v-if="invoice.document_type !== 'invoice'" :type="invoice.document_type" />
              <InvoiceStatusBadge :status="invoice.status" />
            </div>
          </RouterLink>
        </li>
      </ul>
    </Card>
  </div>
</template>
